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

    def setup(self, name=None, initial_ports=[]):
        """
        Setups this Ethernet switch.

        :param name: optional name for this switch
        :param initial_ports: ports to be automatically added when creating this switch
        """

        # let's create a unique name if none has been chosen
        if not name:
            name = self.allocateName("SW")

        if not name:
            self.error_signal.emit(self.id(), "could not allocate a name for this Ethernet switch")
            return

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
                                                          "vlan": initial_port["vlan"]}

        params = {"name": name}
        self._server.send_message("dynamips.ethsw.create", params, self._setupCallback)

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

        self._ethsw_id = result["id"]
        if not self._ethsw_id:
            self.error_signal.emit(self.id(), "returned ID from server is null")
            return

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
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        log.info("Ethernet switch {} has been deleted".format(self.name()))
        self.deleted_signal.emit()
        self._module.removeNode(self)

    def update(self, new_settings):
        """
        Updates the settings for this Ethernet switch.

        :param new_settings: settings dictionary
        """

        updated = False
        params = {"id": self._ethsw_id}
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
                params["ports"] = {}
                for port_number, info in ports_to_update.items():
                    params["ports"][port_number] = info
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
            self._server.send_message("dynamips.ethsw.update", params, self._updateCallback)

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
                self.updateAllocatedName(result["name"])
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
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
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
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
            self.nio_cancel_signal.emit(self.id())
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
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
            return

        log.debug("{} has deleted a NIO: {}".format(self.name(), result))

    def startPacketCapture(self, port, capture_file_name, data_link_type):
        """
        Starts a packet capture.

        :param port: Port instance
        :param capture_file_name: PCAP capture file path
        :param data_link_type: PCAP data link type
        """

        params = {"id": self._ethsw_id,
                  "port_id": port.id(),
                  "port": port.portNumber(),
                  "capture_file_name": capture_file_name,
                  "data_link_type": data_link_type}

        log.debug("{} is starting a packet capture on {}: {}".format(self.name(), port.name(), params))
        self._server.send_message("dynamips.ethsw.start_capture", params, self._startPacketCaptureCallback)

    def _startPacketCaptureCallback(self, result, error=False):
        """
        Callback for starting a packet capture.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while starting capture {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:
            for port in self._ports:
                if port.id() == result["port_id"]:
                    log.info("{} has successfully started capturing packets on {}".format(self.name(), port.name()))
                    try:
                        port.startPacketCapture(result["capture_file_path"])
                    except OSError as e:
                        self.error_signal.emit(self.id(), "could not start the packet capture reader: {}: {}".format(e, e.filename))
                    self.updated_signal.emit()
                    break

    def stopPacketCapture(self, port):
        """
        Stops a packet capture.

        :param port: Port instance
        """

        params = {"id": self._ethsw_id,
                  "port_id": port.id(),
                  "port": port.portNumber()}

        log.debug("{} is stopping a packet capture on {}: {}".format(self.name(), port.name(), params))
        self._server.send_message("dynamips.ethsw.stop_capture", params, self._stopPacketCaptureCallback)

    def _stopPacketCaptureCallback(self, result, error=False):
        """
        Callback for stopping a packet capture.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while stopping capture {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:
            for port in self._ports:
                if port.id() == result["port_id"]:
                    log.info("{} has successfully stopped capturing packets on {}".format(self.name(), port.name()))
                    port.stopPacketCapture()
                    self.updated_signal.emit()
                    break

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

        ports = []
        if "ports" in node_info:
            ports = node_info["ports"]

        log.info("Ethernet switch {} is loading".format(name))
        self.setName(name)
        self.setup(name, ports)

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
