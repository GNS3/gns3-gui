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
VPCS node implementation.
"""

from gns3.node import Node

import logging
log = logging.getLogger(__name__)


class VPCSNode(Node):
    """
    VPCS node.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "vpcs"

    def __init__(self, module, server, project):
        super().__init__(module, server, project)

        vpcs_settings = {"startup_script": None,
                         "console_type": "telnet",
                         "console_auto_start": True}

        self.settings().update(vpcs_settings)

    def info(self):
        """
        Returns information about this VPCS node.

        :returns: formatted string
        """

        info = """Node {name} is {state}
  Running on server {host} with port {port}
  Local ID is {id} and server ID is {node_id}
  Console is on port {console} and type is {console_type}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           state=self.state(),
           host=self.compute().name(),
           port=self.compute().port(),
           console=self._settings["console"],
           console_type=self._settings["console_type"])

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "     {port_name} is empty\n".format(port_name=port.name())
            else:
                port_info += "     {port_name} {port_description}\n".format(port_name=port.name(),
                                                                            port_description=port.description())

        return info + port_info

    def configFiles(self):
        """
        Name of the configuration files
        """

        return ["startup.vpc"]

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

        :returns: QWidget object
        """

        from .pages.vpcs_node_configuration_page import VPCSNodeConfigurationPage
        return VPCSNodeConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/vpcs_guest.svg"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the node panel).

        :returns: list of node categories
        """

        return [Node.end_devices]

    def __str__(self):

        return "VPCS node"


# for compatibility pre version 2.0
class VPCSDevice(VPCSNode):
    pass
