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
Default QEMU settings.
"""

from gns3.node import Node

QEMU_SETTINGS = {
    "enable_hardware_acceleration": True,
    "require_hardware_acceleration": True,
}

QEMU_VM_SETTINGS = {
    "name": "",
    "default_name_format": "{name}-{0}",
    "usage": "",
    "symbol": "qemu_guest",
    "category": Node.end_devices,
    "port_name_format": "Ethernet{0}",
    "port_segment_size": 0,
    "first_port_name": "",
    "custom_adapters": [],
    "hda_disk_image": "",
    "hdb_disk_image": "",
    "hdc_disk_image": "",
    "hdd_disk_image": "",
    "hda_disk_interface": "none",
    "hdb_disk_interface": "none",
    "hdc_disk_interface": "none",
    "hdd_disk_interface": "none",
    "cdrom_image": "",
    "bios_image": "",
    "boot_priority": "c",
    "console_type": "telnet",
    "console_auto_start": False,
    "aux_type": "none",
    "ram": 256,
    "cpus": 1,
    "adapters": 1,
    "adapter_type": "e1000",
    "mac_address": "",
    "replicate_network_connection_state": True,
    "tpm": False,
    "uefi": False,
    "create_config_disk": False,
    "on_close": "power_off",
    "platform": "x86_64",
    "qemu_path": "",
    "cpu_throttling": 0,
    "process_priority": "normal",
    "options": "",
    "kernel_image": "",
    "initrd": "",
    "kernel_command_line": "",
    "linked_clone": True,
    "compute_id": "local",
    "node_type": "qemu"
}
