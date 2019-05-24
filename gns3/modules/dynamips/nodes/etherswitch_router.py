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
EtherSwitch router implementation (based on Dynamips c3745).
This is legacy code, kept only to support topologies made with GNS3 < 1.2.2
"""

from .router import Router
from gns3.node import Node


class EtherSwitchRouter(Router):
    """
    EtherSwitch router.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    def __init__(self, module, server, project):
        super().__init__(module, server, project, platform="c3725")

        self._etherswitch_settings = {"ram": 128,
                                      "nvram": 304,
                                      "disk0": 16,
                                      "disk1": 0,
                                      "iomem": 5,
                                      "clock_divisor": 8,
                                      "slot0": "GT96100-FE"}

        # merge platform settings with the generic ones
        self.settings().update(self._etherswitch_settings)

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/multilayer_switch.svg"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.switches]

    def __str__(self):

        return "EtherSwitch router"
