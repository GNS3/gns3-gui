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
Dynamips FRSW implementation on the client side.
Asynchronously sends JSON messages to the GNS3 server and receives responses with callbacks.
"""

from gns3.node import Node
from gns3.ports.serial_port import SerialPort

import logging
log = logging.getLogger(__name__)


class FrameRelaySwitch(Node):
    """
    Dynamips Frame-Relay switch.

    :param module: parent module for this node
    :param server: GNS3 server instance
    """

    def __init__(self, module, server):
        Node.__init__(self, server)

        log.info("Frame-Relay switch is being created")
        self.setStatus(Node.started)  # this is an always-on node
        self._frsw_id = None
        self._ports = []
        self._module = module
        self._settings = {"name": "",
                          "mappings": {}}

    def setup(self, name=None, initial_settings={}):
        """
        Setups this Frame Relay switch.

        :param name: optional name for this switch.
        """

        params = {}
        if name:
            params["name"] = self._settings["name"] = name

        if "mappings" in initial_settings:
            self._settings["mappings"] = initial_settings["mappings"]
        self._server.send_message("dynamips.frsw.create", params, self._setupCallback)

    def _setupCallback(self, result, error=False):
        """
        Callback for setup.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while setting up {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
            return

        self._frsw_id = result["id"]
        if not self._frsw_id:
            log.error("returned ID from server is null")
        self._settings["name"] = result["name"]

        log.info("Frame Relay switch {} has been created".format(self.name()))
        self.setInitialized(True)
        self.created_signal.emit(self.id())
        self._module.addNode(self)

    def delete(self):
        """
        Deletes this Frame Relay switch.
        """

        log.debug("Frame Relay switch {} is being deleted".format(self.name()))
        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        if self._frsw_id:
            self._server.send_message("dynamips.frsw.delete", {"id": self._frsw_id}, self._deleteCallback)
        else:
            self.deleted_signal.emit()
            self._module.removeNode(self)

    def _deleteCallback(self, result, error=False):
        """
        Callback for the delete method.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        log.info("{} has been deleted".format(self.name()))
        self.deleted_signal.emit()
        self._module.removeNode(self)

    def update(self, new_settings):
        """
        Updates the settings for this Frame Relay switch.

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
                self._ports.remove(port)
                updated = True
                log.debug("port {} has been removed".format(port.name()))
            else:
                ports_to_create.remove(port.name())

        for port_name in ports_to_create:
            port = SerialPort(port_name)
            port.setPortNumber(int(port_name))
            port.setStatus(SerialPort.started)
            self._ports.append(port)
            updated = True
            log.debug("port {} has been added".format(port_name))

        params = {}
        if "name" in new_settings and new_settings["name"] != self.name():
            params = {"id": self._frsw_id,
                      "name": new_settings["name"]}
            updated = True

        self._settings["mappings"] = new_settings["mappings"].copy()
        if updated:
            if params:
                log.debug("{} is being updated: {}".format(self.name(), params))
                self._server.send_message("dynamips.frsw.update", params, self._updateCallback)
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
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:
            if "name" in result:
                self._settings["name"] = result["name"]
            log.info("{} has been updated".format(self.name()))
            self.updated_signal.emit()

    def allocateUDPPort(self, port_id):
        """
        Requests an UDP port allocation.
        """

        log.debug("{} is requesting an UDP port allocation".format(self.name()))
        self._server.send_message("dynamips.frsw.allocate_udp_port", {"id": self._frsw_id, "port_id": port_id}, self._allocateUDPPortCallback)

    def _allocateUDPPortCallback(self, result, error=False):
        """
        Callback for allocateUDPPort.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while allocating an UDP port for {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:
            port_id = result["port_id"]
            lport = result["lport"]
            log.debug("{} has allocated UDP port {}".format(self.name(), lport))
            self.allocate_udp_nio_signal.emit(self.id(), port_id, lport)

    def addNIO(self, port, nio):
        """
        Adds a new NIO on the specified port for this Frame Relay switch.

        :param port: Port instance
        :param nio: NIO instance
        """

        params = {"id": self._frsw_id,
                  "port": port.portNumber(),
                  "port_id": port.id()}

        params["nio"] = self.getNIOInfo(nio)
        params["mappings"] = {}
        for source, destination in self._settings["mappings"].items():
            source_port = source.split(":")[0]
            destination_port = destination.split(":")[0]
            if port.name() == source_port:
                params["mappings"][source] = destination
            if port.name() == destination_port:
                params["mappings"][destination] = source
            log.debug("{} is adding an UDP NIO: {}".format(self.name(), params))

        log.debug("{} is adding an {}: {}".format(self.name(), nio, params))
        self._server.send_message("dynamips.frsw.add_nio", params, self._addNIOCallback)

    def _addNIOCallback(self, result, error=False):
        """
        Callback for addNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while adding an UDP NIO for {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:
            log.debug("{} has added a new NIO: {}".format(self.name(), result))
            self.nio_signal.emit(self.id(), result["port_id"])

    def deleteNIO(self, port):
        """
        Deletes an NIO from the specified port on this switch.

        :param port: Port instance
        """

        params = {"id": self._frsw_id,
                  "port": port.portNumber()}

        log.debug("{} is deleting an NIO: {}".format(self.name(), params))
        self._server.send_message("dynamips.frsw.delete_nio", params, self._deleteNIOCallback)

    def _deleteNIOCallback(self, result, error=False):
        """
        Callback for deleteNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting NIO {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
            return

        log.debug("{} has deleted a NIO: {}".format(self.name(), result))

    def info(self):
        """
        Returns information about this Frame Relay switch.

        :returns: formated string
        """

        info = """Frame relay switch {name} is always-on
  Node ID is {id}, server's frame relay switch ID is {frsw_id}
  Hardware is Dynamips emulated simple Frame relay switch
  Switch's server runs on {host}:{port}
""".format(name=self.name(),
           id=self.id(),
           frsw_id=self._frsw_id,
           host=self._server.host,
           port=self._server.port)

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "   Port {} is empty\n".format(port.name())
            else:
                port_info += "   Port {name} {description}\n".format(name=port.name(),
                                                                      description=port.description())

            for source, destination in self._settings["mappings"].items():
                source_port, source_dlci = source.split(":")
                destination_port, destination_dlci = destination.split(":")

                if port.name() == source_port or port.name() == destination_port:
                    if port.name() == source_port:
                        dlci1 = source_dlci
                        port = destination_port
                        dlci2 = destination_dlci
                    else:
                        dlci1 = destination_dlci
                        port = source_port
                        dlci2 = source_dlci
                    port_info += "      incoming DLCI {dlci1} is switched to port {port} outgoing DLCI {dlci2}\n".format(dlci1=dlci1,
                                                                                                                         port=port,
                                                                                                                         dlci2=dlci2)
                    break

        return info + port_info

    def dump(self):
        """
        Returns a representation of this Frame Relay switch
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """

        frsw = {"id": self.id(),
                "type": self.__class__.__name__,
                "description": str(self),
                "properties": {"name": self.name()},
                "server_id": self._server.id(),
                }

        if self._settings["mappings"]:
            frsw["properties"]["mappings"] = self._settings["mappings"]

        # add the ports
        if self._ports:
            ports = frsw["ports"] = []
            for port in self._ports:
                ports.append(port.dump())

        return frsw

    def load(self, node_info):
        """
        Loads a Frame Relay switch representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        settings = node_info["properties"]
        name = settings.pop("name")

        # restore mappings
        if "mappings" in settings:
            self._settings["mappings"] = settings["mappings"].copy()

        # create the ports with the correct port numbers and IDs
        if "ports" in node_info:
            ports = node_info["ports"]
            for topology_port in ports:
                port = SerialPort(topology_port["name"])
                port.setPortNumber(topology_port["port_number"])
                port.setId(topology_port["id"])
                port.setStatus(SerialPort.started)
                self._ports.append(port)

        log.info("Frame-Relay switch {} is loading".format(name))
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

        from ..pages.frame_relay_switch_configuration_page import FrameRelaySwitchConfigurationPage
        return FrameRelaySwitchConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/frame_relay_switch.normal.svg"

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when this node is hovered.

        :returns: symbol path (or resource).
        """

        return ":/symbols/frame_relay_switch.selected.svg"

    @staticmethod
    def symbolName():

        return "Frame Relay switch"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.switches]

    def __str__(self):

        return "Frame Relay switch"
