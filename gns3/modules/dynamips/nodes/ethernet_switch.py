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

    :param server: GNS3 server instance
    """

    def __init__(self, server):
        Node.__init__(self)

        self._server = server
        self._ethsw_id = None
        self._ports = []
        self._settings = {"name": "",
                          "ports": {}}

    def setup(self, name=None):
        """
        Setups this Ethernet switch.

        :param name: optional name for this switch
        """

        self._server.send_message("dynamips.ethsw.create", None, self._setupCallback)

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

        self._ethsw_id = result["id"]
        self._settings["name"] = result["name"]

        log.info("Ethernet switch {} has been created".format(result["name"]))
        # let the GUI knows about this switch name
        self.newname_signal.emit(self._settings["name"])

    def delete(self):
        """
        Deletes this Ethernet switch.
        """

        log.debug("Ethernet switch {} is being deleted".format(self.name()))
        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        self._server.send_message("dynamips.ethsw.delete", {"id": self._ethsw_id}, self._deleteCallback)

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
            log.info("Ethernet switch {} has been deleted".format(self.name()))
            self.delete_signal.emit()

    def update(self, new_settings):
        """
        Updates the settings for this Ethernet switch.

        :param new_settings: settings dictionary
        """

        ports_to_update = {}
        ports = new_settings["ports"]
        for port_id in ports.keys():
            if port_id in self._settings["ports"]:
                if self._settings["ports"][port_id] != ports[port_id]:
                    print("Port {} has been updated".format(port_id))
                    for port in self._ports:
                        if port.port == port_id and not port.isFree():
                            ports_to_update[port_id] = ports[port_id]
                            break
                continue
            port = EthernetPort(str(port_id))
            port.port = port_id
            self._ports.append(port)
            log.debug("port {} has been added".format(port_id))

        if ports_to_update:
            params = {"id": self._ethsw_id,
                      "ports": {}}
            for port_id, info in ports_to_update.items():
                params["ports"][port_id] = info
            log.debug("{} is being updated: {}".format(self.name(), params))
            self._server.send_message("dynamips.ethsw.update", params, self._updateCallback)

        self._settings["ports"] = new_settings["ports"].copy()

    def _updateCallback(self, result, error=False):
        """
        Callback for update.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while updating {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            log.info("{} has been updated".format(self.name()))

    def allocateUDPPort(self):
        """
        Requests an UDP port allocation.
        """

        log.debug("{} is requesting an UDP port allocation".format(self.name()))
        self._server.send_message("dynamips.ethsw.allocate_udp_port", {"id": self._ethsw_id}, self._allocateUDPPortCallback)

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
            lhost = result["lhost"]
            lport = result["lport"]
            log.info("{} has allocated UDP port {} for host {}".format(self.name(), lport, lhost))
            self.allocate_udp_nio_signal.emit(self.id, lport, lhost)

    def addNIO(self, port, nio):
        """
        Adds a new NIO on the specified port for this switch.

        :param port: Port object.
        :param nio: NIO object.
        """

        port_info = self._settings["ports"][port.port]
        nio_type = str(nio)
        params = {"id": self._ethsw_id,
                  "nio": nio_type,
                  "port": port.port,
                  "vlan": port_info["vlan"],
                  "port_type": port_info["type"]}

        self.addNIOInfo(nio, params)
        log.debug("{} is adding an {}: {}".format(self.name(), nio_type, params))
        self._server.send_message("dynamips.ethsw.add_nio", params, self._addNIOCallback)

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
            log.info("{} has added a new NIO: {}".format(self.name(), result))
            self.nio_signal.emit(self.id)

    def deleteNIO(self, port):
        """
        Deletes an NIO from the specified port on this switch.

        :param port: Port object.
        """

        params = {"id": self._ethsw_id,
                  "port": port.port}

        port.nio = None
        log.debug("{} is deleting an NIO: {}".format(self.name(), params))
        self._server.send_message("dynamips.ethsw.delete_nio", params, self._deleteNIOCallback)

    def _deleteNIOCallback(self, result, error=False):
        """
        Callback for deleteNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        log.info("{} has deleted a NIO: {}".format(self.name(), result))

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

        :returns: list of Port objects
        """

        return self._ports

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node configurator.

        :returns: QWidget object.
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

    def __str__(self):

        return "Ethernet switch"
