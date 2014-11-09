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

from gns3.node import Node

import sys
import os


# default path to Dynamips executable
if sys.platform.startswith("win"):
    DEFAULT_DYNAMIPS_PATH = r"dynamips\dynamips.exe"
elif sys.platform.startswith("darwin") and hasattr(sys, "frozen"):
    DEFAULT_DYNAMIPS_PATH = os.path.join(os.getcwd(), "dynamips")
else:
    paths = [os.getcwd()] + os.environ["PATH"].split(os.pathsep)
    # look for dynamips in the current working directory and $PATH
    DEFAULT_DYNAMIPS_PATH = "dynamips"
    for path in paths:
        try:
            if "dynamips" in os.listdir(path) and os.access(os.path.join(path, "dynamips"), os.X_OK):
                DEFAULT_DYNAMIPS_PATH = os.path.join(path, "dynamips")
                break
        except OSError:
            continue

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

IOS_ROUTER_SETTINGS = {
    "name": "",
    "path": "",
    "image": "",
    "default_symbol": ":/symbols/router.normal.svg",
    "hover_symbol": ":/symbols/router.selected.svg",
    "category": Node.routers,
    "startup_config": "",
    "private_config": "",
    "platform": "",
    "chassis": "",
    "idlepc": "",
    "idlemax": 500,
    "idlesleep": 30,
    "exec_area": 64,
    "mmap": True,
    "sparsemem": True,
    "ram": 128,
    "nvram": 256,
    "mac_addr": "",
    "disk0": 1,
    "disk1": 0,
    "confreg": "0x2102",
    "system_id": "FTX0945W0MY",
    "server": "local"
}

IOS_ROUTER_SETTING_TYPES = {
    "name": str,
    "path": str,
    "image": str,
    "default_symbol": str,
    "hover_symbol": str,
    "category": int,
    "startup_config": str,
    "private_config": str,
    "platform": str,
    "chassis": str,
    "idlepc": str,
    "idlemax": int,
    "idlesleep": int,
    "exec_area": int,
    "mmap": bool,
    "sparsemem": bool,
    "ram": int,
    "nvram": int,
    "mac_addr": str,
    "disk0": int,
    "disk1": int,
    "confreg": str,
    "system_id": str,
    "server": str
}

# supported platforms with the default RAM value
PLATFORMS_DEFAULT_RAM = {"c1700": 64,
                         "c2600": 64,
                         "c2691": 128,
                         "c3600": 128,
                         "c3725": 128,
                         "c3745": 128,
                         "c7200": 512}

# platforms with supported chassis
CHASSIS = {"c1700": ("1720", "1721", "1750", "1751", "1760"),
           "c2600": ("2610", "2611", "2620", "2621", "2610XM", "2611XM", "2620XM", "2621XM", "2650XM", "2651XM"),
           "c3600": ("3620", "3640", "3660")}

# Network modules for the c2600 platform
C2600_NMS = (
    "NM-1FE-TX",
    "NM-1E",
    "NM-4E",
    "NM-16ESW"
)

# Network modules for the c3600 platform
C3600_NMS = (
    "NM-1FE-TX",
    "NM-1E",
    "NM-4E",
    "NM-16ESW",
    "NM-4T"
)

# Network modules for the c3700 platform
C3700_NMS = (
    "NM-1FE-TX",
    "NM-4T",
    "NM-16ESW",
)

# Port adapters for the c7200 platform
C7200_PAS = (
    "PA-A1",
    "PA-FE-TX",
    "PA-2FE-TX",
    "PA-GE",
    "PA-4T+",
    "PA-8T",
    "PA-4E",
    "PA-8E",
    "PA-POS-OC3",
)

# I/O controller for the c7200 platform
IO_C7200 = ("C7200-IO-FE",
            "C7200-IO-2FE",
            "C7200-IO-GE-E"
)

"""
Build the adapter compatibility matrix:

ADAPTER_MATRIX = {
    "c3600" : {                     # Router model
        "3620" : {                  # Router chassis (if applicable)
            { 0 : ("NM-1FE-TX", "NM_1E", ...)
            }
        }
    }
"""

