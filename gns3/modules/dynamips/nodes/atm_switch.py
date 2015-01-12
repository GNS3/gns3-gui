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

import re
from gns3.node import Node
from gns3.ports.atm_port import ATMPort

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

        log.info("ATM switch is being created")
        self.setStatus(Node.started)  # this is an always-on node
        self._atmsw_id = None
        self._ports = []
        self._module = module
        self._settings = {"name": "",
                          "mappings": {}}

    def setup(self, name=None, initial_ports=[], initial_mappings={}):
        """
        Setups this ATM switch.

        :param name: optional name for this switch.
        :param initial_ports: ports to be automatically added when creating this ATM switch
        :param initial_mappings: mappings to be automatically added when creating this ATM switch
        """

        # let's create a unique name if none has been chosen
        if not name:
            name = self.allocateName("ATM")

        if not name:
            self.error_signal.emit(self.id(), "could not allocate a name for this ATM switch")
            return

        if initial_mappings:
            # add initial mappings
            self._settings["mappings"] = initial_mappings.copy()

        # add initial ports
        for initial_port in initial_ports:
            port = ATMPort(initial_port["name"])
            port.setPortNumber(initial_port["port_number"])
            if "id" in initial_port:
                port.setId(initial_port["id"])
            port.setStatus(ATMPort.started)
            port.setPacketCaptureSupported(True)
            self._ports.append(port)

        params = {"name": name}
        self._server.send_message("dynamips.atmsw.create", params, self._setupCallback)

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

        self._atmsw_id = result["id"]
        if not self._atmsw_id:
            self.error_signal.emit(self.id(), "returned ID from server is null")
            return

        self._settings["name"] = result["name"]
        log.info("ATM switch {} has been created".format(self.name()))
        self.setInitialized(True)
        self.created_signal.emit(self.id())
        self._module.addNode(self)

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
        log.info("ATM switch {} has been deleted".format(self.name()))
        self.deleted_signal.emit()
        self._module.removeNode(self)

    def update(self, new_settings):
        """
        Updates the settings for this ATM switch.

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
                    updated = True
                    self._ports.remove(port)
                else:
                    ports_to_create.remove(port.name())

            for port_name in ports_to_create:
                port = ATMPort(port_name)
                port.setPortNumber(int(port_name))
                port.setStatus(ATMPort.started)
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
            params = {"id": self._atmsw_id,
                      "name": new_settings["name"]}
            updated = True

        if updated:
            if params:
                log.debug("{} is being updated: {}".format(self.name(), params))
                self._server.send_message("dynamips.atmsw.update", params, self._updateCallback)
            else:
                log.info("ATM switch {} has been updated".format(self.name()))
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
                self.updateAllocatedName(result["name"])
            log.info("{} has been updated".format(self.name()))
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
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:
            port_id = result["port_id"]
            lport = result["lport"]
            log.debug("{} has allocated UDP port {}".format(self.name(), lport))
            self.allocate_udp_nio_signal.emit(self.id(), port_id, lport)

    def addNIO(self, port, nio):
        """
        Adds a new NIO on the specified port for this ATM switch.

        :param port: Port instance
        :param nio: NIO instance
        """

        params = {"id": self._atmsw_id,
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

        log.debug("{} is adding an {}: {}".format(self.name(), nio, params))
        self._server.send_message("dynamips.atmsw.add_nio", params, self._addNIOCallback)

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

        params = {"id": self._atmsw_id,
                  "port_id": port.id(),
                  "port": port.portNumber(),
                  "capture_file_name": capture_file_name,
                  "data_link_type": data_link_type}

        log.debug("{} is starting a packet capture on {}: {}".format(self.name(), port.name(), params))
        self._server.send_message("dynamips.atmsw.start_capture", params, self._startPacketCaptureCallback)

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

        params = {"id": self._atmsw_id,
                  "port_id": port.id(),
                  "port": port.portNumber()}

        log.debug("{} is stopping a packet capture on {}: {}".format(self.name(), port.name(), params))
        self._server.send_message("dynamips.atmsw.stop_capture", params, self._stopPacketCaptureCallback)

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
        Returns information about this ATM switch.

        :returns: formated string
        """

        info = """ATM switch {name} is always-on
  Node ID is {id}, server's ATM switch ID is {atmsw_id}
  Hardware is Dynamips emulated simple ATM switch
  Switch's server runs on {host}:{port}
""".format(name=self.name(),
           id=self.id(),
           atmsw_id=self._atmsw_id,
           host=self._server.host,
           port=self._server.port)

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

        mappings = {}
        if "mappings" in settings:
            mappings = settings["mappings"]

        ports = []
        if "ports" in node_info:
            ports = node_info["ports"]

        log.info("ATM switch {} is loading".format(name))
        self.setName(name)
        self.setup(name, ports, mappings)

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

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.switches]

    def __str__(self):

        return "ATM switch"
