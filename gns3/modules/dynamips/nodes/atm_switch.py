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
Dynamips ATMSW implementation on the client side.
Asynchronously sends JSON messages to the GNS3 server and receives responses with callbacks.
"""

from gns3.node import Node
from gns3.ports.serial_port import SerialPort

import logging
log = logging.getLogger(__name__)


class ATMSwitch(Node):
    """
    Dynamips ATM switch.

    :param module: parent module for this node
    :param server: GNS3 server instance
    """

    def __init__(self, module, server):
        Node.__init__(self, server)

        self._atmsw_id = None
        self._ports = []
        self._module = module
        self._settings = {"name": "",
                          "mappings": {}}

    def setup(self, name=None, initial_settings={}):
        """
        Setups this ATM switch.

        :param name: optional name for this switch.
        """

        params = {}
        if name:
            params["name"] = self._settings["name"] = name

        if "mappings" in initial_settings:
            self._settings["mappings"] = initial_settings["mappings"]
        self._server.send_message("dynamips.atmsw.create", params, self._setupCallback)

    def _setupCallback(self, result, error=False):
        """
        Callback for setup.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while setting up {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
            return

        self._atmsw_id = result["id"]
        self._settings["name"] = result["name"]

        log.info("ATM switch {} has been created".format(result["name"]))
        self.setInitialized(True)
        self.created_signal.emit(self.id())

    def delete(self):
        """
        Deletes this ATM switch.
        """

        log.debug("ATM switch {} is being deleted".format(self.name()))
        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        if self._atmsw_id:
            self._server.send_message("dynamips.atmsw.delete", {"id": self._atmsw_id}, self._deleteCallback)
        else:
            self.delete_signal.emit()

    def _deleteCallback(self, result, error=False):
        """
        Callback for delete.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            log.info("ATM switch {} has been deleted".format(self.name()))
            self.delete_signal.emit()

    def update(self, new_settings):
        """
        Updates the settings for this ATM switch.

        :param new_settings: settings dictionary
        """

        ports_to_create = []
        mapping = new_settings["mappings"]

        updated = False
        for source, destination in mapping.items():
            source_port = source.split(":")[0]
            destination_port = destination.split(":")[0]
            if source_port not in ports_to_create:
                ports_to_create.append(source_port)
            if destination_port not in ports_to_create:
                ports_to_create.append(destination_port)

        for port in self._ports.copy():
            if port.isFree():
                updated = True
                self._ports.remove(port)
            else:
                ports_to_create.remove(port.name())

        for port_name in ports_to_create:
            port = SerialPort(port_name)
            port.setPortNumber(int(port_name))
            self._ports.append(port)
            updated = True
            log.debug("port {} has been added".format(port_name))

        self._settings["mappings"] = new_settings["mappings"].copy()
        if updated:
            self.updated_signal.emit()

    def allocateUDPPort(self, port_id):
        """
        Requests an UDP port allocation.

        :param port_id: port identifier
        """

        log.debug("{} is requesting an UDP port allocation".format(self.name()))
        self._server.send_message("dynamips.atmsw.allocate_udp_port", {"id": self._atmsw_id, "port_id": port_id}, self._allocateUDPPortCallback)

    def _allocateUDPPortCallback(self, result, error=False):
        """
        Callback for allocateUDPPort.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while allocating an UDP port for {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            port_id = result["port_id"]
            lhost = result["lhost"]
            lport = result["lport"]
            log.debug("{} has allocated UDP port {} for host {}".format(self.name(), lport, lhost))
            self.allocate_udp_nio_signal.emit(self.id(), port_id, lport, lhost)

    def addNIO(self, port, nio):
        """
        Adds a new NIO on the specified port for this ATM switch.

        :param port: Port instance
        :param nio: NIO instance
        """

        nio_type = str(nio)
        params = {"id": self._atmsw_id,
                  "nio": nio_type,
                  "port": port.portNumber(),
                  "port_id": port.id()}

        self.addNIOInfo(nio, params)
        params["mappings"] = {}
        for source, destination in self._settings["mappings"].items():
            source_port = source.split(":")[0]
            destination_port = destination.split(":")[0]
            if port.name() == source_port:
                params["mappings"][source] = destination
            if port.name() == destination_port:
                params["mappings"][destination] = source

        log.debug("{} is adding an {}: {}".format(self.name(), nio_type, params))
        self._server.send_message("dynamips.atmsw.add_nio", params, self._addNIOCallback)

    def _addNIOCallback(self, result, error=False):
        """
        Callback for addNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while adding an UDP NIO for {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            log.debug("{} has added a new NIO: {}".format(self.name(), result))
            self.nio_signal.emit(self.id(), result["port_id"])

    def deleteNIO(self, port):
        """
        Deletes an NIO from the specified port on this switch.

        :param port: Port instance
        """

        params = {"id": self._atmsw_id,
                  "port": port.portNumber()}

        log.debug("{} is deleting an NIO: {}".format(self.name(), params))
        self._server.send_message("dynamips.atmsw.delete_nio", params, self.deleteNIOCallback)

    def deleteNIOCallback(self, result, error=False):
        """
        Callback for deleteNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting NIO {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
            return

        log.debug("{} has deleted a NIO: {}".format(self.name(), result))

    def info(self):
        """
        Returns information about this ATM switch.

        :returns: formated string
        """

        return ""

    def dump(self):
        """
        Returns a representation of this ATM switch
        (to be saved in a topology file).

        :returns: dictionary
        """

        atmsw = {"id": self.id(),
                 "type": self.__class__.__name__,
                 "description": str(self),
                 "properties": {"name": self.name()},
                 "server_id": self._server.id(),
                }

        if self._settings["mappings"]:
            atmsw["properties"]["mappings"] = self._settings["mappings"]

        # add the ports
        if self._ports:
            ports = atmsw["ports"] = []
            for port in self._ports:
                ports.append(port.dump())

        return atmsw

    def load(self, node_info):
        """
        Loads an ATM switch representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        settings = node_info["properties"]
        name = settings.pop("name")

        # create the ports with the correct port numbers and IDs
        if "ports" in node_info:
            ports = node_info["ports"]
            for topology_port in ports:
                port = SerialPort(topology_port["name"])
                port.setPortNumber(topology_port["port_number"])
                self._ports.append(port)
                self._settings["ports"].append(port.portNumber())

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

        from ..pages.atm_switch_configuration_page import ATMSwitchConfigurationPage
        return ATMSwitchConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/atm_switch.normal.svg"

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when this node is hovered.

        :returns: symbol path (or resource).
        """

        return ":/symbols/atm_switch.selected.svg"

    @staticmethod
    def symbolName():

        return "ATM switch"

    def __str__(self):

        return "ATM switch"
