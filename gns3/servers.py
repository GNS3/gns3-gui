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
import urllib
import shutil
import string
import random
import socket
import subprocess
import binascii

from .qt import QtNetwork, QtWidgets
from .network_client import getNetworkClientInstance, getNetworkUrl
from .local_config import LocalConfig
from .settings import SERVERS_SETTINGS
from .local_server_config import LocalServerConfig
from .progress import Progress
from collections import OrderedDict

import logging
log = logging.getLogger(__name__)


class Servers():

    """
    Server management class.
    """

    def __init__(self):

        self._settings = {}
        self._local_server = None
        self._vm_server = None
        self._remote_servers = {}
        self._cloud_servers = {}
        self._local_server_path = ""
        self._local_server_auto_start = True
        self._local_server_allow_console_from_anywhere = False
        self._local_server_process = None
        self._network_manager = QtNetwork.QNetworkAccessManager()
        self._network_manager.sslErrors.connect(self._handleSslErrors)
        self._remote_server_iter_pos = 0
        self._loadSettings()
        self.registerLocalServer()

    def registerLocalServer(self):
        """
        Register a new local server.
        """

        local_server_settings = self._settings["local_server"]
        host = local_server_settings["host"]
        port = local_server_settings["port"]
        user = local_server_settings["user"]
        password = local_server_settings["password"]
        self._local_server = getNetworkClientInstance({"host": host, "port": port, "user": user, "password": password},
                                                      self._network_manager)
        self._local_server.setLocal(True)
        log.info("New local server connection {} registered".format(self._local_server.url()))

    @staticmethod
    def _findLocalServer(self):
        """
        Finds the local server path.

        :return: path to the local server
        """

        local_server_path = shutil.which("gns3server")

        if local_server_path is None:
            return ""
        return os.path.abspath(local_server_path)

    @staticmethod
    def _findUbridge(self):
        """
        Finds the ubridge executable path.

        :return: path to the ubridge
        """

        ubridge_path = shutil.which("ubridge")

        if ubridge_path is None:
            return ""
        return os.path.abspath(ubridge_path)

    def _handleSslErrors(self, reply, errorList):
        """
        Called when an SSL error occur
        """

        server = self.getServerFromString(reply.url().toDisplayString())
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
                log.info("SSL error ignored for %s", reply.url().toDisplayString())

    def _passwordGenerate(self):
        """
        Generate a random password
        """
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(64))

    def _loadSettings(self):
        """
        Loads the server settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings("Servers", SERVERS_SETTINGS)

        local_server_settings = self._settings["local_server"]
        if not os.path.exists(local_server_settings["path"]):
            local_server_settings["path"] = self._findLocalServer(self)

        if not os.path.exists(local_server_settings["ubridge_path"]):
            local_server_settings["ubridge_path"] = self._findUbridge(self)

        for remote_server in self._settings["remote_servers"]:
            self._addRemoteServer(protocol=remote_server.get("protocol", "http"),
                                  host=remote_server["host"],
                                  port=remote_server["port"],
                                  ram_limit=remote_server.get("ram_limit", 0),
                                  user=remote_server.get("user", None),
                                  ssh_key=remote_server.get("ssh_key", None),
                                  ssh_port=remote_server.get("ssh_port", None),
                                  accept_insecure_certificate=remote_server.get("accept_insecure_certificate", False))

        if "user" not in local_server_settings or len(local_server_settings["user"]) == 0:
            local_server_settings["user"] = self._passwordGenerate()
            local_server_settings["password"] = self._passwordGenerate()
            #WARNING: This operation should be a the end of the method otherwise you save a partial config
            self._saveSettings()

    def _saveSettings(self):
        """
        Saves the server settings to a persistent settings file.
        """

        # save the remote servers
        self._settings["remote_servers"] = []
        for server in self._remote_servers.values():
            self._settings["remote_servers"].append(server.settings())

        # save the settings
        LocalConfig.instance().saveSectionSettings("Servers", self._settings)

        # save some settings to the local server config files
        local_server_settings = self._settings["local_server"]
        server_settings = OrderedDict([
            ("host", local_server_settings["host"]),
            ("port", local_server_settings["port"]),
            ("ubridge_path", local_server_settings["ubridge_path"]),
            ("auth", local_server_settings.get("auth", False)),
            ("user", local_server_settings.get("user", "")),
            ("password", local_server_settings.get("password", "")),
            ("images_path", local_server_settings["images_path"]),
            ("projects_path", local_server_settings["projects_path"]),
            ("configs_path", local_server_settings["configs_path"]),
            ("console_start_port_range", local_server_settings["console_start_port_range"]),
            ("console_end_port_range", local_server_settings["console_end_port_range"]),
            ("udp_start_port_range", local_server_settings["udp_start_port_range"]),
            ("udp_start_end_range", local_server_settings["udp_end_port_range"]),
            ("report_errors", local_server_settings["report_errors"]),
        ])
        config = LocalServerConfig.instance()
        config.saveSettings("Server", server_settings)

        if self._local_server and self._local_server.connected():
            self._local_server.post("/config/reload", None)

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

    def localServerSettings(self):
        """
        Returns the local server settings.

        :returns: local server settings (dict)
        """

        return self._settings["local_server"]

    def setLocalServerSettings(self, settings):
        """
        Set new local server settings.

        :param settings: local server settings (dict)
        """

        local_server_settings = self._settings["local_server"]
        local_server_settings.update(settings)

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

    def localServerAutoStart(self):
        """
        Returns either the local server
        is automatically started on startup.

        :returns: boolean
        """

        return self._settings["local_server"]["auto_start"]

    def localServerPath(self):
        """
        Returns the local server path.

        :returns: path to local server program.
        """

        return self._settings["local_server"]["path"]

    def initLocalServer(self):
        """
        Initialize the local server.
        """

        from .main_window import MainWindow
        main_window = MainWindow.instance()

        # check the local server path
        local_server_path = self.localServerPath()
        server = self.localServer()
        if not local_server_path:
            log.warn("No local server is configured")
            return
        if not os.path.isfile(local_server_path):
            QtWidgets.QMessageBox.critical(main_window, "Local server", "Could not find local server {}".format(local_server_path))
            return
        elif not os.access(local_server_path, os.X_OK):
            QtWidgets.QMessageBox.critical(main_window, "Local server", "{} is not an executable".format(local_server_path))
            return

        try:
            # check if the local address still exists
            for res in socket.getaddrinfo(server.host(), 0, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
                af, socktype, proto, _, sa = res
                with socket.socket(af, socktype, proto) as sock:
                    sock.bind(sa)
                    break
        except OSError as e:
            QtWidgets.QMessageBox.critical(main_window, "Local server", "Could not bind with {}: {} (please check your host binding setting in the preferences)".format(server.host(), e))
            return False

        try:
            # check if the port is already taken
            find_unused_port = False
            for res in socket.getaddrinfo(server.host(), server.port(), socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
                af, socktype, proto, _, sa = res
                with socket.socket(af, socktype, proto) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(sa)
                    break
        except OSError as e:
            log.warning("Could not use socket {}:{} {}".format(server.host(), server.port(), e))
            find_unused_port = True

        if find_unused_port:
            # find an alternate port for the local server
            old_port = server.port()
            try:
                server.setPort(self._findUnusedLocalPort(server.host()))
            except OSError as e:
                QtWidgets.QMessageBox.critical(main_window, "Local server", "Could not find an unused port for the local server: {}".format(e))
                return False
            log.warning("The server port {} is already in use, fallback to port {}".format(old_port, server.port()))
            print("The server port {} is already in use, fallback to port {}".format(old_port, server.port()))
        return True

    def _findUnusedLocalPort(self, host):
        """
        Find an unused port.

        :param host: server hosts

        :returns: port number
        """

        with socket.socket() as s:
            s.bind((host, 0))
            return s.getsockname()[1]

    def startLocalServer(self):
        """
        Starts the local server process.
        """

        path = self.localServerPath()
        host = self._local_server.host()
        port = self._local_server.port()
        command = '"{executable}" --host={host} --port={port} --local'.format(executable=path,
                                                                              host=host,
                                                                              port=port)

        if self._settings["local_server"]["allow_console_from_anywhere"]:
            # allow connections to console from remote addresses
            command += " --allow"

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            command += " --debug"

        settings_dir = LocalConfig.configDirectory()
        if os.path.isdir(settings_dir):
            # save server logging info to a file in the settings directory
            logpath = os.path.join(settings_dir, "gns3_server.log")
            if os.path.isfile(logpath):
                # delete the previous log file
                try:
                    os.remove(logpath)
                except FileNotFoundError:
                    pass
                except OSError as e:
                    log.warn("could not delete server log file {}: {}".format(logpath, e))
            command += ' --log="{}"'.format(logpath)

        log.info("Starting local server process with {}".format(command))
        try:
            if sys.platform.startswith("win"):
                # use the string on Windows
                self._local_server_process = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                # use arguments on other platforms
                args = shlex.split(command)
                self._local_server_process = subprocess.Popen(args)
        except (OSError, subprocess.SubprocessError) as e:
            log.warning('Could not start local server "{}": {}'.format(command, e))
            return False

        log.info("Local server process has started (PID={})".format(self._local_server_process.pid))
        return True

    def localServerIsRunning(self):
        """
        Returns either the local server is running.

        :returns: boolean
        """

        if self._local_server_process and self._local_server_process.poll() is None:
            return True
        return False

    def stopLocalServer(self, wait=False):
        """
        Stops the local server.

        :param wait: wait for the server to stop
        """

        if self.localServerIsRunning():
            log.info("Stopping local server (PID={})".format(self._local_server_process.pid))
            # local server is running, let's stop it
            if wait:
                try:
                    # wait for the server to stop for maximum 2 seconds
                    self._local_server_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    # the local server couldn't be stopped with the normal procedure
                    if sys.platform.startswith("win"):
                        try:
                            self._local_server_process.send_signal(signal.CTRL_BREAK_EVENT)
                        # If the process is already dead we received a permission error
                        # it's a race condition between the timeout and send signal
                        except PermissionError:
                            pass
                    else:
                        self._local_server_process.send_signal(signal.SIGINT)
                    try:
                        # wait for the server to stop for maximum 2 seconds
                        self._local_server_process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        from .main_window import MainWindow
                        main_window = MainWindow.instance()
                        proceed = QtWidgets.QMessageBox.question(main_window,
                                                                 "Local server",
                                                                 "The Local server cannot be stopped, would you like to kill it?",
                                                                 QtWidgets.QMessageBox.Yes,
                                                                 QtWidgets.QMessageBox.No)

                        if proceed == QtWidgets.QMessageBox.Yes:
                            self._local_server_process.kill()

    def localServer(self):
        """
        Returns the local server.

        :returns: Server instance
        """

        return self._local_server

    def initVMServer(self):
        """
        Initialize the GNS3 VM server.
        """

        gns3_vm_settings = self._settings["vm"]
        server_info = {
            "host": "unset",
            "port": gns3_vm_settings["server_port"],
            "protocol": "http",
            "user": gns3_vm_settings["user"],
            "password": gns3_vm_settings["password"]
        }
        server = getNetworkClientInstance(server_info, self._network_manager)
        server.setLocal(False)
        server.setGNS3VM(True)
        self._vm_server = server
        log.info("GNS3 VM server initialized {}".format(server.url()))

    def vmServer(self):
        """
        Returns the GNS3 VM server.

        :returns: Server instance
        """

        return self._vm_server

    def _addRemoteServer(self, protocol="http", host="localhost", port=8000, ram_limit=0, user=None, ssh_port=None, ssh_key=None, accept_insecure_certificate=False, id=None):
        """
        Adds a new remote server.

        :param protocol: Server protocol
        :param host: host or address of the server
        :param port: port of the server (integer)
        :param ram_limit: maximum RAM to be used (integer)
        :param user: user login or None
        :param ssh_port: ssh port or None
        :param ssh_key: ssh key
        :param accept_insecure_certificate: Accept invalid SSL certificate

        :returns: the new remote server
        """

        server = {"host": host,
                  "port": port,
                  "ram_limit": ram_limit,
                  "protocol": protocol,
                  "user": user,
                  "ssh_port": ssh_port,
                  "ssh_key": ssh_key}
        if accept_insecure_certificate:
            server["accept_insecure_certificate"] = accept_insecure_certificate
        server = getNetworkClientInstance(server, self._network_manager)
        server.setLocal(False)
        self._remote_servers[server.url()] = server
        log.info("New remote server connection {} registered".format(server.url()))

        return server

    def getRemoteServer(self, protocol, host, port, user, settings={}):
        """
        Gets a remote server.

        :param protocol: server protocol (http/ssh)
        :param host: host address
        :param port: port
        :param user: the username
        :param settings: Additional settings

        :returns: remote server (HTTPClient instance)
        """

        url = getNetworkUrl(protocol, host, port, user, settings)
        for server in self._remote_servers.values():
            if server.url() == url:
                return server

        settings['user'] = user
        settings['protocol'] = protocol
        settings['host'] = host
        settings['port'] = port
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
            return self.anyRemoteServer()

        if "://" in server_name:
            url_settings = urllib.parse.urlparse(server_name)
            if url_settings.scheme == "ssh":
                _, ssh_port, port = url_settings.netloc.split(":")
                settings = {"ssh_port": int(ssh_port)}
            else:
                settings = {}
                port = url_settings.port
            return self.getRemoteServer(url_settings.scheme, url_settings.hostname, port, url_settings.username, settings=settings)
        else:
            (host, port) = server_name.split(":")
            return self.getRemoteServer("http", host, port, None)

    def anyRemoteServer(self, ram=0):
        """
        Returns a remote server for load balancing.

        :param ram: RAM amount to be allocated by the node

        :returns: remote server (HTTPClient instance)
        """

        if self._settings["load_balancing_method"] == "ram_usage":
            for server in self._remote_servers.values():
                if not server.RAMLimit():
                    return server
                if (server.allocatedRAM() + ram) <= server.RAMLimit():
                    if ram > 0:
                        server.increaseAllocatedRAM(ram)
                    return server
        elif self._settings["load_balancing_method"] == "round_robin":
            return next(iter(self))
        return next(iter(self))  # default is Round-Robin

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

            new_server = getNetworkClientInstance(server, self._network_manager)
            new_server.setLocal(False)
            self._remote_servers[server_id] = new_server
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

        self._saveSettings()

    def disconnectAllServers(self):
        """
        Disconnects all servers (local and remote).
        """

        if self._local_server.connected():
            self._local_server.close()
        for server in self._remote_servers.values():
            if server.connected():
                server.close()

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of Servers.

        :returns: instance of Servers
        """

        if not hasattr(Servers, "_instance") or Servers._instance is None:
            Servers._instance = Servers()
        return Servers._instance
