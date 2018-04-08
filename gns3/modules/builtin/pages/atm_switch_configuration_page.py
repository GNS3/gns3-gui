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
Configuration page for Dynamips ATM switches.
"""

import re
from gns3.qt import QtCore, QtWidgets
from ..ui.atm_switch_configuration_page_ui import Ui_atmSwitchConfigPageWidget


class ATMSwitchConfigurationPage(QtWidgets.QWidget, Ui_atmSwitchConfigPageWidget):

    """
    QWidget configuration page for ATM switches.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self._mapping = {}
        self._node = None

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

        source = item.text(0)
        destination = item.text(1)
        mapping = re.compile(r"""^([0-9]*):([0-9]*):([0-9]*)$""")
        match_source_mapping = mapping.search(source)
        match_destination_mapping = mapping.search(destination)

        if match_source_mapping and match_destination_mapping:
            self.uiVPICheckBox.setCheckState(QtCore.Qt.Unchecked)
            (source_port, source_vpi, source_vci) = match_source_mapping.group(1, 2, 3)
            (destination_port, destination_vpi, destination_vci) = match_destination_mapping.group(1, 2, 3)
        else:
            self.uiVPICheckBox.setCheckState(QtCore.Qt.Checked)
            (source_port, source_vpi) = source.split(':')
            (destination_port, destination_vpi) = destination.split(':')
            source_vci = destination_vci = 0

        # source
        self.uiSourcePortSpinBox.setValue(int(source_port))
        self.uiSourceVPISpinBox.setValue(int(source_vpi))
        self.uiSourceVCISpinBox.setValue(int(source_vci))

        # destination
        self.uiDestinationPortSpinBox.setValue(int(destination_port))
        self.uiDestinationVPISpinBox.setValue(int(destination_vpi))
        self.uiDestinationVCISpinBox.setValue(int(destination_vci))

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
        source_vpi = self.uiSourceVPISpinBox.value()
        source_vci = self.uiSourceVCISpinBox.value()
        destination_port = self.uiDestinationPortSpinBox.value()
        destination_vpi = self.uiDestinationVPISpinBox.value()
        destination_vci = self.uiDestinationVCISpinBox.value()

        if self.uiVPICheckBox.checkState() == QtCore.Qt.Unchecked:
            source = "{port}:{vpi}:{vci}".format(port=source_port,
                                                 vpi=source_vpi,
                                                 vci=source_vci)

            destination = "{port}:{vpi}:{vci}".format(port=destination_port,
                                                      vpi=destination_vpi,
                                                      vci=destination_vci)
        else:
            source = "{port}:{vpi}".format(port=source_port, vpi=source_vpi)
            destination = "{port}:{vpi}".format(port=destination_port, vpi=destination_vpi)

        if source in self._mapping or destination in self._mapping:
            QtWidgets.QMessageBox.critical(self, self._node.name(), "Mapping already defined")
            return

        item = QtWidgets.QTreeWidgetItem(self.uiMappingTreeWidget)
        item.setText(0, source)
        item.setText(1, destination)
        self.uiMappingTreeWidget.addTopLevelItem(item)
        self.uiSourcePortSpinBox.setValue(source_port + 1)
        self.uiDestinationPortSpinBox.setValue(destination_port + 1)
        self._mapping[source] = destination

    def _deleteMappingSlot(self):
        """
        Deletes a mapping.
        """

        item = self.uiMappingTreeWidget.currentItem()
        if item:

            source = item.text(0)
            source_port = int(source.split(':')[0])
            destination = item.text(1)
            destination_port = int(destination.split(':')[0])

            # check that a link isn't connected to these ports
            # before we delete that mapping
            node_ports = self._node.ports()
            for node_port in node_ports:
                if (node_port.portNumber() == source_port or node_port.portNumber() == destination_port) and not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to port {}, please remove it first".format(node_port.name()))
                    return

            del self._mapping[source]
            self.uiMappingTreeWidget.takeTopLevelItem(self.uiMappingTreeWidget.indexOfTopLevelItem(item))

    def loadSettings(self, settings, node, group=False):
        """
        Loads the ATM switch settings.

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
            item = QtWidgets.QTreeWidgetItem(self.uiMappingTreeWidget)
            item.setText(0, source)
            item.setText(1, destination)
            self.uiMappingTreeWidget.addTopLevelItem(item)
            self._mapping[source] = destination

        self.uiMappingTreeWidget.resizeColumnToContents(0)
        self.uiMappingTreeWidget.resizeColumnToContents(1)

    def saveSettings(self, settings, node, group=False):
        """
        Saves the ATM switch settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            # set the device name
            name = self.uiNameLineEdit.text()
            if not name:
                QtWidgets.QMessageBox.critical(self, "Name", "ATM switch name cannot be empty!")
            else:
                settings["name"] = name
        settings["mappings"] = self._mapping.copy()
        return settings
