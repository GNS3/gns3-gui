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
QEMU module implementation.
"""

import os

from gns3.qt import QtCore, QtGui
from gns3.node import Node

from ..module import Module
from ..module_error import ModuleError
from .qemu_vm import QemuVM
from .settings import QEMU_SETTINGS, QEMU_SETTING_TYPES
from .settings import QEMU_VM_SETTINGS, QEMU_VM_SETTING_TYPES

import logging
log = logging.getLogger(__name__)


class Qemu(Module):
    """
    QEMU module.
    """

    def __init__(self):
        Module.__init__(self)

        self._settings = {}
        self._qemu_vms = {}
        self._nodes = []
        self._servers = []
        self._working_dir = ""

        # load the settings
        self._loadSettings()
        self._loadQemuVMs()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in QEMU_SETTINGS.items():
            self._settings[name] = settings.value(name, value, type=QEMU_SETTING_TYPES[name])
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

    def _loadQemuVMs(self):
        """
        Load the QEMU VMs from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup("QemuVMs")

        # load the VMs
        size = settings.beginReadArray("VM")
        for index in range(0, size):
            settings.setArrayIndex(index)
            name = settings.value("name")
            server = settings.value("server")
            key = "{server}:{name}".format(server=server, name=name)
            if key in self._qemu_vms or not name or not server:
                continue
            self._qemu_vms[key] = {}
            for setting_name, default_value in QEMU_VM_SETTINGS.items():
                self._qemu_vms[key][setting_name] = settings.value(setting_name, default_value, QEMU_VM_SETTING_TYPES[setting_name])

        settings.endArray()
        settings.endGroup()

    def _saveQemuVMs(self):
        """
        Saves the QEMU VMs to the persistent settings file.
        """

        # save the settings
        settings = QtCore.QSettings()
        settings.beginGroup("QemuVMs")
        settings.remove("")

        # save the Qemu VMs
        settings.beginWriteArray("VM", len(self._qemu_vms))
        index = 0
        for qemu_vm in self._qemu_vms.values():
            settings.setArrayIndex(index)
            for name, value in qemu_vm.items():
                settings.setValue(name, value)
            index += 1
        settings.endArray()
        settings.endGroup()

    def qemuVMs(self):
        """
        Returns QEMU VMs settings.

        :returns: QEMU VMs settings (dictionary)
        """

        return self._qemu_vms

    def setQemuVMs(self, new_qemu_vms):
        """
        Sets QEMU VM settings.

        :param new_iou_images: IOS images settings (dictionary)
        """

        self._qemu_vms = new_qemu_vms.copy()
        self._saveQemuVMs()

    def setProjectFilesDir(self, path):
        """
        Sets the project files directory path this module.

        :param path: path to the local project files directory
        """

        self._working_dir = path
        log.info("local working directory for QEMU module: {}".format(self._working_dir))

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

        log.info("adding server {}:{} to QEMU module".format(server.host, server.port))
        self._servers.append(server)
        self._sendSettings(server)

    def removeServer(self, server):
        """
        Removes a server from being used by this module.

        :param server: WebSocketClient instance
        """

        log.info("removing server {}:{} from QEMU module".format(server.host, server.port))
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
                server.send_notification("qemu.settings", params)

        self._settings.update(settings)
        self._saveSettings()

    def _sendSettings(self, server):
        """
        Sends the module settings to the server.

        :param server: WebSocketClient instance
        """

        log.info("sending QEMU settings to server {}:{}".format(server.host, server.port))
        params = self._settings.copy()

        # send the local working directory only if this is a local server
        if server.isLocal():
            params.update({"working_dir": self._working_dir})
        else:
            project_name = os.path.basename(self._working_dir)
            if project_name.endswith("-files"):
                project_name = project_name[:-6]
            params.update({"project_name": project_name})
        server.send_notification("qemu.settings", params)

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
            for vm_key, info in self._qemu_vms.items():
                if node_name == info["name"]:
                    vm = vm_key

        if not vm:
            selected_vms = []
            for vm, info in self._qemu_vms.items():
                if info["server"] == node.server().host or (node.server().isLocal() and info["server"] == "local"):
                    selected_vms.append(vm)

            if not selected_vms:
                raise ModuleError("No QEMU VM on server {}".format(node.server().host))
            elif len(selected_vms) > 1:

                from gns3.main_window import MainWindow
                mainwindow = MainWindow.instance()

                (selection, ok) = QtGui.QInputDialog.getItem(mainwindow, "QEMU VM", "Please choose a VM", selected_vms, 0, False)
                if ok:
                    vm = selection
                else:
                    raise ModuleError("Please select a QEMU VM")
            else:
                vm = selected_vms[0]

        settings = {"ram": self._qemu_vms[vm]["ram"],
                    "adapters": self._qemu_vms[vm]["adapters"],
                    "adapter_type": self._qemu_vms[vm]["adapter_type"]}

        if self._qemu_vms[vm]["hda_disk_image"]:
            settings["hda_disk_image"] = self._qemu_vms[vm]["hda_disk_image"]

        if self._qemu_vms[vm]["hdb_disk_image"]:
            settings["hdb_disk_image"] = self._qemu_vms[vm]["hdb_disk_image"]

        if self._qemu_vms[vm]["initrd"]:
            settings["initrd"] = self._qemu_vms[vm]["initrd"]

        if self._qemu_vms[vm]["kernel_image"]:
            settings["kernel_image"] = self._qemu_vms[vm]["kernel_image"]

        if self._qemu_vms[vm]["kernel_command_line"]:
            settings["kernel_command_line"] = self._qemu_vms[vm]["kernel_command_line"]

        if self._qemu_vms[vm]["options"]:
            settings["options"] = self._qemu_vms[vm]["options"]

        qemu_path = self._qemu_vms[vm]["qemu_path"]
        name = self._qemu_vms[vm]["name"]

        if node.server().isCloud():
            settings["cloud_path"] = "images/qemu"

        node.setup(qemu_path, initial_settings=settings, base_name=name)

    def reset(self):
        """
        Resets the servers.
        """

        log.info("QEMU module reset")
        for server in self._servers:
            if server.connected():
                server.send_notification("qemu.reset")
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

    def getQemuBinariesFromServer(self, server, callback):
        """
        Gets the QEMU binaries list from a server.

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

        server.send_message("qemu.qemu_list", None, callback)

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

        return [QemuVM]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        nodes = []
        for qemu_vm in self._qemu_vms.values():
            nodes.append(
                {"class": QemuVM.__name__,
                 "name": qemu_vm["name"],
                 "server": qemu_vm["server"],
                 "default_symbol": qemu_vm["default_symbol"],
                 "hover_symbol": qemu_vm["hover_symbol"],
                 "categories": [qemu_vm["category"]]
                }
        )
        return nodes

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        from .pages.qemu_preferences_page import QemuPreferencesPage
        from .pages.qemu_vm_preferences_page import QemuVMPreferencesPage
        return [QemuPreferencesPage, QemuVMPreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of QEMU module.

        :returns: instance of Qemu
        """

        if not hasattr(Qemu, "_instance"):
            Qemu._instance = Qemu()
        return Qemu._instance
