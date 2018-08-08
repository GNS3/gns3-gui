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

from gns3.modules.builtin import Builtin
from gns3.modules.dynamips import Dynamips
from gns3.modules.iou import IOU
from gns3.modules.vpcs import VPCS
from gns3.modules.traceng import TraceNG
from gns3.modules.virtualbox import VirtualBox
from gns3.modules.qemu import Qemu
from gns3.modules.vmware import VMware
from gns3.modules.docker import Docker

#MODULES = [Builtin, VPCS, Dynamips, IOU, Qemu, VirtualBox, VMware, Docker, TraceNG]
#FIXME: deactivate TraceNG module
MODULES = [Builtin, VPCS, Dynamips, IOU, Qemu, VirtualBox, VMware, Docker]
