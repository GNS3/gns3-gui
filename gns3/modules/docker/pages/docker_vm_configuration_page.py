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

from gns3.qt import QtWidgets, QtGui

from ..ui.docker_vm_configuration_page_ui import Ui_dockerVMConfigPageWidget
from ....dialogs.file_editor_dialog import FileEditorDialog
from ....dialogs.node_properties_dialog import ConfigurationError
from ....dialogs.symbol_selection_dialog import SymbolSelectionDialog


class DockerVMConfigurationPage(
        QtWidgets.QWidget, Ui_dockerVMConfigPageWidget):
    """QWidget configuration page for Docker images."""

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.uiSymbolToolButton.clicked.connect(self._symbolBrowserSlot)
        self.uiNetworkConfigEditButton.released.connect(self._networkConfigEditSlot)

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
        Loads the Docker VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of images
        """

        self.uiCMDLineEdit.setText(settings["start_command"])
        self.uiEnvironmentTextEdit.setText(settings["environment"])
        self.uiConsoleTypeComboBox.setCurrentIndex(self.uiConsoleTypeComboBox.findText(settings["console_type"]))
        self.uiConsoleResolutionComboBox.setCurrentIndex(self.uiConsoleResolutionComboBox.findText(settings["console_resolution"]))
        self.uiConsoleHttpPortSpinBox.setValue(settings["console_http_port"])
        self.uiHttpConsolePathLineEdit.setText(settings["console_http_path"])

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
            self.uiAdapterSpinBox.setValue(settings["adapters"])
        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiCMDLabel.hide()
            self.uiCMDLineEdit.hide()
            self.uiAdapterLabel.hide()
            self.uiAdapterSpinBox.hide()
            self.uiConsolePortLabel.hide()
            self.uiConsolePortSpinBox.hide()
            self.uiAuxPortLabel.hide()
            self.uiAuxPortSpinBox.hide()
            self.uiCategoryComboBox.hide()

        if not node:
            # these are template settings

            # rename the label from "Name" to "Template name"
            self.uiNameLabel.setText("Template name:")

            # load the default name format
            self.uiDefaultNameFormatLineEdit.setText(settings["default_name_format"])

            # load the symbol
            self.uiSymbolLineEdit.setText(settings["symbol"])
            self.uiSymbolLineEdit.setToolTip('<img src="{}"/>'.format(settings["symbol"]))

            self.uiCategoryComboBox.setCurrentIndex(settings["category"])
            self.uiConsolePortLabel.hide()
            self.uiConsolePortSpinBox.hide()
            self.uiAuxPortLabel.hide()
            self.uiAuxPortSpinBox.hide()
            self.uiNetworkConfigEditButton.hide()
            self.uiNetworkConfigLabel.hide()
        else:
            self._node = node
            self.uiConsolePortSpinBox.setValue(settings["console"])
            self.uiAuxPortSpinBox.setValue(settings["aux"])
            self.uiCategoryComboBox.hide()
            self.uiCategoryLabel.hide()

            self.uiDefaultNameFormatLabel.hide()
            self.uiDefaultNameFormatLineEdit.hide()

            self.uiSymbolLabel.hide()
            self.uiSymbolLineEdit.hide()
            self.uiSymbolToolButton.hide()

    def _networkConfigEditSlot(self):
        dialog = FileEditorDialog(self._node, self._node.networkInterfacesPath())
        dialog.setModal(True)
        self.stackUnder(dialog)
        dialog.show()

    def saveSettings(self, settings, node=None, group=False):
        """Saves the Docker container settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        settings["start_command"] = self.uiCMDLineEdit.text()
        settings["environment"] = self.uiEnvironmentTextEdit.toPlainText()
        settings["console_type"] = self.uiConsoleTypeComboBox.currentText()
        settings["console_resolution"] = self.uiConsoleResolutionComboBox.currentText()
        settings["console_http_port"] = self.uiConsoleHttpPortSpinBox.value()
        settings["console_http_path"] = self.uiHttpConsolePathLineEdit.text()

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

            name = self.uiNameLineEdit.text()
            if not name:
                QtWidgets.QMessageBox.critical(self, "Name", "Docker name cannot be empty!")
            else:
                settings["name"] = name


        if not node:
            # these are template settings
            settings["category"] = self.uiCategoryComboBox.currentIndex()

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
        else:
            settings["console"] = self.uiConsolePortSpinBox.value()
            settings["aux"] = self.uiAuxPortSpinBox.value()


