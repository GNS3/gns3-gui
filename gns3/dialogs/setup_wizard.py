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

import sys
import os
import shutil

from gns3.qt import QtCore, QtWidgets, QtNetwork
from gns3.controller import Controller
from gns3.local_server import LocalServer

from ..settings import DEFAULT_CONTROLLER_HOST
from ..ui.setup_wizard_ui import Ui_SetupWizard


import logging
log = logging.getLogger(__name__)


class SetupWizard(QtWidgets.QWizard, Ui_SetupWizard):

    """
    Base class for VM wizard.
    """

    def __init__(self, parent):

        super().__init__(parent)
        self.setupUi(self)
        self.adjustSize()

        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        if sys.platform.startswith("darwin"):
            # we want to see the cancel button on OSX
            self.setOptions(QtWidgets.QWizard.NoDefaultButton)

        self.uiLocalServerToolButton.clicked.connect(self._localServerBrowserSlot)
        settings = parent.settings()
        self.uiShowCheckBox.setChecked(settings["hide_setup_wizard"])

        # Mandatory fields
        self.uiLocalControllerWizardPage.registerField("path*", self.uiLocalServerPathLineEdit)

        # load all available addresses
        for address in QtNetwork.QNetworkInterface.allAddresses():
            if address.protocol() in [QtNetwork.QAbstractSocket.IPv4Protocol, QtNetwork.QAbstractSocket.IPv6Protocol]:
                address_string = address.toString()
                if address_string.startswith("169.254") or address_string.startswith("fe80"):
                    # ignore link-local addresses, could not use https://doc.qt.io/qt-5/qhostaddress.html#isLinkLocal
                    # because it was introduced in Qt 5.11
                    continue
                self.uiLocalServerHostComboBox.addItem(address_string, address_string)

        self.uiLocalServerHostComboBox.addItem("localhost", "localhost")  # local host
        self.uiLocalServerHostComboBox.addItem("::", "::")  # all IPv6 addresses
        self.uiLocalServerHostComboBox.addItem("0.0.0.0", "0.0.0.0")  # all IPv4 addresses

        if sys.platform.startswith("linux"):
            # only support local controller on Linux
            self.uiLocalControllerRadioButton.setChecked(True)
        else:
            self.uiLocalControllerRadioButton.setEnabled(False)
            self.uiRemoteControllerRadioButton.setChecked(True)

    def _localServerBrowserSlot(self):
        """
        Slot to open a file browser and select a local server.
        """

        filter = ""
        if sys.platform.startswith("win"):
            filter = "Executable (*.exe);;All files (*.*)"
        server_path = shutil.which("gns3server")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the local server", server_path, filter)
        if not path:
            return

        self.uiLocalServerPathLineEdit.setText(path)

    def _setPreferencesPane(self, dialog, name):
        """
        Finds the first child of the QTreeWidgetItem name.

        :param dialog: PreferencesDialog instance
        :param name: QTreeWidgetItem name

        :returns: current QWidget
        """

        pane = dialog.uiTreeWidget.findItems(name, QtCore.Qt.MatchFixedString)[0]
        child_pane = pane.child(0)
        dialog.uiTreeWidget.setCurrentItem(child_pane)
        return dialog.uiStackedWidget.currentWidget()

    def initializePage(self, page_id):
        """
        Initialize Wizard pages.

        :param page_id: page identifier
        """

        super().initializePage(page_id)
        if self.page(page_id) == self.uiControllerWizardPage:
            Controller.instance().setDisplayError(False)
        elif self.page(page_id) == self.uiLocalControllerWizardPage:
            local_server_settings = LocalServer.instance().localServerSettings()
            self.uiLocalServerPathLineEdit.setText(local_server_settings["path"])
            index = self.uiLocalServerHostComboBox.findData(local_server_settings["host"])
            if index != -1:
                self.uiLocalServerHostComboBox.setCurrentIndex(index)
            else:
                index = self.uiLocalServerHostComboBox.findText(DEFAULT_CONTROLLER_HOST)
                if index != -1:
                    self.uiLocalServerHostComboBox.setCurrentIndex(index)

            self.uiLocalServerPortSpinBox.setValue(local_server_settings["port"])

        elif self.page(page_id) == self.uiRemoteControllerWizardPage:
            local_server_settings = LocalServer.instance().localServerSettings()
            if local_server_settings["host"] is None:
                self.uiRemoteMainServerHostLineEdit.setText(DEFAULT_CONTROLLER_HOST)
                self.uiRemoteMainServerUserLineEdit.setText("")
                self.uiRemoteMainServerPasswordLineEdit.setText("")
            else:
                self.uiRemoteMainServerHostLineEdit.setText(local_server_settings["host"])
                self.uiRemoteMainServerUserLineEdit.setText(local_server_settings["username"])
                self.uiRemoteMainServerPasswordLineEdit.setText(local_server_settings["password"])
            self.uiRemoteMainServerPortSpinBox.setValue(local_server_settings["port"])
        elif self.page(page_id) == self.uiSummaryWizardPage:
            self.uiSummaryTreeWidget.clear()
            if self.uiLocalControllerRadioButton.isChecked():
                local_server_settings = LocalServer.instance().localServerSettings()
                self._addSummaryEntry("Type:", "Local")
                self._addSummaryEntry("Path:", local_server_settings["path"])
                self._addSummaryEntry("Host:", local_server_settings["host"])
                self._addSummaryEntry("Port:", str(local_server_settings["port"]))
            elif self.uiRemoteControllerRadioButton.isChecked():
                local_server_settings = LocalServer.instance().localServerSettings()
                self._addSummaryEntry("Type:", "Remote")
                self._addSummaryEntry("Host:", local_server_settings["host"])
                self._addSummaryEntry("Port:", str(local_server_settings["port"]))
                self._addSummaryEntry("User:", local_server_settings["username"])

    def _saveSettingsCallback(self, result, error=False, **kwargs):
        if error:
            if "message" in result:
                QtWidgets.QMessageBox.critical(self, "Save settings", "Error while saving settings: {}".format(result["message"]))
            return

    def _addSummaryEntry(self, name, value):

        item = QtWidgets.QTreeWidgetItem(self.uiSummaryTreeWidget, [name, value])
        item.setText(0, name)
        font = item.font(0)
        font.setBold(True)
        item.setFont(0, font)

    def validateCurrentPage(self):
        """
        Validates the settings.
        """

        Controller.instance().setDisplayError(True)
        if self.currentPage() == self.uiLocalControllerWizardPage:

            local_controller_settings = LocalServer.instance().localServerSettings()
            local_controller_settings["auto_start"] = True
            local_controller_settings["remote"] = False
            local_controller_settings["path"] = self.uiLocalServerPathLineEdit.text().strip()
            local_controller_settings["host"] = self.uiLocalServerHostComboBox.itemData(self.uiLocalServerHostComboBox.currentIndex())
            local_controller_settings["port"] = self.uiLocalServerPortSpinBox.value()

            if not os.path.isfile(local_controller_settings["path"]):
                QtWidgets.QMessageBox.critical(self, "Local server", "Could not find local server {}".format(local_controller_settings["path"]))
                return False
            if not os.access(local_controller_settings["path"], os.X_OK):
                QtWidgets.QMessageBox.critical(self, "Local server", "{} is not an executable".format(local_controller_settings["path"]))
                return False

            LocalServer.instance().updateLocalServerSettings(local_controller_settings)

            # start and connect to the controller if required
            if not LocalServer.instance().localServerAutoStartIfRequired():
                return False

        elif self.currentPage() == self.uiRemoteControllerWizardPage:

            remote_controller_settings = Controller.instance().settings()
            remote_controller_settings["auto_start"] = False
            remote_controller_settings["remote"] = True
            remote_controller_settings["host"] = self.uiRemoteMainServerHostLineEdit.text()
            remote_controller_settings["port"] = self.uiRemoteMainServerPortSpinBox.value()
            remote_controller_settings["protocol"] = "http"
            remote_controller_settings["username"] = self.uiRemoteMainServerUserLineEdit.text()
            remote_controller_settings["password"] = self.uiRemoteMainServerPasswordLineEdit.text()
            Controller.instance().setSettings(remote_controller_settings)
            Controller.instance().connect()
            return Controller.instance().connected()

        return True

    def done(self, result):
        """
        This dialog is closed.

        :param result: ignored
        """

        Controller.instance().setDisplayError(True)
        settings = self.parentWidget().settings()
        if result:
            settings["hide_setup_wizard"] = True
        else:
            local_server_settings = LocalServer.instance().localServerSettings()
            LocalServer.instance().updateLocalServerSettings(local_server_settings)
            settings["hide_setup_wizard"] = not self.uiShowCheckBox.isChecked()
        self.parentWidget().setSettings(settings)
        super().done(result)

    def nextId(self):
        """
        Wizard rules!
        """

        current_id = self.currentId()
        if self.page(current_id) == self.uiLocalControllerWizardPage and self.uiLocalControllerRadioButton.isChecked():
            return self._pageId(self.uiSummaryWizardPage)
        if self.page(current_id) == self.uiControllerWizardPage and self.uiRemoteControllerRadioButton.isChecked():
            return self._pageId(self.uiRemoteControllerWizardPage)
        return QtWidgets.QWizard.nextId(self)

    def _pageId(self, page):
        """
        Return id of the page
        """

        for id in self.pageIds():
            if self.page(id) == page:
                return id
        raise KeyError
