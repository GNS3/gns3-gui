#
# Copyright (C) 2026 GNS3 Technologies Inc.
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

from gns3.dialogs.password_dialog import PasswordDialog
from gns3.qt import QtWidgets


def test_password_dialog_init():
    dialog = PasswordDialog(None)
    assert dialog.uiPasswordLineEdit.echoMode() == QtWidgets.QLineEdit.EchoMode.Password
    assert (
        dialog.uiConfirmPasswordLineEdit.echoMode()
        == QtWidgets.QLineEdit.EchoMode.Password
    )


def test_password_dialog_toggle_visibility():
    dialog = PasswordDialog(None)
    actions = dialog.uiPasswordLineEdit.actions()
    assert len(actions) == 1

    action = actions[0]
    # Toggle to Normal
    action.trigger()
    assert dialog.uiPasswordLineEdit.echoMode() == QtWidgets.QLineEdit.EchoMode.Normal

    # Toggle back to Password
    action.trigger()
    assert dialog.uiPasswordLineEdit.echoMode() == QtWidgets.QLineEdit.EchoMode.Password
