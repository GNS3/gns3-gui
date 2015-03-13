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

from gns3.qt import QtGui
from gns3.dialogs.node_configurator_dialog import ConfigurationError

from ..ui.virtualbox_vm_configuration_page_ui import Ui_virtualBoxVMConfigPageWidget


class VirtualBoxVMConfigurationPage(QtGui.QWidget, Ui_virtualBoxVMConfigPageWidget):

    """
    QWidget configuration page for VirtualBox VMs.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

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
            self.uiVMListLabel.hide()
            self.uiVMListComboBox.hide()

        self.uiAdaptersSpinBox.setValue(settings["adapters"])
        index = self.uiAdapterTypesComboBox.findText(settings["adapter_type"])
        if index != -1:
            self.uiAdapterTypesComboBox.setCurrentIndex(index)
        self.uiUseAnyAdapterCheckBox.setChecked(settings["use_any_adapter"])
        self.uiVMRamSpinBox.setValue(settings["ram"])
        self.uiHeadlessModeCheckBox.setChecked(settings["headless"])
        self.uiEnableConsoleCheckBox.setChecked(settings["enable_remote_console"])


    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the VirtualBox VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        # these settings cannot be shared by nodes and updated
        # in the node configurator.
        if not group:

            if "name" in settings:
                name = self.uiNameLineEdit.text()
                if not name:
                    QtGui.QMessageBox.critical(self, "Name", "VirtualBox name cannot be empty!")
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

        settings["ram"] = self.uiVMRamSpinBox.value()
        settings["adapter_type"] = self.uiAdapterTypesComboBox.currentText()
        settings["headless"] = self.uiHeadlessModeCheckBox.isChecked()
        settings["use_any_adapter"] = self.uiUseAnyAdapterCheckBox.isChecked()

        adapters = self.uiAdaptersSpinBox.value()
        if node:
            if settings["adapters"] != adapters:
                # check if the adapters settings have changed
                node_ports = node.ports()
                for node_port in node_ports:
                    if not node_port.isFree():
                        QtGui.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
                        raise ConfigurationError()
        settings["adapters"] = adapters
