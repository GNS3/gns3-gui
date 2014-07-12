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
Default VirtualBox settings.
"""

import sys
import os

# default path to VirtualBox wrapper executable
if sys.platform.startswith("darwin") and hasattr(sys, "frozen"):
    DEFAULT_VBOXWRAPPER_PATH = os.path.join(os.getcwd(), "vboxwrapper")
else:
    paths = [os.getcwd()] + os.environ["PATH"].split(":")
    # look for VirtualBox wrapper in the current working directory and $PATH
    DEFAULT_VBOXWRAPPER_PATH = "vboxwrapper"
    for path in paths:
        try:
            if "vboxwrapper" in os.listdir(path) and os.access(os.path.join(path, "vboxwrapper"), os.X_OK):
                DEFAULT_VBOXWRAPPER_PATH = os.path.join(path, "vboxwrapper")
                break
        except OSError:
            continue

VBOX_SETTINGS = {
    "vboxwrapper_path": DEFAULT_VBOXWRAPPER_PATH,
    "console_start_port_range": 3501,
    "console_end_port_range": 4000,
    "udp_start_port_range": 35001,
    "udp_end_port_range": 35512,
    "use_local_server": True,
}

VBOX_SETTING_TYPES = {
    "vboxwrapper_path": str,
    "console_start_port_range": int,
    "console_end_port_range": int,
    "udp_start_port_range": int,
    "udp_end_port_range": int,
    "use_local_server": bool,
}
