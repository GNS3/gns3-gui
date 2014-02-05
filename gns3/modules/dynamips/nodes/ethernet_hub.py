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

    :param server: GNS3 server instance
    """

    def __init__(self, server):
        Node.__init__(self)

        self._server = server
        self._ethhub_id = None
        self._ports = []
        self._settings = {"name": "",
                          "ports": []}

    def setup(self, name=None):
        """
        Setups this hub.

        :param name: optional name for this hub
        """

        self._server.send_message("dynamips.ethhub.create", None, self._setupCallback)

    def _setupCallback(self, result, error=False):
        """
        Callback for setup.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        self._ethhub_id = result["id"]
        self._settings["name"] = result["name"]

        # let the GUI knows about this hub name
        log.info("Ethernet hub {} has been created".format(result["name"]))
        self.newname_signal.emit(self._settings["name"])

    def delete(self):
        """
        Deletes this Ethernet hub.
        """

        log.debug("Ethernet hub {} is being deleted".format(self.name()))
        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        self._server.send_message("dynamips.ethhub.delete", {"id": self._ethhub_id}, self._deleteCallback)

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
            log.info("{} has been deleted".format(self.name()))
            self.delete_signal.emit()

    def update(self, new_settings):
        """
        Updates the settings for this Ethernet hub.

        :param new_settings: settings dictionary
        """

        ports_to_create = []
        ports = new_settings["ports"]

        for port_id in ports:
            if port_id not in ports_to_create:
                ports_to_create.append(port_id)

        for port in self._ports.copy():
            if port.isFree():
                self._ports.remove(port)
                log.debug("port {} has been removed".format(port.name))
            else:
                ports_to_create.remove(port.name)

        for port_name in ports_to_create:
            port = EthernetPort(port_name)
            port.port = int(port_name)
            self._ports.append(port)
            log.debug("port {} has been added".format(port_name))

        self._settings["ports"] = new_settings["ports"].copy()

    def allocateUDPPort(self):
        """
        Requests an UDP port allocation.
        """

        log.debug("{} is requesting an UDP port allocation".format(self.name()))
        self._server.send_message("dynamips.ethhub.allocate_udp_port", {"id": self._ethhub_id}, self._allocateUDPPortCallback)

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
        Adds a new NIO on the specified port for this hub.

        :param port: Port object.
        :param nio: NIO object.
        """

        nio_type = str(nio)
        params = {"id": self._ethhub_id,
                  "nio": nio_type,
                  "port": port.port}

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
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            self.nio_signal.emit(self.id)

    def deleteNIO(self, port):
        """
        Deletes an NIO from the specified port on this hub.

        :param port: Port object.
        """

        params = {"id": self._ethhub_id,
                  "port": port.port}

        port.nio = None
        log.debug("{} is deleting an NIO: {}".format(self.name(), params))
        self._server.send_message("dynamips.ethhub.delete_nio", params, self._deleteNIOCallback)

    def _deleteNIOCallback(self, result, error=False):
        """
        Callback for deleteNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        log.info("{} has deleted a NIO: {}".format(self.name(), result))

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

        :returns: list of Port objects
        """

        return self._ports

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node configurator.

        :returns: QWidget object.
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

    def __str__(self):

        return "Ethernet hub"
