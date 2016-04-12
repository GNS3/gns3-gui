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

import sys

from gns3.qt import QtWidgets
from gns3.local_config import LocalConfig
from gns3.local_server_config import LocalServerConfig

from ..module import Module
from ..module_error import ModuleError
from .qemu_vm import QemuVM
from .settings import QEMU_SETTINGS
from .settings import QEMU_VM_SETTINGS

import logging
log = logging.getLogger(__name__)


class Qemu(Module):

    """
    QEMU module.
    """

    def __init__(self):
        super().__init__()

        self._settings = {}
        self._qemu_vms = {}
        self._nodes = []

        self.configChangedSlot()

    def configChangedSlot(self):
        # load the settings
        self._loadSettings()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings(self.__class__.__name__, QEMU_SETTINGS)
        self._loadQemuVMs()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

        # save some settings to the local server config file
        if sys.platform.startswith("linux"):
            server_settings = {
                "enable_kvm": self._settings["enable_kvm"],
            }

            LocalServerConfig.instance().saveSettings(self.__class__.__name__, server_settings)

    def _loadQemuVMs(self):
        """
        Load the QEMU VMs from the persistent settings file.
        """

        settings = LocalConfig.instance().settings()
        if "vms" in settings.get(self.__class__.__name__, {}):
            for vm in settings[self.__class__.__name__]["vms"]:
                name = vm.get("name")
                server = vm.get("server")
                key = "{server}:{name}".format(server=server, name=name)
                if key in self._qemu_vms or not name or not server:
                    continue
                vm_settings = QEMU_VM_SETTINGS.copy()
                vm_settings.update(vm)
                # for backward compatibility before version 1.4
                if "symbol" not in vm_settings:
                    vm_settings["symbol"] = vm_settings.get("default_symbol", vm_settings["symbol"])
                    vm_settings["symbol"] = vm_settings["symbol"][:-11] + ".svg" if vm_settings["symbol"].endswith("normal.svg") else vm_settings["symbol"]
                self._qemu_vms[key] = vm_settings

    def _saveQemuVMs(self):
        """
        Saves the QEMU VMs to the persistent settings file.
        """

        self._settings["vms"] = list(self._qemu_vms.values())
        self._saveSettings()

    def VMs(self):
        """
        Returns QEMU VMs settings.

        :returns: QEMU VMs settings (dictionary)
        """

        return self._qemu_vms

    def setVMs(self, new_qemu_vms):
        """
        Sets QEMU VM settings.

        :param new_qemu_vms: Qemu images settings (dictionary)
        """

        self._qemu_vms = new_qemu_vms.copy()
        self._saveQemuVMs()

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

        self._settings.update(settings)
        self._saveSettings()

    def createNode(self, node_class, server, project):
        """
        Creates a new node.

        :param node_class: Node object
        :param server: HTTPClient instance
        """

        log.info("creating node {}".format(node_class))

        # create an instance of the node class
        return node_class(self, server, project)

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
                if info["server"] == node.server().host() or (node.server().isLocal() and info["server"] == "local"):
                    selected_vms.append(vm)

            if not selected_vms:
                raise ModuleError("No QEMU VM on server {}".format(node.server().host()))
            elif len(selected_vms) > 1:

                from gns3.main_window import MainWindow
                mainwindow = MainWindow.instance()

                (selection, ok) = QtWidgets.QInputDialog.getItem(mainwindow, "QEMU VM", "Please choose a VM", selected_vms, 0, False)
                if ok:
                    vm = selection
                else:
                    raise ModuleError("Please select a QEMU VM")
            else:
                vm = selected_vms[0]

        linked_base = self._qemu_vms[vm]["linked_base"]
        if not linked_base:
            for other_node in self._nodes:
                if other_node.settings()["name"] == self._qemu_vms[vm]["name"] and \
                        (self._qemu_vms[vm]["server"] == "local" and other_node.server().isLocal() or self._qemu_vms[vm]["server"] == other_node.server().host):
                    raise ModuleError("Sorry a Qemu VM without the linked base setting enabled can only be used once in your topology")

        vm_settings = {}
        for setting_name, value in self._qemu_vms[vm].items():
            if setting_name in node.settings() and value != "" and value is not None:
                vm_settings[setting_name] = value

        qemu_path = vm_settings.pop("qemu_path")
        name = vm_settings.pop("name")
        port_name_format = self._qemu_vms[vm]["port_name_format"]
        port_segment_size = self._qemu_vms[vm]["port_segment_size"]
        first_port_name = self._qemu_vms[vm]["first_port_name"]

        default_name_format = QEMU_VM_SETTINGS["default_name_format"]
        if self._qemu_vms[vm]["default_name_format"]:
            default_name_format = self._qemu_vms[vm]["default_name_format"]
        if linked_base:
            default_name_format = default_name_format.replace('{name}', name)
            name = None

        node.setup(qemu_path,
                   name=name,
                   port_name_format=port_name_format,
                   port_segment_size=port_segment_size,
                   first_port_name=first_port_name,
                   linked_clone=linked_base,
                   additional_settings=vm_settings,
                   default_name_format=default_name_format)

    def reset(self):
        """
        Resets the servers.
        """

        log.info("QEMU module reset")
        self._nodes.clear()

    def getQemuBinariesFromServer(self, server, callback, archs=None):
        """
        Gets the QEMU binaries list from a server.

        :param server: server to send the request to
        :param callback: callback for the reply from the server
        :param archs: A list of architectures. Only binaries matching the specified architectures are returned.
        """

        request_body = None
        if archs is not None:
            request_body = {"archs": archs}
        server.get("/qemu/binaries", callback, body=request_body)

    def getQemuImgBinariesFromServer(self, server, callback):
        """
        Gets the QEMU-img binaries list from a server.

        :param server: server to send the request to
        :param callback: callback for the reply from the server
        """

        server.get(r"/qemu/img-binaries", callback)

    def getQemuCapabilitiesFromServer(self, server, callback):
        """
        Gets the capabilities of Qemu at a server.

        :param server: server to send the request to
        :param callback: callback for the reply from the server
        """

        server.get(r"/qemu/capabilities", callback)

    def createDiskImage(self, server, callback, options):
        """
        Create a disk image on the remote server

        :param server: server to send the request to
        :param callback: callback for the reply from the server
        :param options: Options for the image creation
        """

        server.post(r"/qemu/img", callback, body=options)

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
                 "ram": qemu_vm["ram"],
                 "server": qemu_vm["server"],
                 "symbol": qemu_vm["symbol"],
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
    def vmConfigurationPage():
        from .pages.qemu_vm_configuration_page import QemuVMConfigurationPage
        return QemuVMConfigurationPage

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of QEMU module.

        :returns: instance of Qemu
        """

        if not hasattr(Qemu, "_instance"):
            Qemu._instance = Qemu()
        return Qemu._instance
