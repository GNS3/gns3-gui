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
Dynamips c7200 router implementation.
"""

from .router import Router


class C7200(Router):

    """
    Dynamips c7200 router.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    def __init__(self, module, server, project, npe="npe-400"):

        super().__init__(module, server, project, platform="c7200")
        c7200_settings = {"ram": 512,
                          "nvram": 128,
                          "disk0": 64,
                          "disk1": 0,
                          "npe": npe,
                          "midplane": "vxr",
                          "clock_divisor": 4,
                          "sensors": [22, 22, 22, 22],
                          "power_supplies": [1, 1]}

        # first slot is a mandatory Input/Output controller (based on NPE type)
        if npe == "npe-g2":
            c7200_settings["slot0"] = "C7200-IO-GE-E"
        else:
            c7200_settings["slot0"] = "C7200-IO-FE"

        # merge platform settings with the generic ones
        self._settings.update(c7200_settings)

    def __str__(self):

        return "Router c7200"

    @staticmethod
    def symbolName():

        return "Router c7200"
