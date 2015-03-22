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

    :param module: Module instance
    :param server: client connection to a server
    :param project: Project instance
    """

    # signals used to let the GUI know about some events.
    created_signal = QtCore.Signal(int)
    started_signal = QtCore.Signal()
    stopped_signal = QtCore.Signal()
    suspended_signal = QtCore.Signal()
    updated_signal = QtCore.Signal()
    deleted_signal = QtCore.Signal()
    delete_links_signal = QtCore.Signal()
    error_signal = QtCore.Signal(int, str)
    warning_signal = QtCore.Signal(int, str)
    server_error_signal = QtCore.Signal(int, str)
    nio_signal = QtCore.Signal(int, int)
    nio_cancel_signal = QtCore.Signal(int)
    allocate_udp_nio_signal = QtCore.Signal(int, int, int)

    _instance_count = 1
    _allocated_names = []

    # node statuses
    stopped = 0
    started = 1
    suspended = 2

    # node categories
    routers = 0
    switches = 1
    end_devices = 2
    security_devices = 3

    def __init__(self, module, server, project):

        super(Node, self).__init__()

        # create an unique ID
        self._id = Node._instance_count
        Node._instance_count += 1

        self._module = module
        self._server = server
        self._project = project
        self._initialized = False
        self._status = 0

    @classmethod
    def reset(cls):
        """
        Reset the instance count.
        """

        cls._instance_count = 1
        cls._allocated_names.clear()

    def allocateName(self, base_name):
        """
        Allocates a new name for a node.

        :param base_name: base name for the node which will be completed with a
        unique number

        :returns: allocated name or None if one could not be found
        """

        for number in range(1, 100000):
            name = base_name + str(number)
            if name not in self._allocated_names:
                self._allocated_names.append(name)
                return name
        return None

    def removeAllocatedName(self):
        """
        Removes an allocated name from a node.
        """

        if self.name() in self._allocated_names:
            self._allocated_names.remove(self.name())

    def updateAllocatedName(self, name):
        """
        Updates a name for a node.

        :param name: new node name
        """

        self.removeAllocatedName()
        self._allocated_names.append(name)

    def setName(self, name):
        """
        Set a name for a node.

        :param name: node name
        """

        if name not in self._allocated_names:
            self._allocated_names.append(name)

    def hasAllocatedName(self, name):
        """
        Returns either a name is already allocated or not.

        :param name: node name

        :returns: boolean
        """

        if name in self._allocated_names:
            return True
        return False

    def module(self):
        """
        Returns this node module.

        :returns: Module instance
        """

        return self._module

    def server(self):
        """
        Returns this node server.

        :returns: Server instance
        """

        return self._server

    def project(self):
        """
        Returns this node project.

        :returns: Project instance
        """

        return self._project

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

        # update the instance count to avoid conflicts
        if new_id >= Node._instance_count:
            Node._instance_count = new_id + 1

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

    def getNIOInfo(self, nio):
        """
        Returns NIO information for a specific NIO.

        :param nio: NIO instance

        :returns: NIO information (dictionary)
        """

        nio_type = str(nio).lower()
        nio_info = {}
        if nio_type == "nio_udp":
            # return NIO UDP info
            nio_info["type"] = nio_type
            nio_info["lport"] = nio.lport()
            nio_info["rhost"] = nio.rhost()
            nio_info["rport"] = nio.rport()

            log.debug("creating {} for {} with lport={}, rhost={}, rport={}".format(nio,
                                                                                    self.name(),
                                                                                    nio.lport(),
                                                                                    nio.rhost(),
                                                                                    nio.rport()))
            return nio_info

        elif nio_type == "nio_generic_ethernet":
            # return NIO generic Ethernet info
            nio_info["type"] = nio_type
            nio_info["ethernet_device"] = nio.ethernetDevice()

            log.debug("creating {} for {} with Ethernet device {}".format(nio,
                                                                          self.name(),
                                                                          nio.ethernetDevice()))
            return nio_info

        elif nio_type == "nio_linux_ethernet":
            # return NIO Linux Ethernet info
            nio_info["type"] = nio_type
            nio_info["ethernet_device"] = nio.ethernetDevice()

            log.debug("creating {} for {} with Ethernet device {}".format(nio,
                                                                          self.name(),
                                                                          nio.ethernetDevice()))
            return nio_info

        elif nio_type == "nio_tap":
            # return NIO TAP info
            nio_info["type"] = nio_type
            nio_info["tap_device"] = nio.tapDevice()

            log.debug("creating {} for {} with TAP device {}".format(nio,
                                                                     self.name(),
                                                                     nio.tapDevice()))
            return nio_info

        elif nio_type == "nio_unix":
            # return NIO UNIX info
            nio_info["type"] = nio_type
            nio_info["local_file"] = nio.localFile()
            nio_info["remote_file"] = nio.remoteFile()

            log.debug("creating {} for {} with local file '{}' and remote file '{}'".format(nio,
                                                                                            self.name(),
                                                                                            nio.localFile(),
                                                                                            nio.remoteFile()))
            return nio_info

        elif nio_type == "nio_vde":
            # return NIO VDE info
            nio_info["type"] = nio_type
            nio_info["control_file"] = nio.controlFile()
            nio_info["local_file"] = nio.localFile()

            log.debug("creating {} for {} with control file '{}' and local file '{}'".format(nio,
                                                                                             self.name(),
                                                                                             nio.controlFile(),
                                                                                             nio.localFile()))
            return nio_info

        elif nio_type == "nio_null":
            nio_info["type"] = nio_type
            log.debug("creating {} for {} with identifier '{}'".format(nio,
                                                                       self.name(),
                                                                       nio.identifier()))
            return nio_info

        assert("Not supposed to get here!")

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

    def httpPost(self, path, callback, body={}, context={}):
        """
        POST on current server / project

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)
        :param context: Pass a context to the response callback
        """

        self._project.post(self._server, path, callback, body=body, context=context)

    def httpPut(self, path, callback, body={}, context={}):
        """
        PUT on current server / project

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)
        :param context: Pass a context to the response callback
        """

        self._project.put(self._server, path, callback, body=body, context=context)

    def httpGet(self, path, callback, context={}):
        """
        GET on current server / project

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        """

        self._project.get(self._server, path, callback, context=context)

    def httpDelete(self, path, callback, context={}):
        """
        DELETE on current server / project

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        """

        self._project.delete(self._server, path, callback, context=context)

    def allocateUDPPort(self, port_id):
        """
        Requests an UDP port allocation.

        :param port_id: port identifier
        """

        log.debug("{} is requesting an UDP port allocation".format(self.name()))
        self.httpPost("/ports/udp", self._allocateUDPPortCallback, context={"port_id": port_id})

    def _allocateUDPPortCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for allocateUDPPort.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while allocating an UDP port for {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            port_id = context["port_id"]
            lport = result["udp_port"]
            log.debug("{} has allocated UDP port {}".format(self.name(), port_id, lport))
            self.allocate_udp_nio_signal.emit(self.id(), port_id, lport)
