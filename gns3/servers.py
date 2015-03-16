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

import sys
import os
import shlex
import signal
import shutil
import subprocess

from .qt import QtGui, QtCore, QtNetwork
from .http_client import HTTPClient
from .local_config import LocalConfig
from .settings import LOCAL_SERVER_SETTINGS, LOCAL_SERVER_SETTING_TYPES
from .local_server_config import LocalServerConfig
from collections import OrderedDict

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
        self._network_manager = QtNetwork.QNetworkAccessManager(self)
        self._local_server_settings = {}
        self._remote_server_iter_pos = 0
        self._loadSettings()

        host = self._local_server_settings["host"]
        port = self._local_server_settings["port"]
        url = "http://{host}:{port}".format(host=host, port=port)
        self._local_server = HTTPClient(url, self._network_manager)
        self._local_server.setLocal(True)
        log.info("New local server connection {} registered".format(url))

    @staticmethod
    def _findLocalServer(self):
        """
        Finds the local server path.

        :return: path to the local server
        """

        if sys.platform.startswith("win") and hasattr(sys, "frozen"):
            local_server_path = os.path.join(os.getcwd(), "gns3server.exe")
        elif sys.platform.startswith("darwin") and hasattr(sys, "frozen"):
            local_server_path = os.path.join(os.getcwd(), "server/Contents/MacOS/gns3server")
        else:
            local_server_path = shutil.which("gns3server")

        if local_server_path is None:
            return ""
        return local_server_path

    def _loadSettings(self):
        """
        Loads the server settings from the persistent settings file.
        """

        local_config = LocalConfig.instance()

        # restore the local server settings from QSettings (for backward compatibility)
        legacy_settings = {}
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name in LOCAL_SERVER_SETTINGS.keys():
            if settings.contains(name):
                legacy_settings[name] = settings.value(name, type=LOCAL_SERVER_SETTING_TYPES[name])

        # load the remote servers
        size = settings.beginReadArray("remote")
        for index in range(0, size):
            settings.setArrayIndex(index)
            host = settings.value("host", "")
            port = settings.value("port", 0, type=int)
            if host and port:
                self._addRemoteServer(host, port)
        settings.endArray()
        settings.remove("")
        settings.endGroup()

        if legacy_settings:
            local_config.saveSectionSettings("LocalServer", legacy_settings)

        self._local_server_settings = local_config.loadSectionSettings("LocalServer", LOCAL_SERVER_SETTINGS)
        if not os.path.exists(self._local_server_settings["path"]):
            self._local_server_settings["path"] = self._findLocalServer(self)

        settings = local_config.settings()
        if "RemoteServers" in settings:
            for remote_server in settings["RemoteServers"]:
                self._addRemoteServer(remote_server["host"], remote_server["port"])

        # keep the config file sync
        self._saveSettings()
        return settings

    def _saveSettings(self):
        """
        Saves the server settings to a persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings("LocalServer", self._local_server_settings)

        # save the remote servers
        remote_servers = []
        for server in self._remote_servers.values():
            remote_servers.append({"host": server.host,
                                   "port": server.port})
        LocalConfig.instance().setSettings({"RemoteServers": remote_servers})

        # save some settings to the local server config files
        server_settings = OrderedDict([
            ("host", self._local_server_settings["host"]),
            ("port", self._local_server_settings["port"]),
            ("images_path", self._local_server_settings["images_path"]),
            ("projects_path", self._local_server_settings["projects_path"]),
            ("console_start_port_range", self._local_server_settings["console_start_port_range"]),
            ("console_end_port_range", self._local_server_settings["console_end_port_range"]),
            ("udp_start_port_range", self._local_server_settings["udp_start_port_range"]),
            ("udp_start_end_range", self._local_server_settings["udp_end_port_range"]),
            ("report_errors", self._local_server_settings["report_errors"]),
        ])
        config = LocalServerConfig.instance()
        config.saveSettings("Server", server_settings)

        if self._local_server and self._local_server.connected():
            self._local_server.post("/config/reload", None)

    def localServerSettings(self):
        """
        Returns the local server settings.

        :returns: local server settings (dict)
        """

        return self._local_server_settings

    def setLocalServerSettings(self, settings):
        """
        Set new local server settings.

        :param settings: local server settings (dict)
        """

        if settings["host"] != self._local_server_settings["host"] or settings["port"] != self._local_server_settings["port"]:
            url = "http://{host}:{port}".format(host=settings["host"], port=settings["port"])
            self._local_server = HTTPClient(url, self._network_manager)
            self._local_server.setLocal(True)
            log.info("New local server connection {} registered".format(url))

        self._local_server_settings.update(settings)

    def localServerAutoStart(self):
        """
        Returns either the local server
        is automatically started on startup.

        :returns: boolean
        """

        return self._local_server_settings["auto_start"]

    def localServerPath(self):
        """
        Returns the local server path.

        :returns: path to local server program.
        """

        return self._local_server_settings["path"]

    def startLocalServer(self):
        """
        Starts the local server process.
        """

        path = self.localServerPath()
        host = self._local_server.host
        port = self._local_server.port
        command = '"{executable}" --host {host} --port {port} --local'.format(executable=path,
                                                                              host=host,
                                                                              port=port)

        if self._local_server_settings["allow_console_from_anywhere"]:
            # allow connections to console from remote addresses
            command += " --allow"

        log.info("Starting local server process with {}".format(command))
        try:
            if sys.platform.startswith("win"):
                # use the string on Windows
                self._local_server_proccess = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                # use arguments on other platforms
                args = shlex.split(command)
                self._local_server_proccess = subprocess.Popen(args)
        except (OSError, subprocess.SubprocessError) as e:
            log.warning('Could not start local server "{}": {}'.format(command, e))
            return False

        log.info("Local server process has started (PID={})".format(self._local_server_proccess.pid))
        return True

    def localServerIsRunning(self):
        """
        Returns either the local server is running.

        :returns: boolean
        """

        if self._local_server_proccess and self._local_server_proccess.poll() is None:
            return True
        return False

    def stopLocalServer(self, wait=False):
        """
        Stops the local server.

        :param wait: wait for the server to stop
        """

        if self.localServerIsRunning():
            log.info("Stopping local server (PID={})".format(self._local_server_proccess.pid))
            # local server is running, let's stop it
            if wait:
                try:
                    # wait for the server to stop for maximum 2 seconds
                    self._local_server_proccess.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    # the local server couldn't be stopped with the normal procedure
                    if sys.platform.startswith("win"):
                        self._local_server_proccess.send_signal(signal.CTRL_BREAK_EVENT)
                    else:
                        self._local_server_proccess.send_signal(signal.SIGINT)
                    try:
                        # wait for the server to stop for maximum 2 seconds
                        self._local_server_proccess.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        from .main_window import MainWindow
                        main_window = MainWindow.instance()
                        proceed = QtGui.QMessageBox.question(main_window,
                                                             "Local server",
                                                             "The Local server cannot be stopped, would you like to kill it?",
                                                             QtGui.QMessageBox.Yes,
                                                             QtGui.QMessageBox.No)

                        if proceed == QtGui.QMessageBox.Yes:
                            self._local_server_proccess.kill()

    def localServer(self):
        """
        Returns the local server.

        :returns: Server instance
        """

        return self._local_server

    def _addRemoteServer(self, host, port):
        """
        Adds a new remote server.

        :param host: host or address of the server
        :param port: port of the server (integer)

        :returns: the new remote server
        """

        server_socket = "{host}:{port}".format(host=host, port=port)
        url = "http://{server_socket}".format(server_socket=server_socket)
        server = HTTPClient(url, self._network_manager)
        server.setLocal(False)
        self._remote_servers[server_socket] = server
        log.info("New remote server connection {} registered".format(url))
        return server

    def getRemoteServer(self, host, port):
        """
        Gets a remote server.

        :param host: host address
        :param port: port

        :returns: remote server (HTTPClient instance)
        """

        for server in self._remote_servers.values():
            if server.host == host and int(server.port) == int(port):
                return server

        return self._addRemoteServer(host, port)

    def getServerFromString(self, string):
        """
        Finds a server instance from its string representation.
        """

        if string == "local":
            return self._local_server

        (host, port) = string.split(":")
        return self.getRemoteServer(host, port)

    def updateRemoteServers(self, servers):
        """
        Updates the remote servers list.

        :param servers: servers dictionary.
        """

        for server_id, server in self._remote_servers.copy().items():
            if server_id not in servers:
                if server.connected():
                    server.close()
                log.info("Remote server connection {} unregistered".format(server.url()))
                del self._remote_servers[server_id]

        for server_id, server in servers.items():
            if server_id in self._remote_servers:
                continue

            host = server["host"]
            port = server["port"]
            url = "http://{host}:{port}".format(host=host, port=port)
            new_server = HTTPClient(url, self._network_manager)
            new_server.setLocal(False)
            self._remote_servers[server_id] = new_server
            log.info("New remote server connection {} registered".format(url))

        self.updated_signal.emit()

    def remoteServers(self):
        """
        Returns all the remote servers.

        :returns: remote servers dictionary
        """

        return self._remote_servers

    # def getCloudServer(self, host, port, ca_file, auth_user, auth_password, ssh_pkey, instance_id):
    #     """
    #     Return a websocket connection to the cloud server, creating one if none exists.
    #
    #     :param host: host ip address of the cloud server
    #     :param port: port the gns3server process is listening on
    #     :param ca_file: Path to the SSL cert that the server must present
    #     :returns: a websocket connection to the cloud server
    #     """
    #
    #     for server in self._remote_servers.values():
    #         if server.host == host and int(server.port) == int(port):
    #             return server
    #
    #     heartbeat_freq = self._settings.value("heartbeat_freq", DEFAULT_HEARTBEAT_FREQ)
    #     return self._addCloudServer(host, port, ca_file, auth_user, auth_password, ssh_pkey,
    #                                 heartbeat_freq, instance_id)
    #
    # def _addCloudServer(self, host, port, ca_file, auth_user, auth_password, ssh_pkey,
    #                     heartbeat_freq, instance_id):
    #     """
    #     Create a websocket connection to the specified cloud server
    #
    #     :param host: host ip address of the server
    #     :param port: port the gns3server process is listening on
    #     :param ca_file: Path to the SSL cert that the server must present
    #     :param heartbeat_freq: The interval to send heartbeats to the server
    #
    #     :returns: a websocket connection to the cloud server
    #     """
    #
    #     url = "wss://{host}:{port}".format(host=host, port=port)
    #     log.debug('Starting SecureWebSocketClient url={}'.format(url))
    #     log.debug('Starting SecureWebSocketClient ca_file={}'.format(ca_file))
    #     log.debug('Starting SecureWebSocketClient ssh_pkey={}'.format(ssh_pkey))
    #     server = SecureWebSocketClient(url, instance_id=instance_id)
    #     server.setSecureOptions(ca_file, auth_user, auth_password, ssh_pkey)
    #     server.setCloud(True)
    #     server.enableHeartbeatsAt(heartbeat_freq)
    #     self._cloud_servers[host] = server
    #     log.info("new remote server connection {} registered".format(url))
    #     return server
    #
    # def anyCloudServer(self):
    #     # Return the first server for now
    #     for key, value in self._cloud_servers.items():
    #         return value
    #     return None
    #
    # def cloudServerById(self, instance_id):
    #     """
    #     Return the server with the specified instance id, or None.
    #     """
    #     for cs in self.cloud_servers.values():
    #         if cs.instance_id == instance_id:
    #             return cs
    #     return None
    #
    # def removeCloudServer(self, server):
    #     try:
    #         cs = self.cloud_servers[server.host]
    #         cs.close_connection()
    #         del self.cloud_servers[server.host]
    #         return True
    #     except KeyError:
    #         return False
    #
    # @property
    # def cloud_servers(self):
    #     return self._cloud_servers

    def __iter__(self):
        """
        Creates a round-robin system to pick up a remote server.
        """

        return self

    def __next__(self):
        """
        Returns the next available remote server.

        :returns: remote server (HTTPClient instance)
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
