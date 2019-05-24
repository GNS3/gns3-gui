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

from gns3.local_server_config import LocalServerConfig
from gns3.local_config import LocalConfig
from gns3.controller import Controller
from gns3.template_manager import TemplateManager
from gns3.template import Template

from ..module import Module
from .virtualbox_vm import VirtualBoxVM
from .settings import VBOX_SETTINGS, VBOX_VM_SETTINGS

import logging
log = logging.getLogger(__name__)


class VirtualBox(Module):
    """
    VirtualBox module.
    """

    def __init__(self):
        super().__init__()
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

        if vboxmanage_path is None:
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

        # migrate VM settings to the controller (templates are managed on server side starting with version 2.0)
        Controller.instance().connected_signal.connect(self._migrateOldVMs)

    def _migrateOldVMs(self):
        """
        Migrate local VM settings to the controller.
        """

        if self._settings.get("vms"):
            templates = []
            for vm in self._settings.get("vms"):
                vm_settings = VBOX_VM_SETTINGS.copy()
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
        if self._settings["vboxmanage_path"]:
            server_settings = {"vboxmanage_path": os.path.normpath(self._settings["vboxmanage_path"])}
            LocalServerConfig.instance().saveSettings(self.__class__.__name__, server_settings)

    @staticmethod
    def configurationPage():
        """
        Returns the configuration page for this module.

        :returns: QWidget object
        """

        from .pages.virtualbox_vm_configuration_page import VirtualBoxVMConfigurationPage
        return VirtualBoxVMConfigurationPage

    @staticmethod
    def getNodeClass(node_type, platform=None):
        """
        Returns the class corresponding to node type.

        :param node_type: name of the node
        :param platform: not used

        :returns: class or None
        """

        if node_type == "virtualbox":
            return VirtualBoxVM
        return None

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [VirtualBoxVM]

    @staticmethod
    def preferencePages():
        """
        Returns the preference pages for this module.

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

    def __str__(self):
        """
        Returns the module name.
        """

        return "virtualbox"
