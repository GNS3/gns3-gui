#!/usr/bin/env python
#
# Copyright (C) 2015 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import tarfile
import os
import shutil
import json
import re


from gns3.utils import parse_version

from gns3 import version
from gns3.qt import QtNetwork, QtCore, QtWidgets, QtGui, qslot
from gns3.local_config import LocalConfig


import logging
log = logging.getLogger(__name__)


class UpdateManager(QtCore.QObject):

    """
    Manage application updates
    """

    def __init__(self):

        super().__init__()

        if sys.platform.startswith("win"):
            root = os.path.join(os.path.expandvars("%APPDATA%"), "GNS3")
        else:
            root = os.path.dirname(sys.executable)
        self._update_directory = os.path.join(root, 'updates')
        self._package_directory = os.path.join(root, 'site-packages')
        self._network_manager = None

    def isDevVersion(self):
        """
        :returns: Boolean. True if it's a dev build. False it's a release build
        """
        if version.__version_info__[3] != 0:
            return True
        return False

    def _get(self, url, finished_slot, user_attribute=None):
        """
        HTTP get

        :param url: Url to download
        :param user_attribute: Param to pass to the finished slot
        :returns: QNetworkReply
        """
        if self._network_manager is None:
            self._network_manager = QtNetwork.QNetworkAccessManager()
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        request.setRawHeader(b'User-Agent', b'GNS3 Check For Update')
        request.setAttribute(QtNetwork.QNetworkRequest.User, user_attribute)
        if parse_version(QtCore.QT_VERSION_STR) >= parse_version("5.6.0") and parse_version(QtCore.PYQT_VERSION_STR) >= parse_version("5.6.0"):
            # follow redirects only supported starting with Qt 5.6.0
            request.setAttribute(QtNetwork.QNetworkRequest.FollowRedirectsAttribute, True)
        reply = self._network_manager.get(request)
        reply.finished.connect(finished_slot)
        log.debug('Download %s', url)
        return reply

    def checkForUpdate(self, parent, silent):
        """
        Check for update. Start by asking PyPi for minor upgrade
        and next GNS3 for major upgrade.

        :param parent: Parent Windows
        :param silent: Display or not the notifications
        """
        self._silent = silent
        self._parent = parent

        if hasattr(sys, "frozen") and LocalConfig.instance().experimental():
            url = 'https://pypi.org/pypi/gns3-gui/json'
            self._get(url, self._pypiReplySlot)
        else:
            self._get('http://update.gns3.net', self._gns3UpdateReplySlot)

    @qslot
    def _gns3UpdateReplySlot(self):
        network_reply = self.sender()
        if network_reply is None:
            return
        if network_reply.error() != QtNetwork.QNetworkReply.NoError:
            if not self._silent:
                QtWidgets.QMessageBox.critical(self._parent, "Check For Update", "Cannot check for update: {}".format(network_reply.errorString()))
            return
        try:
            latest_release = bytes(network_reply.readAll()).decode("utf-8").rstrip()
        except UnicodeDecodeError:
            log.debug("Invalid answer from the update server")
            return
        if re.match(r"^[a-z0-9\.]+$", latest_release) is None:
            log.debug("Invalid answer from the update server")
            return
        if parse_version(version.__version__) < parse_version(latest_release):
            reply = QtWidgets.QMessageBox.question(self._parent,
                                                   "Check For Update",
                                                   "Newer GNS3 version {} is available, do you want to visit our website to download it?".format(latest_release),
                                                   QtWidgets.QMessageBox.Yes,
                                                   QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://www.gns3.com/software"))
        elif not self._silent:
            QtWidgets.QMessageBox.information(self._parent, "Check For Update", "GNS3 is up-to-date!")

    def _pypiReplySlot(self):
        network_reply = self.sender()
        if network_reply.error() != QtNetwork.QNetworkReply.NoError:
            if not self._silent:
                QtWidgets.QMessageBox.critical(self._parent, "Check For Update", "Cannot check for update: {}".format(network_reply.errorString()))
            return
        try:
            body = bytes(network_reply.readAll()).decode("utf-8")
            body = json.loads(body)
        except (UnicodeEncodeError, ValueError) as e:
            log.warning("Invalid answer from the PyPi server: {}".format(e))
            QtWidgets.QMessageBox.critical(self._parent, "Check For Update", "Invalid answer from PyPi server")
            return

        last_version = self._getLastMinorVersionFromPyPiReply(body)
        if parse_version(last_version) > parse_version(version.__version__):
            reply = QtWidgets.QMessageBox.question(self._parent,
                                                   "Check For Update",
                                                   "Newer GNS3 version {} is available, do you want to to download it in background and install it at next application launch?".format(last_version),
                                                   QtWidgets.QMessageBox.Yes,
                                                   QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                try:
                    self.downloadUpdates(last_version)
                except OSError as e:
                    QtWidgets.QMessageBox.critical(self._parent, "Check For Update", "Cannot download update: {}".format(e))
        else:
            self._get('http://update.gns3.net', self._gns3UpdateReplySlot)

    def _getLastMinorVersionFromPyPiReply(self, body):
        """
        Return the most recent minor version for this release
        from a PyPi answer.

        If no valid version is found it's return the current.
        """

        current_version = parse_version(version.__version__)
        for release in sorted(body['releases'].keys(), reverse=True):
            release_version = parse_version(release)
            if release_version[-1:][0] == "final":
                if self.isDevVersion():
                    continue
            else:
                if not self.isDevVersion():
                    continue
            if release_version > current_version and release_version[:2] == current_version[:2]:
                return release
        return version.__version__

    def downloadUpdates(self, version):
        """
        Download updates from PyPi to disk

        :param version: The version to download
        """
        log.debug('Download updates to %s', self._package_directory)
        os.makedirs(self._update_directory, exist_ok=True)
        self._filesToDownload = 2
        url = 'https://pypi.python.org/packages/source/g/gns3-server/gns3-server-{}.tar.gz'.format(version)
        self._get(url, self._fileDownloadedSlot, user_attribute=os.path.join(self._update_directory, 'gns3-server.tar.gz'))
        url = 'https://pypi.python.org/packages/source/g/gns3-gui/gns3-gui-{}.tar.gz'.format(version)
        self._get(url, self._fileDownloadedSlot, user_attribute=os.path.join(self._update_directory, 'gns3-gui.tar.gz'))

    def _fileDownloadedSlot(self):
        network_reply = self.sender()
        file_path = network_reply.request().attribute(QtNetwork.QNetworkRequest.User)
        if network_reply.error() == QtNetwork.QNetworkReply.NoError:
            log.debug('File downloaded %s', file_path)
            with open(file_path, 'wb+') as f:
                f.write(network_reply.readAll())
            self._filesToDownload -= 1
            if self._filesToDownload == 0:
                reply = QtWidgets.QMessageBox.question(self._parent,
                                                       "Check For Update",
                                                       "GNS3 upgrade downloaded do you want to quit the application?",
                                                       QtWidgets.QMessageBox.Yes,
                                                       QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    QtWidgets.QApplication.instance().closeAllWindows()
        else:
            log.debug('Error when downloading %s', file_path)
        network_reply.deleteLater()

    def installDownloadedUpdates(self):
        """
        If update have been downloaded and
        ready for install we process the install

        :returns: Boolean True if an update is installed
        """

        if os.path.exists(self._update_directory):
            os.makedirs(self._package_directory, exist_ok=True)

            gui_tgz = os.path.join(self._update_directory, 'gns3-gui.tar.gz')
            self._extractTgz(gui_tgz)
            server_tgz = os.path.join(self._update_directory, 'gns3-server.tar.gz')
            self._extractTgz(server_tgz)
            shutil.rmtree(self._update_directory, ignore_errors=True)
            return True
        return False

    def _extractTgz(self, tgz):
        if os.path.exists(tgz):
            log.info('Extract update %s', tgz)
            with tarfile.open(tgz, 'r:gz') as tar:
                # Tar add a folder with the name of archive in first position
                # we need to drop it
                members = tar.getmembers()[1:]
                for member in members:
                    # Path separator is always / even on windows
                    member.name = member.name.split("/", 1)[1]
                tar.extractall(path=self._package_directory, members=members)
