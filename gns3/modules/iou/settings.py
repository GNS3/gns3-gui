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
    "iourc_content": "",
    "license_check": True,
}

IOU_DEVICE_SETTINGS = {
    "name": "",
    "default_name_format": "IOU{0}",
    "path": "",
    "symbol": ":/symbols/multilayer_switch.svg",
    "category": Node.routers,
    "image": "",
    "startup_config": "",
    "private_config": "",
    "use_default_iou_values": True,
    "ram": 256,
    "nvram": 128,
    "ethernet_adapters": 2,
    "serial_adapters": 2,
    "server": "local"
}
