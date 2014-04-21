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
Base class for node classes.
"""

from .qt import QtCore

import logging
log = logging.getLogger(__name__)


class Node(QtCore.QObject):
    """
    Node implementation.

    :param server: client connection to a server
    """

    # signals used to let the GUI know about some events.
    created_signal = QtCore.Signal(int)
    started_signal = QtCore.Signal()
    stopped_signal = QtCore.Signal()
    suspended_signal = QtCore.Signal()
    updated_signal = QtCore.Signal()
    deleted_signal = QtCore.Signal()
    delete_links_signal = QtCore.Signal()
    idlepc_signal = QtCore.Signal()
    error_signal = QtCore.Signal(int, int, str)
    nio_signal = QtCore.Signal(int, int)
    allocate_udp_nio_signal = QtCore.Signal(int, int, int)

    _instance_count = 1

    # node statuses
    stopped = 0
    started = 1
    suspended = 2

    # node categories
    routers = 0
    switches = 1
    end_devices = 2
    security_devices = 3

    def __init__(self, server=None):

        super(Node, self).__init__()

        # create an unique ID
        self._id = Node._instance_count
        Node._instance_count += 1

        self._server = server
        self._initialized = False
        self._status = 0

    @classmethod
    def reset(cls):
        """
        Reset the instance count.
        """

        cls._instance_count = 1

    def server(self):
        """
        Returns this node server.

        :returns: Server instance
        """

        return self._server

    def id(self):
        """
        Returns this node identifier.

        :returns: node identifier (integer)
        """

        return self._id

    def setId(self, new_id):
        """
        Sets an identifier for this node.

        :param new_id: node identifier (integer)
        """

        self._id = new_id

    def status(self):
        """
        Returns the status of this node.
        0 = stopped, 1 = started, 2 = suspended.

        :returns: node status (integer)
        """

        return self._status

    def setStatus(self, status):
        """
        Sets a status for this node.
        0 = stopped, 1 = started, 2 = suspended.

        :param status: node status (integer)
        """

        self._status = status

    def initialized(self):
        """
        Returns if the node has been initialized

        :returns: boolean
        """

        return self._initialized

    def setInitialized(self, initialized):
        """
        Sets if the node has been initialized

        :param initialized: boolean
        """

        self._initialized = initialized

    def dump(self):
        """
        Returns a representation of this node.
        Must be overloaded.

        :returns: dictionary
        """

        raise NotImplementedError()

    def load(self, node_info):
        """
        Loads a node representation
        (from a topology file).
        Must be overloaded.

        :param node_info: representation of the node (dictionary)
        """

        raise NotImplementedError()

    def name(self):
        """
        Returns the name of this node.
        Must be overloaded.

        :returns: name (string)
        """

        raise NotImplementedError()

    def update(self, new_settings):
        """
        Updates the settings for this node.
        Must be overloaded.

        :param new_settings: settings dictionary
        """

        raise NotImplementedError()

    def ports(self):
        """
        Returns all the ports for this node.
        Must be overloaded.

        :returns: list of Port instances
        """

        raise NotImplementedError()

    def addNIOInfo(self, nio, params):
        """
        Adds NIO information to a dictionary.

        :param nio: NIO instance
        :param params: dictionary
        """

        nio_type = str(nio)
        if nio_type == "NIO_UDP":
            # add NIO UDP params
            params["lport"] = nio.lport()
            params["rhost"] = nio.rhost()
            params["rport"] = nio.rport()

            log.debug("creating {} for {} with lport={}, rhost={}, rport={}".format(nio,
                                                                                    self.name(),
                                                                                    nio.lport(),
                                                                                    nio.rhost(),
                                                                                    nio.rport()))

        elif nio_type == "NIO_GenericEthernet":
            # add NIO generic Ethernet param
            params["ethernet_device"] = nio.ethernetDevice()

            log.debug("creating {} for {} with Ethernet device {}".format(nio,
                                                                          self.name(),
                                                                          nio.ethernetDevice()))

        elif nio_type == "NIO_LinuxEthernet":
            # add NIO Linux Ethernet param
            params["ethernet_device"] = nio.ethernetDevice()

            log.debug("creating {} for {} with Ethernet device {}".format(nio,
                                                                          self.name(),
                                                                          nio.ethernetDevice()))

        elif nio_type == "NIO_TAP":
            # add NIO TAP param
            params["tap_device"] = nio.tapDevice()

            log.debug("creating {} for {} with TAP device {}".format(nio,
                                                                     self.name(),
                                                                     nio.tapDevice()))

        elif nio_type == "NIO_UNIX":
            # add NIO UNIX params
            params["local_file"] = nio.localFile()
            params["remote_file"] = nio.remoteFile()

            log.debug("creating {} for {} with local file '{}' and remote file '{}'".format(nio,
                                                                                            nio.localFile(),
                                                                                            nio.remoteFile()))

        elif nio_type == "NIO_VDE":
            # add NIO VDE params
            params["control_file"] = nio.controlFile()
            params["local_file"] = nio.localFile()

            log.debug("creating {} for {} with control file '{}' and local file '{}'".format(nio,
                                                                                             nio.controlFile(),
                                                                                             nio.localFile()))
        elif nio_type == "NIO_Null":

            log.debug("creating {} for {} with identifier '{}'".format(nio,
                                                                       self.name(),
                                                                       nio.identifier()))

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node configurator.
        Must be overloaded.

        :returns: QWidget instance
        """

        raise NotImplementedError()

    def settings(self):
        """
        Returns all the node settings.
        Must be overloaded.

        :returns: settings dictionary
        """

        raise NotImplementedError()

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.
        Must be overloaded.

        :returns: symbol path (or resource).
        """

        raise NotImplementedError()

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when the node is hovered.
        Must be overloaded.

        :returns: symbol path (or resource).
        """

        raise NotImplementedError()

    @staticmethod
    def symbolName():
        """
        Returns the symbol name (for the nodes view).

        :returns: name (string)
        """

        raise NotImplementedError()

    @staticmethod
    def categories(self):
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        raise NotImplementedError()

    def __str__(self):
        """
        Must be overloaded.
        """

        raise NotImplementedError()
