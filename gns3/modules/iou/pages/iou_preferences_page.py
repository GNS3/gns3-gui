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

from gns3.qt import QtGui

from .. import IOU
from ..ui.iou_preferences_page_ui import Ui_IOUPreferencesPageWidget
from ..settings import IOU_SETTINGS


class IOUPreferencesPage(QtGui.QWidget, Ui_IOUPreferencesPageWidget):

    """
    QWidget preference page for IOU.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        # connect signals
        self.uiIOURCPathToolButton.clicked.connect(self._iourcPathBrowserSlot)
        self.uiIouyapPathToolButton.clicked.connect(self._iouyapPathBrowserSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiUseLocalServercheckBox.stateChanged.connect(self._useLocalServerSlot)

        if not sys.platform.startswith("linux"):
            self.uiUseLocalServercheckBox.setChecked(False)
            self.uiUseLocalServercheckBox.setEnabled(False)

    def _iourcPathBrowserSlot(self):
        """
        Slot to open a file browser and select an iourc file
        """

        path = QtGui.QFileDialog.getOpenFileName(self, "Select the IOURC file", ".")
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "IOURC file", "{} cannot be read".format(os.path.basename(path)))
            return

        self.uiIOURCPathLineEdit.setText(os.path.normpath(path))

    def _iouyapPathBrowserSlot(self):
        """
        Slot to open a file browser and select iouyap.
        """

        filter = ""
        if sys.platform.startswith("win"):
            filter = "Executable (*.exe);;All files (*.*)"
        path = QtGui.QFileDialog.getOpenFileName(self, "Select iouyap", ".", filter)
        if not path:
            return

        if not os.access(path, os.X_OK):
            QtGui.QMessageBox.critical(self, "iouyap", "{} is not an executable".format(os.path.basename(path)))
            return

        self.uiIouyapPathLineEdit.setText(os.path.normpath(path))

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

        self.uiIOURCPathLineEdit.setText(settings["iourc_path"])
        self.uiIouyapPathLineEdit.setText(settings["iouyap_path"])
        self.uiLicensecheckBox.setChecked(settings["license_check"])
        self.uiUseLocalServercheckBox.setChecked(settings["use_local_server"])

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

        new_settings = {}
        new_settings["iourc_path"] = self.uiIOURCPathLineEdit.text()
        new_settings["iouyap_path"] = self.uiIouyapPathLineEdit.text()
        new_settings["license_check"] = self.uiLicensecheckBox.isChecked()
        new_settings["use_local_server"] = self.uiUseLocalServercheckBox.isChecked()
        IOU.instance().setSettings(new_settings)
