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

import urllib
import binascii

from .qt import QtNetwork, QtWidgets, QtCore
from .network_client import getNetworkUrl
from .local_config import LocalConfig
from .settings import SERVERS_SETTINGS
from .progress import Progress
from .server import Server
from .controller import Controller
from .http_client import HTTPClient

import logging
log = logging.getLogger(__name__)


class Servers(QtCore.QObject):

    """
    Server management class.
    """

    server_added_signal = QtCore.Signal(str)
    server_removed_signal = QtCore.Signal(str)

    def __init__(self):

        super().__init__()
        self._settings = {}
        self._vm_server = None
        self._controller_server = None
        self._remote_servers = {}
        self._network_manager = QtNetwork.QNetworkAccessManager()
        self._network_manager.sslErrors.connect(self._handleSslErrors)
        self._remote_server_iter_pos = 0
        self._loadSettings()


    def servers(self):
        """
        Return the list of all servers, remote, vm and local
        """
        servers = list(self._remote_servers.values())
        if self._vm_server:
            servers.append(self._vm_server)
        return servers

    def registerLocalServer(self):
        """
        Register a new local server.
        """

        local_server_settings = self._settings["local_server"]
        host = local_server_settings["host"]
        port = local_server_settings["port"]
        user = local_server_settings["user"]
        password = local_server_settings["password"]
        self._local_server = self._getServerInstance({"server_id": "local", "host": host, "port": port, "user": user, "password": password}, self._network_manager, controller=True)
        self._local_server.setLocal(True)
        self.server_added_signal.emit("local")
        log.info("New local server connection {} registered".format(self._local_server.url()))

    def _loadSettings(self):
        """
        Loads the server settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings("Servers", SERVERS_SETTINGS)

        for remote_server in self._settings["remote_servers"]:
            self._addRemoteServer(protocol=remote_server.get("protocol", "http"),
                                  host=remote_server["host"],
                                  port=remote_server["port"],
                                  user=remote_server.get("user", None),
                                  password=remote_server.get("password", None),
                                  accept_insecure_certificate=remote_server.get("accept_insecure_certificate", False))

    def _handleSslErrors(self, reply, errorList):
        """
        Called when an SSL error occur
        """

        url = reply.url().toDisplayString()
        server = self.getServerFromString(url)
        certificate = binascii.hexlify(errorList[0].certificate().digest()).decode('utf-8')
        if server.acceptInsecureCertificate() == certificate:
            reply.ignoreSslErrors()
            return

        with Progress.instance().context(enable=False):
            from .main_window import MainWindow
            main_window = MainWindow.instance()
            proceed = QtWidgets.QMessageBox.warning(
                main_window,
                "SSL Error",
                "SSL certificate for:\n {} is invalid or someone is trying to intercept the communication.\nContinue?".format(reply.url().toDisplayString()),
                QtWidgets.QMessageBox.Yes,
                QtWidgets.QMessageBox.No)

            if proceed == QtWidgets.QMessageBox.Yes:
                server.setAcceptInsecureCertificate(certificate)
                self._saveSettings()
                reply.ignoreSslErrors()
                log.info("SSL error ignored for %s", url)

    def settings(self):
        """
        Returns the servers settings.

        :returns: settings dictionary
        """

        return self._settings

    def setSettings(self, settings):
        """
        Set the servers settings.

        :param settings: settings dictionary
        """

        self._settings.update(settings)

    def vmSettings(self):
        """
        Returns the GNS3 VM settings.

        :returns: GNS3 VM settings (dict)
        """

        return self._settings["vm"]

    def setVMsettings(self, settings):
        """
        Set new GNS3 VM settings.

        :param settings: GNS3 VM settings (dict)
        """

        vm_settings = self._settings["vm"]
        vm_settings.update(settings)

    def initVMServer(self):
        """
        Initialize the GNS3 VM server.
        """

        gns3_vm_settings = self._settings["vm"]

        if gns3_vm_settings["virtualization"] == "remote":
            protocol = gns3_vm_settings["remote_vm_protocol"]
            host = gns3_vm_settings["remote_vm_host"]
            port = gns3_vm_settings["remote_vm_port"]
            user = gns3_vm_settings["remote_vm_user"]
            password = gns3_vm_settings["remote_vm_password"]
        else:
            protocol = "http"
            host = "unset"
            port = 3080  # hardcoded port for local GNS3 VM
            user = ""  # no user for local GNS3 VM
            password = ""  # no password for local GNS3 VM

        server_info = {
            "host": host,
            "port": port,
            "protocol": protocol,
            "user": user,
            "password": password
        }

        server = self._getServerInstance(server_info, self._network_manager)

        server.setLocal(False)
        server.setGNS3VM(True)
        self._vm_server = server
        self.server_added_signal.emit("vm")
        log.info("GNS3 VM server initialized {}".format(server.url()))

    def vmServer(self):
        """
        Returns the GNS3 VM server.

        :returns: Server instance
        """

        return self._vm_server

    def _addRemoteServer(self, protocol="http", host="localhost", port=3080, user=None, password=None, accept_insecure_certificate=False):
        """
        Adds a new remote server.

        :param protocol: Server protocol
        :param host: host or address of the server
        :param port: port of the server (integer)
        :param user: user login or None
        :param password: user password or None
        :param accept_insecure_certificate: Accept invalid SSL certificate

        :returns: the new remote server
        """

        server = {"host": host,
                  "port": port,
                  "protocol": protocol,
                  "user": user,
                  "password": password}
        if accept_insecure_certificate:
            server["accept_insecure_certificate"] = accept_insecure_certificate
        server = self._getServerInstance(server, self._network_manager)
        server.setLocal(False)
        self._remote_servers[server.url()] = server
        self.server_added_signal.emit(server.url())
        log.info("New remote server connection {} registered".format(server.url()))

        return server

    def _getServerInstance(self, settings, network_manager, controller=False):
        """
        Based on url return a network client instance

        :param controller: True if the server is the GNS3 controller
        """

        client = HTTPClient(settings)
        server = Server(settings, client)
        if controller:
            self._controller_server = Controller.instance()
            self._controller_server.setHttpClient(client)
        return server

    def findRemoteServer(self, protocol, host, port, user, settings={}):
        """
        Search a remote server.

        :param protocol: server protocol (http/https)
        :param host: host address
        :param port: port
        :param user: the username
        :param settings: Additional settings

        :returns: remote server (HTTPClient instance). Returns None if it doesn't exist.
        """
        url = getNetworkUrl(protocol, host, port, user, settings)
        for server in self._remote_servers.values():
            if server.url() == url:
                return server
        return None

    def getRemoteServer(self, protocol, host, port, user, settings={}):
        """
        Gets a remote server. Create a new one if it doesn't exists

        :param protocol: server protocol (http/https)
        :param host: host address
        :param port: port
        :param user: the username
        :param settings: Additional settings

        :returns: remote server (HTTPClient instance)
        """

        server = self.findRemoteServer(protocol, host, port, user, settings)
        if server:
            return server
        settings['user'] = user
        settings['protocol'] = protocol
        settings['host'] = host
        settings['port'] = port

        # Feature dropped in 1.5
        if 'ram_limit' in settings:
            del settings['ram_limit']

        return self._addRemoteServer(**settings)

    def getServerFromString(self, server_name):
        """
        Finds a server instance from its string representation.
        """

        if server_name == "local":
            return self._local_server
        elif server_name == "vm":
            return self._vm_server
        elif server_name == "load-balance":
            log.warning("Load-balancing support has been deprecated, using local server...")
            return self._local_server

        if "://" in server_name:
            for server in self.servers():
                if server.url() == server_name:
                    return server
            url_settings = urllib.parse.urlparse(server_name)
            settings = {}
            port = url_settings.port
            return self.getRemoteServer(url_settings.scheme, url_settings.hostname, port, url_settings.username, settings=settings)
        else:
            (host, port) = server_name.split(":")
            return self.getRemoteServer("http", host, port, None)

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

            new_server = self._getServerInstance(server, self._network_manager)
            new_server.setLocal(False)
            self._remote_servers[server_id] = new_server
            self.server_added_signal.emit(new_server.url())
            log.info("New remote server connection {} registered".format(new_server.url()))

    def remoteServers(self):
        """
        Returns all the remote servers.

        :returns: remote servers dictionary
        """

        return self._remote_servers

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

        if not self._remote_servers or len(self._remote_servers) == 0:
            return None

        server_ids = list(self._remote_servers.keys())
        try:
            server_id = server_ids[self._remote_server_iter_pos]
        except IndexError:
            self._remote_server_iter_pos = 0
            server_id = server_ids[0]

        if self._remote_server_iter_pos < len(server_ids) - 1:
            self._remote_server_iter_pos += 1
        else:
            self._remote_server_iter_pos = 0

        return self._remote_servers[server_id]

    def save(self):
        """
        Saves the settings.
        """
        pass

    def isNonLocalServerConfigured(self):
        """
        :returns: True if GNS3 VM or a remote server is configured
        """
        if self._vm_server is not None:
            return True
        if len(self._remote_servers) > 0:
            return True
        return False

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of Servers.

        :returns: instance of Servers
        """

        if not hasattr(Servers, "_instance") or Servers._instance is None:
            Servers._instance = Servers()
        return Servers._instance
