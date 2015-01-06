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
VPCS module implementation.
"""

import os
import subprocess
import sys
import signal
import socket
import re
import pkg_resources

from gns3.qt import QtCore
from gns3.servers import Servers
from gns3.utils.get_resource import get_resource
from gns3.utils.get_default_base_config import get_default_base_config

from ..module import Module
from ..module_error import ModuleError
from .vpcs_device import VPCSDevice
from .settings import VPCS_SETTINGS, VPCS_SETTING_TYPES
from ...settings import ENABLE_CLOUD

import logging
log = logging.getLogger(__name__)


class VPCS(Module):
    """
    VPCS module.
    """

    def __init__(self):
        Module.__init__(self)

        self._settings = {}
        self._nodes = []
        self._servers = []
        self._working_dir = ""

        self._vpcs_multi_host_process = None
        self._vpcs_multi_host_port = 0

        # load the settings
        self._loadSettings()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in VPCS_SETTINGS.items():
            self._settings[name] = settings.value(name, value, type=VPCS_SETTING_TYPES[name])
        settings.endGroup()

        if not self._settings["base_script_file"]:
            self._settings["base_script_file"] = get_default_base_config(get_resource(os.path.join("configs", "vpcs_base_config.txt")))

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in self._settings.items():
            settings.setValue(name, value)
        settings.endGroup()

    def setProjectFilesDir(self, path):
        """
        Sets the project files directory path this module.

        :param path: path to the local project files directory
        """

        self._working_dir = path
        log.info("local working directory for VPCS module: {}".format(self._working_dir))

        # update the server with the new working directory / project name
        for server in self._servers:
            if server.connected():
                self._sendSettings(server)

    def setImageFilesDir(self, path):
        """
        Sets the image files directory path this module.

        :param path: path to the local image files directory
        """

        pass  # not used by this module

    def addServer(self, server):
        """
        Adds a server to be used by this module.

        :param server: WebSocketClient instance
        """

        log.info("adding server {}:{} to VPCS module".format(server.host, server.port))
        self._servers.append(server)
        self._sendSettings(server)

    def removeServer(self, server):
        """
        Removes a server from being used by this module.

        :param server: WebSocketClient instance
        """

        log.info("removing server {}:{} from VPCS module".format(server.host, server.port))
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

    def settings(self):
        """
        Returns the module settings

        :returns: module settings (dictionary)
        """

        return self._settings

    def setSettings(self, settings):
        """
        Sets the module settings

        :param settings: module settings (dictionary)
        """

        params = {}
        for name, value in settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        if params:
            for server in self._servers:
                # send the local working directory only if this is a local server
                if server.isLocal():
                    params.update({"working_dir": self._working_dir})
                else:
                    if "path" in params:
                        del params["path"]  # do not send VPCS path to remote servers
                    project_name = os.path.basename(self._working_dir)
                    if project_name.endswith("-files"):
                        project_name = project_name[:-6]
                    params.update({"project_name": project_name})
                server.send_notification("vpcs.settings", params)

        self._settings.update(settings)
        self._saveSettings()

    def _sendSettings(self, server):
        """
        Sends the module settings to the server.

        :param server: WebSocketClient instance
        """

        log.info("sending VPCS settings to server {}:{}".format(server.host, server.port))
        params = self._settings.copy()

        # do not send the base script file path.
        del params["base_script_file"]

        # send the local working directory only if this is a local server
        if server.isLocal():
            params.update({"working_dir": self._working_dir})
        else:
            if "path" in params:
                del params["path"]  # do not send VPCS path to remote servers
            project_name = os.path.basename(self._working_dir)
            if project_name.endswith("-files"):
                project_name = project_name[:-6]
            params.update({"project_name": project_name})
        server.send_notification("vpcs.settings", params)

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

    def setupNode(self, node, node_name):
        """
        Setups a node.

        :param node: Node instance
        :param node_name: Node name
        """

        log.info("configuring node {}".format(node))
        settings = {}

        script_file = self._settings["base_script_file"]
        if script_file:
            settings["script_file"] = script_file

        node.setup(None, initial_settings=settings)

    def reset(self):
        """
        Resets the servers.
        """

        log.info("vpcs module reset")
        self.stopMultiHostVPCS()
        for server in self._servers:
            if server.connected():
                server.send_notification("vpcs.reset")
        self._servers.clear()
        self._nodes.clear()

    def notification(self, destination, params):
        """
        To received notifications from the server.

        :param destination: JSON-RPC method
        :param params: JSON-RPC params
        """

        if "id" in params:
            for node in self._nodes:
                if node.id() == params["id"]:
                    message = "node {}: {}".format(node.name(), params["message"])
                    self.notification_signal.emit(message, params["details"])
                    node.stop()

    def exportConfigs(self, directory):
        """
        Exports all configs for all nodes to a directory.

        :param directory: destination directory path
        """

        for node in self._nodes:
            if node.initialized():
                node.exportConfigToDirectory(directory)

    def importConfigs(self, directory):
        """
        Imports configs to all nodes from a directory.

        :param directory: source directory path
        """

        for node in self._nodes:
            if node.initialized():
                node.importConfigFromDirectory(directory)

    def _check_vpcs_version(self, working_dir):
        """
        Checks if the VPCS executable version is >= 0.5b1.
        """

        try:
            output = subprocess.check_output([self._settings["path"], "-v"], cwd=working_dir)
            match = re.search("Welcome to Virtual PC Simulator, version ([0-9a-z\.]+)", output.decode("utf-8"))
            if match:
                version = match.group(1)
                if pkg_resources.parse_version(version) < pkg_resources.parse_version("0.5b1"):
                    raise ModuleError("VPCS executable version must be >= 0.5b1")
            else:
                raise ModuleError("Could not determine the VPCS version for {}".format(self._settings["path"]))
        except (OSError, subprocess.SubprocessError) as e:
            raise ModuleError("Error while looking for the VPCS version: {}".format(e))

    def startMultiHostVPCS(self, working_dir):
        """
        Starts a VPCS process for multi-host support.

        :param working_dir: VPCS multi-host working directory
        :return: VPCS listening port
        """

        if self._vpcs_multi_host_process and self._vpcs_multi_host_process.poll() is None:
            return self._vpcs_multi_host_port

        if not self._settings["path"]:
            raise ModuleError("No path to a VPCS executable has been set")

        if not os.path.isfile(self._settings["path"]):
            raise ModuleError("VPCS program '{}' is not accessible".format(self._settings["path"]))

        if not os.access(self._settings["path"], os.X_OK):
            raise ModuleError("VPCS program '{}' is not executable".format(self._settings["path"]))

        self._check_vpcs_version(working_dir)

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(("127.0.0.1", 0))
                self._vpcs_multi_host_port = sock.getsockname()[1]
        except OSError as e:
            raise ModuleError("Cannot get a free port: {}".format(e))

        flags = 0
        if sys.platform.startswith("win32"):
            flags = subprocess.CREATE_NEW_PROCESS_GROUP
        try:
            vpcs_command = [self._settings["path"], "-p", str(self._vpcs_multi_host_port), "-F"]
            self._vpcs_multi_host_process = subprocess.Popen(vpcs_command, cwd=working_dir, creationflags=flags)
        except (OSError, subprocess.SubprocessError) as e:
            raise ModuleError("Could not start VPCS {}".format(e))

        return self._vpcs_multi_host_port

    def stopMultiHostVPCS(self):
        """
        Stops the VPCS process for multi-host support.
        """

        if self._vpcs_multi_host_process and self._vpcs_multi_host_process.poll() is None:
            log.info("stopping VPCS multi-host instance PID={}".format(self._vpcs_multi_host_process.pid))
            if sys.platform.startswith("win32"):
                self._vpcs_multi_host_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                self._vpcs_multi_host_process.terminate()

            self._vpcs_multi_host_process.wait()

        self._vpcs_multi_host_process = None

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
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [VPCSDevice]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        server = "local"
        if not self._settings["use_local_server"]:
            # pick up a remote server (round-robin method)
            remote_server = next(iter(Servers.instance()))
            if remote_server:
                server = "{}:{}".format(remote_server.host, remote_server.port)

        nodes = []
        for node_class in VPCS.classes():
            nodes.append(
                {"class": node_class.__name__,
                 "name": node_class.symbolName(),
                 "server": server,
                 "categories": node_class.categories(),
                 "default_symbol": node_class.defaultSymbol(),
                 "hover_symbol": node_class.hoverSymbol()}
            )
            if ENABLE_CLOUD:
                nodes.append(
                    {"class": node_class.__name__,
                     "name": node_class.symbolName() + " (cloud)",
                     "server": "cloud",
                     "categories": node_class.categories(),
                     "default_symbol": node_class.defaultSymbol(),
                     "hover_symbol": node_class.hoverSymbol()}
                )
        return nodes

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        from .pages.vpcs_preferences_page import VPCSPreferencesPage
        return [VPCSPreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of VPCS module.

        :returns: instance of VPCS
        """

        if not hasattr(VPCS, "_instance"):
            VPCS._instance = VPCS()
        return VPCS._instance
