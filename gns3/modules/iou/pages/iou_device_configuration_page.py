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

from gns3.qt import QtCore, QtGui
from gns3.dialogs.node_configurator_dialog import ConfigurationError
from gns3.utils.get_resource import get_resource
from gns3.utils.get_default_base_config import get_default_base_config
from ..ui.iou_device_configuration_page_ui import Ui_iouDeviceConfigPageWidget


class iouDeviceConfigurationPage(QtGui.QWidget, Ui_iouDeviceConfigPageWidget):
    """
    QWidget configuration page for IOU devices.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self.uiInitialConfigToolButton.clicked.connect(self._initialConfigBrowserSlot)
        self.uiIOUImageToolButton.clicked.connect(self._iouImageBrowserSlot)
        self.uiDefaultValuesCheckBox.stateChanged.connect(self._useDefaultValuesSlot)
        self._current_iou_image = ""

        # location of the base config templates
        self._base_iou_l2_config_template = get_resource(os.path.join("configs", "iou_l2_base_initial-config.txt"))
        self._base_iou_l3_config_template = get_resource(os.path.join("configs", "iou_l3_base_initial-config.txt"))

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
        path = IOUDevicePreferencesPage.getIOUImage(self)
        if not path:
            return
        self.uiIOUImageLineEdit.clear()
        self.uiIOUImageLineEdit.setText(path)

        if "l2" in path:
            # set the default L2 base initial-config
            default_base_config = get_default_base_config(self._base_iou_l2_config_template)
            if default_base_config:
                self.uiInitialConfigLineEdit.setText(default_base_config)
        else:
            # set the default L3 base initial-config
            default_base_config = get_default_base_config(self._base_iou_l3_config_template)
            if default_base_config:
                self.uiInitialConfigLineEdit.setText(default_base_config)

    def _initialConfigBrowserSlot(self):
        """
        Slot to open a file browser and select a initial-config file.
        """

        config_dir = os.path.join(os.path.dirname(QtCore.QSettings().fileName()), "base_configs")
        path = QtGui.QFileDialog.getOpenFileName(self, "Select an initial configuration", config_dir)
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "Initial configuration", "Cannot read {}".format(path))
            return

        self.uiInitialConfigLineEdit.clear()
        self.uiInitialConfigLineEdit.setText(path)

    def loadSettings(self, settings, node=None, group=False):
        """
        Loads the IOU device settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])

            if "console" in settings:
                self.uiConsolePortSpinBox.setValue(settings["console"])
            else:
                self.uiConsolePortLabel.hide()
                self.uiConsolePortSpinBox.hide()

            # load the IOU image path
            self.uiIOUImageLineEdit.setText(settings["path"])

        else:
            self.uiGeneralgroupBox.hide()

        if not node:
            # load the initial-config
            self.uiInitialConfigLineEdit.setText(settings["initial_config"])
        else:
            self.uiInitialConfigLabel.hide()
            self.uiInitialConfigLineEdit.hide()
            self.uiInitialConfigToolButton.hide()

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

    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the IOU device settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        # these settings cannot be shared by nodes and updated
        # in the node configurator.
        if not group:

            # set the device name
            name = self.uiNameLineEdit.text()
            if not name:
                QtGui.QMessageBox.critical(self, "Name", "IOU device name cannot be empty!")
            elif node and not node.validateHostname(name):
                QtGui.QMessageBox.critical(self, "Name", "Invalid name detected for IOU device: {}".format(name))
            else:
                settings["name"] = name

            settings["console"] = self.uiConsolePortSpinBox.value()

            # save the IOU image path
            ios_path = self.uiIOUImageLineEdit.text().strip()
            if ios_path:
                settings["path"] = ios_path
        else:
            del settings["name"]
            del settings["console"]

        if not node:
            initial_config = self.uiInitialConfigLineEdit.text()
            if initial_config != settings["initial_config"]:
                if os.access(initial_config, os.R_OK):
                    settings["initial_config"] = initial_config
                else:
                    QtGui.QMessageBox.critical(self, "Initial-config", "Cannot read the initial-config file")

        # save advanced settings
        settings["l1_keepalives"] = self.uiL1KeepalivesCheckBox.isChecked()
        settings["use_default_iou_values"] = self.uiDefaultValuesCheckBox.isChecked()
        settings["ram"] = self.uiRamSpinBox.value()
        settings["nvram"] = self.uiNvramSpinBox.value()

        ethernet_adapters = self.uiEthernetAdaptersSpinBox.value()
        serial_adapters = self.uiSerialAdaptersSpinBox.value()
        if ethernet_adapters + serial_adapters > 16:
            QtGui.QMessageBox.warning(self, settings["name"], "The total number of adapters cannot exceed 16")
            raise ConfigurationError()

        if node:
            if settings["ethernet_adapters"] != ethernet_adapters or settings["serial_adapters"] != serial_adapters:
                # check if the adapters settings have changed
                node_ports = node.ports()
                for node_port in node_ports:
                    if not node_port.isFree():
                        QtGui.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
                        raise ConfigurationError()

        settings["ethernet_adapters"] = ethernet_adapters
        settings["serial_adapters"] = serial_adapters
