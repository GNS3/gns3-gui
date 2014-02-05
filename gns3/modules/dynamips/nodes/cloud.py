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
Dynamips NIO implementation on the client side (in the form of a pseudo node represented as a cloud).
Asynchronously sends JSON messages to the GNS3 server and receives responses with callbacks.
"""

import re
from gns3.node import Node
from gns3.ports.port import Port
from gns3.nios.nio_generic_ethernet import NIO_GenericEthernet
from gns3.nios.nio_linux_ethernet import NIO_LinuxEthernet
from gns3.nios.nio_udp import NIO_UDP
from gns3.nios.nio_tap import NIO_TAP
from gns3.nios.nio_unix import NIO_UNIX
from gns3.nios.nio_vde import NIO_VDE
from gns3.nios.nio_null import NIO_Null

import logging
log = logging.getLogger(__name__)


class Cloud(Node):
    """
    Dynamips cloud.

    :param server: GNS3 server instance
    """

    _name_instance_count = 1

    def __init__(self, server, platform="c7200"):
        Node.__init__(self)

        self._server = server

        # create an unique id and name
        self._name_id = Cloud._name_instance_count
        Cloud._name_instance_count += 1
        self._name = "Cloud {}".format(self._name_id)

        self._defaults = {}
        self._ports = []
        self._settings = {"nios": [],
                          "interfaces": []}

    def delete(self):
        """
        Deletes this cloud.
        """

        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        self.delete_signal.emit()

    def setup(self, name=None):
        """
        Setups this cloud.

        :param name: optional name for this cloud
        """

        self._server.send_message("dynamips.nio.get_interfaces", None, self._setupCallback)

    def _setupCallback(self, response, error=False):
        """
        Callback for setup.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        for interface in response:
            self._settings["interfaces"].append(interface)

    def _createNIOUDP(self, nio):
        """
        Creates a NIO UDP.

        :param nio: nio string
        """

        match = re.search(r"""^nio_udp:(\d+):(.+):(\d+)$""", nio)
        if match:
            lport = int(match.group(1))
            rhost = match.group(2)
            rport = int(match.group(3))
            return NIO_UDP(lport, rhost, rport)
        return None

    def _createNIOGenericEthernet(self, nio):
        """
        Creates a NIO Generic Ethernet.

        :param nio: nio string
        """

        match = re.search(r"""^nio_gen_eth:(.+)$""", nio)
        if match:
            ethernet_device = match.group(1)
            return NIO_GenericEthernet(ethernet_device)
        return None

    def _createNIOLinuxEthernet(self, nio):
        """
        Creates a NIO Linux Ethernet.

        :param nio: nio string
        """

        match = re.search(r"""^nio_gen_linux:(.+)$""", nio)
        if match:
            linux_device = match.group(1)
            return NIO_LinuxEthernet(linux_device)
        return None

    def _createNIOTAP(self, nio):
        """
        Creates a NIO TAP.

        :param nio: nio string
        """

        match = re.search(r"""^nio_tap:(.+)$""", nio)
        if match:
            tap_device = match.group(1)
            return NIO_TAP(tap_device)
        return None

    def _createNIOUNIX(self, nio):
        """
        Creates a NIO UNIX.

        :param nio: nio string
        """

        match = re.search(r"""^nio_unix:(.+):(.+)$""", nio)
        if match:
            local_file = match.group(1)
            remote_file = match.group(2)
            return NIO_UNIX(local_file, remote_file)
        return None

    def _createNIOVDE(self, nio):
        """
        Creates a NIO VDE.

        :param nio: nio string
        """

        match = re.search(r"""^nio_vde:(.+):(.+)$""", nio)
        if match:
            control_file = match.group(1)
            local_file = match.group(2)
            return NIO_VDE(control_file, local_file)
        return None

    def _createNIONull(self, nio):
        """
        Creates a NIO Null.

        :param nio: nio string
        """

        match = re.search(r"""^nio_null:(.+)$""", nio)
        if match:
            identifier = match.group(1)
            return NIO_Null(identifier)
        return None

    def update(self, new_settings):
        """
        Updates the settings for this cloud.

        :param new_settings: settings dictionary
        """

        nios = new_settings["nios"]

        # add ports
        for nio in nios:
            if nio in self._settings["nios"]:
                # port already created for this NIO
                continue
            nio_object = None
            if nio.lower().startswith("nio_udp"):
                nio_object = self._createNIOUDP(nio)
            if nio.lower().startswith("nio_gen_eth"):
                nio_object = self._createNIOGenericEthernet(nio)
            if nio.lower().startswith("nio_gen_linux"):
                nio_object = self._createNIOLinuxEthernet(nio)
            if nio.lower().startswith("nio_tap"):
                nio_object = self._createNIOTAP(nio)
            if nio.lower().startswith("nio_unix"):
                nio_object = self._createNIOUNIX(nio)
            if nio.lower().startswith("nio_vde"):
                nio_object = self._createNIOVDE(nio)
            if nio.lower().startswith("nio_null"):
                nio_object = self._createNIONull(nio)
            if nio_object == None:
                log.error("Could not create NIO object from {}".format(nio))
                continue
            port = Port(nio, nio_object, stub=True)
            self._ports.append(port)
            log.debug("port {} has been added".format(nio))

        # delete ports
        for nio in self._settings["nios"]:
            if nio not in nios:
                for port in self._ports.copy():
                    if port.name == nio:
                        self._ports.remove(port)
                        log.debug("port {} has been deleted".format(nio))
                        break

        self._settings = new_settings.copy()

    def deleteNIO(self, port):

        port.nio = None

    def name(self):
        """
        Returns the name of this cloud.

        :returns: name (string)
        """

        return self._name

    def settings(self):
        """
        Returns all this cloud settings.

        :returns: settings dictionary
        """

        return self._settings

    def ports(self):
        """
        Returns all the ports for this cloud.

        :returns: list of Port objects
        """

        return self._ports

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node configurator.

        :returns: QWidget object.
        """

        from ..pages.cloud_configuration_page import CloudConfigurationPage
        return CloudConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this cloud.

        :returns: symbol path (or resource).
        """

        return ":/symbols/cloud.normal.svg"

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when the cloud is hovered.

        :returns: symbol path (or resource).
        """

        return ":/symbols/cloud.selected.svg"

    @staticmethod
    def symbolName():

        return "Cloud"

    def __str__(self):

        return "Cloud"
