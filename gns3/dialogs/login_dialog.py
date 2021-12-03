# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 GNS3 Technologies Inc.
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

from ..qt import QtWidgets
from ..ui.login_dialog_ui import Ui_LoginDialog


import logging
log = logging.getLogger(__name__)


class LoginDialog(QtWidgets.QDialog, Ui_LoginDialog):

    """
    Login dialog.
    """

    def __init__(self, parent):
        """
        :param parent: parent widget.
        """

        super().__init__(parent)
        self.setupUi(self)
        self._parent = parent
        self._username = None
        self._password = None

    def getUsername(self):

        return self._username

    def setUsername(self, username):

        self.uiUsernameLineEdit.setText(username)

    def getPassword(self):

        return self._password

    def done(self, result):

        if result:
            self._username = self.uiUsernameLineEdit.text()
            self._password = self.uiPasswordLineEdit.text()
        super().done(result)
