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
Default VPCS settings.
"""

from gns3.node import Node

VPCS_SETTINGS = {
    "vpcs_path": "",
}

VPCS_NODES_SETTINGS = {
    "name": "",
    "default_name_format": "PC{0}",
    "base_script_file": "",
    "console_type": "telnet",
    "console_auto_start": False,
    "symbol": "vpcs_guest",
    "category": Node.end_devices,
    "node_type": "vpcs"
}
