#!/usr/bin/env python
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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

import copy
import uuid


class Appliance:
    """
    An instance of an appliance
    """

    def __init__(self, settings):

        if not settings.get("appliance_id"):
            settings["appliance_id"] = str(uuid.uuid4())
        self._settings = copy.deepcopy(settings)

        # The "node_type" setting has been replaced by "appliance_type" setting in version 2.2
        if "node_type" in self._settings:
            self._settings["appliance_type"] = self._settings.pop("node_type")

    def id(self):
        """
        Returns the appliance ID.

        :returns: appliance identifier
        """

        return self._settings["appliance_id"]

    def compute_id(self):
        """
        Returns the compute ID

        :returns: appliance compute identifier
        """

        return self._settings.get("compute_id")

    def name(self):
        """
        Returns the appliance name.

        :returns: appliance name
        """

        return self._settings["name"]

    def category(self):
        """
        Returns the appliance category.

        :returns: appliance category.
        """

        return self._settings["category"]

    def appliance_type(self):
        """
        Returns the node type

        :returns: node type
        """

        return self._settings["appliance_type"]

    def builtin(self):
        """
        Returns if this is a builtin

        :returns: boolean
        """

        return self._settings["builtin"]

    def symbol(self):
        """
        Returns the appliance symbol

        :returns: appliance symbol
        """

        return self._settings["symbol"]

    def settings(self):
        """
        Returns the appliance settings

        :returns: appliance settings
        """

        return self._settings

    def setSettings(self, settings):
        """
        Updates appliance settings.

        :param settings: appliance settings
        """

        self._settings = copy.deepcopy(settings)

    def __str__(self):

        return self.id

    def __json__(self):

        return self._settings

    def __eq__(self, v):

        if isinstance(v, Appliance):
            return self.__json__() == v.__json__()
        return False
