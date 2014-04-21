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
Dynamips bridge implementation  on the client side (in the form of a hub).
Asynchronously sends JSON messages to the GNS3 server and receives responses with callbacks.
"""

from gns3.node import Node
from gns3.ports.ethernet_port import EthernetPort

import logging
log = logging.getLogger(__name__)


class EthernetHub(Node):
    """
    Dynamips Ethernet hub.

    :param module: parent module for this node
    :param server: GNS3 server instance
    """

    def __init__(self, module, server):
        Node.__init__(self, server)

        log.info("Ethernet hub is being created")
        self.setStatus(Node.started)  # this is an always-on node
        self._ethhub_id = None
        self._module = module
        self._ports = []
        self._settings = {"name": "",
                          "ports": []}

    def setup(self, name=None, initial_settings={}):
        """
        Setups this hub.

        :param name: optional name for this hub
        """

        params = {}
        if name:
            params["name"] = self._settings["name"] = name

        self._server.send_message("dynamips.ethhub.create", params, self._setupCallback)

    def _setupCallback(self, result, error=False):
        """
        Callback for setup.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while setting up {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.id(), result["code"], result["message"])
            return

        self._ethhub_id = result["id"]
        if not self._ethhub_id:
            log.error("returned ID from server is null")
        self._settings["name"] = result["name"]

        log.info("Ethernet hub {} has been created".format(self.name()))
        self.setInitialized(True)
        self.created_signal.emit(self.id())
        self._module.addNode(self)

    def delete(self):
        """
        Deletes this Ethernet hub.
        """

        log.debug("Ethernet hub {} is being deleted".format(self.name()))
        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        if self._ethhub_id:
            self._server.send_message("dynamips.ethhub.delete", {"id": self._ethhub_id}, self._deleteCallback)
        else:
            self.deleted_signal.emit()
            self._module.removeNode(self)

    def _deleteCallback(self, result, error=False):
        """
        Callback for delete.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.id(), result["code"], result["message"])
        log.info("{} has been deleted".format(self.name()))
        self.deleted_signal.emit()
        self._module.removeNode(self)

    def update(self, new_settings):
        """
        Updates the settings for this Ethernet hub.

        :param new_settings: settings dictionary
        """

        ports_to_create = []
        ports = new_settings["ports"]

        updated = False
        for port_number in ports:
            if port_number not in ports_to_create:
                ports_to_create.append(port_number)

        for port in self._ports.copy():
            if port.isFree():
                self._ports.remove(port)
                updated = True
                log.debug("port {} has been removed".format(port.name()))
            else:
                ports_to_create.remove(port.name())

        for port_name in ports_to_create:
            port = EthernetPort(port_name)
            port.setPortNumber(int(port_name))
            port.setStatus(EthernetPort.started)
            self._ports.append(port)
            updated = True
            log.debug("port {} has been added".format(port_name))

        params = {}
        if "name" in new_settings and new_settings["name"] != self.name():
            params = {"id": self._ethhub_id,
                      "name": new_settings["name"]}
            updated = True

        self._settings["ports"] = new_settings["ports"].copy()
        if updated:
            if params:
                log.debug("{} is being updated: {}".format(self.name(), params))
                self._server.send_message("dynamips.ethhub.update", params, self._updateCallback)
            else:
                log.info("{} has been updated".format(self.name()))
                self.updated_signal.emit()

    def _updateCallback(self, result, error=False):
        """
        Callback for update.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while updating {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.id(), result["code"], result["message"])
        else:
            if "name" in result:
                self._settings["name"] = result["name"]
            log.info("{} has been updated".format(self.name()))
            self.updated_signal.emit()

    def allocateUDPPort(self, port_id):
        """
        Requests an UDP port allocation.

        :param port_id: port identifier
        """

        log.debug("{} is requesting an UDP port allocation".format(self.name()))
        self._server.send_message("dynamips.ethhub.allocate_udp_port", {"id": self._ethhub_id, "port_id": port_id}, self._allocateUDPPortCallback)

    def _allocateUDPPortCallback(self, result, error=False):
        """
        Callback for allocateUDPPort.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while allocating an UDP port for {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.id(), result["code"], result["message"])
        else:
            port_id = result["port_id"]
            lport = result["lport"]
            log.debug("{} has allocated UDP port {}".format(self.name(), port_id, lport))
            self.allocate_udp_nio_signal.emit(self.id(), port_id, lport)

    def addNIO(self, port, nio):
        """
        Adds a new NIO on the specified port for this hub.

        :param port: Port instance
        :param nio: NIO instance
        """

        nio_type = str(nio)
        params = {"id": self._ethhub_id,
                  "nio": nio_type,
                  "port": port.portNumber(),
                  "port_id": port.id()}

        self.addNIOInfo(nio, params)
        log.debug("{} is adding an {}: {}".format(self.name(), nio_type, params))
        self._server.send_message("dynamips.ethhub.add_nio", params, self._addNIOCallback)

    def _addNIOCallback(self, result, error=False):
        """
        Callback for addNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while adding an UDP NIO for {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.id(), result["code"], result["message"])
        else:
            self.nio_signal.emit(self.id(), result["port_id"])

    def deleteNIO(self, port):
        """
        Deletes an NIO from the specified port on this hub.

        :param port: Port instance
        """

        params = {"id": self._ethhub_id,
                  "port": port.portNumber()}

        log.debug("{} is deleting an NIO: {}".format(self.name(), params))
        self._server.send_message("dynamips.ethhub.delete_nio", params, self._deleteNIOCallback)

    def _deleteNIOCallback(self, result, error=False):
        """
        Callback for deleteNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting NIO {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.id(), result["code"], result["message"])
            return

        log.debug("{} has deleted a NIO: {}".format(self.name(), result))

    def info(self):
        """
        Returns information about this Ethernet hub.

        :returns: formated string
        """

        info = """Ethernet hub {name} is always-on
  Node ID is {id}, server's Ethernet hub ID is {ethhub_id}
  Hardware is Dynamips emulated simple Ethernet hub
  Hub's server runs on {host}:{port}
