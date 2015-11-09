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
from .device import Device

import logging
log = logging.getLogger(__name__)


class EthernetSwitch(Device):

    """
    Dynamips Ethernet switch.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        self.setStatus(Node.started)  # this is an always-on node
        self._ports = []
        self._settings = {"name": "",
                          "ports": {}}

    def setup(self, name=None, device_id=None, initial_ports=[]):
        """
        Setups this Ethernet switch.

        :param name: optional name for this switch
        :param device_id: device identifier on the server
        :param initial_ports: ports to be automatically added when creating this switch
        """

        # let's create a unique name if none has been chosen
        if not name:
            name = self.allocateName("SW")

        if not name:
            self.error_signal.emit(self.id(), "could not allocate a name for this Ethernet switch")
            return

        self._settings["name"] = name
        if not initial_ports:
            # default configuration if no initial ports
            for port_number in range(1, 9):
                # add 8 ports
                initial_ports.append({"name": str(port_number),
                                      "port_number": port_number,
                                      "type": "access",
                                      "vlan": 1})

        # add initial ports
        for initial_port in initial_ports:
            port = EthernetPort(initial_port["name"])
            port.setPortNumber(initial_port["port_number"])
            if "id" in initial_port:
                port.setId(initial_port["id"])
            port.setStatus(EthernetPort.started)
            port.setPacketCaptureSupported(True)
            self._ports.append(port)
            self._settings["ports"][port.portNumber()] = {"type": initial_port["type"],
                                                          "vlan": initial_port["vlan"],
                                                          "ethertype": initial_port.get("ethertype", "")}

        params = {"name": name,
                  "device_type": "ethernet_switch"}
        if device_id:
            params["device_id"] = device_id
        self.httpPost("/dynamips/devices", self._setupCallback, body=params)

    def update(self, new_settings):
        """
        Updates the settings for this Ethernet switch.

        :param new_settings: settings dictionary
        """

        updated = False
        params = {}
        if "ports" in new_settings:
            ports_to_update = {}
            ports = new_settings["ports"]

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
                port.setPacketCaptureSupported(True)
                self._ports.append(port)
                updated = True
                log.debug("port {} has been added".format(port_number))

            if ports_to_update:
                params["ports"] = []
                for port_number, info in ports_to_update.items():
                    info["port"] = port_number
                    params["ports"].append(info)
                updated = True

            # delete ports that are not configured
            for port_number in self._settings["ports"].keys():
                if port_number not in new_settings["ports"]:
                    for port in self._ports.copy():
                        if port.portNumber() == port_number:
                            self._ports.remove(port)
                            log.debug("port {} has been removed".format(port.name()))
                            break

            self._settings["ports"] = new_settings["ports"].copy()

        if "name" in new_settings and new_settings["name"] != self.name():
            if self.hasAllocatedName(new_settings["name"]):
                self.error_signal.emit(self.id(), 'Name "{}" is already used by another node'.format(new_settings["name"]))
                return
            params["name"] = new_settings["name"]
            updated = True

        if updated:
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
        Adds a new NIO on the specified port for this switch.

        :param port: Port instance
        :param nio: NIO instance
        """

        params = {}
        params["nio"] = self.getNIOInfo(nio)
        port_info = self._settings["ports"][port.portNumber()]
        port_settings = {"vlan": port_info["vlan"],
                         "type": port_info["type"],
                         "ethertype": port_info["ethertype"]}
        params["port_settings"] = port_settings
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
        Returns information about this Ethernet switch.

        :returns: formated string
        """

        info = """Ethernet switch {name} is always-on
  Local node ID is {id}
  Server's Device ID is {device_id}
  Hardware is Dynamips emulated simple Ethernet switch
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
                port_type = self._settings["ports"][port.portNumber()]["type"]
                port_ethertype = self._settings["ports"][port.portNumber()]["ethertype"]
                port_vlan = str(self._settings["ports"][port.portNumber()]["vlan"])
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

        return info + port_info

    def dump(self):
        """
        Returns a representation of this Ethernet switch
        (to be saved in a topology file)

        :returns: dictionary
        """

        switch = {"id": self.id(),
                  "device_id": self._device_id,
                  "type": self.__class__.__name__,
                  "description": str(self),
                  "properties": {"name": self.name()},
                  "server_id": self._server.id()}

        # add the ports
        if self._ports:
            ports = switch["ports"] = []
            for port in self._ports:
                port_info = port.dump()
                if port.portNumber() in self._settings["ports"]:
                    port_info["type"] = self._settings["ports"][port.portNumber()]["type"]
                    if port_info["type"] == "qinq" and "ethertype" != "0x8100":
                        port_info["ethertype"] = self._settings["ports"][port.portNumber()]["ethertype"]
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

        # pre-1.3 projects have no device id, set to 1 to have
        # a proper project conversion on the server side
        device_id = node_info.get("device_id", 1)

        ports = []
        if "ports" in node_info:
            ports = node_info["ports"]

        log.info("Ethernet switch {} is loading".format(name))
        self.setName(name)
        self.setup(name, device_id, ports)

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

        from ..pages.ethernet_switch_configuration_page import EthernetSwitchConfigurationPage
        return EthernetSwitchConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/ethernet_switch.svg"

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
