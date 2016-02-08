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
Default VMware settings.
"""

import sys
from gns3.node import Node

if sys.platform.startswith("win"):
    DEFAULT_VMNET_END_RANGE = 19
else:
    DEFAULT_VMNET_END_RANGE = 100

VMWARE_SETTINGS = {
    "vmrun_path": "",
    "host_type": "ws",
    "vmnet_start_range": 2,
    "vmnet_end_range": DEFAULT_VMNET_END_RANGE,
    "use_local_server": True
}

VMWARE_VM_SETTINGS = {
    "vmx_path": "",
    "default_name_format": "{name}-{0}",
    "symbol": ":/symbols/vmware_guest.svg",
    "category": Node.end_devices,
    "port_name_format": "Ethernet{0}",
    "port_segment_size": 0,
    "first_port_name": "",
    "adapters": 1,
    "adapter_type": "default",
    "use_ubridge": True,
    "use_any_adapter": False,
    "headless": False,
    "acpi_shutdown": False,
    "enable_remote_console": False,
    "linked_base": False,
    "server": "local"
}
