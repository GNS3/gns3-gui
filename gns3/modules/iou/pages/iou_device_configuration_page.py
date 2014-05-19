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
from gns3.qt import QtGui
from gns3.node_configurator import ConfigurationError

from .. import IOU
from ..ui.iou_device_configuration_page_ui import Ui_iouDeviceConfigPageWidget


class iouDeviceConfigurationPage(QtGui.QWidget, Ui_iouDeviceConfigPageWidget):
    """
    QWidget configuration page for IOU devices.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self.uiStartupConfigToolButton.clicked.connect(self._startupConfigBrowserSlot)
        self.uiDefaultValuesCheckBox.stateChanged.connect(self._useDefaultValuesSlot)

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

    def _startupConfigBrowserSlot(self):
        """
        Slot to open a file browser and select a startup-config file.
        """

        #TODO: current directory for startup-config + filter?
        path = QtGui.QFileDialog.getOpenFileName(self, "Select a startup configuration", ".")
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "Startup configuration", "Cannot read {}".format(path))
            return

        self.uiStartupConfigLineEdit.clear()
        self.uiStartupConfigLineEdit.setText(path)

    def loadSettings(self, settings, node, group=False):
        """
        Loads the IOU device settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
            self.uiConsolePortSpinBox.setValue(settings["console"])

            # load the startup-config
            self.uiStartupConfigLineEdit.setText(settings["startup_config"])

            # load the available IOU images
            iou_images = IOU.instance().iouImages()
            for iou_image in iou_images.values():
                #TODO: remote server aware
                self.uiIOUImageComboBox.addItem(iou_image["image"], iou_image["path"])

            index = self.uiIOUImageComboBox.findText(os.path.basename(settings["path"]))
            if index != -1:
                self.uiIOUImageComboBox.setCurrentIndex(index)

        else:
            self.uiGeneralgroupBox.hide()

        # load advanced settings
        self.uiL1KeepalivesCheckBox.setChecked(settings["l1_keepalives"])
        self.uiDefaultValuesCheckBox.setChecked(settings["use_default_iou_values"])
        self.uiRamSpinBox.setValue(settings["ram"])
        self.uiNvramSpinBox.setValue(settings["nvram"])

        # load the number of adapters
        self.uiEthernetAdaptersSpinBox.setValue(settings["ethernet_adapters"])
        self.uiSerialAdaptersSpinBox.setValue(settings["serial_adapters"])

    def saveSettings(self, settings, node, group=False):
        """
        Saves the IOU device settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        # these settings cannot be shared by nodes and updated
        # in the node configurator.
        if not group:
            settings["name"] = self.uiNameLineEdit.text()
            settings["console"] = self.uiConsolePortSpinBox.value()

            startup_config = self.uiStartupConfigLineEdit.text()
            if startup_config != settings["startup_config"]:
                if os.access(startup_config, os.R_OK):
                    settings["startup_config"] = startup_config
                else:
                    QtGui.QMessageBox.critical(self, "Startup-config", "Cannot read the startup-config file")

            # save the IOU image path
            index = self.uiIOUImageComboBox.currentIndex()
            ios_path = self.uiIOUImageComboBox.itemData(index)
            settings["path"] = ios_path
        else:
            del settings["name"]
            del settings["console"]

        # save advanced settings
        settings["l1_keepalives"] = self.uiL1KeepalivesCheckBox.isChecked()
        settings["use_default_iou_values"] = self.uiDefaultValuesCheckBox.isChecked()
        settings["ram"] = self.uiRamSpinBox.value()
        settings["nvram"] = self.uiNvramSpinBox.value()

        ethernet_adapters = self.uiEthernetAdaptersSpinBox.value()
        serial_adapters = self.uiSerialAdaptersSpinBox.value()
        if ethernet_adapters + serial_adapters > 16:
            QtGui.QMessageBox.warning(self, node.name(), "The total number of adapters cannot exceed 16")
            raise ConfigurationError()

        if settings["ethernet_adapters"] != ethernet_adapters or settings["serial_adapters"] != serial_adapters:
            # check if the adapters settings have changed
            node_ports = node.ports()
            for node_port in node_ports:
                if not node_port.isFree():
                    QtGui.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
                    raise ConfigurationError()

        settings["ethernet_adapters"] = ethernet_adapters
        settings["serial_adapters"] = serial_adapters
