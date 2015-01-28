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
Configuration page for Dynamips ATM bridges.
"""

import re
from gns3.qt import QtCore, QtGui
from ..ui.atm_bridge_configuration_page_ui import Ui_atmBridgeConfigPageWidget


class ATMBridgeConfigurationPage(QtGui.QWidget, Ui_atmBridgeConfigPageWidget):

    """
    QWidget configuration page for ATM bridges.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self._mapping = {}

        # connect slots
        self.uiAddPushButton.clicked.connect(self._addMappingSlot)
        self.uiDeletePushButton.clicked.connect(self._deleteMappingSlot)
        self.uiMappingTreeWidget.itemActivated.connect(self._mappingSelectedSlot)
        self.uiMappingTreeWidget.itemSelectionChanged.connect(self._mappingSelectionChangedSlot)

        # enable sorting
        self.uiMappingTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.uiMappingTreeWidget.setSortingEnabled(True)

    def _mappingSelectedSlot(self, item, column):
        """
        Loads a selected mapping from the tree widget.

        :param item: selected QTreeWidgetItem instance
        :param column: ignored
        """

        ethernet_port = item.text(0)
        destination = item.text(1)

        mapping = re.compile(r"""^([0-9]*):([0-9]*):([0-9]*)$""")
        match_atm_mapping = mapping.search(destination)
        (atm_port, atm_vpi, atm_vci) = match_atm_mapping.group(1, 2, 3)

        # source
        self.uiEthernetPortSpinBox.setValue(int(ethernet_port))

        # destination
        self.uiATMPortSpinBox.setValue(int(atm_port))
        self.uiATMVPISpinBox.setValue(int(atm_vpi))
        self.uiATMVCISpinBox.setValue(int(atm_vci))

    def _mappingSelectionChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiMappingTreeWidget.currentItem()
        if item is not None:
            self.uiDeletePushButton.setEnabled(True)
        else:
            self.uiDeletePushButton.setEnabled(False)

    def _addMappingSlot(self):
        """
        Adds a new mapping.
        """

        ethernet_port = self.uiEthernetPortSpinBox.value()
        atm_port = self.uiATMPortSpinBox.value()
        atm_vpi = self.uiATMVPISpinBox.value()
        atm_vci = self.uiATMVCISpinBox.value()

        if ethernet_port == atm_port:
            QtGui.QMessageBox.critical(self, self._node.name(), "Same source and destination ports")
            return

        destination = "{port}:{vpi}:{vci}".format(port=atm_port,
                                                  vpi=atm_vpi,
                                                  vci=atm_vci)

        if destination in self._mapping:
            QtGui.QMessageBox.critical(self, self._node.name(), "Mapping already defined")
            return

        item = QtGui.QTreeWidgetItem(self.uiMappingTreeWidget)
        item.setText(0, str(ethernet_port))
        item.setText(1, destination)
        self.uiMappingTreeWidget.addTopLevelItem(item)
        self.uiEthernetPortSpinBox.setValue(ethernet_port + 1)
        self.uiATMPortSpinBox.setValue(atm_port + 1)
        self._mapping[ethernet_port] = destination

    def _deleteMappingSlot(self):
        """
        Deletes a mapping.
        """

        item = self.uiMappingTreeWidget.currentItem()
        if item:
            ethernet_port = int(item.text(0))
            atm_port = int(item.text(1).split(":")[0])

            # check that a link isn't connected to these ports
            # before we delete that mapping.
            node_ports = self._node.ports()
            for node_port in node_ports:
                if (node_port.portNumber() == ethernet_port or node_port.portNumber() == atm_port) and not node_port.isFree():
                    QtGui.QMessageBox.critical(self, self._node.name(), "A link is connected to port {}, please remove it first".format(node_port.name()))
                    return

            del self.mapping[ethernet_port]
            self.uiMappingTreeWidget.takeTopLevelItem(self.uiMappingTreeWidget.indexOfTopLevelItem(item))

    def loadSettings(self, settings, node, group=False):
        """
        Loads the ATM bridge settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
        else:
            self.uiNameLineEdit.setEnabled(False)

        self.uiMappingTreeWidget.clear()
        self._mapping = {}
        self._node = node

        for ethernet_port, destination in settings["mappings"].items():
            item = QtGui.QTreeWidgetItem(self.uiMappingTreeWidget)
            item.setText(0, ethernet_port)
            item.setText(1, destination)
            self.uiMappingTreeWidget.addTopLevelItem(item)
            self._mapping[ethernet_port] = destination

        self.uiMappingTreeWidget.resizeColumnToContents(0)
        self.uiMappingTreeWidget.resizeColumnToContents(1)

    def saveSettings(self, settings, node, group=False):
        """
        Saves the ATM bridge settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            # set the device name
            name = self.uiNameLineEdit.text()
            if not name:
                QtGui.QMessageBox.critical(self, "Name", "ATM bridge name cannot be empty!")
            else:
                settings["name"] = name
        else:
            del settings["name"]

        settings["mappings"] = self._mapping.copy()
