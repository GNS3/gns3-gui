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
Default QEMU settings.
"""

import sys
import os

# default path to qemu-img executable
if sys.platform.startswith("win"):
    DEFAULT_QEMU_IMG_PATH = r"qemu\qemu-img.exe"
elif sys.platform.startswith("darwin") and hasattr(sys, "frozen"):
    DEFAULT_QEMU_IMG_PATH = os.path.join(os.getcwd(), "qemu-img")
else:
    paths = [os.getcwd()] + os.environ["PATH"].split(":")
    # look for qemu-img in the current working directory and $PATH
    DEFAULT_QEMU_IMG_PATH = "qemu-img"
    for path in paths:
        try:
            if "qemu-img" in os.listdir(path) and os.access(os.path.join(path, "qemu-img"), os.X_OK):
                DEFAULT_QEMU_IMG_PATH = os.path.join(path, "qemu-img")
                break
        except OSError:
            continue

QEMU_SETTINGS = {
    "qemu_img_path": DEFAULT_QEMU_IMG_PATH,
    "console_start_port_range": 5001,
    "console_end_port_range": 5500,
    "udp_start_port_range": 40001,
    "udp_end_port_range": 45500,
    "use_local_server": True,
}

QEMU_SETTING_TYPES = {
    "qemu_img_path": str,
    "console_start_port_range": int,
    "console_end_port_range": int,
    "udp_start_port_range": int,
    "udp_end_port_range": int,
    "use_local_server": bool,
}
