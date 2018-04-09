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
Configuration page for VirtualBox preferences.
"""

import os
import sys
import shutil
from gns3.qt import QtWidgets

from .. import VirtualBox
from ..ui.virtualbox_preferences_page_ui import Ui_VirtualBoxPreferencesPageWidget
from ..settings import VBOX_SETTINGS


class VirtualBoxPreferencesPage(QtWidgets.QWidget, Ui_VirtualBoxPreferencesPageWidget):
    """
    QWidget preference page for VirtualBox.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        # connect signals
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiVboxManagePathToolButton.clicked.connect(self._vboxPathBrowserSlot)

    def _vboxPathBrowserSlot(self):
        """
        Slot to open a file browser and select VBoxManage.
        """

        vboxmanage_path = shutil.which("vboxmanage")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select VBoxManage", vboxmanage_path)
        if not path:
            return

        if self._checkVBoxManagePath(path):
            self.uiVboxManagePathLineEdit.setText(os.path.normpath(path))

    def _checkVBoxManagePath(self, path):
        """
        Checks that the VBoxManage path is valid.

        :param path: VBoxManage path
        :returns: boolean
        """

        if not os.path.exists(path):
            QtWidgets.QMessageBox.critical(self, "VBoxManage", '"{}" does not exist'.format(path))
            return False

        if not os.access(path, os.X_OK):
            QtWidgets.QMessageBox.critical(self, "VBoxManage", "{} is not an executable".format(os.path.basename(path)))
            return False

        if sys.platform.startswith("win") and "virtualbox.exe" in path.lower():
            QtWidgets.QMessageBox.critical(self, "VBoxManage", "VBoxManage.exe must be selected instead of VirtualBox.exe")
            return False

        return True

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(VBOX_SETTINGS)

    def _useLocalServerSlot(self, state):
        """
        Slot to enable or not local server settings.
        """

        if state:
            self.uiVboxManagePathLineEdit.setEnabled(True)
            self.uiVboxManagePathToolButton.setEnabled(True)
        else:
            self.uiVboxManagePathLineEdit.setEnabled(False)
            self.uiVboxManagePathToolButton.setEnabled(False)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: VirtualBox settings
        """

        self.uiVboxManagePathLineEdit.setText(settings["vboxmanage_path"])

    def loadPreferences(self):
        """
        Loads VirtualBox preferences.
        """

        vbox_settings = VirtualBox.instance().settings()
        self._populateWidgets(vbox_settings)

    def savePreferences(self):
        """
        Saves VirtualBox preferences.
        """

        vboxmanage_path = self.uiVboxManagePathLineEdit.text().strip()
        if vboxmanage_path and not self._checkVBoxManagePath(vboxmanage_path):
            return

        new_settings = {"vboxmanage_path": vboxmanage_path}
        VirtualBox.instance().setSettings(new_settings)
