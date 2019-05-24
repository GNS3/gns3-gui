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
import codecs

from gns3.local_server_config import LocalServerConfig
from gns3.local_config import LocalConfig
from collections import OrderedDict
from gns3.controller import Controller
from gns3.template_manager import TemplateManager
from gns3.template import Template
from gns3.modules.module import Module
from gns3.modules.vmware.vmware_vm import VMwareVM
from gns3.modules.vmware.settings import VMWARE_SETTINGS, VMWARE_VM_SETTINGS

import logging
log = logging.getLogger(__name__)


class VMware(Module):

    """
    VMware module.
    """

    def __init__(self):
        super().__init__()
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
    def findVmrun():
        """
        Finds the vmrun path.

        :return: path to vmrun
        """

        vmrun_path = None
        if sys.platform.startswith("win"):
            vmrun_path = shutil.which("vmrun")
            if vmrun_path is None:
                # look for vmrun.exe using the VMware Workstation directory listed in the registry
                vmrun_path = VMware._findVmrunRegistry(r"SOFTWARE\Wow6432Node\VMware, Inc.\VMware Workstation")
                if vmrun_path is None:
                    # look for vmrun.exe using the VIX directory listed in the registry
                    vmrun_path = VMware._findVmrunRegistry(r"SOFTWARE\Wow6432Node\VMware, Inc.\VMware VIX")
        elif sys.platform.startswith("darwin"):
            vmware_fusion_vmrun_path = None
            try:
                output = subprocess.check_output(["mdfind", "kMDItemCFBundleIdentifier == 'com.vmware.fusion'"]).decode("utf-8", errors="ignore").strip()
                if len(output):
                    vmware_fusion_vmrun_path = os.path.join(output, "Contents/Library/vmrun")
            except (OSError, subprocess.SubprocessError) as e:
                pass
            if vmware_fusion_vmrun_path is None:
                vmware_fusion_vmrun_path = "/Applications/VMware Fusion.app/Contents/Library/vmrun"
            if os.path.exists(vmware_fusion_vmrun_path):
                vmrun_path = vmware_fusion_vmrun_path
        else:
            vmrun_path = shutil.which("vmrun")

        if vmrun_path is None:
            return ""
        return os.path.abspath(vmrun_path)

    @staticmethod
    def _determineHostType():

        if sys.platform.startswith("win"):
            import winreg
            try:
                # the Core key indicates which VMware core product is installed (VMware Player vs VMware Workstation)
                hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\VMware, Inc.")
                output, _ = winreg.QueryValueEx(hkey, "Core")
                winreg.CloseKey(hkey)
            except OSError:
                vmrun = VMware.findVmrun()
                if "VIX" in vmrun:
                    return "player"
                return "ws"
        elif sys.platform.startswith("darwin"):
            return "fusion"
        else:
            vmware_path = shutil.which("vmware")
            if vmware_path is None:
                vmware_path = shutil.which("vmplayer")
                if vmware_path is not None:
                    return "player"
            if vmware_path:
                command = [vmware_path, "-v"]
                log.debug("Executing vmware with command: {}".format(command))
                try:
                    output = subprocess.check_output(command).decode("utf-8", errors="ignore").strip()
                except (OSError, subprocess.SubprocessError) as e:
                    log.error("Could not execute {}: {}".format("".join(command), e))
                    return "ws"
            else:
                return "ws"
        if "VMware Player" in output:
            return "player"
        # Workstation is the default
        return "ws"

    @staticmethod
    def parseVMwareFile(path):
        """
        Parses a VMware file (VMX, preferences or inventory).

        :param path: path to the VMware file

        :returns: dict
        """

        pairs = OrderedDict()
        encoding = "utf-8"
        # get the first line to read the .encoding value
        with open(path, "rb") as f:
            line = f.readline().decode(encoding, errors="ignore")
            if line.startswith("#!"):
                # skip the shebang
                line = f.readline().decode(encoding, errors="ignore")
            try:
                key, value = line.split('=', 1)
                if key.strip().lower() == ".encoding":
                    file_encoding = value.strip('" ')
                    try:
                        codecs.lookup(file_encoding)
                        encoding = file_encoding
                    except LookupError:
                        log.warning("Invalid file encoding detected in '{}': {}".format(path, file_encoding))
            except ValueError:
                log.warning("Couldn't find file encoding in {}, using {}...".format(path, encoding))

        # read the file with the correct encoding
        with open(path, encoding=encoding, errors="ignore") as f:
            for line in f.read().splitlines():
                try:
                    key, value = line.split('=', 1)
                    pairs[key.strip().lower()] = value.strip('" ')
                except ValueError:
                    continue
        return pairs

    def _loadSettings(self):
        """
        Loads the settings from the server settings file.
        """

        local_config = LocalConfig.instance()
        self._settings = local_config.loadSectionSettings(self.__class__.__name__, VMWARE_SETTINGS)
        if not os.path.exists(self._settings["vmrun_path"]):
            self._settings["vmrun_path"] = self.findVmrun()
            self._settings["host_type"] = self._determineHostType()

        # migrate VM settings to the controller (templates are managed on server side starting with version 2.0)
        Controller.instance().connected_signal.connect(self._migrateOldVMs)

    def _migrateOldVMs(self):
        """
        Migrate local VM settings to the controller.
        """

        if self._settings.get("vms"):
            templates = []
            for vm in self._settings.get("vms"):
                vm_settings = VMWARE_VM_SETTINGS.copy()
                vm_settings.update(vm)
                templates.append(Template(vm_settings))
            TemplateManager.instance().updateList(templates)
            self._settings["vms"] = []
            self._saveSettings()

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
            "block_host_traffic": self._settings["block_host_traffic"]
        }

        if self._settings["vmrun_path"]:
            server_settings["vmrun_path"] = os.path.normpath(self._settings["vmrun_path"])

        config = LocalServerConfig.instance()
        config.saveSettings(self.__class__.__name__, server_settings)

    @staticmethod
    def configurationPage():
        """
        Returns the configuration page for this module.

        :returns: QWidget object
        """

        from .pages.vmware_vm_configuration_page import VMwareVMConfigurationPage
        return VMwareVMConfigurationPage

    @staticmethod
    def getNodeClass(node_type, platform=None):
        """
        Returns the class corresponding to node type.

        :param node_type: name of the node
        :param platform: not used

        :returns: class or None
        """

        if node_type == "vmware":
            return VMwareVM
        return None

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [VMwareVM]

    @staticmethod
    def preferencePages():
        """
        Returns the preference pages for this module.

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

    def __str__(self):
        """
        Returns the module name.
        """

        return "vmware"

if __name__ == '__main__':
    print("vmrun", VMware.findVmrun())
