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


import re

from gns3.node import Node

import logging
log = logging.getLogger(__name__)


class ATMSwitch(Node):

    """
    ATM switch.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "atm_switch"

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        # this is an always-on node
        self.setStatus(Node.started)
        self._always_on = True
        self.settings().update({"mappings": {}})

    def info(self):
        """
        Returns information about this ATM switch.

        :returns: formatted string
        """

        info = """ATM switch {name} is always-on
  Running on server {host} with port {port}
  Local ID is {id} and node ID is {node_id}
  Hardware is Dynamips emulated simple ATM switch
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           host=self._compute.name(),
           port=self._compute.port())

        port_info = ""
        mapping = re.compile(r"""^([0-9]*):([0-9]*):([0-9]*)$""")
        for port in self._ports:
            if port.isFree():
                port_info += "   Port {} is empty\n".format(port.name())
            else:
                port_info += "   Port {name} {description}\n".format(name=port.name(),
                                                                     description=port.description())

            for source, destination in self._settings["mappings"].items():
                match_source_mapping = mapping.search(source)
                match_destination_mapping = mapping.search(destination)
                if match_source_mapping and match_destination_mapping:
                    source_port, source_vpi, source_vci = match_source_mapping.group(1, 2, 3)
                    destination_port, destination_vpi, destination_vci = match_destination_mapping.group(1, 2, 3)
                else:
                    source_port, source_vpi = source.split(":")
                    destination_port, destination_vpi = destination.split(":")
                    source_vci = destination_vci = 0

                if port.name() == source_port or port.name() == destination_port:
                    if port.name() == source_port:
                        vpi1 = source_vpi
                        vci1 = source_vci
                        port = destination_port
                        vci2 = destination_vci
                        vpi2 = destination_vpi
                    else:
                        vpi1 = destination_vpi
                        vci1 = destination_vci
                        port = source_port
                        vci2 = source_vci
                        vpi2 = source_vpi

                    if vci1 and vci2:
                        port_info += "      incoming VPI {vpi1} and VCI {vci1} is switched to port {port} outgoing VPI {vpi2} and VCI {vci2}\n".format(vpi1=vpi1,
                                                                                                                                                       vci1=vci1,
                                                                                                                                                       port=port,
                                                                                                                                                       vpi2=vpi2,
                                                                                                                                                       vci2=vci2)
                    else:
                        port_info += "      incoming VPI {vpi1} is switched to port {port} outgoing VPI {vpi2}\n".format(vpi1=vpi1,
                                                                                                                         port=port,
                                                                                                                         vpi2=vpi2)

                    break

        return info + port_info

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

        :returns: QWidget object
        """

        from .pages.atm_switch_configuration_page import ATMSwitchConfigurationPage
        return ATMSwitchConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/atm_switch.svg"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.switches]

    def __str__(self):

        return "ATM switch"
