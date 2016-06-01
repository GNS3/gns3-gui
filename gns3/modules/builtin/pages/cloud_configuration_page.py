# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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
Configuration page for clouds.
"""

from gns3.qt import QtCore, QtWidgets
from ..ui.cloud_configuration_page_ui import Ui_cloudConfigPageWidget
from ..cloud import Cloud


class CloudConfigurationPage(QtWidgets.QWidget, Ui_cloudConfigPageWidget):

    """
    QWidget configuration page for clouds.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self._ports = []

        # connect Ethernet slots
        self.uiEthernetListWidget.itemSelectionChanged.connect(self._EthernetChangedSlot)
        self.uiAddEthernetPushButton.clicked.connect(self._EthernetAddSlot)
        self.uiAddAllEthernetPushButton.clicked.connect(self._EthernetAddAllSlot)
        self.uiDeleteEthernetPushButton.clicked.connect(self._EthernetDeleteSlot)

        # connect TAP slots
        self.uiTAPComboBox.currentIndexChanged.connect(self._TAPSelectedSlot)
        self.uiTAPListWidget.itemSelectionChanged.connect(self._TAPChangedSlot)
        self.uiAddTAPPushButton.clicked.connect(self._TAPAddSlot)
        self.uiAddAllTAPPushButton.clicked.connect(self._TAPAddAllSlot)
        self.uiDeleteTAPPushButton.clicked.connect(self._TAPDeleteSlot)

        # connect UDP slots
        self.uiUDPTreeWidget.itemActivated.connect(self._UDPSelectedSlot)
        self.uiUDPTreeWidget.itemSelectionChanged.connect(self._UDPChangedSlot)
        self.uiAddUDPPushButton.clicked.connect(self._UDPAddSlot)
        self.uiDeleteUDPPushButton.clicked.connect(self._UDPDeleteSlot)

        self.uiShowSpecialInterfacesCheckBox.stateChanged.connect(self._showSpecialInterfacesSlot)

    def _EthernetChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiEthernetListWidget.currentItem()
        if item:
            self.uiDeleteEthernetPushButton.setEnabled(True)
        else:
            self.uiDeleteEthernetPushButton.setEnabled(False)

    def _EthernetAddSlot(self, interface=None):
        """
        Adds a new Ethernet interface.
        """

        if not interface:
            interface = self.uiEthernetComboBox.currentText()
        if interface:
            for port in self._ports:
                if port["name"] == interface and port["type"] == "ethernet":
                    return
            self.uiEthernetListWidget.addItem(interface)
            self._ports.append({"name": interface,
                                "port_number": len(self._ports) + 1,
                                "type": "ethernet",
                                "interface": interface})
            index = self.uiEthernetComboBox.findText(interface)
            if index != -1:
                self.uiEthernetComboBox.removeItem(index)

    def _EthernetAddAllSlot(self):
        """
        Adds all Ethernet interfaces.
        """

        for index in range(0, self.uiEthernetComboBox.count()):
            interface = self.uiEthernetComboBox.itemText(index)
            self._EthernetAddSlot(interface)

    def _EthernetDeleteSlot(self):
        """
        Deletes the selected Ethernet interface.
        """

        for item in self.uiEthernetListWidget.selectedItems():
            interface = item.text()
            # check we can delete that interface
            for node_port in self._node.ports():
                if node_port.name() == interface and not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to {}, please remove it first".format(interface))
                    return

        for item in self.uiEthernetListWidget.selectedItems():
            interface = item.text()
            for port in self._ports.copy():
                if port["name"] == interface:
                    self._ports.remove(port)
                    print("remove {}".format(port["name"]))
                    self.uiEthernetListWidget.takeItem(self.uiEthernetListWidget.currentRow())
                    for interface in self._node.interfaces():
                        if not self.uiShowSpecialInterfacesCheckBox.isChecked() and Cloud.isSpecialInterface(interface["name"]):
                            continue
                        if interface["name"] == port["name"] and interface["type"] == "ethernet":
                            self.uiEthernetComboBox.addItem(interface["name"])
                            break
                    break

    def _TAPSelectedSlot(self, index):
        """
        Loads the selected TAP interface.

        :param index: ignored
        """

        self.uiTAPLineEdit.setText(self.uiTAPComboBox.currentText())

    def _TAPChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiTAPListWidget.currentItem()
        if item:
            self.uiDeleteTAPPushButton.setEnabled(True)
            self.uiTAPLineEdit.setText(item.text())
        else:
            self.uiDeleteTAPPushButton.setEnabled(False)

    def _TAPAddSlot(self, interface=None):
        """
        Adds a new TAP interface.
        """

        if not interface:
            interface = self.uiTAPLineEdit.text()
        if interface:
            for port in self._ports:
                if port["name"] == interface and port["type"] == "tap":
                    return
            self.uiTAPListWidget.addItem(interface)
            self._ports.append({"name": interface,
                                "port_number": len(self._ports) + 1,
                                "type": "tap",
                                "interface": interface})
            index = self.uiTAPComboBox.findText(interface)
            if index != -1:
                self.uiTAPComboBox.removeItem(index)

    def _TAPAddAllSlot(self):
        """
        Adds all TAP interfaces
        """

        for index in range(0, self.uiTAPComboBox.count()):
            interface = self.uiTAPComboBox.itemText(index)
            self._TAPAddSlot(interface)

    def _TAPDeleteSlot(self):
        """
        Deletes a TAP interface.
        """

        for item in self.uiTAPListWidget.selectedItems():
            interface = item.text()
            # check we can delete that interface
            for node_port in self._node.ports():
                if node_port.name() == interface and not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to {}, please remove it first".format(interface))
                    return

        for item in self.uiTAPListWidget.selectedItems():
            interface = item.text()
            for port in self._ports.copy():
                if port["name"] == interface:
                    self._ports.remove(port)
                    self.uiTAPListWidget.takeItem(self.uiTAPListWidget.currentRow())
                    for interface in self._node.interfaces():
                        if interface["name"] == port["name"] and interface["type"] == "tap":
                            self.uiTAPComboBox.addItem(interface["name"])
                    break

    def _UDPSelectedSlot(self, item, column):
        """
        Loads a selected UDP tunnel.

        :param item: selected TreeWidgetItem instance
        :param column: ignored
        """

        name = item.text(0)
        local_port = int(item.text(1))
        remote_host = item.text(2)
        remote_port = int(item.text(3))
        self.uiUDPNameLineEdit.setText(name)
        self.uiLocalPortSpinBox.setValue(local_port)
        self.uiRemoteHostLineEdit.setText(remote_host)
        self.uiRemotePortSpinBox.setValue(remote_port)

    def _UDPChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiUDPTreeWidget.currentItem()
        if item:
            self.uiDeleteUDPPushButton.setEnabled(True)
        else:
            self.uiDeleteUDPPushButton.setEnabled(False)

    def _UDPAddSlot(self):
        """
        Adds a new UDP tunnel
        """

        name = self.uiUDPNameLineEdit.text()
        local_port = self.uiLocalPortSpinBox.value()
        remote_host = self.uiRemoteHostLineEdit.text()
        remote_port = self.uiRemotePortSpinBox.value()
        if name and remote_host:
            for port in self._ports:
                if port["name"] == name:
                    return

            # add a new entry in the tree widget
            item = QtWidgets.QTreeWidgetItem(self.uiUDPTreeWidget)
            item.setText(0, name)
            item.setText(1, str(local_port))
            item.setText(2, remote_host)
            item.setText(3, str(remote_port))
            self.uiUDPTreeWidget.addTopLevelItem(item)
            self._ports.append({"name": name,
                                "port_number": len(self._ports) + 1,
                                "type": "udp",
                                "lport": local_port,
                                "rhost": remote_host,
                                "rport": remote_port})
            self.uiLocalPortSpinBox.setValue(local_port + 1)
            self.uiRemotePortSpinBox.setValue(remote_port + 1)
            self.uiUDPTreeWidget.resizeColumnToContents(0)
            self.uiUDPTreeWidget.resizeColumnToContents(1)
            self.uiUDPTreeWidget.resizeColumnToContents(2)
            self.uiUDPTreeWidget.resizeColumnToContents(3)
            nb_tunnels = 0
            for port in self._ports:
                if port["type"] == "udp":
                    nb_tunnels += 1
            self.uiUDPNameLineEdit.setText("UDP tunnel {}".format(nb_tunnels + 1))

    def _UDPDeleteSlot(self):
        """
        Deletes an UDP tunnel.
        """

        for item in self.uiUDPTreeWidget.selectedItems():
            name = item.text(0)
            # check we can delete that UDP tunnel
            for node_port in self._node.ports():
                if node_port.name() == name and not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to {}, please remove it first".format(name))
                    return

        for item in self.uiUDPTreeWidget.selectedItems():
            name = item.text(0)
            for port in self._ports.copy():
                if port["name"] == name:
                    self._ports.remove(port)
            self.uiUDPTreeWidget.takeTopLevelItem(self.uiUDPTreeWidget.indexOfTopLevelItem(item))
            nb_tunnels = 0
            for port in self._ports:
                if port["type"] == "udp":
                    nb_tunnels += 1
            self.uiUDPNameLineEdit.setText("UDP tunnel {}".format(nb_tunnels + 1))

    def _showSpecialInterfacesSlot(self, state):

        self.uiEthernetComboBox.clear()
        index = 0
        for interface in self._node.interfaces():
            if interface["type"] == "ethernet":
                if not state and Cloud.isSpecialInterface(interface["name"]):
                    continue
                if self.uiEthernetListWidget.findItems(interface["name"], QtCore.Qt.MatchFixedString):
                    continue
                self.uiEthernetComboBox.addItem(interface["name"])
                index += 1

    def loadSettings(self, settings, node, group=False):
        """
        Loads the cloud settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
        else:
            self.uiNameLineEdit.setEnabled(False)

        self._node = node

        # load all Ethernet network interfaces
        self.uiEthernetComboBox.clear()
        index = 0
        for interface in self._node.interfaces():
            if interface["type"] == "ethernet" and not Cloud.isSpecialInterface(interface["name"]):
                self.uiEthernetComboBox.addItem(interface["name"])
                index += 1

        # load all TAP interfaces
        self.uiTAPComboBox.clear()
        index = 0
        for interface in self._node.interfaces():
            if interface["type"] == "tap":
                self.uiTAPComboBox.addItem(interface["name"])
                index += 1

        # load the current ports
        self._ports = []
        self.uiEthernetListWidget.clear()
        self.uiTAPListWidget.clear()
        self.uiUDPTreeWidget.clear()

        for port in settings["ports"]:
            self._ports.append(port)
            if port["type"] == "ethernet":
                self.uiEthernetListWidget.addItem(port["name"])
                index = self.uiEthernetComboBox.findText(port["name"])
                if index != -1:
                    self.uiEthernetComboBox.removeItem(index)
            elif port["type"] == "tap":
                self.uiTAPListWidget.addItem(port["name"])
                index = self.uiTAPComboBox.findText(port["name"])
                if index != -1:
                    self.uiTAPComboBox.removeItem(index)
            elif port["type"] == "udp":
                item = QtWidgets.QTreeWidgetItem(self.uiUDPTreeWidget)
                item.setText(0, port["name"])
                item.setText(1, str(port["lport"]))
                item.setText(2, port["rhost"])
                item.setText(3, str(port["rport"]))
                self.uiUDPTreeWidget.addTopLevelItem(item)
                self.uiUDPTreeWidget.resizeColumnToContents(0)
                self.uiUDPTreeWidget.resizeColumnToContents(1)
                self.uiUDPTreeWidget.resizeColumnToContents(2)
                self.uiUDPTreeWidget.resizeColumnToContents(3)

    def saveSettings(self, settings, node, group=False):
        """
        Saves the cloud settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            settings["name"] = self.uiNameLineEdit.text()
        else:
            del settings["name"]

        settings["ports"] = self._ports
