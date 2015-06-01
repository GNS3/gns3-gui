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
Configuration page for Dynamips Ethernet hubs.
"""

from gns3.qt import QtWidgets
from gns3.dialogs.node_properties_dialog import ConfigurationError
from ..ui.ethernet_hub_configuration_page_ui import Ui_ethernetHubConfigPageWidget


class EthernetHubConfigurationPage(QtWidgets.QWidget, Ui_ethernetHubConfigPageWidget):

    """
    QWidget configuration page for Ethernet hubs.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

    def loadSettings(self, settings, node, group=False):
        """
        Loads the Ethernet hub settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
        else:
            self.uiNameLineEdit.hide()
            self.uiNameLabel.hide()

        nbports = len(settings["ports"])
        self.uiPortsSpinBox.setValue(nbports)

    def saveSettings(self, settings, node, group=False):
        """
        Saves the Ethernet hub settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            # set the device name
            name = self.uiNameLineEdit.text()
            if not name:
                QtWidgets.QMessageBox.critical(self, "Name", "Ethernet hub name cannot be empty!")
            else:
                settings["name"] = name
        else:
            del settings["name"]

        nbports = self.uiPortsSpinBox.value()

        # check that a link isn't connected to a port
        # before we delete it
        ports = node.ports()
        for port in ports:
            if not port.isFree() and port.portNumber() > nbports:
                self.loadSettings(settings, node)
                QtWidgets.QMessageBox.critical(self, node.name(), "A link is connected to port {}, please remove it first".format(port.name()))
                raise ConfigurationError()

        settings["ports"] = []
        for port in range(1, nbports + 1):
            settings["ports"].append(str(port))
