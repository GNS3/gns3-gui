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
Dynamips ETHSW implementation on the client side.
Asynchronously sends JSON messages to the GNS3 server and receives responses with callbacks.
"""

from gns3.node import Node
from gns3.ports.ethernet_port import EthernetPort

import logging
log = logging.getLogger(__name__)


class EthernetSwitch(Node):
    """
    Dynamips Ethernet switch.

    :param module: parent module for this node
    :param server: GNS3 server instance
    """

    def __init__(self, module, server):
        Node.__init__(self, server)

        log.info("Ethernet switch is being created")
        self.setStatus(Node.started)  # this is an always-on node
        self._ethsw_id = None
        self._module = module
        self._ports = []
        self._settings = {"name": "",
                          "ports": {}}

    def setup(self, name=None, initial_settings={}):
        """
        Setups this Ethernet switch.

        :param name: optional name for this switch
        """

        params = {}
        if name:
            params["name"] = self._settings["name"] = name

        self._server.send_message("dynamips.ethsw.create", params, self._setupCallback)

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

        self._ethsw_id = result["id"]
        if not self._ethsw_id:
            log.error("returned ID from server is null")
        self._settings["name"] = result["name"]

        log.info("Ethernet switch {} has been created".format(self.name()))
        self.setInitialized(True)
        self.created_signal.emit(self.id())
        self._module.addNode(self)

    def delete(self):
        """
        Deletes this Ethernet switch.
        """

        log.debug("Ethernet switch {} is being deleted".format(self.name()))
        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        if self._ethsw_id:
            self._server.send_message("dynamips.ethsw.delete", {"id": self._ethsw_id}, self._deleteCallback)
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
        log.info("Ethernet switch {} has been deleted".format(self.name()))
        self.deleted_signal.emit()
        self._module.removeNode(self)

    def update(self, new_settings):
        """
        Updates the settings for this Ethernet switch.

        :param new_settings: settings dictionary
        """

        ports_to_update = {}
        ports = new_settings["ports"]
        updated = False
        for port_number in ports.keys():
            if port_number in self._settings["ports"]:
                if self._settings["ports"][port_number] != ports[port_number]:
                    for port in self._ports:
                        if port.portNumber() == port_number and not port.isFree():
                            ports_to_update[port_number] = ports[port_number]
                            break
                continue
            port = EthernetPort(str(port_number))
            port.setPortNumber(port_number)
            port.setStatus(EthernetPort.started)
            self._ports.append(port)
            updated = True
            log.debug("port {} has been added".format(port_number))

        params = {"id": self._ethsw_id}
        if ports_to_update:
            params["ports"] = {}
            for port_number, info in ports_to_update.items():
                params["ports"][port_number] = info
            updated = True

        if "name" in new_settings and new_settings["name"] != self.name():
            params["name"] = new_settings["name"]
            updated = True

        self._settings["ports"] = new_settings["ports"].copy()
        if updated:
            log.debug("{} is being updated: {}".format(self.name(), params))
            self._server.send_message("dynamips.ethsw.update", params, self._updateCallback)

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
        self._server.send_message("dynamips.ethsw.allocate_udp_port", {"id": self._ethsw_id, "port_id": port_id}, self._allocateUDPPortCallback)

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
            log.debug("{} has allocated UDP port {}".format(self.name(), lport))
            self.allocate_udp_nio_signal.emit(self.id(), port_id, lport)

    def addNIO(self, port, nio):
        """
        Adds a new NIO on the specified port for this switch.

        :param port: Port instance
        :param nio: NIO instance
        """

        port_info = self._settings["ports"][port.portNumber()]
        params = {"id": self._ethsw_id,
                  "port": port.portNumber(),
                  "port_id": port.id(),
                  "vlan": port_info["vlan"],
                  "port_type": port_info["type"]}

        params["nio"] = self.getNIOInfo(nio)
        log.debug("{} is adding an {}: {}".format(self.name(), nio, params))
        self._server.send_message("dynamips.ethsw.add_nio", params, self._addNIOCallback)

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
            log.debug("{} has added a new NIO: {}".format(self.name(), result))
            self.nio_signal.emit(self.id(), result["port_id"])

    def deleteNIO(self, port):
        """
        Deletes an NIO from the specified port on this switch.

        :param port: Port instance
        """

        params = {"id": self._ethsw_id,
                  "port": port.portNumber()}

        log.debug("{} is deleting an NIO: {}".format(self.name(), params))
        self._server.send_message("dynamips.ethsw.delete_nio", params, self._deleteNIOCallback)

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
        Returns information about this Ethernet switch.

        :returns: formated string
        """

        info = """Ethernet switch {name} is always-on
  Node ID is {id}, server's Ethernet switch ID is {ethsw_id}
  Hardware is Dynamips emulated simple Ethernet switch
  Switch's server runs on {host}:{port}
""".format(name=self.name(),
           id=self.id(),
           ethsw_id=self._ethsw_id,
           host=self._server.host,
           port=self._server.port)

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "   Port {} is empty\n".format(port.name())
            else:
                port_type = self._settings["ports"][port.portNumber()]["type"]
                port_vlan = str(self._settings["ports"][port.portNumber()]["vlan"])
                if port_type == "access":
                    port_vlan_info = "VLAN ID {}".format(port_vlan)
                elif port_type == "dot1q":
                    port_vlan_info = "native VLAN {}".format(port_vlan)
                elif port_type == "qinq":
                    port_vlan_info = "outer VLAN {}".format(port_vlan)

                port_info += "   Port {name} is in {port_type} mode, with {port_vlan_info},\n".format(name=port.name(),
                                                                                                      port_type=port_type,
                                                                                                      port_vlan_info=port_vlan_info)
                port_info += "    {port_description}\n".format(port_description=port.description())

        return info + port_info

    def dump(self):
        """
        Returns a representation of this Ethernet switch
        (to be saved in a topology file)

        :returns: dictionary
        """

        switch = {"id": self.id(),
                  "type": self.__class__.__name__,
                  "description": str(self),
                  "properties": {"name": self.name()},
                  "server_id": self._server.id(),
                  }

        # add the ports
        if self._ports:
            ports = switch["ports"] = []
            for port in self._ports:
                port_info = port.dump()
                if port.portNumber() in self._settings["ports"]:
                    port_info["type"] = self._settings["ports"][port.portNumber()]["type"]
                    port_info["vlan"] = self._settings["ports"][port.portNumber()]["vlan"]
                ports.append(port_info)

        return switch

    def load(self, node_info):
        """
        Loads an Ethernet switch representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        settings = node_info["properties"]
        name = settings.pop("name")

        # create the ports with the correct port numbers, IDs and settings
        if "ports" in node_info:
            ports = node_info["ports"]
            for topology_port in ports:
                port = EthernetPort(topology_port["name"])
                port.setPortNumber(topology_port["port_number"])
                port.setId(topology_port["id"])
                port.setStatus(EthernetPort.started)
                self._ports.append(port)
                self._settings["ports"][port.portNumber()] = {"type": topology_port["type"],
                                                          "vlan": topology_port["vlan"]}

        log.info("Ethernet switch {} is loading".format(name))
        self.setup(name)

    def name(self):
        """
        Returns the name of this switch.

        :returns: name (string)
        """

        return self._settings["name"]

    def settings(self):
        """
        Returns all this switch settings.

        :returns: settings dictionary
        """

        return self._settings

    def ports(self):
        """
        Returns all the ports for this switch.

        :returns: list of Port instances
        """

        return self._ports

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node configurator.

        :returns: QWidget object
        """

        from ..pages.ethernet_switch_configuration_page import EthernetSwitchConfigurationPage
        return EthernetSwitchConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/ethernet_switch.normal.svg"

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when this node is hovered.

        :returns: symbol path (or resource).
        """

        return ":/symbols/ethernet_switch.selected.svg"

    @staticmethod
    def symbolName():

        return "Ethernet switch"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.switches]

    def __str__(self):

        return "Ethernet switch"
