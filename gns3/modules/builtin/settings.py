# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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
Default Built-in settings.
"""

from gns3.node import Node

BUILTIN_SETTINGS = {
}


NAT_SETTINGS = {
    "name": "",
    "default_name_format": "Nat{0}",
    "symbol": ":/symbols/cloud.svg",
    "category": Node.end_devices,
    "ports_mapping": [],
}

CLOUD_SETTINGS = {
    "name": "",
    "default_name_format": "Cloud{0}",
    "symbol": ":/symbols/cloud.svg",
    "category": Node.end_devices,
    "ports_mapping": [],
}

ETHERNET_HUB_SETTINGS = {
    "name": "",
    "default_name_format": "Hub{0}",
    "symbol": ":/symbols/hub.svg",
    "category": Node.switches,
    "ports_mapping": [],
}

ETHERNET_SWITCH_SETTINGS = {
    "name": "",
    "default_name_format": "Switch{0}",
    "symbol": ":/symbols/ethernet_switch.svg",
    "category": Node.switches,
    "ports_mapping": [],
}
