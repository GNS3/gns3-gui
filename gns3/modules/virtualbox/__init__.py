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

from gns3.qt import QtCore, QtGui
from gns3.local_server_config import LocalServerConfig
from gns3.local_config import LocalConfig

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

        # load the settings
        self._loadSettings()
        self._loadVirtualBoxVMs()

    @staticmethod
    def _findVBoxManage(self):
        """
        Finds the VBoxManage path.

        :return: path to VBoxManage
        """

        if sys.platform.startswith("win"):
            if "VBOX_INSTALL_PATH" in os.environ:
                vboxmanage_path = os.path.join(os.environ["VBOX_INSTALL_PATH"], "VBoxManage.exe")
            elif "VBOX_MSI_INSTALL_PATH" in os.environ:
                vboxmanage_path = os.path.join(os.environ["VBOX_MSI_INSTALL_PATH"], "VBoxManage.exe")
            else:
                vboxmanage_path = "VBoxManage.exe"
        elif sys.platform.startswith("darwin"):
            vboxmanage_path = "/Applications/VirtualBox.app/Contents/MacOS/VBoxManage"
        else:
            vboxmanage_path = shutil.which("vboxmanage")

        if vboxmanage_path is None:
            return ""
        return vboxmanage_path

    def _loadSettings(self):
        """
        Loads the settings from the server settings file.
        """

        local_config = LocalConfig.instance()

        # restore the VirtualBox settings from QSettings (for backward compatibility)
        legacy_settings = {}
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name in VBOX_SETTINGS.keys():
            if settings.contains(name):
                legacy_settings[name] = settings.value(name, type=VBOX_SETTING_TYPES[name])
        settings.remove("")
        settings.endGroup()

        if legacy_settings:
            local_config.saveSectionSettings(self.__class__.__name__, legacy_settings)
        self._settings = local_config.loadSectionSettings(self.__class__.__name__, VBOX_SETTINGS)

        if not os.path.exists(self._settings["vboxmanage_path"]):
            self._settings["vboxmanage_path"] = self._findVBoxManage(self)

        # keep the config file sync
        self._saveSettings()

    def _saveSettings(self):
        """
        Saves the settings to the server settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

        # save some settings to the local server config file
        server_settings = {
            "vbox_user": self._settings["vbox_user"],
        }

        if self._settings["vboxmanage_path"]:
            server_settings["vboxmanage_path"] = os.path.normpath(self._settings["vboxmanage_path"])

        config = LocalServerConfig.instance()
        config.saveSettings(self.__class__.__name__, server_settings)

    def _loadVirtualBoxVMs(self):
        """
        Load the VirtualBox VMs from the client settings file.
        """

        local_config = LocalConfig.instance()

        # restore the VirtualBox settings from QSettings (for backward compatibility)
        virtualbox_vms = []
        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup("VirtualBoxVMs")
        # load the VMs
        size = settings.beginReadArray("VM")
        for index in range(0, size):
            settings.setArrayIndex(index)
            vm = {}
            for setting_name, default_value in VBOX_VM_SETTINGS.items():
                vm[setting_name] = settings.value(setting_name, default_value, VBOX_VM_SETTING_TYPES[setting_name])
            virtualbox_vms.append(vm)
        settings.endArray()
        settings.remove("")
        settings.endGroup()

        if virtualbox_vms:
            local_config.saveSectionSettings(self.__class__.__name__, {"vms": virtualbox_vms})

        settings = local_config.settings()
        if "vms" in settings.get(self.__class__.__name__, {}):
            for vm in settings[self.__class__.__name__]["vms"]:
                vmname = vm.get("vmname")
                server = vm.get("server")
                key = "{server}:{vmname}".format(server=server, vmname=vmname)
                if key in self._virtualbox_vms or not vmname or not server:
                    continue
                vm_settings = VBOX_VM_SETTINGS.copy()
                vm_settings.update(vm)
                self._virtualbox_vms[key] = vm_settings

        # keep things sync
        self._saveVirtualBoxVMs()

    def _saveVirtualBoxVMs(self):
        """
        Saves the VirtualBox VMs to the client settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, {"vms": list(self._virtualbox_vms.values())})

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
        :param project: Project instance
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

        settings = {}
        for setting_name, value in self._virtualbox_vms[vm].items():
            if setting_name in node.settings():
                settings[setting_name] = value

        vmname = self._virtualbox_vms[vm]["vmname"]
        node.setup(vmname, linked_clone=linked_base, additional_settings=settings)

    def reset(self):
        """
        Resets the module.
        """

        log.info("VirtualBox module reset")
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
