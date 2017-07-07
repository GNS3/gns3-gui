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
    "enable_kvm": True,
}

QEMU_VM_SETTINGS = {
    "name": "",
    "default_name_format": "{name}-{0}",
    "usage": "",
    "symbol": ":/symbols/qemu_guest.svg",
    "category": Node.end_devices,
    "port_name_format": "Ethernet{0}",
    "port_segment_size": 0,
    "first_port_name": "",
    "qemu_path": "",
    "hda_disk_image": "",
    "hdb_disk_image": "",
    "hdc_disk_image": "",
    "hdd_disk_image": "",
    "hda_disk_interface": "ide",
    "hdb_disk_interface": "ide",
    "hdc_disk_interface": "ide",
    "hdd_disk_interface": "ide",
    "cdrom_image": "",
    "bios_image": "",
    "boot_priority": "c",
    "console_type": "telnet",
    "ram": 256,
    "cpus": 1,
    "adapters": 1,
    "adapter_type": "e1000",
    "mac_address": "",
    "legacy_networking": False,
    "acpi_shutdown": False,
    "platform": "",
    "cpu_throttling": 0,
    "process_priority": "normal",
    "options": "",
    "kernel_image": "",
    "initrd": "",
    "kernel_command_line": "",
    "linked_clone": True,
    "server": "local"
}
