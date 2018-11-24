# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 GNS3 Technologies Inc.
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
Default TraceNG settings.
"""

from gns3.node import Node

TRACENG_SETTINGS = {
    "traceng_path": "",
}

TRACENG_NODES_SETTINGS = {
    "name": "",
    "ip_address": "",
    "default_destination": "",
    "default_name_format": "TraceNG{0}",
    "console_type": "none",
    "symbol": ":/symbols/traceng.svg",
    "category": Node.end_devices,
    "node_type": "traceng"
}
