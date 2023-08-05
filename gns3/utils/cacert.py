# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 GNS3 Technologies Inc.
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

import os
import sys

from .get_resource import get_resource

import logging
log = logging.getLogger(__name__)


def get_cacert():
    if hasattr(sys, "frozen"):
        cacert_resource = get_resource("cacert.pem")
        if cacert_resource is not None and os.path.isfile(cacert_resource):
            return cacert_resource
        else:
            log.error("The SSL certificate bundle file '{}' could not be found".format(cacert_resource))
    return None  # this means we use the system's CA bundle
