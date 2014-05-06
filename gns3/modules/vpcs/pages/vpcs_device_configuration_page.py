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
Configuration page for VPCS devices.
"""

import os
from gns3.qt import QtGui
from .. import VPCS
from gns3.node_configurator import ConfigurationError
from ..ui.vpcs_device_configuration_page_ui import Ui_vpcsDeviceConfigPageWidget


class vpcsDeviceConfigurationPage(QtGui.QWidget, Ui_vpcsDeviceConfigPageWidget):
    """
    QWidget configuration page for VPCS devices.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self.uiStartupConfigToolButton.clicked.connect(self._startupConfigBrowserSlot)

    def _startupConfigBrowserSlot(self):
        """
        Slot to open a file browser and select a script-file file.
        """

        #TODO: current directory for script-file + filter?
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
        Loads the VPCS device settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
            self.uiConsolePortSpinBox.setValue(settings["console"])

            # load the script-file
            self.uiStartupConfigLineEdit.setText(settings["script_file"])

            # load the available VPCS images
            vpcs_images = VPCS.instance().vpcsImages()
            for vpcs_image in vpcs_images.values():
                #TODO: remote server aware
                self.uiVPCSImageComboBox.addItem(vpcs_image["image"], vpcs_image["path"])

            index = self.uiVPCSImageComboBox.findText(os.path.basename(settings["path"]))
            if index != -1:
                self.uiVPCSImageComboBox.setCurrentIndex(index)

        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiVPCSImageLabel.hide()
            self.uiVPCSImageComboBox.hide()
            self.uiConsolePortLabel.hide()
            self.uiConsolePortSpinBox.hide()
            self.uiStartupConfigLabel.hide()
            self.uiStartupConfigLineEdit.hide()
            self.uiStartupConfigToolButton.hide()


        # load the number of adapters
        self.uiEthernetAdaptersSpinBox.setValue(settings["ethernet_adapters"])

    def saveSettings(self, settings, node, group=False):
        """
        Saves the VPCS device settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        # these settings cannot be shared by nodes and updated
        # in the node configurator.
        if not group:
            settings["name"] = self.uiNameLineEdit.text()
            settings["console"] = self.uiConsolePortSpinBox.value()

            script_file = self.uiStartupConfigLineEdit.text()
            if script_file != settings["script_file"]:
                if os.access(script_file, os.R_OK):
                    settings["script_file"] = script_file
                else:
                    QtGui.QMessageBox.critical(self, "Script-file", "Cannot read the script-file file")

            # save the VPCS image path
            index = self.uiVPCSImageComboBox.currentIndex()
            ios_path = self.uiVPCSImageComboBox.itemData(index)
            settings["path"] = ios_path
        else:
            del settings["name"]
            del settings["console"]

        node_ports = node.ports()
        for node_port in node_ports:
            if not node_port.isFree():
                QtGui.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
#             if (node_port.linkType() == "Ethernet" and node_port.slotNumber() > ethernet_adapters) or \
#                (node_port.linkType() == "Serial" and node_port.slotNumber() > serial_adapters) and not node_port.isFree():
#                 QtGui.QMessageBox.critical(self, node.name(), "A link is connected to port {} on adapter in slot {}, please remove it first".format(node_port.name(),
#                                                                                                                                                     node_port.slotNumber()))
                raise ConfigurationError()
