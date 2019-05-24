# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 GNS3 Technologies Inc.
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
Configuration page for TraceNG nodes
"""

import ipaddress

from gns3.qt import QtWidgets
from gns3.local_server import LocalServer
from gns3.node import Node
from gns3.controller import Controller

from ..ui.traceng_node_configuration_page_ui import Ui_TraceNGNodeConfigPageWidget
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.dialogs.node_properties_dialog import ConfigurationError


class TraceNGNodeConfigurationPage(QtWidgets.QWidget, Ui_TraceNGNodeConfigPageWidget):

    """
    QWidget configuration page for TraceNG nodes.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        self.uiSymbolToolButton.clicked.connect(self._symbolBrowserSlot)
        self._default_configs_dir = LocalServer.instance().localServerSettings()["configs_path"]
        if Controller.instance().isRemote():
            self.uiScriptFileToolButton.hide()

        # add the categories
        for name, category in Node.defaultCategories().items():
            self.uiCategoryComboBox.addItem(name, category)

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
        Loads the TraceNG node settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
            self.uiIPAddressLineEdit.setText(settings["ip_address"])
            self.uiDefaultDestinationLineEdit.setText(settings["default_destination"])
        else:
            self.uiIPAddressLabel.hide()
            self.uiIPAddressLineEdit.hide()
            self.uiDefaultDestinationLabel.hide()
            self.uiDefaultDestinationLineEdit.hide()
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()

        if not node:
            # these are template settings

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

    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the TraceNG node settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        # these settings cannot be shared by nodes and updated
        # in the node properties dialog.
        if not group:
            # set the node name
            name = self.uiNameLineEdit.text()
            if not name:
                QtWidgets.QMessageBox.critical(self, "Name", "TraceNG node name cannot be empty!")
            else:
                settings["name"] = name

            ip_address = self.uiIPAddressLineEdit.text().strip()
            if ip_address:
                try:
                    ipaddress.IPv4Address(ip_address)
                    settings["ip_address"] = ip_address
                except ipaddress.AddressValueError:
                    QtWidgets.QMessageBox.critical(self, "IP address", "Invalid IP address format")
                    if node:
                        raise ConfigurationError()

            settings["default_destination"] = self.uiDefaultDestinationLineEdit.text().strip()

        if not node:
            default_name_format = self.uiDefaultNameFormatLineEdit.text().strip()
            if '{0}' not in default_name_format and '{id}' not in default_name_format:
                QtWidgets.QMessageBox.critical(self, "Default name format", "The default name format must contain at least {0} or {id}")
            else:
                settings["default_name_format"] = default_name_format

            symbol_path = self.uiSymbolLineEdit.text()
            settings["symbol"] = symbol_path
            settings["category"] = self.uiCategoryComboBox.itemData(self.uiCategoryComboBox.currentIndex())
        return settings
