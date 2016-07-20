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
from gns3.compute_manager import ComputeManager


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
        self._compute_id = ComputeManager.instance().computes()[0].id()
        self.uiLocalRadioButton.setChecked(True)
        self._localToggledSlot(True)

        if len(ComputeManager.instance().computes()) == 1:
            # skip the server page if we use the first server
            self.initializePage(0)
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
            self.uiRemoteServersComboBox.setEnabled(True)
            self.uiRemoteServersGroupBox.show()

    def _localToggledSlot(self, checked):
        """
        Slot for when the local server radio button is toggled.

        :param checked: either the button is checked or not
        """
        if checked:
            self.uiRemoteServersGroupBox.setEnabled(False)
            self.uiRemoteServersGroupBox.hide()

    def initializePage(self, page_id):

        if self.page(page_id) == self.uiServerWizardPage:
            self.uiRemoteServersComboBox.clear()

            self.uiRemoteRadioButton.setEnabled(False)
            if hasattr(self, "uiVMRadioButton"):
                self.uiVMRadioButton.setEnabled(False)
            self.uiLocalRadioButton.setEnabled(False)
            for compute in ComputeManager.instance().computes():
                if compute.id() == "local":
                    self.uiLocalRadioButton.setEnabled(True)
                elif compute.id() == "vm" and hasattr(self, "uiVMRadioButton"):
                        self.uiVMRadioButton.setEnabled(True)
                else:
                    self.uiRemoteRadioButton.setEnabled(True)
                    self.uiRemoteServersComboBox.addItem(compute.name(), compute.id())

            if self._use_local_server and self.uiLocalRadioButton.isEnabled():
                self.uiLocalRadioButton.setChecked(True)
            elif self.uiVMRadioButton.isEnabled():
                self.uiVMRadioButton.setChecked(True)
            else:
                if self.uiRemoteRadioButton.isEnabled():
                    self.uiRemoteRadioButton.setChecked(True)
                else:
                    self.uiLocalRadioButton.setChecked(True)

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        if hasattr(self, "uiNameWizardPage") and self.currentPage() == self.uiNameWizardPage:
            name = self.uiNameLineEdit.text()
            for device in self._devices.values():
                if device["name"] == name:
                    QtWidgets.QMessageBox.critical(self, "Name", "{} is already used, please choose another name".format(name))
                    return False
        elif self.currentPage() == self.uiServerWizardPage:
            if self.uiRemoteRadioButton.isChecked():
                if self.uiRemoteServersComboBox.count() == 0:
                    QtWidgets.QMessageBox.critical(self, "Remote server", "There is no remote server registered in your preferences")
                    return False
                self._compute_id = self.uiRemoteServersComboBox.itemData(self.uiRemoteServersComboBox.currentIndex())
            elif hasattr(self, "uiVMRadioButton") and self.uiVMRadioButton.isChecked():
                self._compute_id = "vm"
            else:
                self._compute_id = "local"
        return True
