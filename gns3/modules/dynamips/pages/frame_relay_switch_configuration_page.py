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
Configuration page for Dynamips Frame Relay switches.
"""

from gns3.qt import QtCore, QtGui
from ..ui.frame_relay_switch_configuration_page_ui import Ui_frameRelaySwitchConfigPageWidget


class FrameRelaySwitchConfigurationPage(QtGui.QWidget, Ui_frameRelaySwitchConfigPageWidget):

    """
    QWidget configuration page for Frame Relay switches.
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

        (source_port, source_dlci) = item.text(0).split(':')
        (destination_port, destination_dlci) = item.text(1).split(':')
        self.uiSourcePortSpinBox.setValue(int(source_port))
        self.uiSourceDLCISpinBox.setValue(int(source_dlci))
        self.uiDestinationPortSpinBox.setValue(int(destination_port))
        self.uiDestinationDLCISpinBox.setValue(int(destination_dlci))

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

        source_port = self.uiSourcePortSpinBox.value()
        source_dlci = self.uiSourceDLCISpinBox.value()
        destination_port = self.uiDestinationPortSpinBox.value()
        destination_dlci = self.uiDestinationDLCISpinBox.value()

        if source_port == destination_port:
            QtGui.QMessageBox.critical(self, self._node.name(), "Same source and destination ports")
            return

        source = "{port}:{dlci}".format(port=source_port, dlci=source_dlci)
        destination = "{port}:{dlci}".format(port=destination_port, dlci=destination_dlci)

        if source in self._mapping or destination in self._mapping:
            QtGui.QMessageBox.critical(self, self._node.name(), "Mapping already defined")
            return

        item = QtGui.QTreeWidgetItem(self.uiMappingTreeWidget)
        item.setText(0, source)
        item.setText(1, destination)
        self.uiMappingTreeWidget.addTopLevelItem(item)
        self.uiSourcePortSpinBox.setValue(source_port + 1)
        self.uiSourceDLCISpinBox.setValue(source_dlci + 1)
        self.uiDestinationPortSpinBox.setValue(destination_port + 1)
        self.uiDestinationDLCISpinBox.setValue(destination_dlci + 1)
        self._mapping[source] = destination

    def _deleteMappingSlot(self):
        """
        Deletes a mapping.
        """

        item = self.uiMappingTreeWidget.currentItem()
        if item:
            # connected_ports = self.node.getConnectedInterfaceList()
            source = item.text(0)
            source_port = int(source.split(':')[0])
            destination = item.text(1)
            destination_port = int(destination.split(':')[0])

            # check that a link isn't connected to these ports
            # before we delete that mapping
            node_ports = self._node.ports()
            for node_port in node_ports:
                if (node_port.portNumber() == source_port or node_port.portNumber() == destination_port) and not node_port.isFree():
                    QtGui.QMessageBox.critical(self, self._node.name(), "A link is connected to port {}, please remove it first".format(node_port.name()))
                    return

            del self._mapping[source]
            self.uiMappingTreeWidget.takeTopLevelItem(self.uiMappingTreeWidget.indexOfTopLevelItem(item))

    def loadSettings(self, settings, node, group=False):
        """
        Loads the Frame-Relay switch settings.

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

        for source, destination in settings["mappings"].items():
            item = QtGui.QTreeWidgetItem(self.uiMappingTreeWidget)
            item.setText(0, source)
            item.setText(1, destination)
            self.uiMappingTreeWidget.addTopLevelItem(item)
            self._mapping[source] = destination

        self.uiMappingTreeWidget.resizeColumnToContents(0)
        self.uiMappingTreeWidget.resizeColumnToContents(1)

    def saveSettings(self, settings, node, group=False):
        """
        Saves the Frame-Relay switch settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            # set the device name
            name = self.uiNameLineEdit.text()
            if not name:
                QtGui.QMessageBox.critical(self, "Name", "Frame relay switch name cannot be empty!")
            else:
                settings["name"] = name
        else:
            del settings["name"]

        settings["mappings"] = self._mapping.copy()
