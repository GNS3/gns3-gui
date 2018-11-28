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
Configuration page for VPCS nodes
"""

import os
from gns3.qt import QtWidgets
from gns3.local_server import LocalServer
from gns3.node import Node
from gns3.controller import Controller

from ..ui.vpcs_node_configuration_page_ui import Ui_VPCSNodeConfigPageWidget
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog


class VPCSNodeConfigurationPage(QtWidgets.QWidget, Ui_VPCSNodeConfigPageWidget):
    """
    QWidget configuration page for VPCS nodes.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        self.uiSymbolToolButton.clicked.connect(self._symbolBrowserSlot)
        self.uiScriptFileToolButton.clicked.connect(self._scriptFileBrowserSlot)
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

    def _scriptFileBrowserSlot(self):
        """
        Slot to open a file browser and select a base script file for VPCS
        """

        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a script file", self._default_configs_dir)
        if not path:
            return

        self._default_configs_dir = os.path.dirname(path)
        if not os.access(path, os.R_OK):
            QtWidgets.QMessageBox.critical(self, "Script file", "{} cannot be read".format(os.path.basename(path)))
            return

        self.uiScriptFileEdit.setText(os.path.normpath(path))

    def loadSettings(self, settings, node=None, group=False):
        """
        Loads the VPCS node settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
        else:
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

            self.uiScriptFileEdit.setText(settings["base_script_file"])
        else:
            self.uiDefaultNameFormatLabel.hide()
            self.uiDefaultNameFormatLineEdit.hide()
            self.uiSymbolLabel.hide()
            self.uiSymbolLineEdit.hide()
            self.uiSymbolToolButton.hide()
            self.uiCategoryComboBox.hide()
            self.uiCategoryLabel.hide()
            self.uiCategoryComboBox.hide()
            self.uiScriptFileLabel.hide()
            self.uiScriptFileEdit.hide()
            self.uiScriptFileToolButton.hide()

        # load the console type
        index = self.uiConsoleTypeComboBox.findText(settings["console_type"])
        if index != -1:
            self.uiConsoleTypeComboBox.setCurrentIndex(index)

        self.uiConsoleAutoStartCheckBox.setChecked(settings["console_auto_start"])

    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the VPCS nodesettings.

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
                QtWidgets.QMessageBox.critical(self, "Name", "VPCS node name cannot be empty!")
            else:
                settings["name"] = name

        if not node:
            default_name_format = self.uiDefaultNameFormatLineEdit.text().strip()
            if '{0}' not in default_name_format and '{id}' not in default_name_format:
                QtWidgets.QMessageBox.critical(self, "Default name format", "The default name format must contain at least {0} or {id}")
            else:
                settings["default_name_format"] = default_name_format

            symbol_path = self.uiSymbolLineEdit.text()
            settings["symbol"] = symbol_path

            settings["category"] = self.uiCategoryComboBox.itemData(self.uiCategoryComboBox.currentIndex())
            base_script_file = self.uiScriptFileEdit.text().strip()

            if not base_script_file:
                settings["base_script_file"] = ""
            elif base_script_file != settings["base_script_file"]:
                if self._configFileValid(base_script_file):
                    settings["base_script_file"] = base_script_file
                else:
                    QtWidgets.QMessageBox.critical(self, "Base script config file", "Cannot read the base script config file")

        # save console type
        settings["console_type"] = self.uiConsoleTypeComboBox.currentText().lower()
        settings["console_auto_start"] = self.uiConsoleAutoStartCheckBox.isChecked()
        return settings

    def _configFileValid(self, path):
        """
        Return true if it's a valid configuration file
        """
        if not os.path.isabs(path):
            path = os.path.join(LocalServer.instance().localServerSettings()["configs_path"], path)
        return os.access(path, os.R_OK)
