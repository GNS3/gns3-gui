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
import os
import pkg_resources


def get_resource(resource_name):

    resource_path = None
    if hasattr(sys, "frozen") and sys.platform.startswith("darwin"):
        resource_name = os.path.join("../Resources", resource_name)
    if hasattr(sys, "frozen") and os.path.exists(resource_name):
        resource_path = os.path.normpath(os.path.join(os.getcwd(), resource_name))
    elif not hasattr(sys, "frozen") and pkg_resources.resource_exists("gns3", resource_name):
        resource_path = pkg_resources.resource_filename("gns3", resource_name)
        resource_path = os.path.normpath(resource_path)
    return resource_path
