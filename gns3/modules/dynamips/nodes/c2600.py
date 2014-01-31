# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GNS3 Technologies Inc.
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
Dynamips c2600 router implementation.
"""

from .router import Router


class C2600(Router):
    """
    Dynamips c2600 router.

    :param server: GNS3 server instance
    """

    def __init__(self, server):
        Router.__init__(self, server, platform="c2600")

        self._platform_settings = {"ram": 64,
                                   "nvram": 128,
                                   "disk0": 0,
                                   "disk1": 0,
                                   "chassis": "2610",
                                   "iomem": 15,
                                   "clock_divisor": 8}

        # merge platform settings with the generic ones
        self._settings.update(self._platform_settings)

    def __str__(self):

        return "Router c2600"

    @staticmethod
    def symbolName():

        return "Router c2600"
