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
Configuration page for Ethernet hubs.
"""

from gns3.qt import QtWidgets
from gns3.dialogs.node_properties_dialog import ConfigurationError
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.node import Node

from ..ui.ethernet_hub_configuration_page_ui import Ui_ethernetHubConfigPageWidget


class EthernetHubConfigurationPage(QtWidgets.QWidget, Ui_ethernetHubConfigPageWidget):

    """
    QWidget configuration page for Ethernet hubs.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        # add the categories
        for name, category in Node.defaultCategories().items():
            self.uiCategoryComboBox.addItem(name, category)

        self.uiSymbolToolButton.clicked.connect(self._symbolBrowserSlot)

    def _symbolBrowserSlot(self):
        """
        Slot to open the symbol browser and select a new symbol.
        """

        symbol_path = self.uiSymbolLineEdit.text()
        dialog = SymbolSelectionDialog(self, symbol=symbol_path)
        dialog.show()
        if dialog.exec_():
            new_symbol_path = dialog.getSymbol()
            self.uiSymbolLineEdit.setText(new_symbol_path)
            self.uiSymbolLineEdit.setToolTip('<img src="{}"/>'.format(new_symbol_path))

    def loadSettings(self, settings, node=None, group=False):
        """
        Loads the Ethernet hub settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
        else:
            self.uiNameLineEdit.hide()
            self.uiNameLabel.hide()

        if not node:
            # these are template settings

            # rename the label from "Name" to "Template name"
            self.uiNameLabel.setText("Template name:")

            # load the default name format
            self.uiDefaultNameFormatLineEdit.setText(settings["default_name_format"])

            # load the symbol
            self.uiSymbolLineEdit.setText(settings["symbol"])
            self.uiSymbolLineEdit.setToolTip('<img src="{}"/>'.format(settings["symbol"]))

            # load the category
            index = self.uiCategoryComboBox.findData(settings["category"])
            if index != -1:
                self.uiCategoryComboBox.setCurrentIndex(index)
        else:
            self.uiDefaultNameFormatLabel.hide()
            self.uiDefaultNameFormatLineEdit.hide()
            self.uiSymbolLabel.hide()
            self.uiSymbolLineEdit.hide()
            self.uiSymbolToolButton.hide()
            self.uiCategoryComboBox.hide()
            self.uiCategoryLabel.hide()
            self.uiCategoryComboBox.hide()

        nb_ports = len(settings["ports_mapping"])
        self.uiPortsSpinBox.setValue(nb_ports)

    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the Ethernet hub settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            # set the device name
            name = self.uiNameLineEdit.text()
            if not name:
                QtWidgets.QMessageBox.critical(self, "Name", "Ethernet hub name cannot be empty!")
            else:
                settings["name"] = name

        nb_ports = self.uiPortsSpinBox.value()

        if node:
            # check that a link isn't connected to a port before we delete it
            ports = node.ports()
            for port in ports:
                if not port.isFree() and port.portNumber() > nb_ports:
                    self.loadSettings(settings, node)
                    QtWidgets.QMessageBox.critical(self, node.name(), "A link is connected to port {}, please remove it first".format(port.name()))
                    raise ConfigurationError()

        else:
            # these are template settings

            # save the default name format
            default_name_format = self.uiDefaultNameFormatLineEdit.text().strip()
            if '{0}' not in default_name_format and '{id}' not in default_name_format:
                QtWidgets.QMessageBox.critical(self, "Default name format", "The default name format must contain at least {0} or {id}")
            else:
                settings["default_name_format"] = default_name_format

            symbol_path = self.uiSymbolLineEdit.text()
            settings["symbol"] = symbol_path

            settings["category"] = self.uiCategoryComboBox.itemData(self.uiCategoryComboBox.currentIndex())

        settings["ports_mapping"] = []
        for port_number in range(0, nb_ports):
            settings["ports_mapping"].append({"port_number": int(port_number),
                                              "name": "Ethernet{}".format(port_number)})
        return settings
