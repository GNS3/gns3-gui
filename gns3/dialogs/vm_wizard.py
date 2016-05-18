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

import sys

from gns3.qt import QtWidgets
from gns3.servers import Servers
from gns3.gns3_vm import GNS3VM


class VMWizard(QtWidgets.QWizard):
    """
    Base class for VM wizard.

    :param devices: List of existing device for this type
    :param use_local_server: Value the use_local_server settings for this module
    :param parent: parent widget
    """

    def __init__(self, devices, use_local_server, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setModal(True)

        self._devices = devices
        self._use_local_server = use_local_server

        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        if sys.platform.startswith("darwin"):
            # we want to see the cancel button on OSX
            self.setOptions(QtWidgets.QWizard.NoDefaultButton)

        self.uiRemoteRadioButton.toggled.connect(self._remoteServerToggledSlot)
        if hasattr(self, "uiVMRadioButton"):
            self.uiVMRadioButton.toggled.connect(self._vmToggledSlot)

        self.uiLocalRadioButton.toggled.connect(self._localToggledSlot)

        # By default we use the local server
        self._server = Servers.instance().localServer()
        self.uiLocalRadioButton.setChecked(True)
        self._localToggledSlot(True)

        if Servers.instance().isNonLocalServerConfigured() is False:
            # skip the server page if we use the local server
            self.setStartId(1)

    def _vmToggledSlot(self, checked):
        """
        Slot for when the VM radio button is toggled.

        :param checked: either the button is checked or not
        """
        if checked:
            self.uiRemoteServersGroupBox.setEnabled(False)
            self.uiRemoteServersGroupBox.hide()

    def _remoteServerToggledSlot(self, checked):
        """
        Slot for when the remote server radio button is toggled.

        :param checked: either the button is checked or not
        """

        if checked:
            self.uiRemoteServersGroupBox.setEnabled(True)
            self.uiRemoteServersGroupBox.show()

    def _localToggledSlot(self, checked):
        """
        Slot for when the local server radio button is toggled.

        :param checked: either the button is checked or not
        """
        if checked:
            self.uiRemoteServersGroupBox.setEnabled(False)
            self.uiRemoteServersGroupBox.hide()

    def setStartId(self, index):
        """
        Which page should we use when starting the Wizard
        """
        super().setStartId(index)
        # If we skip the initial page (choosing a server)
        # we check the settings
        if index != 0:
            self.uiLocalRadioButton.setChecked(True)

    def initializePage(self, page_id):

        if self.page(page_id) == self.uiServerWizardPage:
            self.uiRemoteServersComboBox.clear()

            if len(Servers.instance().remoteServers().values()) == 0:
                self.uiRemoteRadioButton.setEnabled(False)
            else:
                for server in Servers.instance().remoteServers().values():
                    self.uiRemoteServersComboBox.addItem(server.url(), server)

            if hasattr(self, "uiVMRadioButton") and not GNS3VM.instance().isRunning():
                self.uiVMRadioButton.setEnabled(False)
            if hasattr(self, "uiVMRadioButton") and GNS3VM.instance().isRunning():
                self.uiVMRadioButton.setChecked(True)
            elif self._use_local_server and self.uiLocalRadioButton.isEnabled():
                self.uiLocalRadioButton.setChecked(True)
            else:
                if self.uiRemoteRadioButton.isEnabled():
                    self.uiRemoteRadioButton.setChecked(True)
                else:
                    self.uiLocalRadioButton.setChecked(True)

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        if hasattr(self, "uiNamePlatformWizardPage") and self.currentPage() == self.uiNamePlatformWizardPage:
            name = self.uiNameLineEdit.text()
            for device in self._devices.values():
                if device["name"] == name:
                    QtWidgets.QMessageBox.critical(self, "Name", "{} is already used, please choose another name".format(name))
                    return False
        elif self.currentPage() == self.uiServerWizardPage:
            if self.uiRemoteRadioButton.isChecked():
                if not Servers.instance().remoteServers():
                    QtWidgets.QMessageBox.critical(self, "Remote server", "There is no remote server registered in your preferences")
                    return False
                self._server = self.uiRemoteServersComboBox.itemData(self.uiRemoteServersComboBox.currentIndex())
            elif hasattr(self, "uiVMRadioButton") and self.uiVMRadioButton.isChecked():
                gns3_vm_server = Servers.instance().vmServer()
                if gns3_vm_server is None:
                    QtWidgets.QMessageBox.critical(self, "GNS3 VM", "The GNS3 VM is not running")
                    return False
                self._server = gns3_vm_server
            else:
                self._server = Servers.instance().localServer()
        return True
