# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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
VMware module implementation.
"""

import os
import sys
import shutil
import subprocess

from gns3.qt import QtWidgets
from gns3.local_server_config import LocalServerConfig
from gns3.local_config import LocalConfig

from ..module import Module
from ..module_error import ModuleError
from .vmware_vm import VMwareVM
from .settings import VMWARE_SETTINGS
from .settings import VMWARE_VM_SETTINGS

import logging
log = logging.getLogger(__name__)


class VMware(Module):

    """
    VMware module.
    """

    def __init__(self):
        super().__init__()

        self._settings = {}
        self._vmware_vms = {}
        self._nodes = []

        self.configChangedSlot()

    def configChangedSlot(self):
        # load the settings
        self._loadSettings()

    @staticmethod
    def _findVmrunRegistry(regkey):

        import winreg
        try:
            # default path not used, let's look in the registry
            hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, regkey)
            ws_install_path, _ = winreg.QueryValueEx(hkey, "InstallPath")
            vmrun_path = os.path.join(ws_install_path, "vmrun.exe")
            winreg.CloseKey(hkey)
            if os.path.exists(vmrun_path):
                return vmrun_path
        except OSError:
            pass
        return None

    @staticmethod
    def _findVmrun(self):
        """
        Finds the vmrun path.

        :return: path to vmrun
        """

        vmrun_path = None
        if sys.platform.startswith("win"):
            vmrun_path = shutil.which("vmrun")
            if vmrun_path is None:
                # look for vmrun.exe in default VMware Workstation directory
                vmrun_ws = os.path.expandvars(r"%PROGRAMFILES(X86)%\VMware\VMware Workstation\vmrun.exe")
                if os.path.exists(vmrun_ws):
                    vmrun_path = vmrun_ws
                else:
                    # look for vmrun.exe using the directory listed in the registry
                    vmrun_path = self._findVmrunRegistry(r"SOFTWARE\Wow6432Node\VMware, Inc.\VMware Workstation")
                if vmrun_path is None:
                    # look for vmrun.exe in default VMware VIX directory
                    vmrun_vix = os.path.expandvars(r"%PROGRAMFILES(X86)%\VMware\VMware VIX\vmrun.exe")
                    if os.path.exists(vmrun_vix):
                        vmrun_path = vmrun_vix
                    else:
                        # look for vmrun.exe using the directory listed in the registry
                        vmrun_path = self._findVmrunRegistry(r"SOFTWARE\Wow6432Node\VMware, Inc.\VMware VIX")
        elif sys.platform.startswith("darwin"):
            vmware_fusion_vmrun_path = "/Applications/VMware Fusion.app/Contents/Library/vmrun"
            if os.path.exists(vmware_fusion_vmrun_path):
                vmrun_path = vmware_fusion_vmrun_path
        else:
            vmrun_path = shutil.which("vmrun")

        if vmrun_path is None:
            return ""
        return os.path.abspath(vmrun_path)

    @staticmethod
    def _determineHostType(self):

        if sys.platform.startswith("win"):
            output = self._settings["vmrun_path"]
        elif sys.platform.startswith("darwin"):
            return "fusion"
        else:
            vmware_path = shutil.which("vmware")
            if vmware_path:
                command = [vmware_path, "-v"]
                log.debug("Executing vmware with command: {}".format(command))
                try:
                    output = subprocess.check_output(command).decode("utf-8", errors="ignore").strip()
                except (OSError, subprocess.SubprocessError) as e:
                    log.error("Could not execute {}: {}".format("".join(command), e))
                    return "ws"
            else:
                log.error("vmware command not found")
                return "ws"
        if "VMware Workstation" in output:
            return "ws"
        else:
            return "player"

    def _loadSettings(self):
        """
        Loads the settings from the server settings file.
        """

        local_config = LocalConfig.instance()
        self._settings = local_config.loadSectionSettings(self.__class__.__name__, VMWARE_SETTINGS)
        if not os.path.exists(self._settings["vmrun_path"]):
            self._settings["vmrun_path"] = self._findVmrun(self)
            self._settings["host_type"] = self._determineHostType(self)
        self._loadVMwareVMs()

    def _saveSettings(self):
        """
        Saves the settings to the server settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

        # save some settings to the local server config file
        server_settings = {
            "host_type": self._settings["host_type"],
            "vmnet_start_range": self._settings["vmnet_start_range"],
            "vmnet_end_range": self._settings["vmnet_end_range"],
        }

        if self._settings["vmrun_path"]:
            server_settings["vmrun_path"] = os.path.normpath(self._settings["vmrun_path"])

        config = LocalServerConfig.instance()
        config.saveSettings(self.__class__.__name__, server_settings)

    def _loadVMwareVMs(self):
        """
        Load the VMware VMs from the client settings file.
        """

        local_config = LocalConfig.instance()
        settings = local_config.settings()
        if "vms" in settings.get(self.__class__.__name__, {}):
            for vm in settings[self.__class__.__name__]["vms"]:
                name = vm.get("name")
                server = vm.get("server")
                key = "{server}:{name}".format(server=server, name=name)
                if key in self._vmware_vms or not name or not server:
                    continue
                vm_settings = VMWARE_VM_SETTINGS.copy()
                vm_settings.update(vm)
                # for backward compatibility before version 1.4
                if "symbol" not in vm_settings:
                    vm_settings["symbol"] = vm_settings.get("default_symbol", vm_settings["symbol"])
                    vm_settings["symbol"] = vm_settings["symbol"][:-11] + ".svg" if vm_settings["symbol"].endswith("normal.svg") else vm_settings["symbol"]
                self._vmware_vms[key] = vm_settings

    def _saveVMwareVMs(self):
        """
        Saves the VMware VMs to the client settings file.
        """

        self._settings["vms"] = list(self._vmware_vms.values())
        self._saveSettings()

    def vmwareVMs(self):
        """
        Returns VMware VMs settings.

        :returns: VMware VMs settings (dictionary)
        """

        return self._vmware_vms

    def setVMwareVMs(self, new_vmware_vms):
        """
        Sets VMware VM settings.

        :param new_vmware_images: VMware VM settings (dictionary)
        """

        self._vmware_vms = new_vmware_vms.copy()
        self._saveVMwareVMs()

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
            for vm_key, info in self._vmware_vms.items():
                if node_name == info["name"]:
                    vm = vm_key

        if not vm:
            selected_vms = []
            for vm, info in self._vmware_vms.items():
                if info["server"] == node.server().host() or (node.server().isLocal() and info["server"] == "local"):
                    selected_vms.append(vm)

            if not selected_vms:
                raise ModuleError("No VMware VM on server {}".format(node.server().url()))
            elif len(selected_vms) > 1:

                from gns3.main_window import MainWindow
                mainwindow = MainWindow.instance()

                (selection, ok) = QtWidgets.QInputDialog.getItem(mainwindow, "VMware VM", "Please choose a VM", selected_vms, 0, False)
                if ok:
                    vm = selection
                else:
                    raise ModuleError("Please select a VMware VM")
            else:
                vm = selected_vms[0]

        linked_base = self._vmware_vms[vm]["linked_base"]
        if not linked_base:
            for other_node in self._nodes:
                if other_node.settings()["vmx_path"] == self._vmware_vms[vm]["vmx_path"] and \
                        (self._vmware_vms[vm]["server"] == "local" and other_node.server().isLocal() or self._vmware_vms[vm]["server"] == other_node.server().host):
                    raise ModuleError("Sorry a VMware VM that is not a linked base can only be used once in your topology")

        vm_settings = {}
        for setting_name, value in self._vmware_vms[vm].items():
            if setting_name in node.settings():
                vm_settings[setting_name] = value

        vmx_path = vm_settings.pop("vmx_path")
        name = vm_settings.pop("name")
        port_name_format = self._vmware_vms[vm]["port_name_format"]
        port_segment_size = self._vmware_vms[vm]["port_segment_size"]
        first_port_name = self._vmware_vms[vm]["first_port_name"]
        node.setup(vmx_path,
                   port_name_format=port_name_format,
                   port_segment_size=port_segment_size,
                   first_port_name=first_port_name,
                   linked_clone=linked_base,
                   additional_settings=vm_settings,
                   base_name=name)

    def reset(self):
        """
        Resets the module.
        """

        log.info("VMware module reset")
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

        return [VMwareVM]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        nodes = []
        for vmware_vm in self._vmware_vms.values():
            nodes.append(
                {"class": VMwareVM.__name__,
                 "name": vmware_vm["name"],
                 "server": vmware_vm["server"],
                 "symbol": vmware_vm["symbol"],
                 "categories": [vmware_vm["category"]]}
            )
        return nodes

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        from .pages.vmware_preferences_page import VMwarePreferencesPage
        from .pages.vmware_vm_preferences_page import VMwareVMPreferencesPage
        return [VMwarePreferencesPage, VMwareVMPreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of VMware module.

        :returns: instance of VMware
        """

        if not hasattr(VMware, "_instance"):
            VMware._instance = VMware()
        return VMware._instance
