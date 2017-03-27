# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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

import os
import sys
import shutil

from gns3.qt import QtWidgets
from gns3.local_config import LocalConfig
from gns3.ui.profile_select_dialog_ui import Ui_ProfileSelectDialog

import logging
log = logging.getLogger(__name__)


class ProfileSelectDialog(QtWidgets.QDialog, Ui_ProfileSelectDialog):
    """
    This dialog allow user to choose a profile of settings
    """

    def __init__(self, parent=None):

        if parent is None:
            self._main = QtWidgets.QMainWindow()
            self._main.hide()
            parent = self._main
        super().__init__(parent)
        self.setupUi(self)

        self.uiNewPushButton.clicked.connect(self._newPushButtonSlot)
        self.uiDeletePushButton.clicked.connect(self._deletePushButtonSlot)

        # Center on screen
        screen = QtWidgets.QApplication.desktop().screenGeometry()
        self.move(screen.center() - self.rect().center())

        if sys.platform.startswith("win"):
            appdata = os.path.expandvars("%APPDATA%")
            path = os.path.join(appdata, "GNS3")
        else:
            home = os.path.expanduser("~")
            path = os.path.join(home, ".config", "GNS3")
        self.profiles_path = os.path.join(path, "profiles")

        self.uiShowAtStartupCheckBox.setChecked(LocalConfig.instance().multiProfiles())
        self._refresh()

    def _refresh(self):
        self.uiProfileSelectComboBox.clear()
        self.uiProfileSelectComboBox.addItem("default")

        try:
            if os.path.exists(self.profiles_path):
                for profil in sorted(os.listdir(self.profiles_path)):
                    if not profil.startswith("."):
                        self.uiProfileSelectComboBox.addItem(profil)
        except OSError:
            pass

    def profile(self):
        return self.uiProfileSelectComboBox.currentText()

    def accept(self):
        LocalConfig.instance().setMultiProfiles(self.uiShowAtStartupCheckBox.isChecked())
        super().accept()

    def _newPushButtonSlot(self):
        profile, ok = QtWidgets.QInputDialog.getText(self.parent(), "New profile", "Profile name:")
        if ok:
            self.uiProfileSelectComboBox.addItem(profile)
            self.uiProfileSelectComboBox.setCurrentText(profile)
            self.accept()

    def _deletePushButtonSlot(self):
        profile = self.uiProfileSelectComboBox.currentText()
        if profile == "default":
            QtWidgets.QMessageBox.critical(self.parentWidget(), "Delete profile", "You can't delete the default profile")
        else:
            try:
                shutil.rmtree(os.path.join(self.profiles_path, profile))
                self._refresh()
            except (OSError, PermissionError) as e:
                QtWidgets.QMessageBox.critical(self.parentWidget(), "Delete profile", str(e))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = ProfileSelectDialog()
    dialog.show()
    exit_code = app.exec_()
