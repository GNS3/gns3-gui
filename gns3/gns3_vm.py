# -*- coding: utf-8 -*-
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

from .settings import SERVERS_SETTINGS
from .local_config import LocalConfig

import logging
log = logging.getLogger(__name__)


class GNS3VM:
    """
    Represents the GNS3 VM.
    """

    def __init__(self):

        self._is_enabled = False
        self._settings = None
        self._loadSettings()

    def isEnabled(self):

        return self._is_enabled

    def _loadSettings(self):
        """
        Loads the server settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings("Servers", SERVERS_SETTINGS)

    def settings(self):
        """
        Returns the GNS3 VM settings.

        :returns: GNS3 VM settings (dict)
        """

        return self._settings["vm"]

    def setSettings(self, settings):
        """
        Set new GNS3 VM settings.

        :param settings: GNS3 VM settings (dict)
        """

        self._settings["vm"].update(settings)
        LocalConfig.instance().instance().saveSettings("Servers", settings)

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of GNS3VM

        :returns: instance of GNS3VM
        """

        if not hasattr(GNS3VM, "_instance") or GNS3VM._instance is None:
            GNS3VM._instance = GNS3VM()
        return GNS3VM._instance
