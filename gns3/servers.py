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
import stat
import struct
import psutil

from .qt import QtNetwork, QtWidgets, QtCore
from .network_client import getNetworkUrl
from .local_config import LocalConfig
from .settings import SERVERS_SETTINGS
from .local_server_config import LocalServerConfig
from .progress import Progress
from .utils.sudo import sudo

from collections import OrderedDict

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
        self._local_server = None
        self._vm_server = None
        self._remote_servers = {}
        self._local_server_path = ""
        self._local_server_auto_start = True
        self._local_server_allow_console_from_anywhere = False
        self._local_server_process = None
        self._network_manager = QtNetwork.QNetworkAccessManager()
        self._network_manager.sslErrors.connect(self._handleSslErrors)
        self._remote_server_iter_pos = 0
        self._loadSettings()
        self._pid_path = os.path.join(LocalConfig.configDirectory(), "gns3_server.pid")
        self.registerLocalServer()

    def servers(self):
        """
        Return the list of all servers, remote, vm and local
        """
        servers = list(self._remote_servers.values())
        if self._local_server:
            servers.append(self._local_server)
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
        self._local_server = self.getNetworkClientInstance({"host": host, "port": port, "user": user, "password": password},
                                                      self._network_manager)
        self._local_server.setLocal(True)
        self.server_added_signal.emit("local")
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
        path = os.path.abspath(ubridge_path)
        return path

    def _checkUbridgePermissions(self):
        """
        Checks that uBridge can interact with network interfaces.
        """

        path = self._settings["local_server"]["ubridge_path"]

        if not path or len(path) == 0 or not os.path.exists(path):
            return False

        if sys.platform.startswith("win"):
            # do not check anything on Windows
            return True

        if os.geteuid() == 0:
            # we are root, so we should have privileged access.
            return True

        from .main_window import MainWindow
        main_window = MainWindow.instance()

        request_setuid = False
        if sys.platform.startswith("linux"):
            # test if the executable has the CAP_NET_RAW capability (Linux only)
            try:
                if "security.capability" in os.listxattr(path):
                    caps = os.getxattr(path, "security.capability")
                    # test the 2nd byte and check if the 13th bit (CAP_NET_RAW) is set
                    if not struct.unpack("<IIIII", caps)[1] & 1 << 13:
                        proceed = QtWidgets.QMessageBox.question(
                            main_window,
                            "uBridge",
                            "uBridge requires CAP_NET_RAW capability to interact with network interfaces. Set the capability to uBridge?",
                            QtWidgets.QMessageBox.Yes,
                            QtWidgets.QMessageBox.No)
                        if proceed == QtWidgets.QMessageBox.Yes:
                            sudo(["setcap", "cap_net_admin,cap_net_raw=ep"])
                else:
                    # capabilities not supported
                    request_setuid = True
            except OSError as e:
                QtWidgets.QMessageBox.critical(main_window, "uBridge", "Can't set CAP_NET_RAW capability to uBridge {}: {}".format(path, str(e)))
                return False

        if sys.platform.startswith("darwin") or request_setuid:
            try:
                if os.stat(path).st_uid != 0 or not os.stat(path).st_mode & stat.S_ISUID:
                    proceed = QtWidgets.QMessageBox.question(
                        main_window,
                        "uBridge",
                        "uBridge requires root permissions to interact with network interfaces. Set root permissions to uBridge?",
                        QtWidgets.QMessageBox.Yes,
                        QtWidgets.QMessageBox.No)
                    if proceed == QtWidgets.QMessageBox.Yes:
                        sudo(["chmod", "4755", path])
                        sudo(["chown", "root", path])
            except OSError as e:
                QtWidgets.QMessageBox.critical(main_window, "uBridge", "Can't set root permissions to uBridge {}: {}".format(path, str(e)))
                return False
        return True

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
                                  user=remote_server.get("user", None),
                                  password=remote_server.get("password", None),
                                  accept_insecure_certificate=remote_server.get("accept_insecure_certificate", False))

        changed = False
        if "user" not in local_server_settings or len(local_server_settings["user"]) == 0:
            local_server_settings["user"] = self._passwordGenerate()
            local_server_settings["password"] = self._passwordGenerate()
            changed = True

        # For 1.3 compatibity old LocalServer section
        local_server = LocalConfig.instance().loadSectionSettings("LocalServer", {})
        if "auth" in local_server:
            local_server["auth"] = local_server_settings["auth"]
            local_server["user"] = local_server_settings["user"]
            local_server["password"] = local_server_settings["password"]
            LocalConfig.instance().saveSectionSettings("LocalServer", local_server)
            changed = True

        # WARNING: This operation should be a the end of the method otherwise you save a partial config
        if changed:
            self._saveSettings()

    def _saveSettings(self):
        """
        Saves the server settings to a persistent settings file.
        """

        # Save the remote servers
        # And emit signal for each server removed
        old_server_urls = [ s["url"] for s in self._settings["remote_servers"] ]
        self._settings["remote_servers"] = []
        for server in self._remote_servers.values():
            settings = server.settings()
            settings["url"] = server.url()
            self._settings["remote_servers"].append(settings)
            if settings["url"] in old_server_urls:
                old_server_urls.remove(settings["url"])

        for old_server_url in old_server_urls:
            self.server_removed_signal.emit(old_server_url)
        old_server_urls = []

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

    def shouldLocalServerAutoStart(self):
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

    def _killAlreadyRunningServer(self):
        """
        Kill a running zombie server (started by a gui that no longer exists)
        This will not kill server started by hand.
        """
        try:
            if os.path.exists(self._pid_path):
                with open(self._pid_path) as f:
                    pid = int(f.read())
                process = psutil.Process(pid=pid)
                log.info("Kill already running server with PID %d", pid)
                process.kill()
        except (OSError, ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
            # Permission issue, or process no longer exists, or file is empty
            return

    def localServerAutoStart(self):
        """
        Try to start the embed gns3 server.
        """

        # We check if two gui are not launched at the same time
        # to avoid killing the server of the other GUI
        if not LocalConfig.isMainGui():
           log.info("Not the main GUI, will not autostart the server")
           return True

        if self.localServer().isLocalServerRunning():
            log.info("A local server already running on this host")
            # Try to kill the server. The server can be still running after
            # if the server was started by hand
            self._killAlreadyRunningServer()

        if not self.localServer().isLocalServerRunning():
            if not self.initLocalServer():
                return False
            if not self.startLocalServer():
                return False
        return True

    def initLocalServer(self):
        """
        Initialize the local server.
        """

        from .main_window import MainWindow
        main_window = MainWindow.instance()

        self._checkUbridgePermissions()

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
            log.warning("The server port {} is already in use, fallback to port {}".format(old_port, server.port()))
            print("The server port {} is already in use, fallback to port {}".format(old_port, server.port()))
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
        command = '"{executable}" --host={host} --port={port} --local --controller'.format(executable=path,
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
            command += ' --log="{}" --pid="{}"'.format(logpath, self._pid_path)

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

        try:
            if self._local_server_process and self._local_server_process.poll() is None:
                return True
        except OSError:
            pass
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
                    try:
                        if sys.platform.startswith("win"):
                            self._local_server_process.send_signal(signal.CTRL_BREAK_EVENT)
                        else:
                            self._local_server_process.send_signal(signal.SIGINT)
                    # If the process is already dead we received a permission error
                    # it's a race condition between the timeout and send signal
                    except PermissionError:
                        pass
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

        server = self.getNetworkClientInstance(server_info, self._network_manager)
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
        server = self.getNetworkClientInstance(server, self._network_manager)
        server.setLocal(False)
        self._remote_servers[server.url()] = server
        self.server_added_signal.emit(server.url())
        log.info("New remote server connection {} registered".format(server.url()))

        return server

    def getNetworkClientInstance(self, settings, network_manager):
        """
        Based on url return a network client instance
        """

        from gns3.http_client import HTTPClient
        client = HTTPClient(settings, network_manager)
        return client

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

            new_server = self.getNetworkClientInstance(server, self._network_manager)
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

        self._saveSettings()

    def disconnectAllServers(self):
        """
        Disconnects all servers (local and remote).
        """

        if self._local_server.connected():
            self._local_server.close()
        if self._vm_server is not None and self._vm_server.connected():
            self._vm_server.close()
        for server in self._remote_servers.values():
            if server.connected():
                server.close()

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
