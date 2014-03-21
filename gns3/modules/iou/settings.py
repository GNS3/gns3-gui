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

import sys

"""
Default IOU settings.
"""

IOU_SETTINGS = {
    "iourc": "",
    "iouyap": "",
    "console_start_port_range": 4001,
    "console_end_port_range": 4512,
    "udp_start_port_range": 30001,
    "udp_end_port_range": 40001,
    "use_local_server": True,
}

# IOU is only available on Linux
if not sys.platform.startswith("linux"):
    IOU_SETTINGS["use_local_server"] = False

IOU_SETTING_TYPES = {
    "iourc": str,
    "iouyap": str,
    "console_start_port_range": int,
    "console_end_port_range": int,
    "udp_start_port_range": int,
    "udp_end_port_range": int,
    "use_local_server": bool,
}
