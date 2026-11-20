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

from gns3.pages.user_preferences_page import UserPreferencesPage


def test_populate_widgets_local_user():
    page = UserPreferencesPage()
    local_data = {
        "username": "localadmin",
        "full_name": "Local Administrator",
        "email": "admin@example.com",
        "auth_source": "local",
    }
    page._populateWidgets(local_data)

    assert page.uiUsernameLineEdit.text() == "localadmin"
    assert page.uiFullNameLineEdit.text() == "Local Administrator"
    assert page.uiEmailLineEdit.text() == "admin@example.com"
    assert page.uiAuthSourceLineEdit.text() == "Local account"
    assert page.uiChangePasswordPushButton.isEnabled() is True
    assert page.uiChangePasswordPushButton.toolTip() == ""
    assert page.uiCopyAccessTokenPushButton.isEnabled() is True


def test_populate_widgets_ldap_user():
    page = UserPreferencesPage()
    ldap_data = {
        "username": "alice",
        "full_name": "Alice Wonderland",
        "email": "alice@example.com",
        "auth_source": "ldap",
    }
    page._populateWidgets(ldap_data)

    assert page.uiUsernameLineEdit.text() == "alice"
    assert page.uiFullNameLineEdit.text() == "Alice Wonderland"
    assert page.uiEmailLineEdit.text() == "alice@example.com"
    assert (
        page.uiAuthSourceLineEdit.text()
        == "Directory account (LDAP / Active Directory)"
    )
    assert page.uiChangePasswordPushButton.isEnabled() is True
    assert (
        "Password is managed by your organization's directory"
        in page.uiChangePasswordPushButton.toolTip()
    )
    assert page.uiCopyAccessTokenPushButton.isEnabled() is True


def test_change_password_slot_shows_info_for_ldap(monkeypatch):
    from gns3.qt import QtWidgets

    page = UserPreferencesPage()
    ldap_data = {
        "username": "alice",
        "full_name": "Alice Wonderland",
        "email": "alice@example.com",
        "auth_source": "ldap",
    }
    page._populateWidgets(ldap_data)

    info_box_called = False

    def mock_information(parent, title, text):
        nonlocal info_box_called
        info_box_called = True
        assert "Password is managed by your organization's directory" in text

    monkeypatch.setattr(QtWidgets.QMessageBox, "information", mock_information)
    page._changePasswordSlot()
    assert info_box_called is True


def test_disconnect_slot_resets_auth_source():
    page = UserPreferencesPage()
    ldap_data = {
        "username": "alice",
        "full_name": "Alice Wonderland",
        "email": "alice@example.com",
        "auth_source": "ldap",
    }
    page._populateWidgets(ldap_data)
    assert page.uiAuthSourceLineEdit.text() != ""

    page._disconnectSlot()

    assert page.uiUsernameLineEdit.text() == ""
    assert page.uiAuthSourceLineEdit.text() == ""
    assert page.uiFullNameLineEdit.text() == ""
    assert page.uiEmailLineEdit.text() == ""
    assert page.uiChangePasswordPushButton.isEnabled() is False
    assert page.uiChangePasswordPushButton.toolTip() == ""
    assert page._auth_source is None
