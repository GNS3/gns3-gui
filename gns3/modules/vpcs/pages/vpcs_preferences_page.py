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
import shutil

from gns3.qt import QtWidgets

from .. import VPCS
from ..ui.vpcs_preferences_page_ui import Ui_VPCSPreferencesPageWidget
from ..settings import VPCS_SETTINGS


class VPCSPreferencesPage(QtWidgets.QWidget, Ui_VPCSPreferencesPageWidget):

    """
    QWidget preference page for VPCS
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        # connect signals
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiVPCSPathToolButton.clicked.connect(self._vpcsPathBrowserSlot)

    def _vpcsPathBrowserSlot(self):
        """
        Slot to open a file browser and select vpcs
        """

        filter = ""
        if sys.platform.startswith("win"):
            filter = "Executable (*.exe);;All files (*.*)"
        vpcs_path = shutil.which("vpcs")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select VPCS", vpcs_path, filter)
        if not path:
            return

        if self._checkVPCSPath(path):
            self.uiVPCSPathLineEdit.setText(os.path.normpath(path))

    def _checkVPCSPath(self, path):
        """
        Checks that the VPCS path is valid.

        :param path: VPCS path
        :returns: boolean
        """

        if not os.path.exists(path):
            QtWidgets.QMessageBox.critical(self, "VPCS", '"{}" does not exist'.format(path))
            return False

        if not os.access(path, os.X_OK):
            QtWidgets.QMessageBox.critical(self, "VPCS", "{} is not an executable".format(os.path.basename(path)))
            return False

        return True

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

        vpcs_path = self.uiVPCSPathLineEdit.text().strip()
        if vpcs_path and not self._checkVPCSPath(vpcs_path):
            return
        new_settings = {"vpcs_path": vpcs_path}
        VPCS.instance().setSettings(new_settings)
