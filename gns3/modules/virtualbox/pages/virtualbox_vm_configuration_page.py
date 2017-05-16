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
Configuration page for VirtualBox VMs.
"""

from gns3.qt import QtWidgets
from gns3.dialogs.node_properties_dialog import ConfigurationError
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.node import Node

from ..ui.virtualbox_vm_configuration_page_ui import Ui_virtualBoxVMConfigPageWidget


class VirtualBoxVMConfigurationPage(QtWidgets.QWidget, Ui_virtualBoxVMConfigPageWidget):

    """
    QWidget configuration page for VirtualBox VMs.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        self.uiSymbolToolButton.clicked.connect(self._symbolBrowserSlot)
        self.uiAdapterTypesComboBox.clear()
        self.uiAdapterTypesComboBox.addItems(["PCnet-PCI II (Am79C970A)",
                                              "PCNet-FAST III (Am79C973)",
                                              "Intel PRO/1000 MT Desktop (82540EM)",
                                              "Intel PRO/1000 T Server (82543GC)",
                                              "Intel PRO/1000 MT Server (82545EM)",
                                              "Paravirtualized Network (virtio-net)"])

        # TODO: finish VM name change
        self.uiVMListLabel.hide()
        self.uiVMListComboBox.hide()

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
        Loads the VirtualBox VM settings.

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

            if "linked_base" in settings:
                self.uiBaseVMCheckBox.setChecked(settings["linked_base"])
            else:
                self.uiBaseVMCheckBox.hide()

        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiVMListLabel.hide()
            self.uiVMListComboBox.hide()

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
        self.uiUseAnyAdapterCheckBox.setChecked(settings["use_any_adapter"])
        self.uiVMRamSpinBox.setValue(settings["ram"])
        self.uiHeadlessModeCheckBox.setChecked(settings["headless"])
        self.uiACPIShutdownCheckBox.setChecked(settings["acpi_shutdown"])

    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the VirtualBox VM settings.

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
                    QtWidgets.QMessageBox.critical(self, "Name", "VirtualBox name cannot be empty!")
                else:
                    settings["name"] = name

            if "linked_base" in settings:
                settings["linked_base"] = self.uiBaseVMCheckBox.isChecked()

        if not node:
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

        settings["ram"] = self.uiVMRamSpinBox.value()
        settings["adapter_type"] = self.uiAdapterTypesComboBox.currentText()
        settings["headless"] = self.uiHeadlessModeCheckBox.isChecked()
        settings["acpi_shutdown"] = self.uiACPIShutdownCheckBox.isChecked()
        settings["use_any_adapter"] = self.uiUseAnyAdapterCheckBox.isChecked()

        adapters = self.uiAdaptersSpinBox.value()
        if node:
            if node.settings()["adapters"] != adapters:
                # check if the adapters settings have changed
                node_ports = node.ports()
                for node_port in node_ports:
                    if not node_port.isFree():
                        QtWidgets.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
                        raise ConfigurationError()
        settings["adapters"] = adapters
        return settings
