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

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    # get the default slot0 adapter based on the chassis
    chassis_to_default_adapter = {"2610": "C2600-MB-1E",
                                  "2611": "C2600-MB-2E",
                                  "2620": "C2600-MB-1FE",
                                  "2621": "C2600-MB-2FE",
                                  "2610XM": "C2600-MB-1FE",
                                  "2611XM": "C2600-MB-2FE",
                                  "2620XM": "C2600-MB-1FE",
                                  "2621XM": "C2600-MB-2FE",
                                  "2650XM": "C2600-MB-1FE",
                                  "2651XM": "C2600-MB-2FE"}

    def __init__(self, module, server, project, chassis="2610"):

        super().__init__(module, server, project, platform="c2600")
        c2600_settings = {"ram": 128,
                          "nvram": 128,
                          "disk0": 0,
                          "disk1": 0,
                          "chassis": chassis,
                          "iomem": 15,
                          "clock_divisor": 8}

        # set the default adapter for slot 0
        c2600_settings["slot0"] = self.chassis_to_default_adapter[chassis]

        # merge platform settings with the generic ones
        self._settings.update(c2600_settings)

    def __str__(self):

        return "Router c2600"

    @staticmethod
    def symbolName():

        return "Router c2600"
