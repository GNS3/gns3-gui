#
# Copyright (C) 2025 GNS3 Technologies Inc.
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

import logging
import re

from ..qt import QtGui, QtWidgets
from ..ui.password_dialog_ui import Ui_PasswordDialog

log = logging.getLogger(__name__)


class PasswordDialog(QtWidgets.QDialog, Ui_PasswordDialog):
    """
    Password dialog.
    """

    def __init__(self, parent):
        """
        :param parent: parent widget.
        """

        super().__init__(parent)
        self.setupUi(self)
        self._password = None

        self._eye_on_icon = QtGui.QIcon(":/icons/eye-on.svg")
        self._eye_off_icon = QtGui.QIcon(":/icons/eye-off.svg")
        for line_edit in [self.uiPasswordLineEdit, self.uiConfirmPasswordLineEdit]:
            action = line_edit.addAction(
                self._eye_on_icon, QtWidgets.QLineEdit.ActionPosition.TrailingPosition
            )
            action.triggered.connect(
                lambda checked=False, le=line_edit, act=action: (
                    self._togglePasswordVisibility(le, act)
                )
            )

    def _togglePasswordVisibility(self, line_edit, action):
        if line_edit.echoMode() == QtWidgets.QLineEdit.EchoMode.Password:
            action.setIcon(self._eye_off_icon)
            line_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        else:
            action.setIcon(self._eye_on_icon)
            line_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

    # def onReleasedSlot(self):
    #
    #     button = self.sender()
    #     button.setIcon(self._eye_on_icon)
    #     button.parent().setEchoMode(QtWidgets.QLineEdit.Password)

    def getPassword(self):

        return self._password

    def done(self, result):

        if result:
            new_password = self.uiPasswordLineEdit.text()
            confirm_password = self.uiConfirmPasswordLineEdit.text()
            if new_password != confirm_password:
                QtWidgets.QMessageBox.critical(self, "Error", "Passwords do not match.")
                return
            pattern = re.compile(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$")
            if not pattern.match(new_password):
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    "Password must be at least 8 characters long and contain at least one digit, one lowercase letter and one uppercase letter.",
                )
                return
            self._password = new_password
        super().done(result)
