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

from gns3.qt import QtCore, QtGui
from gns3.servers import Servers
from gns3.utils.connect_to_server import ConnectToServer
from gns3.modules.module_error import ModuleError

from ..ui.virtualbox_vm_wizard_ui import Ui_VirtualBoxVMWizard
from .. import VirtualBox


class VirtualBoxVMWizard(QtGui.QWizard, Ui_VirtualBoxVMWizard):
    """
    Wizard to create a VirtualBox VM.

    :param virtualbox_vms: existing VirtualBox VMs
    :param parent: parent widget
    """

    def __init__(self, virtualbox_vms, parent):

        QtGui.QWizard.__init__(self, parent)
        self.setupUi(self)
        self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(":/icons/virtualbox.png"))
        self.setWizardStyle(QtGui.QWizard.ModernStyle)

        if VirtualBox.instance().settings()["use_local_server"]:
            # skip the server page if we use the local server
            self.setStartId(1)

        self._virtualbox_vms = virtualbox_vms

        # By default we use the local server
        self._server = Servers.instance().localServer()

    def initializePage(self, page_id):

        if self.page(page_id) == self.uiServerWizardPage:
            self.uiRemoteServersComboBox.clear()
            for server in Servers.instance().remoteServers().values():
                self.uiRemoteServersComboBox.addItem("{}:{}".format(server.host, server.port), server)
        if self.page(page_id) == self.uiVirtualBoxWizardPage:
            self._vbox_vms_progress_dialog = QtGui.QProgressDialog("Loading VirtualBox VMs", "Cancel", 0, 0, parent=self)
            self._vbox_vms_progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            self._vbox_vms_progress_dialog.setWindowTitle("VirtualBox VMs")
            self._vbox_vms_progress_dialog.show()
            try:
                VirtualBox.instance().getVirtualBoxVMsFromServer(self._server, self._getVirtualBoxVMsFromServerCallback)
            except ModuleError as e:
                self._vbox_vms_progress_dialog.reject()
                QtGui.QMessageBox.critical(self, "Qemu binaries", "Error while getting the QEMU binaries: {}".format(e))

    def _getVirtualBoxVMsFromServerCallback(self, result, error=False):
        """
        Callback for getVirtualBoxVMsFromServer.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if self._vbox_vms_progress_dialog.wasCanceled():
            return
        self._vbox_vms_progress_dialog.accept()

        if error:
            print(result)
            QtGui.QMessageBox.critical(self, "VirtualBox VMs", "{}".format(result["message"]))
        else:
            self.uiVMListComboBox.clear()
            existing_vms = []
            for existing_vm in self._virtualbox_vms.values():
                existing_vms.append(existing_vm["vmname"])

            for vm in result["vms"]:
                if vm not in existing_vms:
                    self.uiVMListComboBox.addItem(vm)

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        if self.currentPage() == self.uiServerWizardPage:

            #FIXME: prevent users to use "cloud"
            if self.uiCloudRadioButton.isChecked():
                QtGui.QMessageBox.critical(self, "Cloud", "Sorry not implemented yet!")
                return False

            if VirtualBox.instance().settings()["use_local_server"] or self.uiLocalRadioButton.isChecked():
                server = Servers.instance().localServer()
            else:
                server = self.uiRemoteServersComboBox.itemData(self.uiRemoteServersComboBox.currentIndex())
            if not server.connected() and ConnectToServer(self, server) is False:
                return False
            self._server = server
        return True

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        if not self.uiVMListComboBox.count():
            return {}

        if VirtualBox.instance().settings()["use_local_server"] or self.uiLocalRadioButton.isChecked():
            server = "local"
        else:
            server = self.uiRemoteServersComboBox.currentText()

        vmname = self.uiVMListComboBox.itemText(self.uiVMListComboBox.currentIndex())

        settings = {
            "vmname": vmname,
            "server": server,
        }

        return settings
