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
import shutil

from gns3.qt import QtCore, QtWidgets, QtGui, QtNetwork, qslot
from gns3.controller import Controller
from gns3.local_server import LocalServer
from gns3.utils.progress_dialog import ProgressDialog
from gns3.utils.wait_for_connection_worker import WaitForConnectionWorker

from ..settings import DEFAULT_LOCAL_SERVER_HOST
from ..ui.setup_wizard_ui import Ui_SetupWizard
from ..version import __version__


import logging
log = logging.getLogger(__name__)


class SetupWizard(QtWidgets.QWizard, Ui_SetupWizard):

    """
    Base class for VM wizard.
    """

    def __init__(self, parent):

        super().__init__(parent)
        self.setupUi(self)

        self._gns3_vm_settings = {
            "enable": True,
            "headless": False,
            "when_exit": "stop",
            "engine": "vmware",
            "vcpus": 1,
            "ram": 2048,
            "vmname": "GNS3 VM"
        }

        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        if sys.platform.startswith("darwin"):
            # we want to see the cancel button on OSX
            self.setOptions(QtWidgets.QWizard.NoDefaultButton)

        self.uiLocalServerToolButton.clicked.connect(self._localServerBrowserSlot)

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

        # Mandatory fields
        self.uiLocalServerWizardPage.registerField("path*", self.uiLocalServerPathLineEdit)

        # load all available addresses
        for address in QtNetwork.QNetworkInterface.allAddresses():
            address_string = address.toString()
            if address.protocol() != QtNetwork.QAbstractSocket.IPv6Protocol:
                self.uiLocalServerHostComboBox.addItem(address_string, address.toString())

        if sys.platform.startswith("darwin"):
            self.uiVMwareBannerButton.setIcon(QtGui.QIcon(":/images/vmware_fusion_banner.jpg"))
        else:
            self.uiVMwareBannerButton.setIcon(QtGui.QIcon(":/images/vmware_workstation_banner.jpg"))

        if sys.platform.startswith("linux"):
            self.uiVMRadioButton.setText("Run the topologies in an isolated and standard VM")
            self.uiLocalRadioButton.setText("Run the topologies on my computer")
            self.uiLocalRadioButton.setChecked(True)
            self.uiLocalLabel.setVisible(False)

        Controller.instance().connected_signal.connect(self._refreshLocalServerStatusSlot)
        Controller.instance().connection_failed_signal.connect(self._refreshLocalServerStatusSlot)

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
            QtWidgets.QMessageBox.critical(self, "VMware", "VMware vmrun tool could not be found, VMware or the VIX API (required for VMware player) is probably not installed. You can download it from https://www.vmware.com/support/developer/vix-api/. After installation you need to restart GNS3.")
            return
        self._refreshVMListSlot()

    def _listVirtualBoxVMsSlot(self):
        """
        Slot to refresh the VirtualBox VMs list.
        """

        QtWidgets.QMessageBox.warning(self, "GNS3 VM on VirtualBox", "VirtualBox doesn't support nested virtualization, this means running Qemu based VM could be very slow")
        download_url = "https://github.com/GNS3/gns3-gui/releases/download/v{version}/GNS3.VM.VirtualBox.{version}.zip".format(version=__version__)
        self.uiGNS3VMDownloadLinkUrlLabel.setText('If you don\'t have the GNS3 Virtual Machine you can <a href="{download_url}">download it here</a>.<br>And import the VM in the virtualization software and hit refresh.'.format(download_url=download_url))
        self.uiVmwareRadioButton.setChecked(False)
        from gns3.modules import VirtualBox
        settings = VirtualBox.instance().settings()
        if not os.path.exists(settings["vboxmanage_path"]):
            QtWidgets.QMessageBox.critical(self, "VirtualBox", "VBoxManage could not be found, VirtualBox is probably not installed. After installation you need to restart GNS3.")
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

    def _getSettingsCallback(self, result, error=False, **kwargs):
        if error:
            if "message" in result:
                log.error("Error while get gettings: {}".format(result["message"]))
            return
        self._gns3_vm_settings = result

    def initializePage(self, page_id):
        """
        Initialize Wizard pages.

        :param page_id: page identifier
        """

        super().initializePage(page_id)
        if self.page(page_id) == self.uiServerWizardPage:
            Controller.instance().setDisplayError(False)
            Controller.instance().get("/gns3vm", self._getSettingsCallback)
        elif self.page(page_id) == self.uiVMWizardPage:
            if self._GNS3VMSettings()["engine"] == "vmware":
                self.uiVmwareRadioButton.setChecked(True)
                self._listVMwareVMsSlot()
            elif self._GNS3VMSettings()["engine"] == "virtualbox":
                self.uiVirtualBoxRadioButton.setChecked(True)
                self._listVirtualBoxVMsSlot()
            self.uiCPUSpinBox.setValue(self._GNS3VMSettings()["vcpus"])
            self.uiRAMSpinBox.setValue(self._GNS3VMSettings()["ram"])

        elif self.page(page_id) == self.uiLocalServerWizardPage:
            local_server_settings = LocalServer.instance().localServerSettings()
            self.uiLocalServerPathLineEdit.setText(local_server_settings["path"])
            index = self.uiLocalServerHostComboBox.findData(local_server_settings["host"])
            if index != -1:
                self.uiLocalServerHostComboBox.setCurrentIndex(index)
            self.uiLocalServerPortSpinBox.setValue(local_server_settings["port"])

        elif self.page(page_id) == self.uiRemoteControllerWizardPage:
            local_server_settings = LocalServer.instance().localServerSettings()
            if local_server_settings["host"] is None:
                self.uiRemoteMainServerHostLineEdit.setText(DEFAULT_LOCAL_SERVER_HOST)
                self.uiRemoteMainServerAuthCheckBox.setChecked(False)
                self.uiRemoteMainServerUserLineEdit.setText("")
                self.uiRemoteMainServerPasswordLineEdit.setText("")
            else:
                self.uiRemoteMainServerHostLineEdit.setText(local_server_settings["host"])
                self.uiRemoteMainServerAuthCheckBox.setChecked(local_server_settings["auth"])
                self.uiRemoteMainServerUserLineEdit.setText(local_server_settings["user"])
                self.uiRemoteMainServerPasswordLineEdit.setText(local_server_settings["password"])
            self.uiRemoteMainServerPortSpinBox.setValue(local_server_settings["port"])
            self.uiRemoteMainServerProtocolComboBox.setCurrentText(local_server_settings["protocol"])
        elif self.page(page_id) == self.uiLocalServerStatusWizardPage:
            self._refreshLocalServerStatusSlot()

        elif self.page(page_id) == self.uiSummaryWizardPage:
            self.uiSummaryTreeWidget.clear()
            if self.uiLocalRadioButton.isChecked():
                local_server_settings = LocalServer.instance().localServerSettings()
                self._addSummaryEntry("Server type:", "Local")
                self._addSummaryEntry("Path:", local_server_settings["path"])
                self._addSummaryEntry("Host:", local_server_settings["host"])
                self._addSummaryEntry("Port:", str(local_server_settings["port"]))
            elif self.uiRemoteControllerRadioButton.isChecked():
                local_server_settings = LocalServer.instance().localServerSettings()
                self._addSummaryEntry("Server type:", "Remote")
                self._addSummaryEntry("Host:", local_server_settings["host"])
                self._addSummaryEntry("Port:", str(local_server_settings["port"]))
                self._addSummaryEntry("User:", local_server_settings["user"])
            else:
                self._addSummaryEntry("Server type:", "GNS3 Virtual Machine")
                self._addSummaryEntry("VM engine:", self._GNS3VMSettings()["engine"].capitalize())
                self._addSummaryEntry("VM name:", self._GNS3VMSettings()["vmname"])
                self._addSummaryEntry("VM vCPUs:", str(self._GNS3VMSettings()["vcpus"]))
                self._addSummaryEntry("VM RAM:", str(self._GNS3VMSettings()["ram"]) + " MB")

    @qslot
    def _refreshLocalServerStatusSlot(self):
        """
        Refresh the local server status page
        """
        if Controller.instance().connected():
            self.uiLocalServerStatusLabel.setText("Connection to local server successful")
            Controller.instance().get("/gns3vm", self._getSettingsCallback)
        elif Controller.instance().connecting():
            self.uiLocalServerStatusLabel.setText("Please wait connection to the GNS3 server")
        else:
            local_server_settings = LocalServer.instance().localServerSettings()
            self.uiLocalServerStatusLabel.setText("Connection to local server failed.\n* Make sure GNS3 is allowed in your firewall.\n* Go back and try to change the server port\n* Please check with a browser if you can connect to {protocol}://{host}:{port}.\n* Try to run {path} in a terminal to see if you have an error if the above does not work.".format(protocol=local_server_settings["protocol"], host=local_server_settings["host"], port=local_server_settings["port"], path=local_server_settings["path"]))

    def _GNS3VMSettings(self):
        return self._gns3_vm_settings

    def _setGNS3VMSettings(self, settings):
        Controller.instance().put("/gns3vm", self._saveSettingsCallback, settings, timeout=60 * 5)

    def _saveSettingsCallback(self, result, error=False, **kwargs):
        if error:
            if "message" in result:
                QtWidgets.QMessageBox.critical(self, "Save settings", "Error while save settings: {}".format(result["message"]))
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
        if self.currentPage() == self.uiVMWizardPage:
            vmname = self.uiVMListComboBox.currentText()
            if vmname:
                # save the GNS3 VM settings
                vm_settings = self._GNS3VMSettings()
                vm_settings["enable"] = True
                vm_settings["vmname"] = vmname

                if self.uiVmwareRadioButton.isChecked():
                    vm_settings["engine"] = "vmware"
                elif self.uiVirtualBoxRadioButton.isChecked():
                    vm_settings["engine"] = "virtualbox"

                # set the vCPU count and RAM
                vpcus = self.uiCPUSpinBox.value()
                ram = self.uiRAMSpinBox.value()
                if ram < 1024:
                    QtWidgets.QMessageBox.warning(self, "GNS3 VM memory", "It is recommended to allocate a minimum of 1024 MB of memory to the GNS3 VM")
                vm_settings["vcpus"] = vpcus
                vm_settings["ram"] = ram

                self._setGNS3VMSettings(vm_settings)
            else:
                if not self.uiVmwareRadioButton.isChecked() and not self.uiVirtualBoxRadioButton.isChecked():
                    QtWidgets.QMessageBox.warning(self, "GNS3 VM", "Please select VMware or VirtualBox")
                else:
                    QtWidgets.QMessageBox.warning(self, "GNS3 VM", "Please select a VM. If no VM is listed, check if the GNS3 VM is correctly imported and press refresh.")
                return False
        elif self.currentPage() == self.uiLocalServerWizardPage:
            local_server_settings = LocalServer.instance().localServerSettings()
            local_server_settings["auto_start"] = True
            local_server_settings["path"] = self.uiLocalServerPathLineEdit.text().strip()
            local_server_settings["host"] = self.uiLocalServerHostComboBox.itemData(self.uiLocalServerHostComboBox.currentIndex())
            local_server_settings["port"] = self.uiLocalServerPortSpinBox.value()

            if not os.path.isfile(local_server_settings["path"]):
                QtWidgets.QMessageBox.critical(self, "Local server", "Could not find local server {}".format(local_server_settings["path"]))
                return False
            if not os.access(local_server_settings["path"], os.X_OK):
                QtWidgets.QMessageBox.critical(self, "Local server", "{} is not an executable".format(local_server_settings["path"]))
                return False

            LocalServer.instance().updateLocalServerSettings(local_server_settings)
            LocalServer.instance().localServerAutoStartIfRequire()

        elif self.currentPage() == self.uiRemoteControllerWizardPage:
            local_server_settings = LocalServer.instance().localServerSettings()
            local_server_settings["auto_start"] = False
            local_server_settings["host"] = self.uiRemoteMainServerHostLineEdit.text()
            local_server_settings["port"] = self.uiRemoteMainServerPortSpinBox.value()
            local_server_settings["protocol"] = self.uiRemoteMainServerProtocolComboBox.currentText()
            local_server_settings["user"] = self.uiRemoteMainServerUserLineEdit.text()
            local_server_settings["password"] = self.uiRemoteMainServerPasswordLineEdit.text()
            local_server_settings["auth"] = self.uiRemoteMainServerAuthCheckBox.isChecked()
            LocalServer.instance().updateLocalServerSettings(local_server_settings)

        elif self.currentPage() == self.uiSummaryWizardPage:
            if self.uiLocalRadioButton.isChecked():
                # deactivate the GNS3 VM if using the local server
                vm_settings = self._GNS3VMSettings()
                vm_settings["enable"] = False
                self._setGNS3VMSettings(vm_settings)

        elif self.currentPage() == self.uiLocalServerStatusWizardPage:
            if not Controller.instance().connected():
                return False

        return True

    def _refreshVMListSlot(self):
        """
        Refresh the list of VM available in VMware or VirtualBox.
        """

        if self.uiVmwareRadioButton.isChecked():
            Controller.instance().get("/gns3vm/engines/vmware/vms", self._getVMsFromServerCallback, progressText="Retrieving VMware VM list from server...")
        elif self.uiVirtualBoxRadioButton.isChecked():
            Controller.instance().get("/gns3vm/engines/virtualbox/vms", self._getVMsFromServerCallback, progressText="Retrieving VirtualBox VM list from server...")

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
                self.uiVMListComboBox.addItem(vm["vmname"])

            index = self.uiVMListComboBox.findText(self._GNS3VMSettings()["vmname"])
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

        Controller.instance().setDisplayError(True)
        settings = self.parentWidget().settings()
        if result:
            settings["hide_setup_wizard"] = True
        else:
            local_server_settings = LocalServer.instance().localServerSettings()
            if local_server_settings["host"] is None:
                local_server_settings["host"] = DEFAULT_LOCAL_SERVER_HOST
                LocalServer.instance().updateLocalServerSettings(local_server_settings)
            settings["hide_setup_wizard"] = self.uiShowCheckBox.isChecked()

        self.parentWidget().setSettings(settings)
        super().done(result)

    def nextId(self):
        """
        Wizard rules!
        """

        current_id = self.currentId()
        if self.page(current_id) == self.uiLocalServerStatusWizardPage and not self.uiVMRadioButton.isChecked():
            return self._pageId(self.uiSummaryWizardPage)

        if self.page(current_id) == self.uiServerWizardPage and self.uiRemoteControllerRadioButton.isChecked():
            return self._pageId(self.uiRemoteControllerWizardPage)

        if self.page(current_id) == self.uiVMWizardPage:
            return self._pageId(self.uiSummaryWizardPage)
        return QtWidgets.QWizard.nextId(self)

    def _pageId(self, page):
        """
        Return id of the page
        """
        for id in self.pageIds():
            if self.page(id) == page:
                return id
        raise KeyError
