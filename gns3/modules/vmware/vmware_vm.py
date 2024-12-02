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
VMware VM implementation.
"""

import sys

from gns3.qt import QtCore
from gns3.node import Node
from gns3.utils.bring_to_front import bring_window_to_front_from_process_name
from .settings import VMWARE_VM_SETTINGS

import logging
log = logging.getLogger(__name__)


class VMwareVM(Node):
    """
    VirtualBox VM.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "vmware"
    allocate_vmnet_nio_signal = QtCore.Signal(int, int, str)

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        self._linked_clone = False

        vmware_vm_settings = {"vmx_path": "",
                              "usage": "",
                              "adapters": VMWARE_VM_SETTINGS["adapters"],
                              "adapter_type": VMWARE_VM_SETTINGS["adapter_type"],
                              "use_any_adapter": VMWARE_VM_SETTINGS["use_any_adapter"],
                              "headless": VMWARE_VM_SETTINGS["headless"],
                              "on_close": VMWARE_VM_SETTINGS["on_close"],
                              "console_type": VMWARE_VM_SETTINGS["console_type"],
                              "console_auto_start": VMWARE_VM_SETTINGS["console_auto_start"],
                              "custom_adapters": VMWARE_VM_SETTINGS["custom_adapters"],
                              "port_name_format": "Ethernet{0}",
                              "port_segment_size": 0,
                              "first_port_name": None}

        self.settings().update(vmware_vm_settings)

    def info(self):
        """
        Returns information about this VMware VM instance.

        :returns: formatted string
        """

        info = """VMware VM {name} is {state}
  Running on server {host} with port {port}
  Local ID is {id} and server ID is {node_id}
  Console is on port {console} and type is {console_type}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           state=self.state(),
           host=self.compute().name(),
           port=self.compute().port(),
           console=self._settings["console"],
           console_type=self._settings["console_type"])

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "     {port_name} is empty\n".format(port_name=port.name())
            else:
                port_info += "     {port_name} {port_description}\n".format(port_name=port.name(),
                                                                            port_description=port.description())

        usage = "\n" + self._settings.get("usage")
        return info + port_info + usage

    def allocateVMnetInterface(self, port_id):
        """
        Requests an UDP port allocation.

        :param port_id: port identifier
        """

        log.debug("{} is requesting a VMnet interface allocation".format(self.name()))
        self.httpPost("/vmware/nodes/{node_id}/interfaces/vmnet".format(node_id=self._node_id), self._allocateVMnetInterfaceCallback, context={"port_id": port_id})

    def _allocateVMnetInterfaceCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for allocateVMnetInterface

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while allocating a VMnet interface for {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            port_id = context["port_id"]
            vmnet = result["vmnet"]
            log.debug("{} has allocated VMnet interface {}".format(self.name(), vmnet))
            self.allocate_vmnet_nio_signal.emit(self.id(), port_id, vmnet)

    def bringToFront(self):
        """
        Bring the VM window to front.
        """

        if self.status() == Node.started and sys.platform.startswith("win"):
            try:
                vmx_pairs = self.module().parseVMwareFile(self.settings()["vmx_path"])
            except OSError as e:
                log.debug("Could not read VMX file: {}".format(e))
                return
            if "displayname" in vmx_pairs:
                window_name = "{} -".format(vmx_pairs["displayname"])
                # try for both VMware Player and Workstation
                bring_window_to_front_from_process_name("vmplayer.exe", title=window_name)
                bring_window_to_front_from_process_name("vmware.exe", title=window_name)

        # bring any console to front
        return Node.bringToFront(self)

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

        :returns: QWidget object
        """

        from .pages.vmware_vm_configuration_page import VMwareVMConfigurationPage
        return VMwareVMConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/vmware_guest.svg"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.end_devices]

    def __str__(self):

        return "VMware VM"
