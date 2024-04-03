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
Configuration page for Docker images.
"""

from gns3.qt import QtWidgets
from gns3.node import Node
from gns3.dialogs.custom_adapters_configuration_dialog import CustomAdaptersConfigurationDialog

from ..ui.docker_vm_configuration_page_ui import Ui_dockerVMConfigPageWidget
from ....dialogs.file_editor_dialog import FileEditorDialog
from ....dialogs.node_properties_dialog import ConfigurationError
from ....dialogs.symbol_selection_dialog import SymbolSelectionDialog


class DockerVMConfigurationPage(QtWidgets.QWidget, Ui_dockerVMConfigPageWidget):
    """
    QWidget configuration page for Docker images
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self._settings = None
        self._custom_adapters = []

        self.uiSymbolToolButton.clicked.connect(self._symbolBrowserSlot)
        self.uiNetworkConfigEditButton.released.connect(self._networkConfigEditSlot)
        self.uiCustomAdaptersConfigurationPushButton.clicked.connect(self._customAdaptersConfigurationSlot)

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

    def _customAdaptersConfigurationSlot(self):
        """
        Slot to open the custom adapters configuration dialog
        """

        if self._node:
            adapters = self._settings["adapters"]
        else:
            adapters = self.uiAdapterSpinBox.value()

        ports = []
        for adapter_number in range(0, adapters):
            port_name = "eth{}".format(adapter_number)
            ports.append(port_name)

        dialog = CustomAdaptersConfigurationDialog(ports, self._custom_adapters, parent=self)
        dialog.show()
        dialog.exec_()

    def loadSettings(self, settings, node=None, group=False):
        """
        Loads the Docker container settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of images
        """

        if node:
            self._node = node
            self._settings = settings
        else:
            self._node = None

        self.uiCMDLineEdit.setText(settings["start_command"])
        self.uiEnvironmentTextEdit.setText(settings["environment"])
        self.uiConsoleTypeComboBox.setCurrentIndex(self.uiConsoleTypeComboBox.findText(settings["console_type"]))
        self.uiConsoleAutoStartCheckBox.setChecked(settings["console_auto_start"])
        self.uiAuxTypeComboBox.setCurrentIndex(self.uiAuxTypeComboBox.findText(settings["aux_type"]))
        self.uiConsoleResolutionComboBox.setCurrentIndex(self.uiConsoleResolutionComboBox.findText(settings["console_resolution"]))
        self.uiConsoleHttpPortSpinBox.setValue(settings["console_http_port"])
        self.uiHttpConsolePathLineEdit.setText(settings["console_http_path"])
        self.uiExtraHostsTextEdit.setPlainText(settings["extra_hosts"])
        self.uiExtraVolumeTextEdit.setPlainText("\n".join(settings["extra_volumes"]))
        self.uiMaxMemorySpinBox.setValue(settings["memory"])
        self.uiMaxCPUsDoubleSpinBox.setValue(settings["cpus"])

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
            self.uiAdapterSpinBox.setValue(settings["adapters"])
            self._custom_adapters = settings["custom_adapters"].copy()
        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiCMDLabel.hide()
            self.uiCMDLineEdit.hide()
            self.uiAdapterLabel.hide()
            self.uiAdapterSpinBox.hide()
            self.uiCategoryComboBox.hide()
            self.uiCustomAdaptersLabel.hide()
            self.uiCustomAdaptersConfigurationPushButton.hide()

        if not node:
            # these are template settings

            self.uiNameLabel.setText("Template name:")

            # load the default name format
            self.uiDefaultNameFormatLineEdit.setText(settings["default_name_format"])

            # load the symbol
            self.uiSymbolLineEdit.setText(settings["symbol"])
            self.uiSymbolLineEdit.setToolTip('<img src="{}"/>'.format(settings["symbol"]))

            index = self.uiCategoryComboBox.findData(settings["category"])
            if index != -1:
                self.uiCategoryComboBox.setCurrentIndex(index)
            self.uiNetworkConfigEditButton.hide()
            self.uiNetworkConfigLabel.hide()
        else:
            self._node = node
            self.uiCategoryComboBox.hide()
            self.uiCategoryLabel.hide()

            self.uiDefaultNameFormatLabel.hide()
            self.uiDefaultNameFormatLineEdit.hide()

            self.uiSymbolLabel.hide()
            self.uiSymbolLineEdit.hide()
            self.uiSymbolToolButton.hide()

        self.uiUsageTextEdit.setPlainText(settings["usage"])

    def _networkConfigEditSlot(self):

        dialog = FileEditorDialog(self._node, self._node.configFiles()[0])
        dialog.setModal(True)
        self.stackUnder(dialog)
        dialog.show()

    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the Docker container settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        settings["start_command"] = self.uiCMDLineEdit.text()
        settings["environment"] = self.uiEnvironmentTextEdit.toPlainText()
        settings["console_type"] = self.uiConsoleTypeComboBox.currentText()
        settings["console_auto_start"] = self.uiConsoleAutoStartCheckBox.isChecked()
        settings["aux_type"] = self.uiAuxTypeComboBox.currentText()
        settings["console_resolution"] = self.uiConsoleResolutionComboBox.currentText()
        settings["console_http_port"] = self.uiConsoleHttpPortSpinBox.value()
        settings["console_http_path"] = self.uiHttpConsolePathLineEdit.text()
        settings["extra_hosts"] = self.uiExtraHostsTextEdit.toPlainText()
        # only tidy input here, validation is performed server side
        settings["extra_volumes"] = [ y for x in self.uiExtraVolumeTextEdit.toPlainText().split("\n") for y in [ x.strip() ] if y ]
        settings["memory"] = self.uiMaxMemorySpinBox.value()
        settings["cpus"] = round(self.uiMaxCPUsDoubleSpinBox.value(), self.uiMaxCPUsDoubleSpinBox.decimals())

        if not group:
            adapters = self.uiAdapterSpinBox.value()
            if node:
                if settings["adapters"] != adapters:
                    # check if the adapters settings have changed
                    node_ports = node.ports()
                    for node_port in node_ports:
                        if not node_port.isFree():
                            QtWidgets.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
                            raise ConfigurationError()

            settings["adapters"] = adapters
            settings["custom_adapters"] = self._custom_adapters.copy()

            name = self.uiNameLineEdit.text()
            if not name:
                QtWidgets.QMessageBox.critical(self, "Name", "Docker name cannot be empty!")
            else:
                settings["name"] = name

        if not node:
            # these are template settings
            settings["category"] = self.uiCategoryComboBox.itemData(self.uiCategoryComboBox.currentIndex())

            # save the default name format
            default_name_format = self.uiDefaultNameFormatLineEdit.text().strip()
            if '{0}' not in default_name_format and '{id}' not in default_name_format:
                QtWidgets.QMessageBox.critical(self, "Default name format", "The default name format must contain at least {0} or {id}")
            else:
                settings["default_name_format"] = default_name_format

            symbol_path = self.uiSymbolLineEdit.text()
            settings["symbol"] = symbol_path

        settings["usage"] = self.uiUsageTextEdit.toPlainText()
        return settings
