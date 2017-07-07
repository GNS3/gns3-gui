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

from ...controller import Controller
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

        self._qemu_vms = {}
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

    def instantiateNode(self, node_class, server, project):
        """
        Instantiate a new node.

        :param node_class: Node object
        :param server: HTTPClient instance
        """

        # create an instance of the node class
        return node_class(self, server, project)

    def reset(self):
        """
        Resets the servers.
        """

        self._nodes.clear()

    def getQemuBinariesFromServer(self, compute_id, callback, archs=None):
        """
        Gets the QEMU binaries list from a server.

        :param compute_id: server to send the request to
        :param callback: callback for the reply from the server
        :param archs: A list of architectures. Only binaries matching the specified architectures are returned.
        """

        request_body = None
        if archs is not None:
            request_body = {"archs": archs}
        Controller.instance().getCompute("/qemu/binaries", compute_id, callback, body=request_body)

    def getQemuImgBinariesFromServer(self, compute_id, callback):
        """
        Gets the QEMU-img binaries list from a server.

        :param server: server to send the request to
        :param callback: callback for the reply from the server
        """

        Controller.instance().getCompute("/qemu/img-binaries", compute_id, callback)

    def getQemuCapabilitiesFromServer(self, compute_id, callback):
        """
        Gets the capabilities of Qemu at a server.

        :param server: server to send the request to
        :param callback: callback for the reply from the server
        """

        Controller.instance().getCompute("/qemu/capabilities", compute_id, callback)

    def createDiskImage(self, compute_id, callback, options):
        """
        Create a disk image on the remote server

        :param server: server to send the request to
        :param callback: callback for the reply from the server
        :param options: Options for the image creation
        """

        Controller.instance().postCompute("/qemu/img", compute_id, callback, body=options)

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
    def getNodeType(name, platform=None):
        if name == "qemu":
            return QemuVM
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
