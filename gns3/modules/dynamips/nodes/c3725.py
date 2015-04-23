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
Dynamips c3725 router implementation.
"""

from .router import Router


class C3725(Router):

    """
    Dynamips c3725 router.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    def __init__(self, module, server, project):

        super().__init__(module, server, project, platform="c3725")
        c3725_settings = {"ram": 128,
                          "nvram": 112,
                          "disk0": 16,
                          "disk1": 0,
                          "iomem": 5,
                          "clock_divisor": 8,
                          "slot0": "GT96100-FE"}

        # merge platform settings with the generic ones
        self._settings.update(c3725_settings)

    def __str__(self):

        return "Router c3725"

    @staticmethod
    def symbolName():

        return "Router c3725"
