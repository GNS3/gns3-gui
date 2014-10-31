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

# default path to VirtualBox vboxmanage executable
if sys.platform.startswith("win") and "VBOX_INSTALL_PATH" in os.environ:
    DEFAULT_VBOXMANAGE_PATH = os.path.join(os.environ["VBOX_INSTALL_PATH"], "VBoxManage.exe")
else:
    paths = [os.getcwd()] + os.environ["PATH"].split(os.pathsep)
    # look for vboxmanage in the current working directory and $PATH
    DEFAULT_VBOXMANAGE_PATH = "vboxmanage"
    for path in paths:
        try:
            if "vboxmanage" in os.listdir(path) and os.access(os.path.join(path, "vboxmanage"), os.X_OK):
                DEFAULT_VBOXMANAGE_PATH = os.path.join(path, "vboxmanage")
                break
        except OSError:
            continue

VBOX_SETTINGS = {
    "vboxmanage_path": DEFAULT_VBOXMANAGE_PATH,
    "console_start_port_range": 3501,
    "console_end_port_range": 4000,
    "udp_start_port_range": 35001,
    "udp_end_port_range": 35512,
    "use_local_server": True,
}

VBOX_SETTING_TYPES = {
    "vboxmanage_path": str,
    "console_start_port_range": int,
    "console_end_port_range": int,
    "udp_start_port_range": int,
    "udp_end_port_range": int,
    "use_local_server": bool,
}
