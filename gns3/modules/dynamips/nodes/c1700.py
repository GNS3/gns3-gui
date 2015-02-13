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
Dynamips c1700 router implementation.
"""

from .router import Router


class C1700(Router):

    """
    Dynamips c1700 router.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    def __init__(self, module, server, project, chassis="1720"):

        Router.__init__(self, module, server, project, platform="c1700")
        c1700_settings = {"ram": 128,
                          "nvram": 32,
                          "disk0": 0,
                          "disk1": 0,
                          "chassis": "1720",
                          "iomem": 15,
                          "clock_divisor": 8,
                          "slot0": "C1700-MB-1FE"}

        # set the default adapter for slot 1 for these chassis
        if chassis in ['1751', '1760']:
            c1700_settings["slot1"] = "C1700-MB-WIC1"

        # merge platform settings with the generic ones
        self._settings.update(c1700_settings)

    def __str__(self):

        return "Router c1700"

    @staticmethod
    def symbolName():

        return "Router c1700"
