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
Built-in module implementation.
"""

import os
from gns3.qt import QtCore, QtGui
from gns3.servers import Servers
from ..module import Module
from ..module_error import ModuleError
from .cloud import Cloud


import logging
log = logging.getLogger(__name__)


class Builtin(Module):
    """
    Built-in module.
    """

    def __init__(self):
        Module.__init__(self)

        self._nodes = []
        self._servers = []

    def setProjectFilesDir(self, path):
        """
        Sets the project files directory path this module.

        :param path: path to the local project files directory
        """

        pass

    def addServer(self, server):
        """
        Adds a server to be used by this module.

        :param server: WebSocketClient instance
        """

        log.info("adding server {}:{} to built-in module".format(server.host, server.port))
        self._servers.append(server)

    def removeServer(self, server):
        """
        Removes a server from being used by this module.

        :param server: WebSocketClient instance
        """

        log.info("removing server {}:{} from built-in module".format(server.host, server.port))
        self._servers.remove(server)

    def servers(self):
        """
        Returns all the servers used by this module.

        :returns: list of WebSocketClient instances
        """

        return self._servers

    def addNode(self, node):
        """
        Adds a node to this module.

        :param node: Node instance
        """

        self._nodes.append(node)

    def removeNode(self, node):
        """
        Removes a node from this module.

        :param node: Node instance
        """

        if node in self._nodes:
            self._nodes.remove(node)

    def allocateServer(self, node_class):
        """
        Allocates a server.

        :param node_class: Node object

        :returns: allocated server (WebSocketClient instance)
        """

        # check all other modules to find if they
        # are using a local server
        using_local_server = []
        from gns3.modules import MODULES
        for module in MODULES:
            instance = module.instance()
            if instance != self:
                module_settings = instance.settings()
                if "use_local_server" in module_settings:
                    using_local_server.append(module_settings["use_local_server"])

        # allocate a server for the node
        servers = Servers.instance()
        local_server = servers.localServer()
        remote_servers = servers.remoteServers()

        if not all(using_local_server):
            # a module is not using a local server

            if not True in using_local_server and len(remote_servers) == 1:
                # no module is using a local server and there is only one
                # remote server available, so no need to ask the user.
                return next(iter(servers))

            server_list = []
            server_list.append("Local server ({}:{})".format(local_server.host, local_server.port))
            for remote_server in remote_servers:
                server_list.append("{}".format(remote_server))

            #TODO: move this to graphics_view
            from gns3.main_window import MainWindow
            mainwindow = MainWindow.instance()
            (selection, ok) = QtGui.QInputDialog.getItem(mainwindow, "Server", "Please choose a server", server_list, 0, False)
            if ok:
                if selection.startswith("Local server"):
                    return local_server
                else:
                    return remote_servers[selection]
            else:
                raise ModuleError("Please select a server")
        return local_server

    def createNode(self, node_class, server):
        """
        Creates a new node.

        :param node_class: Node object
        :param server: WebSocketClient instance
        """

        log.info("creating node {}".format(node_class))

        if not server.connected():
            try:
                log.info("reconnecting to server {}:{}".format(server.host, server.port))
                server.reconnect()
            except OSError as e:
                raise ModuleError("Could not connect to server {}:{}: {}".format(server.host,
                                                                                 server.port,
                                                                                 e))
        if server not in self._servers:
            self.addServer(server)

        # create an instance of the node class
        return node_class(self, server)

    def setupNode(self, node):
        """
        Setups a node.

        :param node: Node instance
        """

        log.info("configuring node {}".format(node))
        node.setup()

    def reset(self):
        """
        Resets the servers.
        """

        self._servers.clear()

    @staticmethod
    def getNodeClass(name):
        """
        Returns the object with the corresponding name.

        :param name: object name
        """

        if name in globals():
            return globals()[name]
        return None

    @staticmethod
    def nodes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [Cloud]

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        return []

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of built-in module.

        :returns: instance of Builtin
        """

        if not hasattr(Builtin, "_instance"):
            Builtin._instance = Builtin()
        return Builtin._instance
