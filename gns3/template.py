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


class Template:
    """
    An instance of an template
    """

    def __init__(self, settings):

        if not settings.get("template_id"):
            settings["template_id"] = str(uuid.uuid4())
        self._settings = copy.deepcopy(settings)

        # The "appliance_id" setting has been replaced by "template_id" setting in version 2.2
        if "appliance_id" in self._settings:
            self._settings["template_id"] = self._settings.pop("appliance_id")

        # The "node_type" setting has been replaced by "template_type" setting in version 2.2
        if "node_type" in self._settings:
            self._settings["template_type"] = self._settings.pop("node_type")

        # The "server" setting has been replaced by "compute_id" setting in version 2.2
        if "server" in self._settings:
            self._settings["compute_id"] = self._settings.pop("server")

        for setting in self._settings.copy():
            # remove deprecated settings
            if setting in ["enable_remote_console", "use_ubridge", "acpi_shutdown", "default_symbol", "hover_symbol"]:
                del self._settings[setting]

    def id(self):
        """
        Returns the template ID.

        :returns: template identifier
        """

        return self._settings["template_id"]

    def compute_id(self):
        """
        Returns the compute ID

        :returns: template compute identifier
        """

        return self._settings.get("compute_id")

    def name(self):
        """
        Returns the template name.

        :returns: template name
        """

        return self._settings["name"]

    def category(self):
        """
        Returns the template category.

        :returns: template category.
        """

        return self._settings["category"]

    def template_type(self):
        """
        Returns the template type

        :returns: template type
        """

        return self._settings["template_type"]

    def builtin(self):
        """
        Returns if this is a builtin

        :returns: boolean
        """

        return self._settings["builtin"]

    def symbol(self):
        """
        Returns the template symbol

        :returns: template symbol
        """

        return self._settings["symbol"]

    def settings(self):
        """
        Returns the template settings

        :returns: template settings
        """

        return self._settings

    def setSettings(self, settings):
        """
        Updates template settings.

        :param settings: template settings
        """

        self._settings = copy.deepcopy(settings)

    def __str__(self):

        return self.id

    def __json__(self):

        return self._settings

    def __eq__(self, v):

        if isinstance(v, Template):
            return self.__json__() == v.__json__()
        return False
