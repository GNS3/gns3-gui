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

from ..qt import QtCore
from ..version import __version__
from ..gns3_vm import GNS3VM
from ..servers import Servers

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

    def _look_for_interface(self, network_backend):
        """
        Look for an interface with a specific network backend.

        :returns: interface number or -1 if none is found
        """

        result = self._vm.execute_vboxmanage("showvminfo", [self._vmname, "--machinereadable"])
        interface = -1
        for info in result.splitlines():
            if '=' in info:
                name, value = info.split('=', 1)
                if name.startswith("nic") and value.strip('"') == network_backend:
                    try:
                        interface = int(name[3:])
                        break
                    except ValueError:
                        continue
        return interface

    def _look_for_vboxnet(self, interface_number):
        """
        Look for the VirtualBox network name associated with a host only interface.

        :returns: None or vboxnet name
        """

        result = self._vm.execute_vboxmanage("showvminfo", [self._vmname, "--machinereadable"])
        for info in result.splitlines():
            if '=' in info:
                name, value = info.split('=', 1)
                if name == "hostonlyadapter{}".format(interface_number):
                    return value.strip('"')
        return None

    def _check_dhcp_server(self, vboxnet):
        """
        Check if the DHCP server associated with a vboxnet is enabled.

        :param vboxnet: vboxnet name

        :returns: boolean
        """

        properties = self._vm.execute_vboxmanage("list", ["dhcpservers"])
        flag_dhcp_server_found = False
        for prop in properties.splitlines():
            try:
                name, value = prop.split(':', 1)
            except ValueError:
                continue
            if name.strip() == "NetworkName" and value.strip().endswith(vboxnet):
                flag_dhcp_server_found = True
            if flag_dhcp_server_found and name.strip() == "Enabled":
                if value.strip() == "Yes":
                    return True
        return False

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

    def _waitForServer(self, vm_server, endpoint, retry=0):
        """
        Wait for a VM server to reply to a request.

        :param vm_server: The server instance
        :param retry: How many time we need to retry if server doesn't answer wait 1 second between test
        """

        json_data = []
        status = 0
        while retry >= 0:
            status, json_data = vm_server.getSynchronous(endpoint, timeout=3)
            if status != 0 or not self._is_running:
                break
            self.thread().sleep(1)
            retry -= 1
        return status, json_data

    def run(self):
        """
        Worker starting point.
        """

        vm_server = Servers.instance().vmServer()
        self._is_running = True
        if self._virtualization == "VMware":
            self._is_running = self._start_vmware(vm_server)
        elif self._virtualization == "VirtualBox":
            self._is_running = self._start_virtualbox(vm_server)

        if not self._is_running:
            return

        log.info("GNS3 VM is started and server is running on {}:{}".format(vm_server.host(), vm_server.port()))
        try:
            status, json_data = self._waitForServer(vm_server, "version", retry=40)
            if status == 401:
                self.error.emit("Wrong user or password for the GNS3 VM".format(status), True)
                return
            elif status != 200:
                if status == 0:
                    msg = "Could not connect to GNS3 server {}:{} (please check your firewall settings)".format(vm_server.host(),
                                                                                                                vm_server.port())
                else:
                    msg = "Server has replied with status code {} when retrieving version number".format(status)
                log.error(msg)
                self.error.emit(msg, True)
                return
            server_version = json_data["version"]
            if __version__ != server_version:
                # Just a warning: the HTTP code for the connection to the server will block if the version has a mismatch
                print("Client version {} differs with server version {} in the GNS3 VM, please upgrade the VM by selecting the Upgrade options in the VM menu.".format(__version__, server_version))
        except OSError as e:
            self.error.emit("Request error {}".format(e), True)
            return

        self.finished.emit()

    def _start_vmware(self, vm_server):
        """
        Handle a VMware based GNS3 VM
        """

        # check we have a valid VMX file path
        if not self._vmx_path:
            self.error.emit("GNS3 VM is not configured", True)
            return False
        if not os.path.exists(self._vmx_path):
            self.error.emit("VMware VMX file {} doesn't exist".format(self._vmx_path), True)
            return False

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
                return False

            if not self._is_running:
                return False

            # get the guest IP address (first adapter only)
            guest_ip_address = self._vm.execute_vmrun("getGuestIPAddress", [self._vmx_path, "-wait"], timeout=120)
            vm_server.setHost(guest_ip_address)
            log.info("GNS3 VM IP address set to {}".format(guest_ip_address))
        except OSError as e:
            self.error.emit("Could not execute vmrun: {}".format(e), True)
            return False
        except subprocess.SubprocessError as e:
            self.error.emit("Could not execute vmrun: {} with output '{}'\n\nMake sure the correct product (Fusion, Workstation or Player) is selected in Preferences / VMware".format(e, e.output.decode("utf-8", errors="ignore").strip()), True)
            return False
        except subprocess.TimeoutExpired:
            self.error.emit("vmrun timeout expired", True)
            return False
        return True

    def _start_virtualbox(self, vm_server):
        """
        Handle a VirtualBox based GNS3 VM
        """

        try:
            # get a NAT interface number
            nat_interface_number = self._look_for_interface("nat")
            if nat_interface_number < 0:
                self.error.emit("The GNS3 VM must have a NAT interface configured in order to start", True)
                return False

            hostonly_interface_number = self._look_for_interface("hostonly")
            if hostonly_interface_number < 0:
                self.error.emit("The GNS3 VM must have a host only interface configured in order to start", True)
                return False

            vboxnet = self._look_for_vboxnet(hostonly_interface_number)
            if vboxnet is None:
                self.error.emit("VirtualBox host-only network could not be found for interface {}".format(hostonly_interface_number), True)
                return False

            if not self._check_dhcp_server(vboxnet):
                self.error.emit("DHCP must be enabled on VirtualBox host-only network: {}".format(vboxnet), True)
                return False

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
                return False

            if self._check_vbox_port_forwarding():
                # delete the GNS3VM NAT port forwarding rule if it exists
                log.debug("Removing GNS3VM NAT port forwarding rule from interface {}".format(nat_interface_number))
                self._vm.execute_vboxmanage("controlvm", [self._vmname, "natpf{}".format(nat_interface_number), "delete", "GNS3VM"])

            # add a GNS3VM NAT port forwarding rule to redirect 127.0.0.1 with random port to port 3080 in the VM
            log.debug("Adding GNS3VM NAT port forwarding rule with port {} to interface {}".format(port, nat_interface_number))
            self._vm.execute_vboxmanage("controlvm", [self._vmname, "natpf{}".format(nat_interface_number), "GNS3VM,tcp,{},{},,3080".format(ip_address, port)])

            if not self._is_running:
                return False

            original_port = vm_server.port()
            vm_server.setPort(port)
            vm_server.setHost(ip_address)
            # ask the server all a list of all its interfaces along with IP addresses
            status, json_data = self._waitForServer(vm_server, "interfaces", retry=120)
            if status == 401:
                self.error.emit("Wrong user or password for the GNS3 VM".format(status), True)
                return False
            if status != 200:
                msg = "Server {} has replied with status code {} when retrieving the network interfaces".format(vm_server.url(), status)
                log.error(msg)
                self.error.emit(msg, True)
                return False

            # find the ip address for the first hostonly interface
            hostonly_ip_address_found = False
            for interface in json_data:
                if "name" in interface and interface["name"] == "eth{}".format(hostonly_interface_number - 1):
                    if "ip_address" in interface:
                        vm_server.setHost(interface["ip_address"])
                        vm_server.setPort(original_port)
                        log.info("GNS3 VM IP address set to {}".format(interface["ip_address"]))
                        hostonly_ip_address_found = True
                        break

            if not hostonly_ip_address_found:
                self.error.emit("Not IP address could be found in the GNS3 VM for eth{}".format(hostonly_interface_number - 1), True)
                return False

        except OSError as e:
            self.error.emit("Could not execute VBoxManage: {}".format(e), True)
            return False
        except subprocess.SubprocessError as e:
            self.error.emit("Could not execute VBoxManage: {} with output '{}'".format(e, e.output.decode("utf-8", errors="ignore").strip()), True)
            return False
        except subprocess.TimeoutExpired:
            self.error.emit("VBoxmanage timeout expired", True)
            return False
        return True

    def cancel(self):
        """
        Cancel this worker.
        """

        if not self:
            return
        self._is_running = False
        self._vm.killRunningProcess()
        self._vm.setRunning(False)
