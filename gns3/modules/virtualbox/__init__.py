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
from gns3.node import Node
from ..module import Module
from ..module_error import ModuleError
from .virtualbox_vm import VirtualBoxVM
from .settings import VBOX_SETTINGS, VBOX_SETTING_TYPES
from .settings import VBOX_VM_SETTINGS, VBOX_VM_SETTING_TYPES

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
        self._virtualbox_vm_list = {}

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
            vmname = settings.value("vmname")
            server = settings.value("server")
            key = "{server}:{vmname}".format(server=server, vmname=vmname)
            if key in self._virtualbox_vms or not vmname or not server:
                continue
            self._virtualbox_vms[key] = {}
            for setting_name, default_value in VBOX_VM_SETTINGS.items():
                self._virtualbox_vms[key][setting_name] = settings.value(setting_name, default_value, VBOX_VM_SETTING_TYPES[setting_name])

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

        # save the VirtualBox VMs
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
        Sets VirtualBox VM settings.

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
                    if "vboxmanage_path" in params:
                        del params["vboxmanage_path"]  # do not send VBoxManage path to remote servers
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
            if "vboxmanage_path" in params:
                del params["vboxmanage_path"]  # do not send VBoxManage path to remote servers
            project_name = os.path.basename(self._working_dir)
            if project_name.endswith("-files"):
                project_name = project_name[:-6]
            params.update({"project_name": project_name})
        server.send_notification("virtualbox.settings", params)

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

        log.info("configuring node {} with id {}".format(node, node.id()))

        vm = None
        if node_name:
            for vm_key, info in self._virtualbox_vms.items():
                if node_name == info["vmname"]:
                    vm = vm_key

        if not vm:
            selected_vms = []
            for vm, info in self._virtualbox_vms.items():
                if info["server"] == node.server().host or (node.server().isLocal() and info["server"] == "local"):
                    selected_vms.append(vm)

            if not selected_vms:
                raise ModuleError("No VirtualBox VM on server {}".format(node.server().host))
            elif len(selected_vms) > 1:

                from gns3.main_window import MainWindow
                mainwindow = MainWindow.instance()

                (selection, ok) = QtGui.QInputDialog.getItem(mainwindow, "VirtualBox VM", "Please choose a VM", selected_vms, 0, False)
                if ok:
                    vm = selection
                else:
                    raise ModuleError("Please select a VirtualBox VM")

            else:
                vm = selected_vms[0]

        linked_base = self._virtualbox_vms[vm]["linked_base"]

        if not linked_base:
            for other_node in self._nodes:
                if other_node.settings()["vmname"] == self._virtualbox_vms[vm]["vmname"] and \
                        (self._virtualbox_vms[vm]["server"] == "local" and other_node.server().isLocal() or self._virtualbox_vms[vm]["server"] == other_node.server().host):
                    raise ModuleError("Sorry a VirtualBox VM can only be used once in your topology (this will change in future versions)")

        settings = {"adapters": self._virtualbox_vms[vm]["adapters"],
                    "adapter_start_index": self._virtualbox_vms[vm]["adapter_start_index"],
                    "adapter_type": self._virtualbox_vms[vm]["adapter_type"],
                    "headless": self._virtualbox_vms[vm]["headless"],
                    "enable_remote_console": self._virtualbox_vms[vm]["enable_remote_console"]}

        vmname = self._virtualbox_vms[vm]["vmname"]
        node.setup(vmname, linked_clone=linked_base, initial_settings=settings)

    def reset(self):
        """
        Resets the servers.
        """

        log.info("VirtualBox module reset")
        for server in self._servers:
            if server.connected():
                server.send_notification("virtualbox.reset")
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

    def getVirtualBoxVMsFromServer(self, server, callback):
        """
        Gets the VirtualBox VM list from a server.

        :param server: server to send the request to
        :param callback: callback for the reply from the server
        """

        if not server.connected():
            try:
                log.info("reconnecting to server {}:{}".format(server.host, server.port))
                server.reconnect()
            except OSError as e:
                raise ModuleError("Could not connect to server {}:{}: {}".format(server.host,
                                                                                 server.port,
                                                                                 e))
        params = {}
        if server.isLocal():
            params["vboxmanage_path"] = self._settings["vboxmanage_path"]
        server.send_message("virtualbox.vm_list", params, callback)

    def getVirtualBoxVMList(self):
        """
        Returns the list of VirtualBox VMs

        :return: dict
        """

        return self._virtualbox_vm_list

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

        return [VirtualBoxVM]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        nodes = []
        for vbox_vm in self._virtualbox_vms.values():
            nodes.append(
                {"class": VirtualBoxVM.__name__,
                 "name": vbox_vm["vmname"],
                 "server": vbox_vm["server"],
                 "categories": VirtualBoxVM.categories(),
                 "default_symbol": vbox_vm["default_symbol"],
                 "hover_symbol": vbox_vm["hover_symbol"],
                 "categories": [vbox_vm["category"]]}
            )
        return nodes

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
        Singleton to return only one instance of VirtualBox module.

        :returns: instance of VirtualBox
        """

        if not hasattr(VirtualBox, "_instance"):
            VirtualBox._instance = VirtualBox()
        return VirtualBox._instance
