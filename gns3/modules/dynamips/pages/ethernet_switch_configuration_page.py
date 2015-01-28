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
Configuration page for Dynamips Ethernet switches.
"""

from gns3.qt import QtCore, QtGui
from ..utils.tree_widget_item import TreeWidgetItem
from ..ui.ethernet_switch_configuration_page_ui import Ui_ethernetSwitchConfigPageWidget


class EthernetSwitchConfigurationPage(QtGui.QWidget, Ui_ethernetSwitchConfigPageWidget):

    """
    QWidget configuration page for Ethernet switches.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self._ports = {}

        # connect slots
        self.uiAddPushButton.clicked.connect(self._addPortSlot)
        self.uiDeletePushButton.clicked.connect(self._deletePortSlot)
        self.uiPortsTreeWidget.itemActivated.connect(self._portSelectedSlot)
        self.uiPortsTreeWidget.itemSelectionChanged.connect(self._portSelectionChangedSlot)

        # enable sorting
        self.uiPortsTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.uiPortsTreeWidget.setSortingEnabled(True)

    def _portSelectedSlot(self, item, column):
        """
        Loads a selected port from the tree widget.

        :param item: selected TreeWidgetItem instance
        :param column: ignored
        """

        port = int(item.text(0))
        vlan = int(item.text(1))
        port_type = item.text(2)
        self.uiPortSpinBox.setValue(port)
        self.uiVlanSpinBox.setValue(vlan)
        index = self.uiPortTypeComboBox.findText(port_type)
        if index != -1:
            self.uiPortTypeComboBox.setCurrentIndex(index)

    def _portSelectionChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiPortsTreeWidget.currentItem()
        if item:
            self.uiDeletePushButton.setEnabled(True)
        else:
            self.uiDeletePushButton.setEnabled(False)

    def _addPortSlot(self):
        """
        Adds a new port.
        """

        port = self.uiPortSpinBox.value()
        vlan = self.uiVlanSpinBox.value()
        port_type = self.uiPortTypeComboBox.currentText()

        if port in self._ports:
            # update a given entry in the tree widget
            item = self.uiPortsTreeWidget.findItems(str(port), QtCore.Qt.MatchFixedString)[0]
            item.setText(1, str(vlan))
            item.setText(2, port_type)

        else:
            # add a new entry in the tree widget
            item = TreeWidgetItem(self.uiPortsTreeWidget)
            item.setText(0, str(port))
            item.setText(1, str(vlan))
            item.setText(2, port_type)
            self.uiPortsTreeWidget.addTopLevelItem(item)

        self._ports[port] = {"type": port_type,
                             "vlan": vlan}

        self.uiPortSpinBox.setValue(max(self._ports) + 1)
        self.uiPortsTreeWidget.resizeColumnToContents(0)

    def _deletePortSlot(self):
        """
        Deletes a port.
        """

        item = self.uiPortsTreeWidget.currentItem()
        if item:
            port = int(item.text(0))
            node_ports = self._node.ports()
            for node_port in node_ports:
                if node_port.portNumber() == port and not node_port.isFree():
                    QtGui.QMessageBox.critical(self, self._node.name(), "A link is connected to port {}, please remove it first".format(node_port.name()))
                    return
            del self._ports[port]
            self.uiPortsTreeWidget.takeTopLevelItem(self.uiPortsTreeWidget.indexOfTopLevelItem(item))

        if len(self._ports):
            self.uiPortSpinBox.setValue(max(self._ports) + 1)
        else:
            self.uiPortSpinBox.setValue(1)

    def loadSettings(self, settings, node, group=False):
        """
        Loads the Ethernet switch settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
        else:
            self.uiNameLineEdit.setEnabled(False)

        self.uiPortsTreeWidget.clear()
        self._ports = {}
        self._node = node

        for port, info in settings["ports"].items():
            item = TreeWidgetItem(self.uiPortsTreeWidget)
            item.setText(0, str(port))
            item.setText(1, str(info["vlan"]))
            item.setText(2, info["type"])
            self.uiPortsTreeWidget.addTopLevelItem(item)
            self._ports[port] = info

        self.uiPortsTreeWidget.resizeColumnToContents(0)
        self.uiPortsTreeWidget.resizeColumnToContents(1)
        if len(self._ports) > 0:
            self.uiPortSpinBox.setValue(max(self._ports) + 1)

    def saveSettings(self, settings, node, group=False):
        """
        Saves the Ethernet switch settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            # set the device name
            name = self.uiNameLineEdit.text()
            if not name:
                QtGui.QMessageBox.critical(self, "Name", "Ethernet switch name cannot be empty!")
            else:
                settings["name"] = name
        else:
            del settings["name"]

        settings["ports"] = self._ports.copy()
