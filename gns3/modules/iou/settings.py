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
Default IOU settings.
"""

import sys
from gns3.node import Node


IOU_SETTINGS = {
    "iourc_path": "",
    "iouyap_path": "",
    "license_check": True,
    "use_local_server": True,
}

# IOU is only available on Linux
if not sys.platform.startswith("linux"):
    IOU_SETTINGS["use_local_server"] = False

IOU_SETTING_TYPES = {
    "iourc_path": str,
    "iouyap_path": str,
    "license_check": bool,
    "use_local_server": bool,
}

IOU_DEVICE_SETTINGS = {
    "name": "",
    "path": "",
    "default_symbol": ":/symbols/multilayer_switch.normal.svg",
    "hover_symbol": ":/symbols/multilayer_switch.selected.svg",
    "category": Node.routers,
    "image": "",
    "initial_config": "",
    "use_default_iou_values": True,
    "ram": 256,
    "nvram": 128,
    "ethernet_adapters": 2,
    "serial_adapters": 2,
    "server": "local"
}

IOU_DEVICE_SETTING_TYPES = {
    "name": str,
    "path": str,
    "default_symbol": str,
    "hover_symbol": str,
    "category": int,
    "image": str,
    "initial_config": str,
    "use_default_iou_values": bool,
    "ram": int,
    "nvram": int,
    "ethernet_adapters": int,
    "serial_adapters": int,
    "server": str
}
