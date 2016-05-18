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

import os
import sys
import subprocess
import codecs
import shutil

from .qt import QtNetwork
from collections import OrderedDict
from .servers import Servers

import logging
log = logging.getLogger(__name__)


class GNS3VM:

    """
    GNS3 VM management class.
    """

    def __init__(self):

        self._is_running = False
        # The current running vboxmanage and vmrun process
        self._running_process = None

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

    def killRunningProcess(self):
        """
        Kill the VBoxManage or vmrun process if running
        """

        if self._running_process is not None:
            self._running_process.kill()
            self._running_process.wait()
            self._running_process = None

    def _process_check_output(self, command, timeout=None):
        # Original code from Python's subprocess.check_output
        # https://github.com/python/cpython/blob/3.4/Lib/subprocess.py
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=os.environ) as process:
            self._running_process = process
            try:
                output, unused_err = process.communicate(None, timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                output, unused_err = process.communicate()
                self._running_process = None
                raise subprocess.TimeoutExpired(process.args, timeout, output=output)
            except:
                self.killRunningProcess()
                raise
            retcode = process.poll()
            if retcode:
                self._running_process = None
                raise subprocess.CalledProcessError(retcode, process.args, output=output)
        self._running_process = None
        return output.decode("utf-8", errors="ignore").strip()

    def execute_vmrun(self, subcommand, args, timeout=60):

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
        return self._process_check_output(command, timeout=timeout)

    def execute_vboxmanage(self, subcommand, args, timeout=60):

        from gns3.modules.virtualbox import VirtualBox
        virtualbox_settings = VirtualBox.instance().settings()
        vboxmanage_path = virtualbox_settings["vboxmanage_path"]
        command = [vboxmanage_path, "--nologo", subcommand]
        command.extend(args)
        log.debug("Executing VBoxManage with command: {}".format(command))
        return self._process_check_output(command, timeout=timeout)

    @staticmethod
    def parse_vmx_file(path):
        """
        Parses a VMX file.

        :param path: path to the VMX file

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

    @staticmethod
    def write_vmx_file(path, pairs):
        """
        Write a VMware VMX file.

        :param path: path to the VMX file
        :param pairs: settings to write
        """

        encoding = "utf-8"
        if ".encoding" in pairs:
            file_encoding = pairs[".encoding"]
            try:
                codecs.lookup(file_encoding)
                encoding = file_encoding
            except LookupError:
                log.warning("Invalid file encoding detected in '{}': {}".format(path, file_encoding))
        with open(path, "w", encoding=encoding, errors="ignore") as f:
            if sys.platform.startswith("linux"):
                # write the shebang on the first line on Linux
                vmware_path = shutil.which("vmware")
                if vmware_path:
                    f.write("#!{}\n".format(vmware_path))
            for key, value in pairs.items():
                entry = '{} = "{}"\n'.format(key, value)
                f.write(entry)

    def autoStart(self):
        """
        Automatically start the GNS3 VM at startup.

        :returns: boolean
        """

        vm_settings = Servers.instance().vmSettings()
        return vm_settings["auto_start"]

    def isRemote(self):
        """
        Checks if the GNS3 VM is remote.

        :returns: boolean
        """

        vm_settings = Servers.instance().vmSettings()
        if vm_settings["virtualization"] == "remote":
            return True
        return False

    def adjustLocalServerIP(self):
        """
        Adjust the local server IP address to be in the same subnet as the GNS3 VM.

        :returns: the local server IP/host address
        """

        servers = Servers.instance()
        local_server_settings = servers.localServerSettings()
        if Servers.instance().vmSettings()["adjust_local_server_ip"]:
            vm_server = servers.vmServer()
            vm_ip_address = vm_server.host()
            log.debug("GNS3 VM IP address is {}".format(vm_ip_address))

            for interface in QtNetwork.QNetworkInterface.allInterfaces():
                for address in interface.addressEntries():
                    ip = address.ip().toString()
                    prefix_length = address.prefixLength()
                    subnet = QtNetwork.QHostAddress.parseSubnet("{}/{}".format(ip, prefix_length))
                    if QtNetwork.QHostAddress(vm_ip_address).isInSubnet(subnet):
                        if local_server_settings["host"] != ip:
                            log.info("Adjust local server IP address to {}".format(ip))
                            servers.setLocalServerSettings({"host": ip})
                            servers.registerLocalServer()
                            servers.save()
                            return ip
        return local_server_settings["host"]

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

    def setvCPUandRAM(self, vcpus, ram):
        """
        Set the vCPU cores and RAM amount for the GNS3 VM.

        :param vcpus: number of vCPU cores
        :param ram: amount of memory

        :returns: boolean
        """

        vm_settings = self.settings()
        if vm_settings["virtualization"] == "VMware":
            try:
                pairs = self.parse_vmx_file(vm_settings["vmx_path"])
                pairs["numvcpus"] = str(vcpus)
                pairs["memsize"] = str(ram)
                self.write_vmx_file(vm_settings["vmx_path"], pairs)
            except OSError as e:
                log.error('Could not read/write VMware VMX file "{}": {}'.format(vm_settings["vmx_path"], e))
                return False

        elif vm_settings["virtualization"] == "VirtualBox":
            try:
                self.execute_vboxmanage("modifyvm", [vm_settings["vmname"], "--cpus", str(vcpus)], timeout=3)
                self.execute_vboxmanage("modifyvm", [vm_settings["vmname"], "--memory", str(ram)], timeout=3)
            except OSError as e:
                log.error("Could not execute VBoxManage: {}".format(e), True)
                return False
            except subprocess.SubprocessError as e:
                log.error("Could not execute VBoxManage: {} with output '{}'".format(e, e.output.decode("utf-8", errors="ignore").strip()), True)
                return False
            except subprocess.TimeoutExpired:
                log.error("VBoxmanage timeout expired", True)
                return False
        log.info("GNS3 VM vCPU count set to {} and RAM to {} MB".format(vcpus, ram))
        return True

    def shutdown(self, force=False):
        """
        Gracefully shutdowns the GNS3 VM.
        """

        vm_settings = self.settings()
        if self._is_running and (vm_settings["auto_stop"] or force):
            try:
                if vm_settings["virtualization"] == "VMware":
                    if vm_settings["vmx_path"] is None:
                        log.error("No vm path configured, can't stop the VM")
                        return
                    self.execute_vmrun("stop", [vm_settings["vmx_path"], "soft"])
                elif vm_settings["virtualization"] == "VirtualBox":
                    self.execute_vboxmanage("controlvm", [vm_settings["vmname"], "acpipowerbutton"], timeout=3)
            except (OSError, subprocess.SubprocessError):
                pass
            except subprocess.TimeoutExpired:
                log.warning("Could not ACPI shutdown the VM (timeout expired)")
        self._is_running = False

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of GNS3VM

        :returns: instance of GNS3VM
        """

        if not hasattr(GNS3VM, "_instance") or GNS3VM._instance is None:
            GNS3VM._instance = GNS3VM()
        return GNS3VM._instance
