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

import sys
import os

# default path to VPCS executable
if sys.platform.startswith("win"):
    DEFAULT_VPCS_PATH = r"vpcs\vpcs.exe"
elif sys.platform.startswith("darwin") and hasattr(sys, "frozen"):
    DEFAULT_VPCS_PATH = os.path.join(os.getcwd(), "vpcs")
else:
    paths = [os.getcwd()] + os.environ["PATH"].split(os.pathsep)
    # look for VPCS in the current working directory and $PATH
    DEFAULT_VPCS_PATH = "vpcs"
    for path in paths:
        try:
            if "vpcs" in os.listdir(path) and os.access(os.path.join(path, "vpcs"), os.X_OK):
                DEFAULT_VPCS_PATH = os.path.join(path, "vpcs")
                break
        except OSError:
            continue

VPCS_SETTINGS = {
    "path": DEFAULT_VPCS_PATH,
    "console_start_port_range": 4501,
    "console_end_port_range": 5000,
    "udp_start_port_range": 20501,
    "udp_end_port_range": 21000,
    "use_local_server": True,
    "base_script_file": "",
}

VPCS_SETTING_TYPES = {
    "path": str,
    "console_start_port_range": int,
    "console_end_port_range": int,
    "udp_start_port_range": int,
    "udp_end_port_range": int,
    "use_local_server": bool,
    "base_script_file": str,
}
