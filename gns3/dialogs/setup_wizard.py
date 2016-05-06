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
import os
import psutil

from gns3.qt import QtCore, QtWidgets, QtGui
from gns3.servers import Servers
from ..gns3_vm import GNS3VM
from ..dialogs.preferences_dialog import PreferencesDialog
from ..ui.setup_wizard_ui import Ui_SetupWizard
from ..utils.progress_dialog import ProgressDialog
from ..utils.wait_for_vm_worker import WaitForVMWorker
from ..utils.wait_for_connection_worker import WaitForConnectionWorker
from ..version import __version__


class SetupWizard(QtWidgets.QWizard, Ui_SetupWizard):

    """
    Base class for VM wizard.
    """

    def __init__(self, parent):

        super().__init__(parent)
        self.setupUi(self)

        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        if sys.platform.startswith("darwin"):
            # we want to see the cancel button on OSX
            self.setOptions(QtWidgets.QWizard.NoDefaultButton)

        self._server = Servers.instance().localServer()
        self.uiGNS3VMDownloadLinkUrlLabel.setText('')
        self.uiRefreshPushButton.clicked.connect(self._refreshVMListSlot)
        self.uiVmwareRadioButton.clicked.connect(self._listVMwareVMsSlot)
        self.uiVirtualBoxRadioButton.clicked.connect(self._listVirtualBoxVMsSlot)
        self.uiVMwareBannerButton.clicked.connect(self._VMwareBannerButtonClickedSlot)
        settings = parent.settings()
        self.uiShowCheckBox.setChecked(settings["hide_setup_wizard"])

        # by default all radio buttons are unchecked
        self.uiVmwareRadioButton.setAutoExclusive(False)
        self.uiVirtualBoxRadioButton.setAutoExclusive(False)
        self.uiVmwareRadioButton.setChecked(False)
        self.uiVirtualBoxRadioButton.setChecked(False)

        if sys.platform.startswith("darwin"):
            self.uiVMwareBannerButton.setIcon(QtGui.QIcon(":/images/vmware_fusion_banner.jpg"))
        else:
            self.uiVMwareBannerButton.setIcon(QtGui.QIcon(":/images/vmware_workstation_banner.jpg"))

    def _VMwareBannerButtonClickedSlot(self):
        if sys.platform.startswith("darwin"):
            url = "http://send.onenetworkdirect.net/z/616461/CD225091/"
        else:
            url = "http://send.onenetworkdirect.net/z/616460/CD225091/"
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def _listVMwareVMsSlot(self):
        """
        Slot to refresh the VMware VMs list.
        """

        download_url = "https://github.com/GNS3/gns3-gui/releases/download/v{version}/GNS3.VM.VMware.Workstation.{version}.zip".format(version=__version__)
        self.uiGNS3VMDownloadLinkUrlLabel.setText('The GNS3 VM can <a href="{download_url}">downloaded here</a>.<br>Import the VM in your virtualization software and hit refresh.'.format(download_url=download_url))
        self.uiVirtualBoxRadioButton.setChecked(False)
        from gns3.modules import VMware
        settings = VMware.instance().settings()
        if not os.path.exists(settings["vmrun_path"]):
            QtWidgets.QMessageBox.critical(self, "VMware", "VMware vmrun tool could not be found, VMware or the VIX API (required for VMware player) is probably not installed. You can download it from https://www.vmware.com/support/developer/vix-api/")
            return
        self._refreshVMListSlot()

    def _listVirtualBoxVMsSlot(self):
        """
        Slot to refresh the VirtualBox VMs list.
        """

        QtWidgets.QMessageBox.warning(self, "GNS3 VM on VirtualBox", "VirtualBox doesn't support nested virtulization, this means running Qemu based VM could be very slow")
        download_url = "https://github.com/GNS3/gns3-gui/releases/download/v{version}/GNS3.VM.VirtualBox.{version}.zip".format(version=__version__)
        self.uiGNS3VMDownloadLinkUrlLabel.setText('If you don\'t have the GNS3 Virtual Machine you can <a href="{download_url}">download it here</a>.<br>And import the VM in the virtualization software and hit refresh.'.format(download_url=download_url))
        self.uiVmwareRadioButton.setChecked(False)
        from gns3.modules import VirtualBox
        settings = VirtualBox.instance().settings()
        if not os.path.exists(settings["vboxmanage_path"]):
            QtWidgets.QMessageBox.critical(self, "VirtualBox", "VBoxManage could not be found, VirtualBox is probably not installed")
            return
        self._refreshVMListSlot()

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
        if self.page(page_id) == self.uiVMWizardPage:
            # limit the number of vCPUs to the number of physical cores (hyper thread CPUs are excluded)
            # because this is likely to degrade performances.
            cpu_count = psutil.cpu_count(logical=False)
            self.uiCPUSpinBox.setValue(cpu_count)
            # we want to allocate half of the available physical memory
            ram = int(psutil.virtual_memory().total / (1024 * 1024) / 2)
            # value must be a multiple of 4 (VMware requirement)
            ram -= ram % 4
            self.uiRAMSpinBox.setValue(ram)

    def validateCurrentPage(self):
        """
        Validates the settings.
        """

        gns3_vm = GNS3VM.instance()
        servers = Servers.instance()
        if self.currentPage() == self.uiVMWizardPage:
            vmname = self.uiVMListComboBox.currentText()
            if vmname:
                # save the GNS3 VM settings
                vm_settings = {"auto_start": True,
                               "vmname": vmname,
                               "vmx_path": self.uiVMListComboBox.currentData()}
                if self.uiVmwareRadioButton.isChecked():
                    vm_settings["virtualization"] = "VMware"
                elif self.uiVirtualBoxRadioButton.isChecked():
                    vm_settings["virtualization"] = "VirtualBox"
                gns3_vm.setSettings(vm_settings)
                servers.save()

                # set the vCPU count and RAM
                vpcus = self.uiCPUSpinBox.value()
                ram = self.uiRAMSpinBox.value()
                if ram < 1024:
                    QtWidgets.QMessageBox.warning(self, "GNS3 VM memory", "It is recommended to allocate a minimum of 1024 MB of RAM to the GNS3 VM")
                available_ram = int(psutil.virtual_memory().available / (1024 * 1024))
                if ram > available_ram:
                    QtWidgets.QMessageBox.warning(self, "GNS3 VM memory", "You have probably allocated too much memory for the GNS3 VM! (available memory is {} MB)".format(available_ram))
                if gns3_vm.setvCPUandRAM(vpcus, ram) is False:
                    QtWidgets.QMessageBox.warning(self, "GNS3 VM", "Could not configure vCPUs and RAM amounts for the GNS3 VM")

                # start the GNS3 VM
                servers.initVMServer()
                worker = WaitForVMWorker()
                progress_dialog = ProgressDialog(worker, "GNS3 VM", "Starting the GNS3 VM...", "Cancel", busy=True, parent=self, delay=5)
                progress_dialog.show()
                if progress_dialog.exec_():
                    previous_local_server_ip = servers.localServer().host()
                    new_local_server_ip = gns3_vm.adjustLocalServerIP()
                    self.uiShowCheckBox.setChecked(True)
                    # restart the local server if necessary
                    if new_local_server_ip != previous_local_server_ip:
                        servers.stopLocalServer(wait=True)
                        if servers.startLocalServer():
                            worker = WaitForConnectionWorker(new_local_server_ip, servers.localServer().port())
                            dialog = ProgressDialog(worker, "Local server", "Connecting...", "Cancel", busy=True, parent=self)
                            dialog.show()
                            dialog.exec_()
            else:
                if not self.uiVmwareRadioButton.isChecked() and not self.uiVirtualBoxRadioButton.isChecked():
                    QtWidgets.QMessageBox.warning(self, "GNS3 VM", "Please select VMware or VirtualBox")
                else:
                    QtWidgets.QMessageBox.warning(self, "GNS3 VM", "Please select a VM. If no VM is listed, check if the GNS3 VM is correctly imported and press refresh.")
                return False
        elif self.currentPage() == self.uiAddVMsWizardPage:

            use_local_server = self.uiLocalRadioButton.isChecked()
            if use_local_server:
                # deactivate the GNS3 VM if using the local server
                vm_settings = {"auto_start": False}
                gns3_vm.setSettings(vm_settings)
                servers.save()
                self.uiShowCheckBox.setChecked(True)

            from gns3.modules import Dynamips
            Dynamips.instance().setSettings({"use_local_server": use_local_server})
            if sys.platform.startswith("linux"):
                # IOU only works on Linux
                from gns3.modules import IOU
                IOU.instance().setSettings({"use_local_server": use_local_server})
            from gns3.modules import Qemu
            Qemu.instance().setSettings({"use_local_server": use_local_server})
            from gns3.modules import VPCS
            VPCS.instance().setSettings({"use_local_server": use_local_server})

            dialog = PreferencesDialog(self)
            if self.uiAddIOSRouterCheckBox.isChecked():
                self._setPreferencesPane(dialog, "Dynamips").uiNewIOSRouterPushButton.clicked.emit(False)
            if self.uiAddIOUDeviceCheckBox.isChecked():
                self._setPreferencesPane(dialog, "IOS on UNIX").uiNewIOUDevicePushButton.clicked.emit(False)
            if self.uiAddQemuVMcheckBox.isChecked():
                self._setPreferencesPane(dialog, "QEMU").uiNewQemuVMPushButton.clicked.emit(False)
            if self.uiAddVirtualBoxVMcheckBox.isChecked():
                self._setPreferencesPane(dialog, "VirtualBox").uiNewVirtualBoxVMPushButton.clicked.emit(False)
            if self.uiAddVMwareVMcheckBox.isChecked():
                self._setPreferencesPane(dialog, "VMware").uiNewVMwareVMPushButton.clicked.emit(False)
            if self.uiAddDockerVMCheckBox.isChecked():
                self._setPreferencesPane(dialog, "Docker").uiNewDockerVMPushButton.clicked.emit(False)
            dialog.exec_()
        return True

    def _refreshVMListSlot(self):
        """
        Refresh the list of VM available in VMware or VirtualBox.
        """

        server = Servers.instance().localServer()
        if self.uiVmwareRadioButton.isChecked():
            server.get("/vmware/vms", self._getVMsFromServerCallback)
        elif self.uiVirtualBoxRadioButton.isChecked():
            server.get("/virtualbox/vms", self._getVMsFromServerCallback)

    def _getVMsFromServerCallback(self, result, error=False, **kwargs):
        """
        Callback for getVMsFromServer.

        :param progress_dialog: QProgressDialog instance
        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtWidgets.QMessageBox.critical(self, "VM List", "{}".format(result["message"]))
        else:
            self.uiVMListComboBox.clear()
            for vm in result:
                self.uiVMListComboBox.addItem(vm["vmname"], vm.get("vmx_path", ""))
            gns3_vm = Servers.instance().vmSettings()
            index = self.uiVMListComboBox.findText(gns3_vm["vmname"])
            if index != -1:
                self.uiVMListComboBox.setCurrentIndex(index)
            else:
                index = self.uiVMListComboBox.findText("GNS3 VM")
                if index != -1:
                    self.uiVMListComboBox.setCurrentIndex(index)
                else:
                    QtWidgets.QMessageBox.critical(self, "GNS3 VM", "Could not find a VM named 'GNS3 VM', is it imported in VMware or VirtualBox?")

    def done(self, result):
        """
        This dialog is closed.

        :param result: ignored
        """

        settings = self.parentWidget().settings()
        settings["hide_setup_wizard"] = self.uiShowCheckBox.isChecked()
        self.parentWidget().setSettings(settings)
        super().done(result)

    def nextId(self):
        """
        Wizard rules!
        """

        current_id = self.currentId()
        if self.page(current_id) == self.uiServerWizardPage and not self.uiVMRadioButton.isChecked():
            # skip the GNS3 VM page if using the local server.
            return self.uiServerWizardPage.nextId() + 1
        return QtWidgets.QWizard.nextId(self)
