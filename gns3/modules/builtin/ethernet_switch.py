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

from gns3.node import Node

import logging
log = logging.getLogger(__name__)


class EthernetSwitch(Node):
    """
    Ethernet switch.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "ethernet_switch"

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        # this is an always-on node
        self.setStatus(Node.started)
        self._always_on = True
        self.settings().update({"ports_mapping": [], "console_type": "none"})

    def info(self):
        """
        Returns information about this Ethernet switch.

        :returns: formatted string
        """

        info = """Ethernet switch {name} is always-on
  Running on server {host} with port {port}
  Local ID is {id} and server ID is {node_id}
  Console is on port {console} and type is {console_type}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           host=self.compute().name(),
           port=self.compute().port(),
           console=self._settings["console"],
           console_type=self._settings["console_type"])

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "   Port {} is empty\n".format(port.name())
            else:
                for port_settings in self._settings["ports_mapping"]:
                    if port_settings["port_number"] == port.portNumber():

                        port_type = port_settings["type"]
                        port_ethertype = port_settings.get("ethertype", "")
                        port_vlan = port_settings["vlan"]
                        port_ethertype_info = ""

                        if port_type == "access":
                            port_vlan_info = "VLAN ID {}".format(port_vlan)
                        elif port_type == "dot1q":
                            port_vlan_info = "native VLAN {}".format(port_vlan)
                        elif port_type == "qinq":
                            port_vlan_info = "outer VLAN {}".format(port_vlan)
                            port_ethertype_info = "({})".format(port_ethertype)

                        port_info += "   Port {name} is in {port_type} {port_ethertype_info} mode, with {port_vlan_info},\n".format(name=port.name(),
                                                                                                                                    port_type=port_type,
                                                                                                                                    port_ethertype_info=port_ethertype_info,
                                                                                                                                    port_vlan_info=port_vlan_info)
                        port_info += "    {port_description}\n".format(port_description=port.description())
                        break

        return info + port_info

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

        :returns: QWidget object
        """

        from .pages.ethernet_switch_configuration_page import EthernetSwitchConfigurationPage
        return EthernetSwitchConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/ethernet_switch.svg"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.switches]

    def __str__(self):

        return "Ethernet switch"
