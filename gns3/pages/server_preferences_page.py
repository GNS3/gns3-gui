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
import re
import uuid
import shutil

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


class ServerPreferencesPage(QtWidgets.QWidget, Ui_ServerPreferencesPageWidget):

    """
    QWidget configuration page for server preferences.
    """

    def __init__(self, parent=None):

        super().__init__()
        self.setupUi(self)
        self._remote_servers = {}

        # connect the slots
        self.uiServerPreferenceTabWidget.currentChanged.connect(self._tabChangedSlot)
        self.uiLocalServerToolButton.clicked.connect(self._localServerBrowserSlot)
        self.uiUbridgeToolButton.clicked.connect(self._ubridgeBrowserSlot)
        self.uiAddRemoteServerPushButton.clicked.connect(self._remoteServerAddSlot)
        self.uiDeleteRemoteServerPushButton.clicked.connect(self._remoteServerDeleteSlot)
        self.uiRemoteServersTreeWidget.itemClicked.connect(self._remoteServerClickedSlot)
        self.uiRemoteServersTreeWidget.itemSelectionChanged.connect(self._remoteServerChangedSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiLocalServerAutoStartCheckBox.stateChanged.connect(self._useLocalServerAutoStartSlot)
        self.uiRemoteServerProtocolComboBox.currentIndexChanged.connect(self._remoteServerProtocolCurrentIndexSlot)
        self.uiRemoteServerSSHKeyPushButton.clicked.connect(self._remoteServerSSHKeyPushButtonSlot)
        self.uiEnableVMCheckBox.stateChanged.connect(self._enableGNS3VMSlot)
        self.uiRefreshPushButton.clicked.connect(self._refreshVMListSlot)
        self.uiVmwareRadioButton.clicked.connect(self._listVMwareVMsSlot)
        self.uiVirtualBoxRadioButton.clicked.connect(self._listVirtualBoxVMsSlot)

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

        self._remoteServerProtocolCurrentIndexSlot(0)

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

    def _enableGNS3VMSlot(self, state):
        """
        Slot to enable or not the GNS3 VM settings.
        """

        if state:
            if not self.uiLocalServerAutoStartCheckBox.isChecked():
                QtWidgets.QMessageBox.critical(self, "GNS3 VM", "The local server need to be enable in order to use the GNS3 VM")
                self.uiEnableVMCheckBox.setChecked(False)
                return
            self.uiGNS3VMSettingsGroupBox.setEnabled(True)
            self._refreshVMListSlot()
        else:
            self.uiGNS3VMSettingsGroupBox.setEnabled(False)

    def _remoteServerSSHKeyPushButtonSlot(self):
        """
        Slot to open a file browser and select an ssh key.
        """

        filter = ""
        ssh_dir = os.path.join(os.path.expanduser("~"), ".ssh")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the SSH key", ssh_dir, filter)
        if not path:
            return

        self.uiRemoteServerSSHKeyLineEdit.setText(path)

    def _remoteServerProtocolCurrentIndexSlot(self, index):
        if self.uiRemoteServerProtocolComboBox.currentText() == "SSH":
            self.uiRemoteServerPasswordLabel.hide()
            self.uiRemoteServerPasswordLineEdit.hide()
            self.uiRemoteServerSSHPortLabel.show()
            self.uiRemoteServerSSHPortSpinBox.show()
            self.uiRemoteServerSSHKeyLabel.show()
            self.uiRemoteServerSSHKeyLineEdit.show()
            self.uiRemoteServerSSHKeyPushButton.show()
        else:
            self.uiRemoteServerPasswordLabel.show()
            self.uiRemoteServerPasswordLineEdit.show()
            self.uiRemoteServerSSHPortLabel.hide()
            self.uiRemoteServerSSHPortSpinBox.hide()
            self.uiRemoteServerSSHKeyLabel.hide()
            self.uiRemoteServerSSHKeyLineEdit.hide()
            self.uiRemoteServerSSHKeyPushButton.hide()

    def _useLocalServerAutoStartSlot(self, state):
        """
        Slot to enable or not local server settings.
        """

        if state:
            self.uiGeneralSettingsGroupBox.setEnabled(True)
            self.uiConsolePortRangeGroupBox.setEnabled(True)
            self.uiUDPPortRangeGroupBox.setEnabled(True)
        else:
            if self.uiEnableVMCheckBox.isChecked():
                QtWidgets.QMessageBox.critical(self, "GNS3 VM", "The local server need to be enable in order to use the GNS3 VM. Please turn off the GNS3 VM before turning off the local server.")
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

    def _remoteServerClickedSlot(self, item, column):
        """
        Loads a selected remote server from the tree widget.

        :param item: selected QTreeWidgetItem instance
        :param column: ignored
        """

        settings = item.settings
        protocol = settings["protocol"].upper()
        try:
            port = int(settings["port"])
        except ValueError:
            QtWidgets.QMessageBox.critical(self, "Remote server", "Invalid port")
            return
        self.uiRemoteServerProtocolComboBox.setCurrentIndex(self.uiRemoteServerProtocolComboBox.findText(protocol))
        self.uiRemoteServerPortLineEdit.setText(settings["host"])
        self.uiRemoteServerPortSpinBox.setValue(port)
        self.uiRAMLimitSpinBox.setValue(settings["ram_limit"])
        self.uiRemoteServerUserLineEdit.setText(settings["user"])
        self.uiRemoteServerSSHKeyLineEdit.setText(settings.get("ssh_key", None))
        self.uiRemoteServerSSHPortSpinBox.setValue(settings.get("ssh_port", 22))

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

        protocol = self.uiRemoteServerProtocolComboBox.currentText().lower()
        host = self.uiRemoteServerPortLineEdit.text().strip()
        port = self.uiRemoteServerPortSpinBox.value()
        ram_limit = self.uiRAMLimitSpinBox.value()
        user = self.uiRemoteServerUserLineEdit.text().strip()
        password = self.uiRemoteServerPasswordLineEdit.text().strip()
        ssh_port = self.uiRemoteServerSSHPortSpinBox.value()
        ssh_key = self.uiRemoteServerSSHKeyLineEdit.text().strip()

        if not re.match(r"^[a-zA-Z0-9\.{}-]+$".format("\u0370-\u1CDF\u2C00-\u30FF\u4E00-\u9FBF"), host):
            QtWidgets.QMessageBox.critical(self, "Remote server", "Invalid remote server hostname {}".format(host))
            return
        if port is None or port < 1:
            QtWidgets.QMessageBox.critical(self, "Remote server", "Invalid remote server port {}".format(port))
            return

        if protocol == "ssh" and len(user) == 0:
            QtWidgets.QMessageBox.critical(self, "Remote server", "Missing user login")
            return

        if protocol == "ssh" and len(ssh_key) == 0:
            QtWidgets.QMessageBox.critical(self, "Remote server", "Missing SSH key")
            return

        # check if the remote server is already defined
        for server in self._remote_servers.values():
            if server["protocol"] == protocol and server["host"] == host and server["port"] == port and server["user"] == user:
                QtWidgets.QMessageBox.critical(self, "Remote server", "Remote server is already defined.")
                return

        settings = {"protocol": protocol,
                    "host": host,
                    "port": port,
                    "ram_limit": ram_limit,
                    "user": user,
                    "password": password,
                    "ssh_port": ssh_port,
                    "ssh_key": ssh_key}

        # add a new entry in the tree widget
        item = QtWidgets.QTreeWidgetItem(self.uiRemoteServersTreeWidget)
        item.setText(0, protocol)
        item.setText(1, host)
        item.setText(2, str(port))
        item.setText(3, user)
        item.settings = settings
        item.server_id = uuid.uuid4()  # Create a temporary unique server id

        # keep track of this remote server
        self._remote_servers[item.server_id] = settings

        self.uiRemoteServerPortSpinBox.setValue(self.uiRemoteServerPortSpinBox.value() + 1)
        self.uiRemoteServersTreeWidget.resizeColumnToContents(0)

    def _remoteServerDeleteSlot(self):
        """
        Deletes a remote server.
        """

        item = self.uiRemoteServersTreeWidget.currentItem()
        if item:
            assert item.server_id in self._remote_servers, "Missing {} in {}".format(item.server_id, self._remote_servers)
            del self._remote_servers[item.server_id]
            self.uiRemoteServersTreeWidget.takeTopLevelItem(self.uiRemoteServersTreeWidget.indexOfTopLevelItem(item))

    def _populateWidgets(self, servers_settings):
        """
        Populates the widgets with the settings.

        :param servers_settings: servers settings
        """

        if servers_settings["load_balancing_method"] == "ram_usage":
            self.uiRAMUsageRadioButton.setChecked(True)
        elif servers_settings["load_balancing_method"] == "round_robin":
            self.uiRoundRobinRadioButton.setChecked(True)
        elif servers_settings["load_balancing_method"] == "rendezvous_hashing":
            self.uiRendezVousHashingRadioButton.setChecked(True)

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

        # GNS3 VM settings
        vm_settings = servers_settings["vm"]
        self.uiVMUserLineEdit.setText(vm_settings["user"])
        self.uiVMPasswordLineEdit.setText(vm_settings["password"])
        self.uiEnableVMCheckBox.setChecked(vm_settings["auto_start"])
        self.uiShutdownCheckBox.setChecked(vm_settings["auto_stop"])
        self.uiAdjustLocalServerIPCheckBox.setChecked(vm_settings["adjust_local_server_ip"])
        index = self.uiVMListComboBox.findText(vm_settings["vmname"])
        if index != -1:
            self.uiVMListComboBox.setCurrentIndex(index)
        else:
            self.uiVMListComboBox.clear()
            self.uiVMListComboBox.addItem(vm_settings["vmname"], vm_settings["vmx_path"])
        if vm_settings["virtualization"] == "VMware":
            self.uiVmwareRadioButton.setChecked(True)
        elif vm_settings["virtualization"] == "VirtualBox":
            self.uiVirtualBoxRadioButton.setChecked(True)
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
                    MessageBox(self, "Local server", "Please close your project or delete all the nodes running on the \
                    local server before changing the local server settings", nodes)
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
                                    "headless": self.uiHeadlessCheckBox.isChecked(),
                                    "user": self.uiVMUserLineEdit.text(),
                                    "password": self.uiVMPasswordLineEdit.text()})
        if self.uiVmwareRadioButton.isChecked():
            new_gns3vm_settings["virtualization"] = "VMware"
        elif self.uiVirtualBoxRadioButton.isChecked():
            new_gns3vm_settings["virtualization"] = "VirtualBox"
        if new_gns3vm_settings != servers_settings["vm"]:
            restart_gns3_vm = True
        servers_settings["vm"].update(new_gns3vm_settings)

        # save the load-balancing preference
        if self.uiRAMUsageRadioButton.isChecked():
            servers_settings["load_balancing_method"] = "ram_usage"
        elif self.uiRoundRobinRadioButton.isChecked():
            servers_settings["load_balancing_method"] = "round_robin"
        elif self.uiRendezVousHashingRadioButton.isChecked():
            servers_settings["load_balancing_method"] = "rendezvous_hashing"

        # save the server preferences
        servers.setSettings(servers_settings)
        # save the remote server preferences
        servers.updateRemoteServers(self._remote_servers)
        servers.save()

        # start or restart the GNS3 VM if required
        if restart_gns3_vm:
            gns3_vm = GNS3VM.instance()
            gns3_vm.shutdown(force=True)
            if gns3_vm.autoStart():
                servers.initVMServer()
                worker = WaitForVMWorker()
                progress_dialog = ProgressDialog(worker, "GNS3 VM", "Starting the GNS3 VM...", "Cancel", busy=True, parent=self)
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
