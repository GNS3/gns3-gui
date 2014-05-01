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
Default Dynamips settings.
"""

import sys
import os

# default path to Dynamips executable
if sys.platform.startswith("win"):
    DEFAULT_DYNAMIPS_PATH = "C:/Program Files (x86)/GNS3-ER/dynamips.exe"
elif sys.platform.startswith('darwin'):
    if hasattr(sys, "frozen"):
        DEFAULT_DYNAMIPS_PATH = os.path.join(os.getcwd(), "../Resources/dynamips-0.2.12-OSX.intel64.bin")
    else:
        DEFAULT_DYNAMIPS_PATH = os.path.join(os.getcwd(), "dynamips-0.2.12-OSX.intel64.bin")
else:
    DEFAULT_DYNAMIPS_PATH = "dynamips"

DYNAMIPS_SETTINGS = {
    "path": DEFAULT_DYNAMIPS_PATH,
    "hypervisor_start_port_range": 7200,
    "hypervisor_end_port_range": 7700,
    "console_start_port_range": 2001,
    "console_end_port_range": 2500,
    "aux_start_port_range": 2501,
    "aux_end_port_range": 3000,
    "udp_start_port_range": 10001,
    "udp_end_port_range": 20000,
    "use_local_server": True,
    "allocate_hypervisor_per_device": True,
    "memory_usage_limit_per_hypervisor": 1024,
    "allocate_hypervisor_per_ios_image": True,
    "ghost_ios_support": True,
    "jit_sharing_support": False,
    "sparse_memory_support": True,
    "mmap_support": True,
}

DYNAMIPS_SETTING_TYPES = {
    "path": str,
    "hypervisor_start_port_range": int,
    "hypervisor_end_port_range": int,
    "console_start_port_range": int,
    "console_end_port_range": int,
    "aux_start_port_range": int,
    "aux_end_port_range": int,
    "udp_start_port_range": int,
    "udp_end_port_range": int,
    "use_local_server": bool,
    "allocate_hypervisor_per_device": bool,
    "memory_usage_limit_per_hypervisor": int,
    "allocate_hypervisor_per_ios_image": bool,
    "ghost_ios_support": bool,
    "jit_sharing_support": bool,
    "sparse_memory_support": bool,
    "mmap_support": bool,
}

# supported platforms with the default RAM value
PLATFORMS_DEFAULT_RAM = {"c1700": 64,
                         "c2600": 64,
                         "c2691": 128,
                         "c3600": 128,
                         "c3725": 128,
                         "c3745": 128,
                         "c7200": 256}

# platforms with supported chassis
CHASSIS = {"c1700": ("1720", "1721", "1750", "1751", "1760"),
           "c2600": ("2610", "2611", "2620", "2621", "2610XM", "2611XM", "2620XM", "2621XM", "2650XM", "2651XM"),
           "c3600": ("3620", "3640", "3660")}
