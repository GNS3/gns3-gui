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
Wizard for VirtualBox VMs.
"""

from gns3.qt import QtGui, QtWidgets
from gns3.controller import Controller
from gns3.dialogs.vm_wizard import VMWizard

from ..ui.virtualbox_vm_wizard_ui import Ui_VirtualBoxVMWizard


class VirtualBoxVMWizard(VMWizard, Ui_VirtualBoxVMWizard):
    """
    Wizard to create a VirtualBox VM.

    :param virtualbox_vms: existing VirtualBox VMs
    :param parent: parent widget
    """

    def __init__(self, virtualbox_vms, parent):

        super().__init__(virtualbox_vms, parent)
        self._virtualbox_vms = virtualbox_vms
        self._allow_dynamic_compute_allocation = False
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/vbox_guest.svg"))

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        if super().validateCurrentPage() is False:
            return False

        if self.currentPage() == self.uiVirtualBoxWizardPage:
            if not self.uiVMListComboBox.count():
                QtWidgets.QMessageBox.critical(self, "VirtualBox VMs", "There is no VirtualBox VM available!")
                return False
        return True

    def initializePage(self, page_id):

        super().initializePage(page_id)
        if self.page(page_id) == self.uiVirtualBoxWizardPage:
            self.uiVMListComboBox.clear()
            Controller.instance().getCompute(
                "/virtualbox/vms",
                self._compute_id,
                self._getVirtualBoxVMsFromServerCallback,
                progress_text="Listing VirtualBox VMs...",
                wait=True
            )

    def _getVirtualBoxVMsFromServerCallback(self, result, error=False, **kwargs):
        """
        Callback for getVirtualBoxVMsFromServer.

        :param progress_dialog: QProgressDialog instance
        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtWidgets.QMessageBox.critical(self, "VirtualBox VMs", "{}".format(result["message"]))
        else:
            self.uiVMListComboBox.clear()
            existing_vms = []
            for existing_vm in self._virtualbox_vms.values():
                existing_vms.append(existing_vm["vmname"])

            for vm in result:
                if vm["vmname"] not in existing_vms:
                    self.uiVMListComboBox.addItem(vm["vmname"], vm)

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        index = self.uiVMListComboBox.currentIndex()
        vmname = self.uiVMListComboBox.itemText(index)
        vminfo = self.uiVMListComboBox.itemData(index)

        settings = {"name": vmname,
                    "vmname": vmname,
                    "compute_id": self._compute_id,
                    "ram": vminfo["ram"],
                    "linked_clone": self.uiBaseVMCheckBox.isChecked()}
        return settings
