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
Configuration page for server preferences.
"""

import os
import sys
import shutil

import logging
log = logging.getLogger(__name__)

from gns3.qt import QtNetwork, QtWidgets
from ..ui.server_preferences_page_ui import Ui_ServerPreferencesPageWidget
from ..servers import Servers
from ..topology import Topology
from ..utils.message_box import MessageBox
from ..utils.progress_dialog import ProgressDialog
from ..utils.wait_for_connection_worker import WaitForConnectionWorker
from ..utils.wait_for_vm_worker import WaitForVMWorker
from ..settings import SERVERS_SETTINGS
from ..gns3_vm import GNS3VM
from ..dialogs.new_server_dialog import NewServerDialog


class ServerPreferencesPage(QtWidgets.QWidget, Ui_ServerPreferencesPageWidget):

    """
    QWidget configuration page for server preferences.
    """

    def __init__(self, parent=None):

        super().__init__()
        self.setupUi(self)
        self._remote_servers = {}
        self.uiRemoteGNS3VMSettingsGroupBox.setEnabled(False)

        # connect the slots
        self.uiServerPreferenceTabWidget.currentChanged.connect(self._tabChangedSlot)
        self.uiLocalServerToolButton.clicked.connect(self._localServerBrowserSlot)
        self.uiUbridgeToolButton.clicked.connect(self._ubridgeBrowserSlot)
        self.uiAddRemoteServerPushButton.clicked.connect(self._remoteServerAddSlot)
        self.uiDeleteRemoteServerPushButton.clicked.connect(self._remoteServerDeleteSlot)
        self.uiRemoteServersTreeWidget.itemSelectionChanged.connect(self._remoteServerChangedSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiLocalServerAutoStartCheckBox.stateChanged.connect(self._useLocalServerAutoStartSlot)
        self.uiEnableVMCheckBox.stateChanged.connect(self._enableGNS3VMSlot)
        self.uiRefreshPushButton.clicked.connect(self._refreshVMListSlot)
        self.uiVmwareRadioButton.clicked.connect(self._listVMwareVMsSlot)
        self.uiVirtualBoxRadioButton.clicked.connect(self._listVirtualBoxVMsSlot)
        self.uiRemoteRadioButton.toggled.connect(self._remoteGNS3VMToggledSlot)
        self.uiAddServerPushButton.clicked.connect(self._remoteServerAddSlot)

        # load all available addresses
        for address in QtNetwork.QNetworkInterface.allAddresses():
            address_string = address.toString()
            # if address.protocol() == QtNetwork.QAbstractSocket.IPv6Protocol:
            # we do not want the scope id when using an IPv6 address...
            # address.setScopeId("")
            self.uiLocalServerHostComboBox.addItem(address_string, address.toString())

        # default is 127.0.0.1
        index = self.uiLocalServerHostComboBox.findText("127.0.0.1")
        if index != -1:
            self.uiLocalServerHostComboBox.setCurrentIndex(index)

    def _tabChangedSlot(self, index):
        if index == 1:
            self._refreshVMListSlot()

    def _listVMwareVMsSlot(self):
        """
        Slot to refresh the VMware VMs list.
        """

        self._refreshVMListSlot()

    def _listVirtualBoxVMsSlot(self):
        """
        Slot to refresh the VirtualBox VMs list.
        """

        QtWidgets.QMessageBox.warning(self, "GNS3 VM on VirtualBox", "VirtualBox doesn't support nested virtulization, this means running Qemu based VM could be very slow")
        self._refreshVMListSlot()

    def _refreshVMListSlot(self):
        """
        Refresh the list of VM available in VMware or VirtualBox.
        """

        if not self.uiEnableVMCheckBox.isChecked():
            return
        server = Servers.instance().localServer()
        if self.uiVmwareRadioButton.isChecked():
            server.get("/vmware/vms", self._getVMsFromServerCallback)
        elif self.uiVirtualBoxRadioButton.isChecked():
            server.get("/virtualbox/vms", self._getVMsFromServerCallback)

    def _remoteGNS3VMToggledSlot(self, state):
        """
        Toggled when remote radio button state changes.

        :param state: boolean
        """

        if state:
            self.uiLocalGNS3VMSettingsGroupBox.setEnabled(False)
            self.uiRemoteGNS3VMSettingsGroupBox.setEnabled(True)
        else:
            self.uiLocalGNS3VMSettingsGroupBox.setEnabled(True)
            self.uiRemoteGNS3VMSettingsGroupBox.setEnabled(False)

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
            vm_settings = Servers.instance().settings()["vm"]
            for vm in result:
                vmx_path = ""
                if self.uiVmwareRadioButton.isChecked():
                    vmx_path = vm.get("vmx_path")
                self.uiVMListComboBox.addItem(vm["vmname"], vmx_path)
            gns3_vm = Servers.instance().vmSettings()
            index = self.uiVMListComboBox.findText(gns3_vm["vmname"])
            if index != -1:
                self.uiVMListComboBox.setCurrentIndex(index)
            else:
                index = self.uiVMListComboBox.findText("GNS3 VM")
                if index != -1:
                    self.uiVMListComboBox.setCurrentIndex(index)

    def _enableGNS3VMSlot(self, state):
        """
        Slot to enable or not the GNS3 VM settings.
        """

        if state:
            if not self.uiLocalServerAutoStartCheckBox.isChecked() and not self.uiRemoteRadioButton.isChecked():
                QtWidgets.QMessageBox.critical(self, "Local GNS3 VM", "The local server must be enabled in order to use a local GNS3 VM")
                self.uiEnableVMCheckBox.setChecked(False)
                return
            if self.uiRemoteRadioButton.isChecked():
                self.uiRemoteGNS3VMSettingsGroupBox.setEnabled(True)
                self.uiLocalGNS3VMSettingsGroupBox.setEnabled(False)
            else:
                self.uiLocalGNS3VMSettingsGroupBox.setEnabled(True)
                self.uiRemoteGNS3VMSettingsGroupBox.setEnabled(False)
                self._refreshVMListSlot()
        else:
            self.uiLocalGNS3VMSettingsGroupBox.setEnabled(False)
            self.uiRemoteGNS3VMSettingsGroupBox.setEnabled(False)

    def _useLocalServerAutoStartSlot(self, state):
        """
        Slot to enable or not local server settings.
        """

        if state:
            self.uiGeneralSettingsGroupBox.setEnabled(True)
            self.uiConsolePortRangeGroupBox.setEnabled(True)
            self.uiUDPPortRangeGroupBox.setEnabled(True)
        else:
            if self.uiEnableVMCheckBox.isChecked() and not self.uiRemoteRadioButton.isChecked():
                QtWidgets.QMessageBox.critical(self, "Local GNS3 VM", "The local server need to be enable in order to use a local GNS3 VM. Please deactivate the local GNS3 VM before turning off the local server.")
                self.uiLocalServerAutoStartCheckBox.setChecked(True)
                return
            self.uiGeneralSettingsGroupBox.setEnabled(False)
            self.uiConsolePortRangeGroupBox.setEnabled(False)
            self.uiUDPPortRangeGroupBox.setEnabled(False)

    def _restoreDefaultsSlot(self):
        """
        Slot to restore default settings
        """

        self._populateWidgets(SERVERS_SETTINGS)

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

    def _ubridgeBrowserSlot(self):
        """
        Slot to open a file browser and select the ubridge executable path.
        """

        filter = ""
        if sys.platform.startswith("win"):
            filter = "Executable (*.exe);;All files (*.*)"

        ubridge_path = shutil.which("ubridge")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select ubridge executable", ubridge_path, filter)
        if not path:
            return

        self.uiUbridgePathLineEdit.setText(path)

    def _remoteServerChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiRemoteServersTreeWidget.currentItem()
        if item:
            self.uiDeleteRemoteServerPushButton.setEnabled(True)
        else:
            self.uiDeleteRemoteServerPushButton.setEnabled(False)

    def _remoteServerAddSlot(self):
        """
        Adds a new remote server.
        """

        dialog = NewServerDialog(self.parent())
        dialog.show()
        if dialog.exec_():
            self.loadPreferences()

    def _remoteServerDeleteSlot(self):
        """
        Deletes a remote server.
        """

        item = self.uiRemoteServersTreeWidget.currentItem()
        if item:
            assert item.server_id in self._remote_servers, "Missing {} in {}".format(item.server_id, self._remote_servers)
            del self._remote_servers[item.server_id]
            self.uiRemoteServersTreeWidget.takeTopLevelItem(self.uiRemoteServersTreeWidget.indexOfTopLevelItem(item))

    def _populateWidgets(self, servers_settings):
        """
        Populates the widgets with the settings.

        :param servers_settings: servers settings
        """

        # local server settings
        local_server_settings = servers_settings["local_server"]
        self.uiLocalServerPathLineEdit.setText(local_server_settings["path"])
        self.uiUbridgePathLineEdit.setText(local_server_settings["ubridge_path"])
        index = self.uiLocalServerHostComboBox.findData(local_server_settings["host"])
        if index != -1:
            self.uiLocalServerHostComboBox.setCurrentIndex(index)
        self.uiLocalServerPortSpinBox.setValue(local_server_settings["port"])
        self.uiLocalServerAutoStartCheckBox.setChecked(local_server_settings["auto_start"])
        self.uiLocalServerAuthCheckBox.setChecked(local_server_settings["auth"])
        self.uiConsoleConnectionsToAnyIPCheckBox.setChecked(local_server_settings["allow_console_from_anywhere"])
        self.uiConsoleStartPortSpinBox.setValue(local_server_settings["console_start_port_range"])
        self.uiConsoleEndPortSpinBox.setValue(local_server_settings["console_end_port_range"])
        self.uiUDPStartPortSpinBox.setValue(local_server_settings["udp_start_port_range"])
        self.uiUDPEndPortSpinBox.setValue(local_server_settings["udp_end_port_range"])

        # Local GNS3 VM settings
        vm_settings = servers_settings["vm"]
        self.uiEnableVMCheckBox.setChecked(vm_settings["auto_start"])
        self.uiShutdownCheckBox.setChecked(vm_settings["auto_stop"])
        self.uiAdjustLocalServerIPCheckBox.setChecked(vm_settings["adjust_local_server_ip"])
        index = self.uiVMListComboBox.findText(vm_settings["vmname"])
        if index != -1:
            self.uiVMListComboBox.setCurrentIndex(index)
        else:
            self.uiVMListComboBox.clear()
            vmx_path = ""
            if vm_settings["virtualization"] == "VMware":
                vmx_path = vm_settings["vmx_path"]
            self.uiVMListComboBox.addItem(vm_settings["vmname"], vmx_path)
        if vm_settings["virtualization"] == "VMware":
            self.uiVmwareRadioButton.setChecked(True)
        elif vm_settings["virtualization"] == "VirtualBox":
            self.uiVirtualBoxRadioButton.setChecked(True)
        else:
            self.uiRemoteRadioButton.setChecked(True)
        self.uiHeadlessCheckBox.setChecked(vm_settings["headless"])

    def loadPreferences(self):
        """
        Loads the server preferences.
        """

        servers = Servers.instance()
        # load the servers settings
        servers_settings = servers.settings()
        self._populateWidgets(servers_settings)

        # load remote server preferences
        self._remote_servers.clear()
        self.uiServersComboBox.clear()
        self.uiRemoteServersTreeWidget.clear()
        for server_id, server in servers.remoteServers().items():
            protocol = server.protocol()
            host = server.host()
            port = server.port()
            user = server.user()
            self._remote_servers[server_id] = server.settings()
            item = QtWidgets.QTreeWidgetItem(self.uiRemoteServersTreeWidget)
            item.setText(0, protocol)
            item.setText(1, host)
            item.setText(2, str(port))
            item.setText(3, user)
            item.settings = server.settings()
            item.server_id = server_id

            self.uiServersComboBox.addItem(server.url(), server)

        self.uiServersComboBox.setCurrentIndex(self.uiServersComboBox.findText(servers_settings['vm']['remote_vm_url']))

        self.uiRemoteServersTreeWidget.resizeColumnToContents(0)

    def savePreferences(self):
        """
        Saves the server preferences.
        """

        servers = Servers.instance()
        servers_settings = servers.settings()
        local_server_settings = servers_settings["local_server"]
        restart_local_server = False
        restart_gns3_vm = False

        # save the local server preferences
        new_local_server_settings = local_server_settings.copy()
        new_local_server_settings.update({"path": self.uiLocalServerPathLineEdit.text(),
                                          "ubridge_path": self.uiUbridgePathLineEdit.text(),
                                          "host": self.uiLocalServerHostComboBox.itemData(self.uiLocalServerHostComboBox.currentIndex()),
                                          "port": self.uiLocalServerPortSpinBox.value(),
                                          "auto_start": self.uiLocalServerAutoStartCheckBox.isChecked(),
                                          "allow_console_from_anywhere": self.uiConsoleConnectionsToAnyIPCheckBox.isChecked(),
                                          "auth": self.uiLocalServerAuthCheckBox.isChecked(),
                                          "console_start_port_range": self.uiConsoleStartPortSpinBox.value(),
                                          "console_end_port_range": self.uiConsoleEndPortSpinBox.value(),
                                          "udp_start_port_range": self.uiUDPStartPortSpinBox.value(),
                                          "udp_end_port_range": self.uiUDPEndPortSpinBox.value()})

        if new_local_server_settings["console_end_port_range"] <= new_local_server_settings["console_start_port_range"]:
            QtWidgets.QMessageBox.critical(self, "Port range", "Invalid console port range from {} to {}".format(new_local_server_settings["console_start_port_range"],
                                                                                                                 new_local_server_settings["console_end_port_range"]))
            return

        if new_local_server_settings["udp_end_port_range"] <= new_local_server_settings["udp_start_port_range"]:
            QtWidgets.QMessageBox.critical(self, "Port range", "Invalid UDP port range from {} to {}".format(new_local_server_settings["udp_start_port_range"],
                                                                                                             new_local_server_settings["udp_end_port_range"]))
            return

        if new_local_server_settings["auto_start"]:
            if not os.path.isfile(new_local_server_settings["path"]):
                QtWidgets.QMessageBox.critical(self, "Local server", "Could not find local server {}".format(new_local_server_settings["path"]))
                return
            if not os.access(new_local_server_settings["path"], os.X_OK):
                QtWidgets.QMessageBox.critical(self, "Local server", "{} is not an executable".format(new_local_server_settings["path"]))

            if new_local_server_settings != local_server_settings:
                # first check if we have nodes on the local server
                local_nodes = []
                topology = Topology.instance()
                for node in topology.nodes():
                    if node.server().isLocal():
                        local_nodes.append(node.name())
                if local_nodes:
                    nodes = "\n".join(local_nodes)
                    MessageBox(self, "Local server", "Please close your project or delete all the nodes running on the local server before changing the local server settings", nodes)
                    return
                servers.setLocalServerSettings(new_local_server_settings)
                servers.registerLocalServer()
                restart_local_server = True
        else:
            servers.setLocalServerSettings(new_local_server_settings)
            servers.stopLocalServer(wait=True)

        # save the GNS3 VM preferences
        new_gns3vm_settings = servers_settings["vm"].copy()
        new_gns3vm_settings.update({"auto_start": self.uiEnableVMCheckBox.isChecked(),
                                    "auto_stop": self.uiShutdownCheckBox.isChecked(),
                                    "adjust_local_server_ip": self.uiAdjustLocalServerIPCheckBox.isChecked(),
                                    "vmname": self.uiVMListComboBox.currentText(),
                                    "vmx_path": self.uiVMListComboBox.currentData(),
                                    "headless": self.uiHeadlessCheckBox.isChecked()})


        if self.uiVmwareRadioButton.isChecked():
            new_gns3vm_settings["virtualization"] = "VMware"
        elif self.uiVirtualBoxRadioButton.isChecked():
            new_gns3vm_settings["virtualization"] = "VirtualBox"
        elif self.uiRemoteRadioButton.isChecked() and self.uiEnableVMCheckBox.isChecked():
            if self.uiServersComboBox.currentData() is None:
                QtWidgets.QMessageBox.critical(self, "Remote GNS3 VM host", "The remote GNS3 VM cannot be empty")
                return
            new_gns3vm_settings["virtualization"] = "remote"
            new_gns3vm_settings["remote_vm_protocol"] = self.uiServersComboBox.currentData().protocol()
            new_gns3vm_settings["remote_vm_password"] = self.uiServersComboBox.currentData().password()
            new_gns3vm_settings["remote_vm_host"] = self.uiServersComboBox.currentData().host()
            new_gns3vm_settings["remote_vm_port"] = self.uiServersComboBox.currentData().port()
            new_gns3vm_settings["remote_vm_user"] = self.uiServersComboBox.currentData().user()
            new_gns3vm_settings["remote_vm_url"] = self.uiServersComboBox.currentData().url()

        if new_gns3vm_settings != servers_settings["vm"]:
            log.info("GNS3 VM restart required!")
            restart_gns3_vm = True
        servers_settings["vm"].update(new_gns3vm_settings)

        # save the server preferences
        servers.setSettings(servers_settings)
        # save the remote server preferences
        servers.updateRemoteServers(self._remote_servers)
        servers.save()

        # start or restart the local GNS3 VM if required
        if restart_gns3_vm:
            gns3_vm = GNS3VM.instance()
            gns3_vm.shutdown(force=True)
            if servers_settings["vm"]["virtualization"] == "remote":
                servers.initVMServer()
            elif gns3_vm.autoStart():
                servers.initVMServer()
                worker = WaitForVMWorker()
                progress_dialog = ProgressDialog(worker, "Local GNS3 VM", "Starting the GNS3 VM...", "Cancel", busy=True, parent=self, delay=5)
                progress_dialog.show()
                if progress_dialog.exec_():
                    local_server_ip = gns3_vm.adjustLocalServerIP()
                    if local_server_ip != new_local_server_settings["host"]:
                        new_local_server_settings["host"] = local_server_ip
                        index = self.uiLocalServerHostComboBox.findData(local_server_ip)
                        if index != -1:
                            restart_local_server = True
                            self.uiLocalServerHostComboBox.setCurrentIndex(index)

        # start or restart the local server if required
        if restart_local_server:
            servers.stopLocalServer(wait=True)
            if servers.startLocalServer():
                worker = WaitForConnectionWorker(new_local_server_settings["host"], new_local_server_settings["port"])
                dialog = ProgressDialog(worker, "Local server", "Connecting...", "Cancel", busy=True, parent=self)
                dialog.show()
                dialog.exec_()
            else:
                QtWidgets.QMessageBox.critical(self, "Local server", "Could not start the local server process: {}".format(new_local_server_settings["path"]))

        self.loadPreferences()
