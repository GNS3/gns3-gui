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

from gns3.node import Node

VBOX_SETTINGS = {
    "vboxmanage_path": "",
    "vbox_user": "",
    "use_local_server": True,
}

VBOX_SETTING_TYPES = {
    "vboxmanage_path": str,
    "vbox_user": str,
    "use_local_server": bool,
}

VBOX_VM_SETTINGS = {
    "vmname": "",
    "default_symbol": ":/symbols/vbox_guest.normal.svg",
    "hover_symbol": ":/symbols/vbox_guest.selected.svg",
    "category": Node.end_devices,
    "adapters": 1,
    "ram": 0,
    "use_any_adapter": False,
    "adapter_type": "Intel PRO/1000 MT Desktop (82540EM)",
    "headless": False,
    "enable_remote_console": False,
    "linked_base": False,
    "server": "local"
}

VBOX_VM_SETTING_TYPES = {
    "vmname": str,
    "default_symbol": str,
    "hover_symbol": str,
    "category": int,
    "adapters": int,
    "ram": int,
    "use_any_adapter": bool,
    "adapter_type": str,
    "headless": bool,
    "enable_remote_console": bool,
    "linked_base": bool,
    "server": str
}
