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
Thread to wait for the GNS3 VM.
"""

import os
import socket
import subprocess
import urllib.request
import json

from ..qt import QtCore
from ..version import __version__
from ..gns3_vm import GNS3VM

import logging
log = logging.getLogger(__name__)


class WaitForVMWorker(QtCore.QObject):

    """
    Thread to wait for the GNS3 VM to be started.
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    def __init__(self):

        super().__init__()
        self._is_running = False
        self._vm = GNS3VM.instance()

        vm_settings = self._vm.settings()
        self._vmname = vm_settings["vmname"]
        self._vmx_path = vm_settings["vmx_path"]
        self._headless = vm_settings["headless"]
        self._virtualization = vm_settings["virtualization"]
        self._server_host = vm_settings["server_host"]
        self._server_port = vm_settings["server_port"]

    def _get_vbox_vm_state(self):
        """
        Returns the VM state (e.g. running, paused etc.)

        :returns: state (string)
        """

        result = self._vm.execute_vboxmanage("showvminfo", [self._vmname, "--machinereadable"])
        for info in result.splitlines():
            if '=' in info:
                name, value = info.split('=', 1)
                if name == "VMState":
                    return value.strip('"')
        return "unknown"

    def _look_for_nat_interface(self):
        """
        Look for a NAT interface.

        :returns: nat interface number or -1 if none is found
        """

        result = self._vm.execute_vboxmanage("showvminfo", [self._vmname, "--machinereadable"])
        interface = -1
        for info in result.splitlines():
            if '=' in info:
                name, value = info.split('=', 1)
                if name.startswith("nic") and value.strip('"') == "nat":
                    try:
                        interface = int(name[3:])
                        break
                    except ValueError:
                        continue
        return interface

    def _check_vbox_port_forwarding(self):
        """
        Checks if the NAT port forwarding rule exists.

        :returns: boolean
        """

        result = self._vm.execute_vboxmanage("showvminfo", [self._vmname, "--machinereadable"])
        for info in result.splitlines():
            if '=' in info:
                name, value = info.split('=', 1)
                if name.startswith("Forwarding") and value.strip('"').startswith("GNS3VM"):
                    return True
        return False

    def _server_request(self, host, port, endpoint, timeout=120):
        """
        Sends an HTTP request to a server.

        :param host: server host
        :param port: server port
        :param endpoint: server endpoint
        :returns: response code, json data
        """

        url = "{protocol}://{host}:{port}{endpoint}".format(protocol="http", host=host, port=port, endpoint=endpoint)
        response = urllib.request.urlopen(url, timeout=timeout)
        content_type = response.getheader("CONTENT-TYPE")
        if response.status == 200 and content_type == "application/json":
            content = response.read()
            json_data = json.loads(content.decode("utf-8"))
            return response.status, json_data
        return response.status, None

    def run(self):
        """
        Worker starting point.
        """

        self._is_running = True
        if self._virtualization == "VMware":
            # handle a VMware based GNS3 VM

            # check we have a valid VMX file path
            if not self._vmx_path:
                self.error.emit("GNS3 VM is not configured", True)
                return
            if not os.path.exists(self._vmx_path):
                self.error.emit("VMware VMX file {} doesn't exist".format(self._vmx_path), True)
                return

            try:
                # start the VM
                args = [self._vmx_path]
                if self._headless:
                    args.extend(["nogui"])
                self._vm.execute_vmrun("start", args)
                self._vm.setRunning(True)

                # check if the VMware guest tools are installed
                vmware_tools_state = self._vm.execute_vmrun("checkToolsState", [self._vmx_path])
                if vmware_tools_state not in ("installed", "running"):
                    self.error.emit("VMware tools are not installed in {}".format(self._vmname), True)
                    return

                # get the guest IP address (first adapter only)
                self._server_host = self._vm.execute_vmrun("getGuestIPAddress", [self._vmx_path, "-wait"])
            except (OSError, subprocess.SubprocessError) as e:
                self.error.emit("Could not execute vmrun: {}".format(e), True)
                return

        elif self._virtualization == "VirtualBox":
            # handle a VirtualBox based GNS3 VM

            try:
                # get a NAT interface number
                nat_interface_number = self._look_for_nat_interface()
                if nat_interface_number < 0:
                    self.error.emit("The GNS3 VM must have a NAT interface configured in order to start", True)
                    return

                vm_state = self._get_vbox_vm_state()
                log.info('"{}" state is {}'.format(self._vmname, vm_state))
                if vm_state in ("poweroff", "saved"):
                    # start the VM if it is not running
                    args = [self._vmname]
                    if self._headless:
                        args.extend(["--type", "headless"])
                    self._vm.execute_vboxmanage("startvm", args)
                self._vm.setRunning(True)

                ip_address = "127.0.0.1"
                try:
                    # get a random port on localhost
                    with socket.socket() as s:
                        s.bind((ip_address, 0))
                        port = s.getsockname()[1]
                except OSError as e:
                    self.error.emit("Error while getting random port: {}".format(e), True)
                    return

                if self._check_vbox_port_forwarding():
                    # delete the GNS3VM NAT port forwarding rule if it exists
                    log.debug("Removing GNS3VM NAT port forwarding rule from interface {}".format(nat_interface_number))
                    self._vm.execute_vboxmanage("controlvm", [self._vmname, "natpf{}".format(nat_interface_number), "delete", "GNS3VM"])

                # add a GNS3VM NAT port forwarding rule to redirect 127.0.0.1 with random port to port 8000 in the VM
                log.debug("Adding GNS3VM NAT port forwarding rule with port {} to interface {}".format(port, nat_interface_number))
                self._vm.execute_vboxmanage("controlvm", [self._vmname, "natpf{}".format(nat_interface_number), "GNS3VM,tcp,{},{},,8000".format(ip_address, port)])

                # TODO: get the guest IP address
                self._server_host = ip_address

            except (OSError, subprocess.SubprocessError) as e:
                self.error.emit("Could not execute VBoxManage: {}".format(e), True)
                return

        log.info("GNS3 VM is started and server is running on {}:{}".format(self._server_host, self._server_port))
        try:
            status, json_data = self._server_request(self._server_host, self._server_port, "/v1/version")
            if status != 200:
                self.error.emit("Server has replied with status code {} when retrieving version number".format(status), True)
                return
            server_version = json_data["version"]
            if __version__ != server_version:
                self.error.emit("Client version {} differs with server version {} in the GNS3 VM, please upgrade...".format(__version__, server_version), True)
                return
        except OSError as e:
            self.error.emit("Request error {}".format(e), True)
            return

        self.finished.emit()

    def cancel(self):
        """
        Cancel this worker.
        """

        self._is_running = False
