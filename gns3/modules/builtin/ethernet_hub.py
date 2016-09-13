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

import uuid
from gns3.node import Node
from gns3.ports.ethernet_port import EthernetPort

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

    def create(self, name=None, node_id=None, ports=None, default_name_format="Hub{0}"):
        """
        Creates this hub.

        :param name: optional name for this hub
        :param node_id: node identifier on the server
        :param ports: ports to automatically be added when creating this hub
        """

        params = {}
        if ports:
            params["ports_mapping"] = ports
        self._create(name, node_id, params, default_name_format)

    def _createCallback(self, result):
        """
        Callback for create.

        :param result: server response (dict)
        """

        if "ports_mapping" in result:
            for port_info in result["ports_mapping"]:
                port = EthernetPort(port_info["name"])
                port.setAdapterNumber(0)  # adapter number is always 0
                port.setPortNumber(port_info["port_number"])
                port.setStatus(EthernetPort.started)
                self._ports.append(port)
                log.debug("port {} has been added".format(port_info["port_number"]))

    def update(self, new_settings):
        """
        Updates the settings for this Ethernet hub.

        :param new_settings: settings dictionary
        """

        params = {}
        if "name" in new_settings:
            params["name"] = new_settings["name"]
        if "ports_mapping" in new_settings:
            params["ports_mapping"] = new_settings["ports_mapping"]
        if params:
            self._update(params)

    def _updatePort(self, port_name, port_number):

        # update the port if existing
        for port in self._ports:
            if port.portNumber() == port_number:
                port.setName(port_name)
                log.debug("port {} has been updated".format(port_number))
                return

        # otherwise create a new port
        port = EthernetPort(port_name)
        port.setAdapterNumber(0)  # adapter number is always 0
        port.setPortNumber(port_number)
        port.setStatus(EthernetPort.started)
        self._ports.append(port)
        log.debug("port {} has been added".format(port_number))

    def _updateCallback(self, result):
        """
        Callback for update.

        :param result: server response
        """

        if "ports_mapping" in result:
            updated_port_list = []
            # add/update ports
            for port_info in result["ports_mapping"]:
                self._updatePort(port_info["name"], port_info["port_number"])
                updated_port_list.append(port_info["port_number"])

            # delete ports
            for port in self._ports.copy():
                if port.isFree() and port.portNumber() not in updated_port_list:
                    self._ports.remove(port)
                    log.debug("port {} has been removed".format(port.portNumber()))

            self._settings["ports_mapping"] = list(map(int, updated_port_list))

    def info(self):
        """
        Returns information about this Ethernet hub.

        :returns: formatted string
        """

        info = """Ethernet hub {name} is always-on
  Local node ID is {id}
  Server's node ID is {node_id}
  Hub's server runs on {host}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           host=self.compute().id())

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "   Port {} is empty\n".format(port.name())
            else:
                port_info += "   Port {name} {description}\n".format(name=port.name(),
                                                                     description=port.description())

        return info + port_info

    def dump(self):
        """
        Returns a representation of this Ethernet hub
        (to be saved in a topology file)

        :returns: representation of the node (dictionary)
        """

        return super().dump()

    def load(self, node_info):
        """
        Loads an Ethernet hub representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        super().load(node_info)
        properties = node_info["properties"]
        name = properties.pop("name")

        # Ethernet hubs do not have an UUID before version 2.0
        node_id = properties.get("node_id", str(uuid.uuid4()))

        ports = []
        if "ports_mapping" in node_info:
            ports = [{"port_number": port["port_number"], "name": port["name"]} for port in node_info["ports_mapping"]]

        log.info("Ethernet hub {} is loading".format(name))
        self.create(name, node_id, ports)

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
    def symbolName():

        return "Ethernet hub"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.switches]

    def __str__(self):

        return "Ethernet hub"
