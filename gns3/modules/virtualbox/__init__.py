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
import sys
import shutil

from gns3.qt import QtWidgets
from gns3.local_server_config import LocalServerConfig
from gns3.local_config import LocalConfig

from ..module import Module
from ..module_error import ModuleError
from .virtualbox_vm import VirtualBoxVM
from .settings import VBOX_SETTINGS
from .settings import VBOX_VM_SETTINGS

import logging
log = logging.getLogger(__name__)


class VirtualBox(Module):

    """
    VirtualBox module.
    """

    def __init__(self):
        super().__init__()

        self._settings = {}
        self._virtualbox_vms = {}
        self._nodes = []

        self.configChangedSlot()

    def configChangedSlot(self):
        # load the settings
        self._loadSettings()

    @staticmethod
    def _findVBoxManage(self):
        """
        Finds the VBoxManage path.

        :return: path to VBoxManage
        """

        vboxmanage_path = None
        if sys.platform.startswith("win"):
            if "VBOX_INSTALL_PATH" in os.environ:
                vboxmanage_path_windows = os.path.join(os.environ["VBOX_INSTALL_PATH"], "VBoxManage.exe")
                if os.path.exists(vboxmanage_path_windows):
                    vboxmanage_path = vboxmanage_path_windows
            elif "VBOX_MSI_INSTALL_PATH" in os.environ:
                vboxmanage_path_windows = os.path.join(os.environ["VBOX_MSI_INSTALL_PATH"], "VBoxManage.exe")
                if os.path.exists(vboxmanage_path_windows):
                    vboxmanage_path = vboxmanage_path_windows
        elif sys.platform.startswith("darwin"):
            vboxmanage_path_osx = "/Applications/VirtualBox.app/Contents/MacOS/VBoxManage"
            if os.path.exists(vboxmanage_path_osx):
                vboxmanage_path = vboxmanage_path_osx
        else:
            vboxmanage_path = shutil.which("vboxmanage")

        if vboxmanage_path is None:
            return ""
        return os.path.abspath(vboxmanage_path)

    def _loadSettings(self):
        """
        Loads the settings from the server settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings(self.__class__.__name__, VBOX_SETTINGS)

        if not os.path.exists(self._settings["vboxmanage_path"]):
            self._settings["vboxmanage_path"] = self._findVBoxManage(self)

        self._loadVirtualBoxVMs()

    def _saveSettings(self):
        """
        Saves the settings to the server settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

        # save some settings to the local server config file
        if self._settings["vboxmanage_path"]:
            server_settings = {
                "vboxmanage_path": os.path.normpath(self._settings["vboxmanage_path"])
            }
            LocalServerConfig.instance().saveSettings(self.__class__.__name__, server_settings)

    def _loadVirtualBoxVMs(self):
        """
        Load the VirtualBox VMs from the client settings file.
        """

        self._virtualbox_vms = {}
        settings = LocalConfig.instance().settings()
        if "vms" in settings.get(self.__class__.__name__, {}):
            for vm in settings[self.__class__.__name__]["vms"]:
                vmname = vm.get("vmname")
                server = vm.get("server")
                key = "{server}:{vmname}".format(server=server, vmname=vmname)
                if key in self._virtualbox_vms or not vmname or not server:
                    continue
                vm_settings = VBOX_VM_SETTINGS.copy()
                vm_settings.update(vm)
                # For backward compatibility we use vmname
                if not vm_settings["name"]:
                    vm_settings["name"] = vmname
                # for backward compatibility before version 1.4
                if "symbol" not in vm_settings:
                    vm_settings["symbol"] = vm_settings.get("default_symbol", vm_settings["symbol"])
                    vm_settings["symbol"] = vm_settings["symbol"][:-11] + ".svg" if vm_settings["symbol"].endswith("normal.svg") else vm_settings["symbol"]
                self._virtualbox_vms[key] = vm_settings

    def _saveVirtualBoxVMs(self):
        """
        Saves the VirtualBox VMs to the client settings file.
        """

        self._settings["vms"] = list(self._virtualbox_vms.values())
        self._saveSettings()

    def VMs(self):
        """
        Returns VirtualBox VMs settings.

        :returns: VirtualBox VMs settings (dictionary)
        """

        return self._virtualbox_vms

    @staticmethod
    def vmConfigurationPage():
        from .pages.virtualbox_vm_configuration_page import VirtualBoxVMConfigurationPage
        return VirtualBoxVMConfigurationPage

    def setVMs(self, new_virtualbox_vms):
        """
        Sets VirtualBox VM settings.

        :param new_virtualbox_vms: VirtualBox VM settings (dictionary)
        """

        self._virtualbox_vms = new_virtualbox_vms.copy()
        self._saveVirtualBoxVMs()

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
        :param project: Project instance
        """

        # create an instance of the node class
        return node_class(self, server, project)

    def reset(self):
        """
        Resets the module.
        """

        self._nodes.clear()

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
        if name == "virtualbox":
            return VirtualBoxVM
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
                 "name": vbox_vm["name"],
                 "server": vbox_vm["server"],
                 "symbol": vbox_vm["symbol"],
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