ADAPTER_MATRIX = {}
for platform in ("c1700", "c2600", "c2691", "c3725", "c3745", "c3600", "c7200"):
    ADAPTER_MATRIX[platform] = {}

# 1700s have one interface on the MB, 2 sub-slots for WICs, an no NM slots
for chassis in ("1720", "1721", "1750", "1751", "1760"):
    ADAPTER_MATRIX["c1700"][chassis] = {0: "C1700-MB-1FE"}

# Add a fake NM in slot 1 on 1751s and 1760s to provide two WIC slots
for chassis in ("1751", "1760"):
    ADAPTER_MATRIX["c1700"][chassis][1] = "C1700-MB-WIC1"

# 2600s have one or more interfaces on the MB , 2 subslots for WICs, and an available NM slot 1
for chassis in ("2620", "2610XM", "2620XM", "2650XM"):
    ADAPTER_MATRIX["c2600"][chassis] = {0: "C2600-MB-1FE", 1: C2600_NMS}

for chassis in ("2621", "2611XM", "2621XM", "2651XM"):
    ADAPTER_MATRIX["c2600"][chassis] = {0: "C2600-MB-2FE", 1: C2600_NMS}

ADAPTER_MATRIX["c2600"]["2610"] = {0: "C2600-MB-1E", 1: C2600_NMS}
ADAPTER_MATRIX["c2600"]["2611"] = {0: "C2600-MB-2E", 1: C2600_NMS}

# 2691s have two FEs on the motherboard and one NM slot
ADAPTER_MATRIX["c2691"][""] = {0: "GT96100-FE", 1: C3700_NMS}

# 3620s have two generic NM slots
ADAPTER_MATRIX["c3600"]["3620"] = {}
for slot in range(2):
    ADAPTER_MATRIX["c3600"]["3620"][slot] = C3600_NMS

# 3640s have four generic NM slots
ADAPTER_MATRIX["c3600"]["3640"] = {}
for slot in range(4):
    ADAPTER_MATRIX["c3600"]["3640"][slot] = C3600_NMS

# 3660s have 2 FEs on the motherboard and 6 generic NM slots
ADAPTER_MATRIX["c3600"]["3660"] = {0: "Leopard-2FE"}
for slot in range(1, 7):
    ADAPTER_MATRIX["c3600"]["3660"][slot] = C3600_NMS

# 3725s have 2 FEs on the motherboard and 2 generic NM slots
ADAPTER_MATRIX["c3725"][""] = {0: "GT96100-FE"}
for slot in range(1, 3):
    ADAPTER_MATRIX["c3725"][""][slot] = C3700_NMS

# 3745s have 2 FEs on the motherboard and 4 generic NM slots
ADAPTER_MATRIX["c3745"][""] = {0: "GT96100-FE"}
for slot in range(1, 5):
    ADAPTER_MATRIX["c3745"][""][slot] = C3700_NMS

# 7206s allow an IO controller in slot 0, and a generic PA in slots 1-6
ADAPTER_MATRIX["c7200"][""] = {0: IO_C7200}
for slot in range(1, 7):
    ADAPTER_MATRIX["c7200"][""][slot] = C7200_PAS

C1700_WICS = ("WIC-1T", "WIC-2T", "WIC-1ENET")
C2600_WICS = ("WIC-1T", "WIC-2T")
C3700_WICS = ("WIC-1T", "WIC-2T")

WIC_MATRIX = {}

WIC_MATRIX["c1700"] = {0: C1700_WICS, 1: C1700_WICS}
WIC_MATRIX["c2600"] = {0: C2600_WICS, 1: C2600_WICS, 2: C2600_WICS}
WIC_MATRIX["c2691"] = {0: C3700_WICS, 1: C3700_WICS, 2: C3700_WICS}
WIC_MATRIX["c3725"] = {0: C3700_WICS, 1: C3700_WICS, 2: C3700_WICS}
WIC_MATRIX["c3745"] = {0: C3700_WICS, 1: C3700_WICS, 2: C3700_WICS}
