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
import copy
import shutil

import logging
log = logging.getLogger(__name__)

from gns3.qt import QtNetwork, QtWidgets
from ..ui.server_preferences_page_ui import Ui_ServerPreferencesPageWidget
from ..topology import Topology
from ..utils.progress_dialog import ProgressDialog
from ..settings import LOCAL_SERVER_SETTINGS
from ..dialogs.edit_compute_dialog import EditComputeDialog
from ..local_server import LocalServer
from ..local_config import LocalConfig
from ..compute_manager import ComputeManager


class ServerPreferencesPage(QtWidgets.QWidget, Ui_ServerPreferencesPageWidget):

    """
    QWidget configuration page for server preferences.
    """

    def __init__(self, parent=None):

        super().__init__()
        self.setupUi(self)
        self._remote_computes = {}

        # connect the slots
        self.uiLocalServerToolButton.clicked.connect(self._localServerBrowserSlot)
        self.uiUbridgeToolButton.clicked.connect(self._ubridgeBrowserSlot)
        self.uiAddRemoteServerPushButton.clicked.connect(self._remoteServerAddSlot)
        self.uiDeleteRemoteServerPushButton.clicked.connect(self._remoteServerDeleteSlot)
        self.uiUpdateRemoteServerPushButton.clicked.connect(self._remoteServerUpdateSlot)

        self.uiRemoteServersTreeWidget.itemSelectionChanged.connect(self._remoteServerChangedSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiLocalServerAutoStartCheckBox.stateChanged.connect(self._useLocalServerAutoStartSlot)

        # load all available addresses
        for address in QtNetwork.QNetworkInterface.allAddresses():
            if address.protocol() == QtNetwork.QAbstractSocket.IPv4Protocol:
                address_string = address.toString()
                self.uiLocalServerHostComboBox.addItem(address_string, address_string)
        self.uiLocalServerHostComboBox.addItem("0.0.0.0", "0.0.0.0")

        # default is 127.0.0.1
        index = self.uiLocalServerHostComboBox.findText("127.0.0.1")
        if index != -1:
            self.uiLocalServerHostComboBox.setCurrentIndex(index)

    def _useLocalServerAutoStartSlot(self, state):
        """
        Slot to enable or not local server settings.
        """

        if state:
            self.uiGeneralSettingsGroupBox.setVisible(True)
            self.uiConsolePortRangeGroupBox.setVisible(True)
            self.uiUDPPortRangeGroupBox.setVisible(True)
            self.uiRemoteMainServerGroupBox.setVisible(False)
        else:
            self.uiRemoteMainServerGroupBox.setVisible(True)
            self.uiGeneralSettingsGroupBox.setVisible(False)
            self.uiConsolePortRangeGroupBox.setVisible(False)
            self.uiUDPPortRangeGroupBox.setVisible(False)

    def _restoreDefaultsSlot(self):
        """
        Slot to restore default settings
        """

        self._populateWidgets(LOCAL_SERVER_SETTINGS)

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
            self.uiUpdateRemoteServerPushButton.setEnabled(True)
        else:
            self.uiDeleteRemoteServerPushButton.setEnabled(False)
            self.uiUpdateRemoteServerPushButton.setEnabled(False)

    def _remoteServerAddSlot(self):
        """
        Adds a new remote server.
        """

        dialog = EditComputeDialog(self.parent())
        dialog.show()
        if dialog.exec_():
            self._remote_computes[dialog.compute().id()] = dialog.compute()
            self._populateRemoteServersTree()

    def _remoteServerDeleteSlot(self):
        """
        Deletes a remote server.
        """

        item = self.uiRemoteServersTreeWidget.currentItem()
        if item:
            del self._remote_computes[item.compute_id]
            self.uiRemoteServersTreeWidget.takeTopLevelItem(self.uiRemoteServersTreeWidget.indexOfTopLevelItem(item))

    def _remoteServerUpdateSlot(self):
        """
        Update a remote server.
        """

        item = self.uiRemoteServersTreeWidget.currentItem()
        dialog = EditComputeDialog(self.parent(), item.compute)
        dialog.show()
        if dialog.exec_():
            self._populateRemoteServersTree()

    def _populateWidgets(self, servers_settings):
        """
        Populates the widgets with the settings.

        :param servers_settings: servers settings
        """

        self.uiLocalServerPathLineEdit.setText(servers_settings["path"])
        self.uiUbridgePathLineEdit.setText(servers_settings["ubridge_path"])
        index = self.uiLocalServerHostComboBox.findData(servers_settings["host"])
        if index != -1:
            self.uiLocalServerHostComboBox.setCurrentIndex(index)
        self.uiLocalServerPortSpinBox.setValue(servers_settings["port"])

        self.uiRemoteMainServerHostLineEdit.setText(servers_settings["host"])
        self.uiRemoteMainServerPortSpinBox.setValue(servers_settings["port"])
        self.uiRemoteMainServerUserLineEdit.setText(servers_settings["user"])
        self.uiRemoteMainServerPasswordLineEdit.setText(servers_settings["password"])
        self.uiRemoteMainServerProtocolComboBox.setCurrentText(servers_settings["protocol"])
        self.uiRemoteMainServerAuthCheckBox.setChecked(servers_settings["auth"])

        self.uiLocalServerAutoStartCheckBox.setChecked(servers_settings["auto_start"])
        self._useLocalServerAutoStartSlot(servers_settings["auto_start"])

        self.uiLocalServerAuthCheckBox.setChecked(servers_settings["auth"])
        self.uiConsoleConnectionsToAnyIPCheckBox.setChecked(servers_settings["allow_console_from_anywhere"])
        self.uiConsoleStartPortSpinBox.setValue(servers_settings["console_start_port_range"])
        self.uiConsoleEndPortSpinBox.setValue(servers_settings["console_end_port_range"])
        self.uiUDPStartPortSpinBox.setValue(servers_settings["udp_start_port_range"])
        self.uiUDPEndPortSpinBox.setValue(servers_settings["udp_end_port_range"])

    def _populateRemoteServersTree(self):
        self.uiRemoteServersTreeWidget.clear()
        for compute in self._remote_computes.values():
            item = QtWidgets.QTreeWidgetItem(self.uiRemoteServersTreeWidget)
            item.setText(0, compute.name())
            item.setText(1, compute.protocol())
            item.setText(2, compute.host())
            item.setText(3, str(compute.port()))
            item.setText(4, compute.user())
            item.compute = self._remote_computes[compute.id()]
            item.compute_id = compute.id()
        self.uiRemoteServersTreeWidget.resizeColumnToContents(0)
        self._remoteServerChangedSlot()

    def loadPreferences(self):
        """
        Loads the server preferences.
        """

        # Settings from the gns3_server.conf
        local_server_settings = LocalServer.instance().localServerSettings()
        self._populateWidgets(local_server_settings)

        cm = ComputeManager.instance()
        # load remote server preferences
        self._remote_computes.clear()
        for compute in cm.remoteComputes():
            # We copy to be able to detect the change with the original element
            # when we apply the settings
            self._remote_computes[compute.id()] = copy.copy(compute)
        self._populateRemoteServersTree()

    def savePreferences(self):
        """
        Saves the server preferences.
        """

        local_server_settings = LocalServer.instance().localServerSettings()

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
                topology = Topology.instance()
                if len(topology.nodes()):
                    QtWidgets.QMessageBox.critical(self, "Local server", "Please close your project or delete all the nodes running on the local server before changing the local server settings")
                    return
                LocalServer.instance().updateLocalServerSettings(new_local_server_settings)
        else:
            new_local_server_settings["host"] = self.uiRemoteMainServerHostLineEdit.text()
            new_local_server_settings["port"] = self.uiRemoteMainServerPortSpinBox.value()
            new_local_server_settings["protocol"] = self.uiRemoteMainServerProtocolComboBox.currentText()
            new_local_server_settings["user"] = self.uiRemoteMainServerUserLineEdit.text()
            new_local_server_settings["password"] = self.uiRemoteMainServerPasswordLineEdit.text()
            new_local_server_settings["auth"] = self.uiRemoteMainServerAuthCheckBox.isChecked()

            # Some users get confused by remote server and  main server and same
            # configure the same server twice
            for compute in self._remote_computes.values():
                if new_local_server_settings["host"] == compute.host() and new_local_server_settings["port"] == compute.port():
                    QtWidgets.QMessageBox.critical(self, "Local server", "You can't use a server as main server and as a remote server.")
                    return
            LocalServer.instance().updateLocalServerSettings(new_local_server_settings)

        ComputeManager.instance().updateList(self._remote_computes.values())
        self.loadPreferences()
