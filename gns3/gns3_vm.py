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
Manages the GNS3 VM.
"""

import subprocess

from .settings import GNS3_VM_SETTINGS
from .local_config import LocalConfig

import logging
log = logging.getLogger(__name__)


class GNS3VM:

    """
    GNS3 VM management class.
    """

    def __init__(self):

        self._settings = {}
        self._loadSettings()
        self._is_running = False

    def _loadSettings(self):
        """
        Loads the server settings from the persistent settings file.
        """

        local_config = LocalConfig.instance()
        self._settings = local_config.loadSectionSettings("GNS3VM", GNS3_VM_SETTINGS)

        # keep the config file sync
        self._saveSettings()

    def _saveSettings(self):
        """
        Saves the server settings to a persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings("GNS3VM", self._settings)

    def settings(self):
        """
        Returns the GNS3 VM settings.

        :returns: GNS3 VM settings (dict)
        """

        return self._settings

    def setSettings(self, settings):
        """
        Set new GNS3 VM settings.

        :param settings: GNS3 VM settings (dict)
        """

        self._settings.update(settings)
        self._saveSettings()

    @staticmethod
    def execute_vmrun(subcommand, args):

        from gns3.modules.vmware import VMware
        vmware_settings = VMware.instance().settings()
        vmrun_path = vmware_settings["vmrun_path"]
        host_type = vmware_settings["host_type"]
        command = [vmrun_path, "-T", host_type, subcommand]
        command.extend(args)
        log.debug("Executing vmrun with command: {}".format(command))
        output = subprocess.check_output(command)
        return output.decode("utf-8", errors="ignore").strip()

    @staticmethod
    def execute_vboxmanage(subcommand, args):

        from gns3.modules.virtualbox import VirtualBox
        virtualbox_settings = VirtualBox.instance().settings()
        vboxmanage_path = virtualbox_settings["vboxmanage_path"]
        command = [vboxmanage_path, "--nologo", subcommand]
        command.extend(args)
        log.debug("Executing VBoxManage with command: {}".format(command))
        output = subprocess.check_output(command)
        return output.decode("utf-8", errors="ignore").strip()

    def autoStart(self):
        """
        Automatically start the GNS3 VM at startup.

        :returns: boolean
        """

        return self._settings["auto_start"]

    def server_host(self):
        """
        Returns the IP address or hostname of server running in the GNS3 VM.

        :returns: boolean
        """

        return self._settings["server_host"]

    def server_port(self):
        """
        Returns the port of server running in the GNS3 VM.

        :returns: boolean
        """

        return self._settings["server_port"]

    def setRunning(self, value):
        """
        Sets either the GNS3 VM is running or not.

        :param value: boolean
        """

        self._is_running = value

    def isRunning(self):
        """
        Returns either the GNS3 VM is running or not.

        :returns: boolean
        """

        return self._is_running

    def shutdown(self):
        """
        Gracefully shutdowns the GNS3 VM.
        """

        if self._is_running and self._settings["auto_stop"]:
            try:
                if self._settings["virtualization"] == "VMware":
                    self.execute_vmrun("stop", [self._settings["vmx_path"], "soft"])
                elif self._settings["virtualization"] == "VirtualBox":
                    self.execute_vboxmanage("controlvm", [self._settings["vmname"], "acpipowerbutton"])
            except (OSError, subprocess.SubprocessError):
                pass

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of GNS3VM

        :returns: instance of GNS3VM
        """

        if not hasattr(GNS3VM, "_instance") or GNS3VM._instance is None:
            GNS3VM._instance = GNS3VM()
        return GNS3VM._instance
