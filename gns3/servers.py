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
Keeps track of all the local and remote servers and their settings.
"""

from .qt import QtCore
from .websocket_client import WebSocketClient


class Servers(object):
    """
    Server management class.
    """

    def __init__(self):

        self._local_server = None
        self._remote_servers = {}
        self._loadSettings()

    def _loadSettings(self):
        """
        Loads the server settings from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)

        # set the local server
        local_server_host = settings.value("local_server_host", "127.0.0.1")
        local_server_port = settings.value("local_server_port", 8000, type=int)
        self.setLocalServer(local_server_host, local_server_port)

        # load the remote servers
        size = settings.beginReadArray("remote")
        for index in range(0, size):
            settings.setArrayIndex(index)
            host = settings.value("host", "")
            port = settings.value("port", 0, type=int)
            if host and port:
                self._addRemoteServer(host, port)
        settings.endArray()
        settings.endGroup()

    def _saveSettings(self):
        """
        Saves the server settings to a persistent settings file.
        """

        # save the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        settings.remove("")

        # save the local server
        if self._local_server:
            settings.setValue("local_server_host", self._local_server.host)
            settings.setValue("local_server_port", self._local_server.port)

        # save the remote servers
        settings.beginWriteArray("remote", len(self._remote_servers))
        index = 0
        for server in self._remote_servers.values():
            settings.setArrayIndex(index)
            settings.setValue("host", server.host)
            settings.setValue("port", server.port)
            index += 1
        settings.endArray()
        settings.endGroup()

    def setLocalServer(self, host, port):
        """
        Sets the local server.

        :param host: host or address of the server
        :param port: port of the server (integer)
        """

        if self._local_server:
            if self._local_server.host == host and self._local_server.port == port:
                return
            elif self._local_server.connected:
                self._local_server.close()

        url = "ws://{host}:{port}".format(host=host, port=port)
        self._local_server = WebSocketClient(url)

    def localServer(self):
        """
        Returns the local server.

        :returns: local server (object)
        """

        return self._local_server

    def _addRemoteServer(self, host, port):
        """
        Adds a new remote server.

        :param host: host or address of the server
        :param port: port of the server (integer)
        """

        server_socket = "{host}:{port}".format(host=host, port=port)
        url = "ws://{server_socket}".format(server_socket=server_socket)
        server = WebSocketClient(url)
        self._remote_servers[server_socket] = server

    def updateRemoteServers(self, servers):
        """
        Updates the remote servers list.

        :param servers: servers dictionary.
        """

        for server_id, server in self._remote_servers.copy().items():
            if not server_id in servers:
                if server.connected:
                    server.close()
                del self._remote_servers[server_id]

        for server_id, server in servers.items():
            if server_id in self._remote_servers:
                continue

            host = server["host"]
            port = server["port"]
            url = "ws://{host}:{port}".format(host=host, port=port)
            new_server = WebSocketClient(url)
            self._remote_servers[server_id] = new_server

    def remoteServers(self):
        """
        Returns all the remote servers.

        :returns: remote servers dictionary
        """

        return self._remote_servers

    def save(self):
        """
        Saves the settings.
        """

        self._saveSettings()

    def disconnectAllServers(self):
        """
        Disconnects all servers (local and remote).
        """

        if self._local_server.connected:
            self._local_server.close_connection()
        for server in self._remote_servers:
            if server.connected:
                server.close_connection()

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of Servers.

        :returns: instance of Servers
        """

        if not hasattr(Servers, "_instance"):
            Servers._instance = Servers()
        return Servers._instance
