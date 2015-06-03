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
    "use_local_server": True,
}

QEMU_SETTING_TYPES = {
    "use_local_server": bool,
}

QEMU_VM_SETTINGS = {
    "name": "",
    "default_symbol": ":/symbols/qemu_guest.normal.svg",
    "hover_symbol": ":/symbols/qemu_guest.selected.svg",
    "category": Node.end_devices,
    "qemu_path": "",
    "hda_disk_image": "",
    "hdb_disk_image": "",
    "hdc_disk_image": "",
    "hdd_disk_image": "",
    "ram": 256,
    "adapters": 1,
    "adapter_type": "e1000",
    "mac_address": "",
    "legacy_networking": False,
    "acpi_shutdown": False,
    "cpu_throttling": 0,
    "process_priority": "normal",
    "options": "",
    "initrd": "",
    "kernel_image": "",
    "kernel_command_line": "",
    "server": "local"
}

QEMU_VM_SETTING_TYPES = {
    "name": str,
    "default_symbol": str,
    "hover_symbol": str,
    "category": int,
    "qemu_path": str,
    "hda_disk_image": str,
    "hdb_disk_image": str,
    "hdc_disk_image": str,
    "hdd_disk_image": str,
    "ram": int,
    "adapters": int,
    "adapter_type": str,
    "mac_address": str,
    "legacy_networking": bool,
    "acpi_shutdown": bool,
    "cpu_throttling": int,
    "process_priority": str,
    "options": str,
    "initrd": str,
    "kernel_image": str,
    "kernel_command_line": str,
    "server": str
}


