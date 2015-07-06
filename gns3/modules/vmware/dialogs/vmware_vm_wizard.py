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

import sys

from gns3.qt import QtGui, QtWidgets
from gns3.servers import Servers

from ..ui.vmware_vm_wizard_ui import Ui_VMwareVMWizard
from .. import VMware


class VMwareVMWizard(QtWidgets.QWizard, Ui_VMwareVMWizard):

    """
    Wizard to create a VMware VM.

    :param vmware_vms: existing VMware VMs
    :param parent: parent widget
    """

    def __init__(self, vmware_vms, parent):

        super().__init__(parent)
        self.setupUi(self)
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/vmware_guest.svg"))
        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        if sys.platform.startswith("darwin"):
            # we want to see the cancel button on OSX
            self.setOptions(QtWidgets.QWizard.NoDefaultButton)

        if VMware.instance().settings()["use_local_server"]:
            # skip the server page if we use the local server
            self.setStartId(1)

        self._vmware_vms = vmware_vms

        # By default we use the local server
        self._server = Servers.instance().localServer()

    def initializePage(self, page_id):

        if self.page(page_id) == self.uiServerWizardPage:
            self.uiRemoteServersComboBox.clear()
            for server in Servers.instance().remoteServers().values():
                self.uiRemoteServersComboBox.addItem(server.url(), server)
        if self.page(page_id) == self.uiVirtualBoxWizardPage:
            self._server.get("/vmware/vms", self._getVMwareVMsFromServerCallback)

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

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        # Fusion is not yet supported
        if sys.platform.startswith("darwin"):
            if VMware.instance().settings()["use_local_server"] or self.uiLocalRadioButton.isChecked():
                QtWidgets.QMessageBox.critical(self, "VMware VMs", "Sorry, VMware Fusion is not supported yet")
                return False

        if self.currentPage() == self.uiServerWizardPage:

            if VMware.instance().settings()["use_local_server"] or self.uiLocalRadioButton.isChecked():
                server = Servers.instance().localServer()
            else:
                if not Servers.instance().remoteServers():
                    QtWidgets.QMessageBox.critical(self, "Remote server", "There is no remote server registered in your preferences")
                    return False
                server = self.uiRemoteServersComboBox.itemData(self.uiRemoteServersComboBox.currentIndex())
            self._server = server
        if self.currentPage() == self.uiVirtualBoxWizardPage:
            if not self.uiVMListComboBox.count():
                QtWidgets.QMessageBox.critical(self, "VMware VMs", "There is no VMware VM available!")
                return False
        return True

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        if VMware.instance().settings()["use_local_server"] or self.uiLocalRadioButton.isChecked():
            server = "local"
        else:
            server = self.uiRemoteServersComboBox.currentText()

        index = self.uiVMListComboBox.currentIndex()
        vmname = self.uiVMListComboBox.itemText(index)
        vminfo = self.uiVMListComboBox.itemData(index)

        settings = {
            "name": vmname,
            "server": server,
            "vmx_path": vminfo["vmx_path"],
            "linked_base": self.uiBaseVMCheckBox.isChecked()
        }

        return settings
