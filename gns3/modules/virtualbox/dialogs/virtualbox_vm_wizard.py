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

import sys

from functools import partial
from gns3.qt import QtCore, QtGui
from gns3.servers import Servers

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
        if sys.platform.startswith("darwin"):
            # we want to see the cancel button on OSX
            self.setOptions(QtGui.QWizard.NoDefaultButton)

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
            progress_dialog = QtGui.QProgressDialog("Loading VirtualBox VMs", "Cancel", 0, 0, parent=self)
            progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            progress_dialog.setWindowTitle("VirtualBox VMs")
            progress_dialog.show()
            self._server.get("/virtualbox/vms", partial(self._getVirtualBoxVMsFromServerCallback, progress_dialog))

    def _getVirtualBoxVMsFromServerCallback(self, progress_dialog, result, error=False, **kwargs):
        """
        Callback for getVirtualBoxVMsFromServer.

        :param progress_dialog: QProgressDialog instance
        :param result: server response
        :param error: indicates an error (boolean)
        """

        if progress_dialog.wasCanceled():
            return
        if error:
            progress_dialog.reject()
            QtGui.QMessageBox.critical(self, "VirtualBox VMs", "Error while getting the VirtualBox VMs: {}".format(result["message"]))
            return

        progress_dialog.accept()
        if error:
            QtGui.QMessageBox.critical(self, "VirtualBox VMs", "{}".format(result["message"]))
        else:
            self.uiVMListComboBox.clear()
            existing_vms = []
            for existing_vm in self._virtualbox_vms.values():
                existing_vms.append(existing_vm["vmname"])

            for vm in result:
                if vm["vmname"] not in existing_vms:
                    self.uiVMListComboBox.addItem(vm["vmname"], vm)

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        if self.currentPage() == self.uiServerWizardPage:

            # FIXME: prevent users to use "cloud"
            if self.uiCloudRadioButton.isChecked():
                QtGui.QMessageBox.critical(self, "Cloud", "Sorry not implemented yet!")
                return False

            if VirtualBox.instance().settings()["use_local_server"] or self.uiLocalRadioButton.isChecked():
                server = Servers.instance().localServer()
            else:
                if not Servers.instance().remoteServers():
                    QtGui.QMessageBox.critical(self, "Remote server", "There is no remote server registered in VirtualBox preferences")
                    return False
                server = self.uiRemoteServersComboBox.itemData(self.uiRemoteServersComboBox.currentIndex())
            self._server = server
        if self.currentPage() == self.uiVirtualBoxWizardPage:
            if not self.uiVMListComboBox.count():
                QtGui.QMessageBox.critical(self, "VirtualBox VMs", "There is no VirtualBox VM available!")
                return False
        return True

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        if VirtualBox.instance().settings()["use_local_server"] or self.uiLocalRadioButton.isChecked():
            server = "local"
        else:
            server = self.uiRemoteServersComboBox.currentText()

        index = self.uiVMListComboBox.currentIndex()
        vmname = self.uiVMListComboBox.itemText(index)
        vminfo = self.uiVMListComboBox.itemData(index)

        settings = {
            "vmname": vmname,
            "server": server,
            "ram": vminfo["ram"],
            "linked_base": self.uiBaseVMCheckBox.isChecked()
        }

        return settings
