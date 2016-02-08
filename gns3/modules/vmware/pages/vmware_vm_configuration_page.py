# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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
Configuration page for VMware VMs.
"""

from gns3.qt import QtGui, QtWidgets
from gns3.dialogs.node_properties_dialog import ConfigurationError
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.node import Node

from ..ui.vmware_vm_configuration_page_ui import Ui_VMwareVMConfigPageWidget


class VMwareVMConfigurationPage(QtWidgets.QWidget, Ui_VMwareVMConfigPageWidget):

    """
    QWidget configuration page for VMware VMs.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        self.uiSymbolToolButton.clicked.connect(self._symbolBrowserSlot)
        self.uiAdapterTypesComboBox.clear()
        self.uiAdapterTypesComboBox.addItems(["default",
                                              "e1000",
                                              "e1000e",
                                              "flexible",
                                              "vlance",
                                              "vmxnet",
                                              "vmxnet2",
                                              "vmxnet3"])

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
        Loads the VMware VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        if not group:

            # set the device name
            if "name" in settings:
                self.uiNameLineEdit.setText(settings["name"])
            else:
                self.uiNameLabel.hide()
                self.uiNameLineEdit.hide()

            if "console" in settings:
                self.uiConsolePortSpinBox.setValue(settings["console"])
            else:
                self.uiConsolePortLabel.hide()
                self.uiConsolePortSpinBox.hide()

            if "linked_base" in settings:
                self.uiBaseVMCheckBox.setChecked(settings["linked_base"])
            else:
                self.uiBaseVMCheckBox.hide()

        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiConsolePortLabel.hide()
            self.uiConsolePortSpinBox.hide()
            # self.uiVMListLabel.hide()
            # self.uiVMListComboBox.hide()

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

            self.uiPortNameFormatLineEdit.setText(settings["port_name_format"])
            self.uiPortSegmentSizeSpinBox.setValue(settings["port_segment_size"])
            self.uiFirstPortNameLineEdit.setText(settings["first_port_name"])
        else:
            self.uiDefaultNameFormatLabel.hide()
            self.uiDefaultNameFormatLineEdit.hide()
            self.uiSymbolLabel.hide()
            self.uiSymbolLineEdit.hide()
            self.uiSymbolToolButton.hide()
            self.uiCategoryComboBox.hide()
            self.uiCategoryLabel.hide()
            self.uiCategoryComboBox.hide()
            self.uiPortNameFormatLabel.hide()
            self.uiPortNameFormatLineEdit.hide()
            self.uiPortSegmentSizeLabel.hide()
            self.uiPortSegmentSizeSpinBox.hide()
            self.uiFirstPortNameLabel.hide()
            self.uiFirstPortNameLineEdit.hide()

        self.uiAdaptersSpinBox.setValue(settings["adapters"])
        index = self.uiAdapterTypesComboBox.findText(settings["adapter_type"])
        if index != -1:
            self.uiAdapterTypesComboBox.setCurrentIndex(index)
        self.uiUseUbridgeCheckBox.setChecked(settings["use_ubridge"])
        self.uiUseAnyAdapterCheckBox.setChecked(settings["use_any_adapter"])
        self.uiHeadlessModeCheckBox.setChecked(settings["headless"])
        self.uiACPIShutdownCheckBox.setChecked(settings["acpi_shutdown"])
        self.uiEnableConsoleCheckBox.setChecked(settings["enable_remote_console"])

    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the VMware VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        # these settings cannot be shared by nodes and updated
        # in the node properties dialog.
        if not group:

            if "name" in settings:
                name = self.uiNameLineEdit.text()
                if not name:
                    QtWidgets.QMessageBox.critical(self, "Name", "VMware name cannot be empty!")
                else:
                    settings["name"] = name

            if "console" in settings:
                settings["console"] = self.uiConsolePortSpinBox.value()

            if "linked_base" in settings:
                settings["linked_base"] = self.uiBaseVMCheckBox.isChecked()

            settings["enable_remote_console"] = self.uiEnableConsoleCheckBox.isChecked()

        else:
            del settings["name"]
            del settings["console"]
            del settings["enable_remote_console"]

        if not node:
            # these are template settings

            # save the default name format
            default_name_format = self.uiDefaultNameFormatLineEdit.text().strip()
            if '{0}' not in default_name_format and '{id}' not in default_name_format:
                QtWidgets.QMessageBox.critical(self, "Default name format", "The default name format must contain at least {0} or {id}")
            else:
                settings["default_name_format"] = default_name_format

            symbol_path = self.uiSymbolLineEdit.text()
            pixmap = QtGui.QPixmap(symbol_path)
            if pixmap.isNull():
                QtWidgets.QMessageBox.critical(self, "Symbol", "Invalid file or format not supported")
            else:
                settings["symbol"] = symbol_path

            settings["category"] = self.uiCategoryComboBox.itemData(self.uiCategoryComboBox.currentIndex())
            port_name_format = self.uiPortNameFormatLineEdit.text()
            if '{0}' not in port_name_format and '{port0}' not in port_name_format and '{port1}' not in port_name_format:
                QtWidgets.QMessageBox.critical(self, "Port name format", "The format must contain at least {0}, {port0} or {port1}")
            else:
                settings["port_name_format"] = self.uiPortNameFormatLineEdit.text()

            port_segment_size = self.uiPortSegmentSizeSpinBox.value()
            if port_segment_size and '{1}' not in port_name_format and '{segment0}' not in port_name_format and '{segment1}' not in port_name_format:
                QtWidgets.QMessageBox.critical(self, "Port name format", "If the segment size is not 0, the format must contain {1}, {segment0} or {segment1}")
            else:
                settings["port_segment_size"] = port_segment_size

            settings["first_port_name"] = self.uiFirstPortNameLineEdit.text().strip()

        settings["adapter_type"] = self.uiAdapterTypesComboBox.currentText()
        use_ubridge = self.uiUseUbridgeCheckBox.isChecked()
        if node and settings["use_ubridge"] != use_ubridge:
            for node_port in node.ports():
                if not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, node.name(), "Changing the use uBridge setting while links are connected isn't supported! Please delete all the links first.")
                    raise ConfigurationError()
        settings["use_ubridge"] = use_ubridge
        settings["use_any_adapter"] = self.uiUseAnyAdapterCheckBox.isChecked()
        settings["headless"] = self.uiHeadlessModeCheckBox.isChecked()
        settings["acpi_shutdown"] = self.uiACPIShutdownCheckBox.isChecked()

        adapters = self.uiAdaptersSpinBox.value()
        if node and settings["adapters"] != adapters:
            # check if the adapters settings have changed
            for node_port in node.ports():
                if not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
                    raise ConfigurationError()
        settings["adapters"] = adapters
