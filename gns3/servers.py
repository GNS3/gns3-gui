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

import os
import sys
import shlex
import signal
import socket
import subprocess
import ssl
from .qt import QtCore
from .websocket_client import WebSocketClient, SecureWebSocketClient
from .settings import DEFAULT_LOCAL_SERVER_PATH
from .settings import DEFAULT_LOCAL_SERVER_HOST
from .settings import DEFAULT_LOCAL_SERVER_PORT
from .settings import DEFAULT_HEARTBEAT_FREQ

import logging
log = logging.getLogger(__name__)


class Servers(QtCore.QObject):
    """
    Server management class.
    """

    # to let other pages know about remote server updates
    updated_signal = QtCore.Signal()

    def __init__(self):

        super(Servers, self).__init__()
        self._local_server = None
        self._remote_servers = {}
        self._cloud_servers = {}
        self._local_server_path = ""
        self._local_server_auto_start = True
        self._local_server_allow_console_from_anywhere = False
        self._local_server_proccess = None
        self._settings = self._loadSettings()
        self._remote_server_iter_pos = 0

    def _loadSettings(self):
        """
        Loads the server settings from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)

        # set the local server
        default_local_server_host = DEFAULT_LOCAL_SERVER_HOST
        #try:
        #    address = socket.gethostbyname(socket.gethostname())
        #    if not address.startswith("127") and address != "::1":
        #        default_local_server_host = address
        #except OSError as e:
        #    log.warn("could not determine a default local server address other than 127.0.0.1: {}".format(e))
        local_server_host = settings.value("local_server_host", default_local_server_host)
        local_server_port = settings.value("local_server_port", DEFAULT_LOCAL_SERVER_PORT, type=int)
        local_server_path = settings.value("local_server_path", DEFAULT_LOCAL_SERVER_PATH)
        local_server_auto_start = settings.value("local_server_auto_start", True, type=bool)
        local_server_allow_console_from_anywhere = settings.value("local_server_allow_console_from_anywhere", False, type=bool)
        heartbeat_freq = settings.value("heartbeat_freq", DEFAULT_HEARTBEAT_FREQ, type=int)

        self.setLocalServer(local_server_path,
                            local_server_host,
                            local_server_port,
                            local_server_auto_start,
                            local_server_allow_console_from_anywhere,
                            heartbeat_freq)

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
        return settings

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
            settings.setValue("local_server_path", self._local_server_path)
            settings.setValue("local_server_auto_start", self._local_server_auto_start)
            settings.setValue("local_server_allow_console_from_anywhere", self._local_server_allow_console_from_anywhere)

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

    def localServerAutoStart(self):
        """
        Returns either the local server
        is automatically started on startup.

        :returns: boolean
        """

        return self._local_server_auto_start

    def localServerAllowConsoleFromAnywhere(self):
        """
        Returns either the local server
        is allows console connections to any local IP address.

        :returns: boolean
        """

        return self._local_server_allow_console_from_anywhere

    def localServerPath(self):
        """
        Returns the local server path.

        :returns: path to local server program.
        """

        return self._local_server_path

    def startLocalServer(self, path, host, port):
        """
        Starts the local server process.
        """

        command = '"{executable}" --host={host} --port={port} --console_bind_to_any={bind}'.format(executable=path,
                                                                                                   host=host,
                                                                                                   port=port,
                                                                                                   bind=self._local_server_allow_console_from_anywhere)

        # settings_dir = os.path.dirname(QtCore.QSettings().fileName())
        # if os.path.isdir(settings_dir):
        #     # save server logging info to a file in the settings directory
        #     logpath = os.path.join(settings_dir, "GNS3_server.log")
        #     if os.path.isfile(logpath):
        #         # delete the previous log file
        #         try:
        #             os.remove(logpath)
        #         except FileNotFoundError:
        #             pass
        #         except OSError as e:
        #             log.warn("could not delete server log file {}: {}".format(logpath, e))
        #
        #     command += " --log_file_prefix={logpath} --log_file_num_backups=0 --log_to_stderr".format(logpath=logpath)

        log.info("starting local server process with {}".format(command))

        try:
            if sys.platform.startswith("win"):
                # use the string on Windows
                self._local_server_proccess = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                # use arguments on other platforms
                args = shlex.split(command)
                self._local_server_proccess = subprocess.Popen(args)
        except OSError as e:
            log.warning('could not start local server "{}": {}'.format(command, e))
            return False

        return True

    def stopLocalServer(self, wait=False):

        if self._local_server and self._local_server.connected() and not sys.platform.startswith('win'):
            # only gracefully disconnect if we are not on Windows
            self._local_server.close_connection()
        if self._local_server_proccess and self._local_server_proccess.poll() is None:
            if sys.platform.startswith("win"):
                self._local_server_proccess.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                self._local_server_proccess.send_signal(signal.SIGINT)
            if wait:
                self._local_server_proccess.wait()

    def setLocalServer(self, path, host, port, auto_start, allow_console_from_anywhere, heartbeat_freq=DEFAULT_HEARTBEAT_FREQ):
        """
        Sets the local server.

        :param path: path to the local server
        :param host: host or address of the server
        :param port: port of the server (integer)
        :param auto_start: either the local server should be
        automatically started on startup (boolean)
        :param allow_console_from_anywhere: allow console connections to any local IP address
        :param heartbeat_freq: The interval to send heartbeats to the server
        """

        self._local_server_path = path
        self._local_server_auto_start = auto_start
        self._local_server_allow_console_from_anywhere = allow_console_from_anywhere
        if self._local_server:
            if self._local_server.host == host and self._local_server.port == port:
                return
            if self._local_server.connected():
                self._local_server.close_connection()
            log.info("local server connection {} unregistered".format(self._local_server.url))

        url = "ws://{host}:{port}".format(host=host, port=port)
        self._local_server = WebSocketClient(url)
        self._local_server.setLocal(True)
        self._local_server.enableHeartbeatsAt(heartbeat_freq)
        log.info("new local server connection {} registered".format(url))

    def localServer(self):
        """
        Returns the local server.

        :returns: Server instance
        """

        return self._local_server


    def _addRemoteServer(self, host, port, heartbeat_freq=DEFAULT_HEARTBEAT_FREQ):
        """
        Adds a new remote server.

        :param host: host or address of the server
        :param port: port of the server (integer)
        :param heartbeat_freq: The interval to send heartbeats to the server

        :returns: the new remote server
        """

        server_socket = "{host}:{port}".format(host=host, port=port)
        url = "ws://{server_socket}".format(server_socket=server_socket)
        server = WebSocketClient(url)
        server.enableHeartbeatsAt(heartbeat_freq)
        self._remote_servers[server_socket] = server
        log.info("new remote server connection {} registered".format(url))
        return server

    def getRemoteServer(self, host, port):
        """
        Gets a remote server.

        :param host: host address
        :param port: port

        :returns: remote server (WebSocketClient instance)
        """

        for server in self._remote_servers.values():
            if server.host == host and int(server.port) == int(port):
                return server

        return self._addRemoteServer(host, port)

    def updateRemoteServers(self, servers):
        """
        Updates the remote servers list.

        :param servers: servers dictionary.
        """

        for server_id, server in self._remote_servers.copy().items():
            if not server_id in servers:
                if server.connected():
                    server.close()
                log.info("remote server connection {} unregistered".format(server.url))
                del self._remote_servers[server_id]

        for server_id, server in servers.items():
            if server_id in self._remote_servers:
                continue

            host = server["host"]
            port = server["port"]
            url = "ws://{host}:{port}".format(host=host, port=port)
            new_server = WebSocketClient(url)
            self._remote_servers[server_id] = new_server
            log.info("new remote server connection {} registered".format(url))

        self.updated_signal.emit()

    def remoteServers(self):
        """
        Returns all the remote servers.

        :returns: remote servers dictionary
        """

        return self._remote_servers

    def getCloudServer(self, host, port, ca_file, auth_user, auth_password, ssh_pkey, instance_id):
        """
        Return a websocket connection to the cloud server, creating one if none exists.

        :param host: host ip address of the cloud server
        :param port: port the gns3server process is listening on
        :param ca_file: Path to the SSL cert that the server must present
        :returns: a websocket connection to the cloud server
        """

        for server in self._remote_servers.values():
            if server.host == host and int(server.port) == int(port):
                return server

        heartbeat_freq = self._settings.value("heartbeat_freq", DEFAULT_HEARTBEAT_FREQ)
        return self._addCloudServer(host, port, ca_file, auth_user, auth_password, ssh_pkey,
                                    heartbeat_freq, instance_id)
    
    def _addCloudServer(self, host, port, ca_file, auth_user, auth_password, ssh_pkey,
                        heartbeat_freq, instance_id):
        """
        Create a websocket connection to the specified cloud server

        :param host: host ip address of the server
        :param port: port the gns3server process is listening on
        :param ca_file: Path to the SSL cert that the server must present
        :param heartbeat_freq: The interval to send heartbeats to the server

        :returns: a websocket connection to the cloud server
        """

        url = "wss://{host}:{port}".format(host=host, port=port)
        log.debug('Starting SecureWebSocketClient url={}'.format(url))
        log.debug('Starting SecureWebSocketClient ca_file={}'.format(ca_file))
        log.debug('Starting SecureWebSocketClient ssh_pkey={}'.format(ssh_pkey))
        server = SecureWebSocketClient(url, instance_id=instance_id)
        server.setSecureOptions(ca_file, auth_user, auth_password, ssh_pkey)
        server.setCloud(True)
        server.enableHeartbeatsAt(heartbeat_freq)
        self._cloud_servers[host] = server
        log.info("new remote server connection {} registered".format(url))
        return server

    def anyCloudServer(self):
        # Return the first server for now
        for key, value in self._cloud_servers.items():
            return value
        return None

    def __iter__(self):
        """
        Creates a round-robin system to pick up a remote server.
        """

        return self

    def __next__(self):
        """
        Returns the next available remote server.

        :returns: remote server (WebSocketClient instance)
        """

        if not self._remote_servers:
            return None

        server_ids = list(self._remote_servers.keys())
        server_id = server_ids[self._remote_server_iter_pos]

        if self._remote_server_iter_pos < len(server_ids) - 1:
            self._remote_server_iter_pos += 1
        else:
            self._remote_server_iter_pos = 0

        return self._remote_servers[server_id]

    def save(self):
        """
        Saves the settings.
        """

        self._saveSettings()

    def disconnectAllServers(self):
        """
        Disconnects all servers (local and remote).
        """

        if self._local_server.connected():
            self._local_server.close_connection()
        for server in self._remote_servers:
            if server.connected():
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
