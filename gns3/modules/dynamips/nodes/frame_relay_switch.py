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
from gns3.ports.frame_relay_port import FrameRelayPort
from .device import Device

import logging
log = logging.getLogger(__name__)


class FrameRelaySwitch(Device):

    """
    Dynamips Frame-Relay switch.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        self.setStatus(Node.started)  # this is an always-on node
        self._ports = []
        self._settings = {"name": "",
                          "mappings": {}}

    def setup(self, name=None, device_id=None, initial_ports=[], initial_mappings={}):
        """
        Setups this Frame Relay switch.

        :param name: name for this switch.
        :param device_id: device identifier on the server
        :param initial_ports: ports to be automatically added when creating this Frame relay switch
        :param initial_mappings: mappings to be automatically added when creating this Frame relay switch
        """

        # let's create a unique name if none has been chosen
        if not name:
            name = self.allocateName("FR")

        if not name:
            self.error_signal.emit(self.id(), "could not allocate a name for this Frame Relay switch")
            return

        self._settings["name"] = name
        if initial_mappings:
            # add initial mappings
            self._settings["mappings"] = initial_mappings.copy()

        # add initial ports
        for initial_port in initial_ports:
            port = FrameRelayPort(initial_port["name"])
            port.setPortNumber(initial_port["port_number"])
            if "id" in initial_port:
                port.setId(initial_port["id"])
            port.setStatus(FrameRelayPort.started)
            port.setPacketCaptureSupported(True)
            self._ports.append(port)

        params = {"name": name,
                  "device_type": "frame_relay_switch"}
        if device_id:
            params["device_id"] = device_id
        self.httpPost("/dynamips/devices", self._setupCallback, body=params)

    def update(self, new_settings):
        """
        Updates the settings for this Frame Relay switch.

        :param new_settings: settings dictionary
        """

        updated = False
        if "mappings" in new_settings:
            ports_to_create = []
            mapping = new_settings["mappings"]

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
                port = FrameRelayPort(port_name)
                port.setPortNumber(int(port_name))
                port.setStatus(FrameRelayPort.started)
                port.setPacketCaptureSupported(True)
                self._ports.append(port)
                updated = True
                log.debug("port {} has been added".format(port_name))

            self._settings["mappings"] = new_settings["mappings"].copy()

        params = {}
        if "name" in new_settings and new_settings["name"] != self.name():
            if self.hasAllocatedName(new_settings["name"]):
                self.error_signal.emit(self.id(), 'Name "{}" is already used by another node'.format(new_settings["name"]))
                return
            params["name"] = new_settings["name"]
            updated = True

        if updated:
            if params:
                log.debug("{} is being updated: {}".format(self.name(), params))
                self.httpPut("/dynamips/devices/{device_id}".format(device_id=self._device_id), self._updateCallback, body=params)
            else:
                log.info("{} has been updated".format(self.name()))
                self.updated_signal.emit()

    def _updateCallback(self, result, error=False, **kwargs):
        """
        Callback for update.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while updating {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            if "name" in result:
                self._settings["name"] = result["name"]
                self.updateAllocatedName(result["name"])
            log.info("{} has been updated".format(self.name()))
            self.updated_signal.emit()

    def addNIO(self, port, nio):
        """
        Adds a new NIO on the specified port for this Frame Relay switch.

        :param port: Port instance
        :param nio: NIO instance
        """

        params = {"nio": self.getNIOInfo(nio)}
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
        self.httpPost("/{prefix}/devices/{device_id}/ports/{port}/nio".format(
            port=port.portNumber(),
            prefix=self.URL_PREFIX,
            device_id=self._device_id),
            self._addNIOCallback,
            context={"port_id": port.id()},
            body=params)

    def info(self):
        """
        Returns information about this Frame Relay switch.

        :returns: formated string
        """

        info = """Frame relay switch {name} is always-on
  Local node ID is {id}
  Server's Device ID is {device_id}
  Hardware is Dynamips emulated simple Frame relay switch
  Switch's server runs on {host}:{port}
""".format(name=self.name(),
           id=self.id(),
           device_id=self._device_id,
           host=self._server.host(),
           port=self._server.port())

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
                "device_id": self._device_id,
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

        # pre-1.3 projects have no device id, set to 1 to have
        # a proper project conversion on the server side
        device_id = node_info.get("device_id", 1)

        mappings = {}
        if "mappings" in settings:
            mappings = settings["mappings"]

        ports = []
        if "ports" in node_info:
            ports = node_info["ports"]

        log.info("Frame-Relay switch {} is loading".format(name))
        self.setName(name)
        self.setup(name, device_id, ports, mappings)

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
        Returns the configuration page widget to be used by the node properties dialog.

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

        return ":/symbols/frame_relay_switch.svg"

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
