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
VirtualBox module implementation.
"""

import os
from gns3.qt import QtCore, QtGui
from gns3.servers import Servers
from ..module import Module
from ..module_error import ModuleError
from .virtualbox_vm import VirtualBoxVM
from .settings import VBOX_SETTINGS, VBOX_SETTING_TYPES

import logging
log = logging.getLogger(__name__)


class VirtualBox(Module):
    """
    VirtualBox module.
    """

    def __init__(self):
        Module.__init__(self)

        self._settings = {}
        self._virtualbox_vms = {}
        self._nodes = []
        self._servers = []
        self._working_dir = ""

        # load the settings
        self._loadSettings()
        self._loadVirtualBoxVMs()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in VBOX_SETTINGS.items():
            self._settings[name] = settings.value(name, value, type=VBOX_SETTING_TYPES[name])
        settings.endGroup()

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

    def _loadVirtualBoxVMs(self):
        """
        Load the VirtualBox VMs from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup("VirtualBoxVMs")

        # load the VMs
        size = settings.beginReadArray("VM")
        for index in range(0, size):
            settings.setArrayIndex(index)

            name = settings.value("name", "")
            adapters = settings.value("adapters", 1, type=int)
            console_support = settings.value("console_support", True, type=bool)
            console_server = settings.value("console_server", False, type=bool)
            headless = settings.value("headless", False, type=bool)
            server = settings.value("server", "local")

            key = "{server}:{name}".format(server=server, name=name)
            self._virtualbox_vms[key] = {"name": name,
                                         "adapters": adapters,
                                         "console_support": console_support,
                                         "console_server": console_server,
                                         "headless": headless,
                                         "server": server}

        settings.endArray()
        settings.endGroup()

    def _saveVirtualBoxVMs(self):
        """
        Saves the VirtualBox VMs to the persistent settings file.
        """

        # save the settings
        settings = QtCore.QSettings()
        settings.beginGroup("VirtualBoxVMs")
        settings.remove("")

        # save the IOU images
        settings.beginWriteArray("VM", len(self._virtualbox_vms))
        index = 0
        for vbox_vm in self._virtualbox_vms.values():
            settings.setArrayIndex(index)
            for name, value in vbox_vm.items():
                settings.setValue(name, value)
            index += 1
        settings.endArray()
        settings.endGroup()

    def virtualBoxVMs(self):
        """
        Returns VirtualBox VMs settings.

        :returns: VirtualBox VMs settings (dictionary)
        """

        return self._virtualbox_vms

    def setVirtualBoxVMs(self, new_virtualbox_vms):
        """
        Sets IOS images settings.

        :param new_iou_images: IOS images settings (dictionary)
        """

        self._virtualbox_vms = new_virtualbox_vms.copy()
        self._saveVirtualBoxVMs()

    def setProjectFilesDir(self, path):
        """
        Sets the project files directory path this module.

        :param path: path to the local project files directory
        """

        self._working_dir = path
        log.info("local working directory for VirtualBox module: {}".format(self._working_dir))

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

        log.info("adding server {}:{} to VirtualBox module".format(server.host, server.port))
        self._servers.append(server)
        self._sendSettings(server)

    def removeServer(self, server):
        """
        Removes a server from being used by this module.

        :param server: WebSocketClient instance
        """

        log.info("removing server {}:{} from VirtualBox module".format(server.host, server.port))
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
                    project_name = os.path.basename(self._working_dir)
                    if project_name.endswith("-files"):
                        project_name = project_name[:-6]
                    params.update({"project_name": project_name})
                server.send_notification("virtualbox.settings", params)

        self._settings.update(settings)
        self._saveSettings()

    def _sendSettings(self, server):
        """
        Sends the module settings to the server.

        :param server: WebSocketClient instance
        """

        log.info("sending VirtualBox settings to server {}:{}".format(server.host, server.port))
        params = self._settings.copy()

        # send the local working directory only if this is a local server
        if server.isLocal():
            params.update({"working_dir": self._working_dir})
        else:
            if "vboxwrapper_path" in params:
                del params["vboxwrapper_path"]  # do not send VPCS path to remote servers
            project_name = os.path.basename(self._working_dir)
            if project_name.endswith("-files"):
                project_name = project_name[:-6]
            params.update({"project_name": project_name})
        server.send_notification("virtualbox.settings", params)

    def allocateServer(self, node_class):
        """
        Allocates a server.

        :param node_class: Node object

        :returns: allocated server (WebSocketClient instance)
        """

        # allocate a server for the node
        servers = Servers.instance()
        if self._settings["use_local_server"]:
            # use the local server
            server = servers.localServer()
        else:
            # pick up a remote server (round-robin method)
            server = next(iter(servers))
            if not server:
                raise ModuleError("No remote server is configured")
        return server

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
        settings = {}

        node.setup(None, initial_settings=settings)

    def reset(self):
        """
        Resets the servers.
        """

        log.info("VirtualBox module reset")
        for server in self._servers:
            if server.connected():
                server.send_notification("virtualbox.reset")
        self._servers.clear()

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

        return [VirtualBoxVM]

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        from .pages.virtualbox_preferences_page import VirtualBoxPreferencesPage
        from .pages.virtualbox_vm_preferences_page import VirtualBoxVMPreferencesPage
        return [VirtualBoxPreferencesPage, VirtualBoxVMPreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of VirtualBox module.

        :returns: instance of VirtualBox
        """

        if not hasattr(VirtualBox, "_instance"):
            VirtualBox._instance = VirtualBox()
        return VirtualBox._instance
