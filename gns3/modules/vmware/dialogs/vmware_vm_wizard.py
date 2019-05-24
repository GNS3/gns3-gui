# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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
Wizard for VMware VMs.
"""

from gns3.qt import QtGui, QtWidgets
from gns3.controller import Controller
from gns3.dialogs.vm_wizard import VMWizard

from ..ui.vmware_vm_wizard_ui import Ui_VMwareVMWizard


class VMwareVMWizard(VMWizard, Ui_VMwareVMWizard):
    """
    Wizard to create a VMware VM.

    :param vmware_vms: existing VMware VMs
    :param parent: parent widget
    """

    def __init__(self, vmware_vms, parent):

        super().__init__(vmware_vms, parent)
        self._vmware_vms = vmware_vms
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/vmware_guest.svg"))

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        if super().validateCurrentPage() is False:
            return False

        if self.currentPage() == self.uiVMwareWizardPage:
            if not self.uiVMListComboBox.count():
                QtWidgets.QMessageBox.critical(self, "VMware VMs", "There is no VMware VM available!")
                return False
        return True

    def initializePage(self, page_id):

        super().initializePage(page_id)
        if self.page(page_id) == self.uiVMwareWizardPage:
            self.uiVMListComboBox.clear()
            Controller.instance().getCompute("/vmware/vms", self._compute_id, self._getVMwareVMsFromServerCallback, progressText="Listing VMware VMs...")

    def _getVMwareVMsFromServerCallback(self, result, error=False, **kwargs):
        """
        Callback for getVMwareVMsFromServer.

        :param progress_dialog: QProgressDialog instance
        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtWidgets.QMessageBox.critical(self, "VMware VMs", "{}".format(result["message"]))
        else:
            self.uiVMListComboBox.clear()
            existing_vms = []
            for existing_vm in self._vmware_vms.values():
                existing_vms.append(existing_vm["name"])

            for vm in result:
                if vm["vmname"] not in existing_vms:
                    self.uiVMListComboBox.addItem(vm["vmname"], vm)

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        index = self.uiVMListComboBox.currentIndex()
        if index == -1:
            return
        vmname = self.uiVMListComboBox.itemText(index)
        vminfo = self.uiVMListComboBox.itemData(index)

        settings = {"name": vmname,
                    "compute_id": self._compute_id,
                    "vmx_path": vminfo["vmx_path"],
                    "linked_clone": self.uiBaseVMCheckBox.isChecked()}

        return settings
