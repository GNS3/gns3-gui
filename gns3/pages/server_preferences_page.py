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
from gns3.qt import QtNetwork, QtGui
from ..ui.server_preferences_page_ui import Ui_ServerPreferencesPageWidget
from ..servers import Servers
from ..topology import Topology
from ..utils.message_box import MessageBox
from ..utils.progress_dialog import ProgressDialog
from ..utils.wait_for_connection_thread import WaitForConnectionThread
from ..settings import LOCAL_SERVER_SETTINGS


class ServerPreferencesPage(QtGui.QWidget, Ui_ServerPreferencesPageWidget):

    """
    QWidget configuration page for server preferences.
    """

    def __init__(self, parent=None):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self._remote_servers = {}

        # connect the slots
        self.uiLocalServerToolButton.clicked.connect(self._localServerBrowserSlot)
        self.uiAddRemoteServerPushButton.clicked.connect(self._remoteServerAddSlot)
        self.uiDeleteRemoteServerPushButton.clicked.connect(self._remoteServerDeleteSlot)
        self.uiRemoteServersTreeWidget.itemClicked.connect(self._remoteServerClickedSlot)
        self.uiRemoteServersTreeWidget.itemSelectionChanged.connect(self._remoteServerChangedSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiLocalServerAutoStartCheckBox.stateChanged.connect(self._useLocalServerAutoStartSlot)

        # load all available addresses
        for address in QtNetwork.QNetworkInterface.allAddresses():
            address_string = address.toString()
            if address.protocol() == QtNetwork.QAbstractSocket.IPv6Protocol:
                continue  # FIXME: finish IPv6 support (problem with ws4py)
                # we do not want the scope id when using an IPv6 address...
                address.setScopeId("")
            self.uiLocalServerHostComboBox.addItem(address_string, address.toString())

        # default is 127.0.0.1
        index = self.uiLocalServerHostComboBox.findText("127.0.0.1")
        if index != -1:
            self.uiLocalServerHostComboBox.setCurrentIndex(index)

    def _useLocalServerAutoStartSlot(self, state):
        """
        Slot to enable or not local server settings.
        """

        if state:
            self.uiGeneralSettingsGroupBox.setEnabled(True)
            self.uiConsolePortRangeGroupBox.setEnabled(True)
            self.uiUDPPortRangeGroupBox.setEnabled(True)
        else:
            self.uiGeneralSettingsGroupBox.setEnabled(False)
            self.uiConsolePortRangeGroupBox.setEnabled(False)
            self.uiUDPPortRangeGroupBox.setEnabled(False)

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
        path = QtGui.QFileDialog.getOpenFileName(self, "Select the local server", ".", filter)
        if not path:
            return

        self.uiLocalServerPathLineEdit.setText(path)

    def _remoteServerClickedSlot(self, item, column):
        """
        Loads a selected remote server from the tree widget.

        :param item: selected QTreeWidgetItem instance
        :param column: ignored
        """

        host = item.text(0)
        try:
            port = int(item.text(1))
        except ValueError:
            QtGui.QMessageBox.critical(self, "Remote server", "Invalid port")
            return
        self.uiRemoteServerPortLineEdit.setText(host)
        self.uiRemoteServerPortSpinBox.setValue(port)

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

        host = self.uiRemoteServerPortLineEdit.text()
        port = self.uiRemoteServerPortSpinBox.value()

        # check if the remote server is already defined
        remote_server = "{host}:{port}".format(host=host, port=port)
        if remote_server in self._remote_servers:
            QtGui.QMessageBox.critical(self, "Remote server", "Remote server {} is already defined.".format(remote_server))
            return

        # add a new entry in the tree widget
        item = QtGui.QTreeWidgetItem(self.uiRemoteServersTreeWidget)
        item.setText(0, host)
        item.setText(1, str(port))

        # keep track of this remote server
        self._remote_servers[remote_server] = {"host": host,
                                               "port": port}

        self.uiRemoteServerPortSpinBox.setValue(self.uiRemoteServerPortSpinBox.value() + 1)
        self.uiRemoteServersTreeWidget.resizeColumnToContents(0)

    def _remoteServerDeleteSlot(self):
        """
        Deletes a remote server.
        """

        item = self.uiRemoteServersTreeWidget.currentItem()
        if item:
            host = item.text(0)
            port = int(item.text(1))
            remote_server = "{host}:{port}".format(host=host, port=port)
            del self._remote_servers[remote_server]
            self.uiRemoteServersTreeWidget.takeTopLevelItem(self.uiRemoteServersTreeWidget.indexOfTopLevelItem(item))

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: Local server settings
        """

        self.uiLocalServerPathLineEdit.setText(settings["path"])
        index = self.uiLocalServerHostComboBox.findData(settings["host"])
        if index != -1:
            self.uiLocalServerHostComboBox.setCurrentIndex(index)
        self.uiLocalServerPortSpinBox.setValue(settings["port"])
        self.uiLocalServerAutoStartCheckBox.setChecked(settings["auto_start"])
        self.uiConsoleConnectionsToAnyIPCheckBox.setChecked(settings["allow_console_from_anywhere"])
        self.uiConsoleStartPortSpinBox.setValue(settings["console_start_port_range"])
        self.uiConsoleEndPortSpinBox.setValue(settings["console_end_port_range"])
        self.uiUDPStartPortSpinBox.setValue(settings["udp_start_port_range"])
        self.uiUDPEndPortSpinBox.setValue(settings["udp_end_port_range"])

    def loadPreferences(self):
        """
        Loads the server preferences.
        """

        servers = Servers.instance()

        # load the local server preferences
        local_server_settings = servers.localServerSettings()
        self._populateWidgets(local_server_settings)

        # load remote server preferences
        self._remote_servers.clear()
        self.uiRemoteServersTreeWidget.clear()
        for server_id, server in servers.remoteServers().items():
            host = server.host
            port = server.port
            self._remote_servers[server_id] = {"host": host,
                                               "port": port}
            item = QtGui.QTreeWidgetItem(self.uiRemoteServersTreeWidget)
            item.setText(0, host)
            item.setText(1, str(port))

        self.uiRemoteServersTreeWidget.resizeColumnToContents(0)

    def savePreferences(self):
        """
        Saves the server preferences.
        """

        servers = Servers.instance()
        current_settings = servers.localServerSettings()
        restart_local_server = False

        # save the local server preferences
        new_settings = {}
        new_settings["path"] = self.uiLocalServerPathLineEdit.text()
        new_settings["host"] = self.uiLocalServerHostComboBox.itemData(self.uiLocalServerHostComboBox.currentIndex())
        new_settings["port"] = self.uiLocalServerPortSpinBox.value()
        new_settings["auto_start"] = self.uiLocalServerAutoStartCheckBox.isChecked()
        new_settings["allow_console_from_anywhere"] = self.uiConsoleConnectionsToAnyIPCheckBox.isChecked()
        new_settings["console_start_port_range"] = self.uiConsoleStartPortSpinBox.value()
        new_settings["console_end_port_range"] = self.uiConsoleEndPortSpinBox.value()
        new_settings["udp_start_port_range"] = self.uiUDPStartPortSpinBox.value()
        new_settings["udp_end_port_range"] = self.uiUDPEndPortSpinBox.value()
        new_settings["images_path"] = current_settings["images_path"]
        new_settings["projects_path"] = current_settings["projects_path"]
        new_settings["report_errors"] = current_settings["report_errors"]

        if new_settings["console_end_port_range"] <= new_settings["console_start_port_range"]:
            QtGui.QMessageBox.critical(self, "Local", "Invalid console port range from {} to {}".format(new_settings["console_start_port_range"],
                                                                                                        new_settings["console_end_port_range"]))
            return

        if new_settings["udp_end_port_range"] <= new_settings["udp_start_port_range"]:
            QtGui.QMessageBox.critical(self, "Local", "Invalid UDP port range from {} to {}".format(new_settings["udp_start_port_range"],
                                                                                                    new_settings["udp_end_port_range"]))
            return

        if new_settings["auto_start"]:
            if not os.path.isfile(new_settings["path"]):
                QtGui.QMessageBox.critical(self, "Local server", "Could not find local server {}".format(new_settings["path"]))
                return
            if not os.access(new_settings["path"], os.X_OK):
                QtGui.QMessageBox.critical(self, "Local server", "{} is not an executable".format(new_settings["path"]))

            if new_settings != current_settings:
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
                restart_local_server = True
        else:
            servers.stopLocalServer(wait=True)

        # save the local server preferences
        servers.setLocalServerSettings(new_settings)
        # save the remote server preferences
        servers.updateRemoteServers(self._remote_servers)
        servers.save()

        # restart the local server if required
        if restart_local_server:
            servers.stopLocalServer(wait=True)
            if servers.startLocalServer():
                thread = WaitForConnectionThread(new_settings["host"], new_settings["port"])
                thread.deleteLater()
                dialog = ProgressDialog(thread, "Local server", "Connecting...", "Cancel", busy=True, parent=self)
                dialog.show()
                dialog.exec_()
            else:
                QtGui.QMessageBox.critical(self, "Local server", "Could not start the local server process: {}".format(new_settings["path"]))
