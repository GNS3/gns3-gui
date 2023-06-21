# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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


class EthernetHub(Node):
    """
    Ethernet hub.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "ethernet_hub"

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        # this is an always-on node
        self.setStatus(Node.started)
        self._always_on = True
        self.settings().update({"ports_mapping": []})

    def info(self):
        """
        Returns information about this Ethernet hub.

        :returns: formatted string
        """

        info = """Ethernet hub {name} is always-on
  Running on server {host} with port {port}
  Local ID is {id} and node ID is {node_id}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           host=self.compute().name(),
           port=self.compute().port())

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "   Port {} is empty\n".format(port.name())
            else:
                port_info += "   Port {name} {description}\n".format(name=port.name(),
                                                                     description=port.description())

        return info + port_info

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

        :returns: QWidget object
        """

        from .pages.ethernet_hub_configuration_page import EthernetHubConfigurationPage
        return EthernetHubConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/hub.svg"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.switches]

    def __str__(self):

        return "Ethernet hub"
