# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 GNS3 Technologies Inc.
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
TraceNG node implementation.
"""

from gns3.node import Node
from gns3.qt import QtWidgets

import logging
log = logging.getLogger(__name__)


class TraceNGNode(Node):
    """
    TraceNG node.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "traceng"

    def __init__(self, module, server, project):
        super().__init__(module, server, project)

        traceng_settings = {"console_type": "none",
                            "ip_address": "",
                            "default_destination": ""}

        self._last_destination = ""
        self.settings().update(traceng_settings)

    def start(self):
        """
        Starts this node instance.
        """

        if self.isStarted():
            log.debug("{} is already running".format(self.name()))
            return

        if self._last_destination:
            destination = self._last_destination
        else:
            destination = self.settings()["default_destination"]
        destination, ok = QtWidgets.QInputDialog.getText(self.parent(), "TraceNG", "Destination host or IP address:", text=destination)
        if ok:
            if not destination:
                QtWidgets.QMessageBox.critical(self, "TraceNG", "Please provide a host or IP address to trace")
                return
            ip_address = self.settings()["ip_address"]
            if destination == ip_address:
                QtWidgets.QMessageBox.critical(self, "TraceNG", "Destination cannot be the same as this node IP address ({})".format(ip_address))
                return
            self._last_destination = destination
            params = {"destination": destination}
            log.debug("{} is starting".format(self.name()))
            self.controllerHttpPost("/nodes/{node_id}/start".format(node_id=self._node_id), self._startCallback, body=params, timeout=None, progressText="{} is starting".format(self.name()))

    def info(self):
        """
        Returns information about this TraceNG node.

        :returns: formatted string
        """

        info = """Node {name} is {state}
  Running on server {host} with port {port}
  Local ID is {id} and server ID is {node_id}
  Console is on port {console}
  IP address is {ip_address}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           state=self.state(),
           host=self.compute().name(),
           port=self.compute().port(),
           console=self._settings["console"],
           ip_address=self._settings["ip_address"])

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "     {port_name} is empty\n".format(port_name=port.name())
            else:
                port_info += "     {port_name} {port_description}\n".format(port_name=port.name(),
                                                                            port_description=port.description())

        return info + port_info

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

        :returns: QWidget object
        """

        from .pages.traceng_node_configuration_page import TraceNGNodeConfigurationPage
        return TraceNGNodeConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/traceng.svg"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the node panel).

        :returns: list of node categories
        """

        return [Node.end_devices]

    def __str__(self):

        return "TraceNG node"
