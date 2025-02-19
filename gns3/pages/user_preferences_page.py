# -*- coding: utf-8 -*-
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

"""
Configuration page for user preferences.
"""

from gns3.qt import QtWidgets, qslot, sip_is_deleted
from ..ui.user_preferences_page_ui import Ui_UserPreferencesPageWidget
from gns3.controller import Controller
from gns3.dialogs.password_dialog import PasswordDialog

import logging
log = logging.getLogger(__name__)


class UserPreferencesPage(QtWidgets.QWidget, Ui_UserPreferencesPageWidget):

    """
    QWidget configuration page for user preferences.
    """

    def __init__(self, parent=None):

        super().__init__()
        self.setupUi(self)

        self.uiChangePasswordPushButton.clicked.connect(self._changePasswordSlot)
        self.uiCopyAccessTokenPushButton.clicked.connect(self._copyAccessTokenSlot)
        self.uiChangePasswordPushButton.setEnabled(False)
        self.uiCopyAccessTokenPushButton.setEnabled(False)
        Controller.instance().connected_signal.connect(self.loadPreferences)
        Controller.instance().disconnected_signal.connect(self._disconnectSlot)

    def _populateWidgets(self, result):
        """
        Populates the widgets with the user information.

        :param result: user information
        """

        self.uiUsernameLineEdit.setText(result.get("username", "N/A"))
        self.uiFullNameLineEdit.setText(result.get("full_name", "N/A"))
        self.uiEmailLineEdit.setText(result.get("email", "N/A"))
        self.uiChangePasswordPushButton.setEnabled(True)
        self.uiCopyAccessTokenPushButton.setEnabled(True)

    def _disconnectSlot(self):
        """
        Resets the widgets when the controller is disconnected.
        """

        self.uiUsernameLineEdit.clear()
        self.uiFullNameLineEdit.clear()
        self.uiEmailLineEdit.clear()
        self.uiChangePasswordPushButton.setEnabled(False)
        self.uiCopyAccessTokenPushButton.setEnabled(False)

    def loadPreferences(self):
        """
        Loads the user preferences.
        """

        if Controller.instance().connected():
            Controller.instance().get("/access/users/me", self._getUserInfoCallback)
        else:
            log.error("Cannot load the user information in the preferences dialog: not connected to the controller")

    @qslot
    def _getUserInfoCallback(self, result, error=False, **kwargs):
        """
        Callback to get the user information.
        """

        if sip_is_deleted(self):
            return
        if error:
            if "message" in result:
                log.error("Error while getting the logged-in user information: {}".format(result["message"]))
            return
        self._populateWidgets(result)

    def savePreferences(self):
        """
        Saves the user preferences.
        """

        pass

    def _changePasswordSlot(self):
        """
        Slot to change the user password.
        """

        dialog = PasswordDialog(self)
        if dialog.exec_():
            password = dialog.getPassword()
            new_settings = {"password": password}
            Controller.instance().put("/access/users/me", self._saveUserSettingsCallback, new_settings)

    def _saveUserSettingsCallback(self, result, error=False, **kwargs):
        """
        Callback to save the user settings.
        """

        if error and "message" in result:
            QtWidgets.QMessageBox.critical(
                self,
                "Save user settings",
                "Error while saving user settings: {}".format(result["message"])
            )
        else:
            QtWidgets.QMessageBox.information(self, "Change password", "New password saved successfully")

    def _copyAccessTokenSlot(self):
        """
        Slot to copy the access token to the clipboard.
        """

        if Controller.instance().connected():
            token = Controller.instance().httpClient().getToken()
            if token:
                QtWidgets.QApplication.clipboard().setText(token)
                log.info("Access token copied to the clipboard")
