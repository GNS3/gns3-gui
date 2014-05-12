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
        self.uiScriptFileToolButton.clicked.connect(self._scriptFileBrowserSlot)

    def _scriptFileBrowserSlot(self):
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

        self.uiScriptFileLineEdit.clear()
        self.uiScriptFileLineEdit.setText(path)

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
            self.uiScriptFileLineEdit.setText(settings["script_file"])

        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiConsolePortLabel.hide()
            self.uiConsolePortSpinBox.hide()
            self.uiScriptFileLabel.hide()
            self.uiScriptFileLineEdit.hide()
            self.uiScriptFileToolButton.hide()

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

            script_file = self.uiScriptFileLineEdit.text()
            if script_file != settings["script_file"]:
                if os.access(script_file, os.R_OK):
                    settings["script_file"] = script_file
                else:
                    QtGui.QMessageBox.critical(self, "Script-file", "Cannot read the script-file file")
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
