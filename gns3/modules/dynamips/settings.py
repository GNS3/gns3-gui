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

DYNAMIPS_SETTINGS = {
    "dynamips_path": "",
    "allocate_aux_console_ports": False,
    "ghost_ios_support": True,
    "sparse_memory_support": True,
    "mmap_support": True,
}

IOS_ROUTER_SETTINGS = {
    "name": "",
    "default_name_format": "R{0}",
    "usage": "",
    "image": "",
    "symbol": "router",
    "category": Node.routers,
    "startup_config": "",
    "private_config": "",
    "console_type": "telnet",
    "console_auto_start": False,
    "aux_type": "none",
    "platform": "",
    "idlepc": "",
    "idlemax": 500,
    "idlesleep": 30,
    "exec_area": 64,
    "mmap": True,
    "sparsemem": True,
    "ram": 128,
    "nvram": 128,
    "mac_addr": "",
    "disk0": 0,
    "disk1": 0,
    "auto_delete_disks": False,
    "system_id": "FTX0945W0MY",
    "compute_id": "local",
    "node_type": "dynamips"
}

# supported platforms with the default RAM value
PLATFORMS_DEFAULT_RAM = {"c1700": 160,
                         "c2600": 160,
                         "c2691": 192,
                         "c3600": 192,
                         "c3725": 128,
                         "c3745": 256,
                         "c7200": 512}

# supported platforms with the default NVRAM value
PLATFORMS_DEFAULT_NVRAM = {"c1700": 128,
                           "c2600": 128,
                           "c2691": 256,
                           "c3600": 256,
                           "c3725": 256,
                           "c3745": 256,
                           "c7200": 512}

# MD5 checksum done on uncompressed IOS images
DEFAULT_IDLEPC = {"7f4ae12a098391bc0edcaf4f44caaf9d": "0x80358a60",  # c1700-adventerprisek9-mz.124-25d
                  "3aaecd2222e812c16c211bc9f7c77512": "0x824a4dc4",  # c1700-adventerprisek9-mz.124-15.T14
                  "062a32e9e3f59aeec930ea5694fda9c9": "0x80519c48",  # c2600-adventerprisek9-mz.124-25d
                  "483e3a579a5144ec23f2f160d4b0c0e2": "0x8027ec88",  # c2600-adventerprisek9-mz.124-15.T14
                  "37b444b29191630e5b688f002de2171c": "0x603a8bac",  # c3620-a3jk8s-mz.122-26c
                  "493c4ef6578801d74d715e7d11596964": "0x6050b114",  # c3640-a3js-mz.124-25d
                  "b88ee1b2ed182737395db2df27f34a33": "0x606071f8",  # c3660-a3jk9s-mz.124-25d
                  "daed99f508fd42dbaacf711e560643ed": "0x6076e0b4",  # c3660-a3jk9s-mz.124-15.T14
                  "8dc8486065de63883f29c85825a2f18c": "0x60a48cb8",  # c2691-adventerprisek9-mz.124-25d
                  "e7ee5a4a57ed1433e5f73ba6e7695c90": "0x60bcf9f8",  # c2691-adventerprisek9-mz.124-15.T14
                  "606484061b9e52e71d4f4ddab9af19e7": "0x602467a4",  # c3725-adventerprisek9-mz.124-25d
                  "64f8c427ed48fd21bd02cf1ff254c4eb": "0x60c09aa0",  # c3725-adventerprisek9-mz.124-15.T14
                  "ddbaf74274822b50fa9670e10c75b08f": "0x60aa1da0",  # c3745-adventerprisek9-mz.124-25d
                  "4af2e752220ed1397924150ff7bbe4ce": "0x602701e4",  # c3745-adventerprisek9-mz.124-15.T14
                  "6b89d0d804e1f2bb5b8bda66b5692047": "0x606df838",  # c7200-adventerprisek9-mz.124-24.T5
                  "dda82f22a39215bc6b27af891e12b8f6": "0x6018c294"}  # c7200-adventerprisek9-mz.155-2.XB

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