""".format(name=self.name(),
           id=self.id(),
           ethhub_id=self._ethhub_id,
           host=self._server.host,
           port=self._server.port)

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

        hub = {"id": self.id(),
               "type": self.__class__.__name__,
               "description": str(self),
               "properties": {"name": self.name()},
               "server_id": self._server.id(),
               }

        # add the ports
        if self._ports:
            ports = hub["ports"] = []
            for port in self._ports:
                ports.append(port.dump())

        return hub

    def load(self, node_info):
        """
        Loads an Ethernet hub representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        settings = node_info["properties"]
        name = settings.pop("name")

        # create the ports with the correct port numbers and IDs
        if "ports" in node_info:
            ports = node_info["ports"]
            for topology_port in ports:
                port = EthernetPort(topology_port["name"])
                port.setPortNumber(topology_port["port_number"])
                port.setStatus(EthernetPort.started)
                self._ports.append(port)
                self._settings["ports"].append(port.portNumber())

        log.info("Ethernet hub {} is loading".format(name))
        self.setup(name)

    def name(self):
        """
        Returns the name of this hub.

        :returns: name (string)
        """

        return self._settings["name"]

    def settings(self):
        """
        Returns all this hub settings.

        :returns: settings dictionary
        """

        return self._settings

    def ports(self):
        """
        Returns all the ports for this hub.

        :returns: list of Port instances
        """

        return self._ports

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node configurator.

        :returns: QWidget object
        """

        from ..pages.ethernet_hub_configuration_page import EthernetHubConfigurationPage
        return EthernetHubConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/hub.normal.svg"

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when this node is hovered.

        :returns: symbol path (or resource).
        """

        return ":/symbols/hub.selected.svg"

    @staticmethod
    def symbolName():

        return "Ethernet hub"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.switches]

    def __str__(self):

        return "Ethernet hub"
