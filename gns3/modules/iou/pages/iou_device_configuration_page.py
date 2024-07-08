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
Configuration page for IOU devices.
"""

import os

from gns3.qt import QtWidgets
from gns3.local_server import LocalServer
from gns3.local_config import LocalConfig
from gns3.dialogs.node_properties_dialog import ConfigurationError
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.node import Node
from gns3.controller import Controller
from gns3.utils.get_resource import get_resource
from ..ui.iou_device_configuration_page_ui import Ui_iouDeviceConfigPageWidget

import logging
log = logging.getLogger(__name__)


class iouDeviceConfigurationPage(QtWidgets.QWidget, Ui_iouDeviceConfigPageWidget):

    """
    QWidget configuration page for IOU devices.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        self.uiSymbolToolButton.clicked.connect(self._symbolBrowserSlot)
        self.uiStartupConfigToolButton.clicked.connect(self._startupConfigBrowserSlot)
        self.uiPrivateConfigToolButton.clicked.connect(self._privateConfigBrowserSlot)
        self.uiIOUImageToolButton.clicked.connect(self._iouImageBrowserSlot)
        self.uiDefaultValuesCheckBox.stateChanged.connect(self._useDefaultValuesSlot)
        self._current_iou_image = ""
        self._compute_id = None
        if Controller.instance().isRemote():
            self.uiStartupConfigToolButton.hide()
            self.uiPrivateConfigToolButton.hide()

        # location of the base config templates
        # FIXME: this does not work
        self._base_iou_l2_config_template = get_resource(os.path.join("configs", "iou_l2_base_startup-config.txt"))
        self._base_iou_l3_config_template = get_resource(os.path.join("configs", "iou_l3_base_startup-config.txt"))
        self._default_configs_dir = LocalServer.instance().localServerSettings()["configs_path"]

        # add the categories
        for name, category in Node.defaultCategories().items():
            self.uiCategoryComboBox.addItem(name, category)

    def _useDefaultValuesSlot(self, state):
        """
        Slot to enable or not the RAM and NVRAM spin boxes.
        """

        if state:
            self.uiRamSpinBox.setEnabled(False)
            self.uiNvramSpinBox.setEnabled(False)
        else:
            self.uiRamSpinBox.setEnabled(True)
            self.uiNvramSpinBox.setEnabled(True)

    def _iouImageBrowserSlot(self):
        """
        Slot to open a file browser and select an IOU image.
        """

        from .iou_device_preferences_page import IOUDevicePreferencesPage
        path = IOUDevicePreferencesPage.getIOUImage(self, self._compute_id)
        if not path:
            return
        self.uiIOUImageLineEdit.clear()
        self.uiIOUImageLineEdit.setText(path)

        if len(self.uiStartupConfigLineEdit.text().strip()) == 0:
            if "l2" in path:
                # set the default L2 base startup-config
                default_base_config = self._base_iou_l2_config_template
                if default_base_config:
                    self.uiStartupConfigLineEdit.setText(default_base_config)
            else:
                # set the default L3 base startup-config
                default_base_config = self._base_iou_l3_config_template
                if default_base_config:
                    self.uiStartupConfigLineEdit.setText(default_base_config)

    def _startupConfigBrowserSlot(self):
        """
        Slot to open a file browser and select a startup-config file.
        """

        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a startup-config file", self._default_configs_dir)
        if not path:
            return

        self._default_configs_dir = os.path.dirname(path)
        if not os.access(path, os.R_OK):
            QtWidgets.QMessageBox.critical(self, "Startup-config", "Cannot read {}".format(path))
            return

        self.uiStartupConfigLineEdit.clear()
        self.uiStartupConfigLineEdit.setText(path)

    def _privateConfigBrowserSlot(self):
        """
        Slot to open a file browser and select a private-config file.
        """

        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a private-config file", self._default_configs_dir)
        if not path:
            return

        self._default_configs_dir = os.path.dirname(path)
        if not os.access(path, os.R_OK):
            QtWidgets.QMessageBox.critical(self, "Private-config", "Cannot read {}".format(path))
            return

        self.uiPrivateConfigLineEdit.clear()
        self.uiPrivateConfigLineEdit.setText(path)

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
        Loads the IOU device settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        if node:
            self._compute_id = node.compute().id()
        else:
            self._compute_id = settings["compute_id"]

        if not group:
            self.uiNameLineEdit.setText(settings["name"])

            # load the IOU image path
            self.uiIOUImageLineEdit.setText(settings["path"])

        else:
            self.uiGeneralgroupBox.hide()

        if not node:
            # these are template settings

            self.uiNameLabel.setText("Template name:")

            # load the default name format
            self.uiDefaultNameFormatLineEdit.setText(settings["default_name_format"])

            # load the startup-config and private-config
            self.uiStartupConfigLineEdit.setText(settings["startup_config"])
            self.uiPrivateConfigLineEdit.setText(settings["private_config"])

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
            self.uiStartupConfigLabel.hide()
            self.uiStartupConfigLineEdit.hide()
            self.uiStartupConfigToolButton.hide()
            self.uiPrivateConfigLabel.hide()
            self.uiPrivateConfigLineEdit.hide()
            self.uiPrivateConfigToolButton.hide()
            self.uiSymbolLabel.hide()
            self.uiSymbolLineEdit.hide()
            self.uiSymbolToolButton.hide()
            self.uiCategoryComboBox.hide()
            self.uiCategoryLabel.hide()
            self.uiCategoryComboBox.hide()

        # load the console type
        index = self.uiConsoleTypeComboBox.findText(settings["console_type"])
        if index != -1:
            self.uiConsoleTypeComboBox.setCurrentIndex(index)

        self.uiConsoleAutoStartCheckBox.setChecked(settings["console_auto_start"])

        # load advanced settings
        if "l1_keepalives" in settings:
            self.uiL1KeepalivesCheckBox.setChecked(settings["l1_keepalives"])
        else:
            self.uiL1KeepalivesCheckBox.hide()
        self.uiDefaultValuesCheckBox.setChecked(settings["use_default_iou_values"])
        self.uiRamSpinBox.setValue(settings["ram"])
        self.uiNvramSpinBox.setValue(settings["nvram"])

        # load the number of adapters
        self.uiEthernetAdaptersSpinBox.setValue(settings["ethernet_adapters"])
        self.uiSerialAdaptersSpinBox.setValue(settings["serial_adapters"])
        self.uiUsageTextEdit.setPlainText(settings["usage"])

    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the IOU device settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        # these settings cannot be shared by nodes and updated
        # in the node properties dialog.
        if not group:
            # set the device name
            name = self.uiNameLineEdit.text()
            if not name:
                QtWidgets.QMessageBox.critical(self, "Name", "IOU device name cannot be empty!")
            elif node and not node.validateHostname(name) and not LocalConfig.instance().experimental():
                QtWidgets.QMessageBox.critical(self, "Name", "Invalid name detected for IOU device: {}".format(name))
            else:
                settings["name"] = name

            # save the IOU image path
            ios_path = self.uiIOUImageLineEdit.text().strip()
            if ios_path:
                settings["path"] = ios_path

        if not node:
            # these are template settings

            # save the default name format
            default_name_format = self.uiDefaultNameFormatLineEdit.text().strip()
            if '{0}' not in default_name_format and '{id}' not in default_name_format:
                QtWidgets.QMessageBox.critical(self, "Default name format", "The default name format must contain at least {0} or {id}")
            else:
                settings["default_name_format"] = default_name_format

            # save the startup-config
            startup_config = self.uiStartupConfigLineEdit.text().strip()
            if not startup_config:
                settings["startup_config"] = ""
            elif startup_config != settings["startup_config"]:
                if self._configFileValid(startup_config):
                    settings["startup_config"] = startup_config
                else:
                    QtWidgets.QMessageBox.critical(self, "Startup-config", "Cannot access or read the startup-config file")

            # save the private-config
            private_config = self.uiPrivateConfigLineEdit.text().strip()
            if not private_config:
                settings["private_config"] = ""
            elif private_config != settings["private_config"]:
                if self._configFileValid(private_config):
                    settings["private_config"] = private_config
                else:
                    QtWidgets.QMessageBox.critical(self, "Private-config", "Cannot access or read the private-config file")

            settings["symbol"] = self.uiSymbolLineEdit.text()
            settings["category"] = self.uiCategoryComboBox.itemData(self.uiCategoryComboBox.currentIndex())

        # save advanced settings
        settings["l1_keepalives"] = self.uiL1KeepalivesCheckBox.isChecked()
        settings["use_default_iou_values"] = self.uiDefaultValuesCheckBox.isChecked()
        settings["ram"] = self.uiRamSpinBox.value()
        settings["nvram"] = self.uiNvramSpinBox.value()

        ethernet_adapters = self.uiEthernetAdaptersSpinBox.value()
        serial_adapters = self.uiSerialAdaptersSpinBox.value()
        if ethernet_adapters + serial_adapters > 16:
            QtWidgets.QMessageBox.warning(self, settings["name"], "The total number of adapters cannot exceed 16")
            raise ConfigurationError()

        if node:
            if node.settings()["ethernet_adapters"] != ethernet_adapters or node.settings()["serial_adapters"] != serial_adapters:
                # check if the adapters settings have changed
                node_ports = node.ports()
                for node_port in node_ports:
                    if not node_port.isFree():
                        QtWidgets.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
                        raise ConfigurationError()

        settings["ethernet_adapters"] = ethernet_adapters
        settings["serial_adapters"] = serial_adapters
        # save console type
        settings["console_type"] = self.uiConsoleTypeComboBox.currentText().lower()
        settings["console_auto_start"] = self.uiConsoleAutoStartCheckBox.isChecked()
        settings["usage"] = self.uiUsageTextEdit.toPlainText()
        return settings

    def _configFileValid(self, path):
        """
        Return true if it is a valid configuration file
        """

        if not os.path.isabs(path):
            path = os.path.join(LocalServer.instance().localServerSettings()["configs_path"], path)
        result = os.access(path, os.R_OK)
        if not result:
            if not os.path.exists(path):
                log.error("Cannot access config file '{}'".format(path))
            else:
                log.error("Cannot read config file '{}'".format(path))
        return result
