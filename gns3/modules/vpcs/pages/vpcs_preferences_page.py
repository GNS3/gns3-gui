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
Configuration page for VPCS preferences.
"""

import os
import sys

from gns3.qt import QtCore, QtGui

from .. import VPCS
from ..ui.vpcs_preferences_page_ui import Ui_VPCSPreferencesPageWidget
from ..settings import VPCS_SETTINGS


class VPCSPreferencesPage(QtGui.QWidget, Ui_VPCSPreferencesPageWidget):

    """
    QWidget preference page for VPCS
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        # connect signals
        self.uiUseLocalServercheckBox.stateChanged.connect(self._useLocalServerSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiVPCSPathToolButton.clicked.connect(self._vpcsPathBrowserSlot)
        self.uiScriptFileToolButton.clicked.connect(self._scriptFileBrowserSlot)

    def _vpcsPathBrowserSlot(self):
        """
        Slot to open a file browser and select vpcs
        """

        filter = ""
        if sys.platform.startswith("win"):
            filter = "Executable (*.exe);;All files (*.*)"
        path = QtGui.QFileDialog.getOpenFileName(self, "Select VPCS", ".", filter)
        if not path:
            return

        if not os.access(path, os.X_OK):
            QtGui.QMessageBox.critical(self, "VPCS", "{} is not an executable".format(os.path.basename(path)))
            return

        self.uiVPCSPathLineEdit.setText(os.path.normpath(path))

    def _scriptFileBrowserSlot(self):
        """
        Slot to open a file browser and select a base script file for VPCS
        """

        config_dir = os.path.join(os.path.dirname(QtCore.QSettings().fileName()), "base_configs")
        path = QtGui.QFileDialog.getOpenFileName(self, "Select a script file", config_dir)
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "Script file", "{} cannot be read".format(os.path.basename(path)))
            return

        self.uiScriptFileEdit.setText(os.path.normpath(path))

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(VPCS_SETTINGS)

    def _useLocalServerSlot(self, state):
        """
        Slot to enable or not local server settings.
        """

        if state:
            self.uiVPCSPathLineEdit.setEnabled(True)
            self.uiVPCSPathToolButton.setEnabled(True)
        else:
            self.uiVPCSPathLineEdit.setEnabled(False)
            self.uiVPCSPathToolButton.setEnabled(False)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: VPCS settings
        """

        self.uiVPCSPathLineEdit.setText(settings["vpcs_path"])
        self.uiScriptFileEdit.setText(settings["base_script_file"])
        self.uiUseLocalServercheckBox.setChecked(settings["use_local_server"])

    def loadPreferences(self):
        """
        Loads VPCS preferences.
        """

        vpcs_settings = VPCS.instance().settings()
        self._populateWidgets(vpcs_settings)

    def savePreferences(self):
        """
        Saves VPCS preferences.
        """

        new_settings = {}
        new_settings["vpcs_path"] = self.uiVPCSPathLineEdit.text()
        new_settings["base_script_file"] = self.uiScriptFileEdit.text()
        new_settings["use_local_server"] = self.uiUseLocalServercheckBox.isChecked()
        VPCS.instance().setSettings(new_settings)
