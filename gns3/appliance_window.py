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


import jinja2
import os
import shutil

from .utils.get_resource import get_resource
from .qt import QtCore, QtWidgets, QtWebKit, QtWebKitWidgets, QtGui
from .ui.appliance_window_ui import Ui_ApplianceWindow
from .image_manager import ImageManager
from .registry.appliance import Appliance
from .registry.registry import Registry
from .registry.config import Config
from .registry.image import Image


import logging
log = logging.getLogger(__name__)


def human_filesize(num):
    for unit in ['B','KB','MB','GB']:
        if abs(num) < 1024.0:
            return "%3.1f%s" % (num, unit)
        num /= 1024.0
    return "%.1f%s" % (num, 'TB')


class ApplianceWindow(QtWidgets.QWidget, Ui_ApplianceWindow):

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(path)

        self._path = path

        # Call linkClickedSlot() for all non local links
        self.uiWebView.page().setLinkDelegationPolicy(QtWebKitWidgets.QWebPage.DelegateExternalLinks)
        self.uiWebView.linkClicked.connect(self._linkClickedSlot)

        # Expose JavaScript objects
        self.uiWebView.page().mainFrame().javaScriptWindowObjectCleared.connect(self.javaScriptWindowObject)

        # Enable the inspector on right click
        self.uiWebView.settings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)

        self._refresh()

        self.show()

    def _refresh(self):
        renderer = jinja2.Environment(loader=jinja2.FileSystemLoader(get_resource('templates')))
        renderer.filters['nl2br'] = lambda s: s.replace('\n', '<br />')
        renderer.filters['human_filesize'] = human_filesize
        template = renderer.get_template("appliance.html")

        registry = Registry(ImageManager.instance().getDirectory())

        try:
            self._appliance = Appliance(registry, self._path)
        except ApplianceError as e:
            QtWidgets.QMessageBox.critical(self.parent(), "Add appliance", str(e))

        self.uiWebView.setHtml(template.render(appliance=self._appliance, registry=registry))

    def javaScriptWindowObject(self):
        frame = self.uiWebView.page().mainFrame()
        frame.addToJavaScriptWindowObject('gns3', self)

    def _linkClickedSlot(self, url):
        """
        Open in a new browser other url
        """
        QtGui.QDesktopServices.openUrl(url)

    #
    # Public Javascript methods
    #
    @QtCore.pyqtSlot(str)
    def install(self, version):
        """
        Install an appliance based on appliance version

        :param version: Version to install
        """

        try:
            config = Config()
        except OSError as e:
            QtWidgets.QMessageBox.critical(self.parent(), "Add appliance", str(e))
            self.close()
            return

        appliance_configuration = self._appliance.search_images_for_version(version)

        if config.servers == ["local"]:
            server = "local"
        else:
            server_types = {}
            for server in Config().servers:
                if server == "local":
                    server_types["Local server"] = server
                elif server == "vm":
                    server_types["GNS3 VM"] = server
                else:
                    server_types[server] = server
            selection, ok = QtWidgets.QInputDialog.getItem(self.parent(), "GNS3 server", "Please select a GNS3 server:", list(server_types.keys()), 0, False)
            if ok:
                server = server_types[selection]
            else:
                return

        if config.add_appliance(appliance_configuration, server):
            self.close()
            try:
                config.save()
            except OSError as e:
                QtWidgets.QMessageBox.critical(self.parent(), "Add appliance", str(e))
                return
            QtWidgets.QMessageBox.information(self.parent(), "Add appliance", "{} {} installed!".format(self._appliance["name"], version))

    @QtCore.pyqtSlot(str, str)
    def importAppliance(self, filename, md5sum):
        path, _ = QtWidgets.QFileDialog.getOpenFileName()
        if len(path) == 0:
            return

        #Do not create temporary file
        md5 = Image(path, cache=False).md5sum
        if md5 != md5sum:
            QtWidgets.QMessageBox.warning(self.parent(), "Add appliance", "This is not the correct image file.")
            return

        try:
            config = Config()
            #TODO: ASK for VM type
            os.makedirs(os.path.join(config.images_dir, "QEMU"), exist_ok=True)
            dst_path = os.path.join(config.images_dir, "QEMU", filename)
            shutil.copy(path, dst_path)
            md5 = Image(dst_path).md5sum
        except OSError as e:
            QtWidgets.QMessageBox.critical(self.parent(), "Add appliance", str(e))
            return False

        self._refresh()
