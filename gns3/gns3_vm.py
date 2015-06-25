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

import sys
import subprocess

from .servers import Servers

import logging
log = logging.getLogger(__name__)


class GNS3VM:

    """
    GNS3 VM management class.
    """

    def __init__(self):

        self._is_running = False

    def settings(self):
        """
        Returns the GNS3 VM settings.

        :returns: GNS3 VM settings (dict)
        """

        return Servers.instance().vmSettings()

    def setSettings(self, settings):
        """
        Set new GNS3 VM settings.

        :param settings: GNS3 VM settings (dict)
        """

        Servers.instance().setVMsettings(settings)

    @staticmethod
    def execute_vmrun(subcommand, args):

        from gns3.modules.vmware import VMware
        vmware_settings = VMware.instance().settings()
        vmrun_path = vmware_settings["vmrun_path"]
        if sys.platform.startswith("darwin"):
            command = [vmrun_path, "-T", "fusion", subcommand]
        else:
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

        vm_settings = Servers.instance().vmSettings()
        return vm_settings["auto_start"]

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

    def shutdown(self, force=False):
        """
        Gracefully shutdowns the GNS3 VM.
        """

        vm_settings = self.settings()
        if self._is_running and (vm_settings["auto_stop"] or force):
            try:
                if vm_settings["virtualization"] == "VMware":
                    self.execute_vmrun("stop", [vm_settings["vmx_path"], "soft"])
                elif vm_settings["virtualization"] == "VirtualBox":
                    self.execute_vboxmanage("controlvm", [vm_settings["vmname"], "acpipowerbutton"])
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
