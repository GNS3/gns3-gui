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
QEMU VM implementation.
"""

import re

from gns3.node import Node
from .settings import QEMU_VM_SETTINGS


import logging
log = logging.getLogger(__name__)


class QemuVM(Node):
    """
    QEMU VM.

    :param module: parent module for this node
    :param server: GNS3 server instance
    """

    URL_PREFIX = "qemu"

    def __init__(self, module, server, project):
        super().__init__(module, server, project)

        self._linked_clone = True

        qemu_vm_settings = {"usage": "",
                            "qemu_path": "",
                            "hda_disk_image": "",
                            "hdb_disk_image": "",
                            "hdc_disk_image": "",
                            "hdd_disk_image": "",
                            "hda_disk_interface": QEMU_VM_SETTINGS["hda_disk_interface"],
                            "hdb_disk_interface": QEMU_VM_SETTINGS["hdb_disk_interface"],
                            "hdc_disk_interface": QEMU_VM_SETTINGS["hdc_disk_interface"],
                            "hdd_disk_interface": QEMU_VM_SETTINGS["hdd_disk_interface"],
                            "cdrom_image": "",
                            "bios_image": "",
                            "hda_disk_image_md5sum": "",
                            "hdb_disk_image_md5sum": "",
                            "hdc_disk_image_md5sum": "",
                            "hdd_disk_image_md5sum": "",
                            "cdrom_image_md5sum": "",
                            "bios_image_md5sum": "",
                            "boot_priority": QEMU_VM_SETTINGS["boot_priority"],
                            "options": "",
                            "ram": QEMU_VM_SETTINGS["ram"],
                            "cpus": QEMU_VM_SETTINGS["cpus"],
                            "console_type": QEMU_VM_SETTINGS["console_type"],
                            "console_auto_start": QEMU_VM_SETTINGS["console_auto_start"],
                            "adapters": QEMU_VM_SETTINGS["adapters"],
                            "custom_adapters": QEMU_VM_SETTINGS["custom_adapters"],
                            "adapter_type": QEMU_VM_SETTINGS["adapter_type"],
                            "mac_address": QEMU_VM_SETTINGS["mac_address"],
                            "legacy_networking": QEMU_VM_SETTINGS["legacy_networking"],
                            "replicate_network_connection_state": QEMU_VM_SETTINGS["replicate_network_connection_state"],
                            "tpm": QEMU_VM_SETTINGS["tpm"],
                            "uefi": QEMU_VM_SETTINGS["uefi"],
                            "create_config_disk": QEMU_VM_SETTINGS["create_config_disk"],
                            "platform": QEMU_VM_SETTINGS["platform"],
                            "on_close": QEMU_VM_SETTINGS["on_close"],
                            "cpu_throttling": QEMU_VM_SETTINGS["cpu_throttling"],
                            "process_priority": QEMU_VM_SETTINGS["process_priority"],
                            "initrd": "",
                            "kernel_image": "",
                            "initrd_md5sum": "",
                            "kernel_image_md5sum": "",
                            "kernel_command_line": "",
                            "port_name_format": "Ethernet{0}",
                            "port_segment_size": 0,
                            "first_port_name": ""}

        self.settings().update(qemu_vm_settings)

    def resizeDiskImage(self, drive_name, size, callback):
        """
        Resize a disk image allocated to the VM.

        :param callback: callback for the reply from the server
        """

        params = {"drive_name": drive_name,
                  "extend": size}
        self.post("/resize_disk", callback, body=params)

    def info(self):
        """
        Returns information about this QEMU VM instance.

        :returns: formatted string
        """

        info = """QEMU VM {name} is {state}
  Running on server {host} with port {port}
  Local ID is {id} and server ID is {node_id}
  Number of processors is {cpus} and amount of memory is {ram}MB
  Console is on port {console} and type is {console_type}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           state=self.state(),
           host=self.compute().name(),
           port=self.compute().port(),
           cpus=self._settings["cpus"],
           ram=self._settings["ram"],
           console=self._settings["console"],
           console_type=self._settings["console_type"])

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "     {port_name} is empty\n".format(port_name=port.name())
            else:
                port_info += "     {port_name} {port_description}\n".format(port_name=port.name(),
                                                                            port_description=port.description())
            if port.macAddress():
                port_info += "       MAC address is {mac_address}\n".format(mac_address=port.macAddress())

        usage = "\n" + self._settings.get("usage")
        return info + port_info + usage

    def configFiles(self):
        """
        Name of the configuration files
        """

        if self._settings.get("create_config_disk"):
            return ["config.zip"]
        return None

    def configTextFiles(self):
        """
        Name of the configuration files, which are plain text files

        :returns: List of configuration files, False if no files
        """

        return None

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

        :returns: QWidget object
        """

        from .pages.qemu_vm_configuration_page import QemuVMConfigurationPage
        return QemuVMConfigurationPage

    @staticmethod
    def validateHostname(hostname):
        """
        Checks if the hostname is valid.

        :param hostname: hostname to check

        :returns: boolean
        """

        return QemuVM.isValidRfc1123Hostname(hostname)

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/qemu_guest.svg"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.end_devices]

    def __str__(self):

        return "QEMU VM"
