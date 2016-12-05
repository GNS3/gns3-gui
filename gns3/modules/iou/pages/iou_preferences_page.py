# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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

"""
Configuration page for IOU preferences.
"""

import os
import sys
import shutil

from gns3.qt import QtCore, QtWidgets, qpartial
from gns3.controller import Controller

from .. import IOU
from ..ui.iou_preferences_page_ui import Ui_IOUPreferencesPageWidget
from ..settings import IOU_SETTINGS


class IOUPreferencesPage(QtWidgets.QWidget, Ui_IOUPreferencesPageWidget):

    """
    QWidget preference page for IOU.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        # connect signals
        self.uiIOURCPathToolButton.clicked.connect(self._iourcPathBrowserSlot)
        self.uiIouyapPathToolButton.clicked.connect(self._iouyapPathBrowserSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)

        #if not sys.platform.startswith("linux"):
        #    self.uiUseLocalServercheckBox.setChecked(False)
        #    self.uiUseLocalServercheckBox.setEnabled(False)

    def _iourcPathBrowserSlot(self):
        """
        Slot to open a file browser and select an iourc file
        """

        documents_path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the IOURC file", documents_path)
        if not path:
            return

        try:
            with open(path) as f:
                content = f.read().strip()
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "IOURC file", "{} cannot be read.\n{}".format(os.path.basename(path), str(e)))
            return
        except UnicodeDecodeError as e:
            QtWidgets.QMessageBox.critical(self, "IOURC file", "{} is not a licence file.".format(os.path.basename(path)))
            return
        if not content.startswith("[license]"):
            QtWidgets.QMessageBox.critical(self, "IOURC file", "This is not a valid IOURC file")
            return

        self.IOULicenceTextEdit.setPlainText(content)

    def _iouyapPathBrowserSlot(self):
        """
        Slot to open a file browser and select iouyap.
        """

        filter = ""
        if sys.platform.startswith("win"):
            filter = "Executable (*.exe);;All files (*.*)"

        iouyap_path = shutil.which("iouyap")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select iouyap", iouyap_path, filter)
        if not path:
            return

        if self._checkIouyapPath(path):
            self.uiIouyapPathLineEdit.setText(os.path.normpath(path))

    def _checkIouyapPath(self, path):
        """
        Checks that the iouyap path is valid.

        :param path: iouyap path
        :returns: boolean
        """

        if not os.path.exists(path):
            QtWidgets.QMessageBox.critical(self, "iouyap", '"{}" does not exist'.format(path))
            return False

        if not os.access(path, os.X_OK):
            QtWidgets.QMessageBox.critical(self, "iouyap", "{} is not an executable".format(os.path.basename(path)))
            return False

        return True

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(IOU_SETTINGS)

    def _useLocalServerSlot(self, state):
        """
        Slot to enable or not local server settings.
        """

        if state:
            self.uiIouyapPathLineEdit.setEnabled(True)
            self.uiIouyapPathToolButton.setEnabled(True)
            self.uiLicensecheckBox.setEnabled(True)
        else:
            self.uiIouyapPathLineEdit.setEnabled(False)
            self.uiIouyapPathToolButton.setEnabled(False)
            self.uiLicensecheckBox.setEnabled(False)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: IOU settings
        """

        self.IOULicenceTextEdit.setPlainText(settings["iourc_content"])
        self.uiIouyapPathLineEdit.setText(settings["iouyap_path"])
        self.uiLicensecheckBox.setChecked(settings["license_check"])

    def loadPreferences(self):
        """
        Loads IOU preferences.
        """

        iou_settings = IOU.instance().settings()
        self._populateWidgets(iou_settings)

    def savePreferences(self):
        """
        Saves IOU preferences.
        """

        iouyap_path = self.uiIouyapPathLineEdit.text().strip()
        if iouyap_path and not self._checkIouyapPath(iouyap_path):
            return

        iourc_content = self.IOULicenceTextEdit.toPlainText().strip().replace("\r\n", "\n")

        new_settings = {"iouyap_path": iouyap_path,
                        "iourc_content": iourc_content,
                        "license_check": self.uiLicensecheckBox.isChecked()}
        IOU.instance().setSettings(new_settings)
