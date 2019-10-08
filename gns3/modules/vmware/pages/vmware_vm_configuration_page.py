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

from gns3.qt import QtWidgets
from gns3.dialogs.node_properties_dialog import ConfigurationError
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.dialogs.custom_adapters_configuration_dialog import CustomAdaptersConfigurationDialog
from gns3.ports.port_name_factory import StandardPortNameFactory
from gns3.node import Node

from ..ui.vmware_vm_configuration_page_ui import Ui_VMwareVMConfigPageWidget


class VMwareVMConfigurationPage(QtWidgets.QWidget, Ui_VMwareVMConfigPageWidget):

    """
    QWidget configuration page for VMware VMs.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self._settings = None
        self._custom_adapters = []

        self.uiSymbolToolButton.clicked.connect(self._symbolBrowserSlot)
        self.uiCustomAdaptersConfigurationPushButton.clicked.connect(self._customAdaptersConfigurationSlot)
        self.uiAdapterTypesComboBox.clear()


        self._adapter_types = ["default",
                               "e1000",
                               "e1000e",
                               "flexible",
                               "vlance",
                               "vmxnet",
                               "vmxnet2",
                               "vmxnet3"]

        self.uiAdapterTypesComboBox.addItems(self._adapter_types)

        # add the categories
        for name, category in Node.defaultCategories().items():
            self.uiCategoryComboBox.addItem(name, category)

        # add the on close options
        for name, option_name in Node.onCloseOptions().items():
            self.uiOnCloseComboBox.addItem(name, option_name)

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

    def _customAdaptersConfigurationSlot(self):
        """
        Slot to open the custom adapters configuration dialog
        """

        if self._node:
            first_port_name = self._settings["first_port_name"]
            port_segment_size = self._settings["port_segment_size"]
            port_name_format = self._settings["port_name_format"]
            adapters = self._settings["adapters"]
            default_adapter = self._settings["adapter_type"]
        else:
            first_port_name = self.uiFirstPortNameLineEdit.text().strip()
            port_name_format = self.uiPortNameFormatLineEdit.text()
            port_segment_size = self.uiPortSegmentSizeSpinBox.value()
            adapters = self.uiAdaptersSpinBox.value()
            default_adapter = self.uiAdapterTypesComboBox.currentText()

        try:
            ports = StandardPortNameFactory(adapters, first_port_name, port_name_format, port_segment_size)
        except (IndexError, ValueError, KeyError):
            QtWidgets.QMessageBox.critical(self, "Invalid format", "Invalid port name format")
            return

        dialog = CustomAdaptersConfigurationDialog(ports, self._custom_adapters, default_adapter, self._adapter_types, parent=self)
        dialog.show()
        dialog.exec_()

    def loadSettings(self, settings, node=None, group=False):
        """
        Loads the VMware VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        if node:
            self._node = node
            self._settings = settings
        else:
            self._node = None

        if not group:

            # set the device name
            if "name" in settings:
                self.uiNameLineEdit.setText(settings["name"])
            else:
                self.uiNameLabel.hide()
                self.uiNameLineEdit.hide()

            if "linked_clone" in settings:
                self.uiBaseVMCheckBox.setChecked(settings["linked_clone"])
            else:
                self.uiBaseVMCheckBox.hide()

        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            # self.uiVMListLabel.hide()
            # self.uiVMListComboBox.hide()

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

        # load the console type
        index = self.uiConsoleTypeComboBox.findText(settings["console_type"])
        if index != -1:
            self.uiConsoleTypeComboBox.setCurrentIndex(index)

        self.uiConsoleAutoStartCheckBox.setChecked(settings["console_auto_start"])
        self.uiAdaptersSpinBox.setValue(settings["adapters"])
        self._custom_adapters = settings["custom_adapters"].copy()
        index = self.uiAdapterTypesComboBox.findText(settings["adapter_type"])
        if index != -1:
            self.uiAdapterTypesComboBox.setCurrentIndex(index)
        self.uiUseAnyAdapterCheckBox.setChecked(settings["use_any_adapter"])
        self.uiHeadlessModeCheckBox.setChecked(settings["headless"])

        # load the on close option
        index = self.uiOnCloseComboBox.findData(settings["on_close"])
        if index != -1:
            self.uiOnCloseComboBox.setCurrentIndex(index)

        self.uiUsageTextEdit.setPlainText(settings["usage"])

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

            if "linked_clone" in settings:
                settings["linked_clone"] = self.uiBaseVMCheckBox.isChecked()

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
            port_segment_size = self.uiPortSegmentSizeSpinBox.value()
            first_port_name = self.uiFirstPortNameLineEdit.text().strip()

            try:
                StandardPortNameFactory(self.uiAdaptersSpinBox.value(), first_port_name, port_name_format, port_segment_size)
            except (IndexError, ValueError, KeyError):
                QtWidgets.QMessageBox.critical(self, "Invalid format", "Invalid port name format")
                raise ConfigurationError()

            settings["port_name_format"] = self.uiPortNameFormatLineEdit.text()
            settings["port_segment_size"] = port_segment_size
            settings["first_port_name"] = first_port_name

        settings["adapter_type"] = self.uiAdapterTypesComboBox.currentText()
        settings["use_any_adapter"] = self.uiUseAnyAdapterCheckBox.isChecked()
        settings["headless"] = self.uiHeadlessModeCheckBox.isChecked()
        settings["on_close"] = self.uiOnCloseComboBox.itemData(self.uiOnCloseComboBox.currentIndex())

        # save console type
        settings["console_type"] = self.uiConsoleTypeComboBox.currentText().lower()
        settings["console_auto_start"] = self.uiConsoleAutoStartCheckBox.isChecked()

        adapters = self.uiAdaptersSpinBox.value()
        if node and node.settings()["adapters"] != adapters:
            # check if the adapters settings have changed
            for node_port in node.ports():
                if not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
                    raise ConfigurationError()
        settings["adapters"] = adapters
        settings["custom_adapters"] = self._custom_adapters.copy()
        settings["usage"] = self.uiUsageTextEdit.toPlainText()
        return settings
