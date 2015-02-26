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

import sys
import os
import pkg_resources
from .router import Router
from gns3.node import Node


class EtherSwitchRouter(Router):

    """
    EtherSwitch router.

    :param module: parent module for this node
    :param server: GNS3 server instance
    """

    def __init__(self, module, server):
        Router.__init__(self, module, server, platform="c3725")

        self._platform_settings = {"ram": 128,
                                   "nvram": 304,
                                   "disk0": 16,
                                   "disk1": 0,
                                   "iomem": 5,
                                   "clock_divisor": 8,
                                   "slot0": "GT96100-FE"}

        # merge platform settings with the generic ones
        self._settings.update(self._platform_settings)

        # save the default settings
        self._defaults = self._settings.copy()

    def setup(self, image, ram, name=None, router_id=None, initial_settings={}):
        """
        Setups this router.

        :param image: IOS image path
        :param ram: amount of RAM
        :param name: optional name for this router
        :param initial_settings: other additional and not mandatory settings
        """
        # let's create a unique name if none has been chosen
        if not name:
            name = self.allocateName("ESW")

        self._settings["name"] = name
        resource_name = "configs/ios_etherswitch_startup-config.txt"
        if hasattr(sys, "frozen") and os.path.isfile(resource_name):
            startup_config = os.path.normpath(resource_name)
        elif pkg_resources.resource_exists("gns3", resource_name):
            ios_etherswitch_config_path = pkg_resources.resource_filename("gns3", resource_name)
            startup_config = os.path.normpath(ios_etherswitch_config_path)

        initial_settings.update({"slot1": "NM-16ESW",  # add the EtherSwitch module
                                 "startup_config": startup_config})  # add the EtherSwitch startup-config
        Router.setup(self, image, ram, name, router_id, initial_settings)

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/multilayer_switch.normal.svg"

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when this node is hovered.

        :returns: symbol path (or resource).
        """

        return ":/symbols/multilayer_switch.selected.svg"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.switches]

    def __str__(self):

        return "EtherSwitch router"

    @staticmethod
    def symbolName():

        return "EtherSwitch router"
