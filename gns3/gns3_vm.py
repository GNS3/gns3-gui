# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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
Manages the GNS3 VM.
"""

from .settings import GNS3_VM_SETTINGS
from .local_config import LocalConfig

import logging
log = logging.getLogger(__name__)


class GNS3VM:

    """
    GNS3 VM management class.
    """

    def __init__(self):

        self._settings = {}
        self._loadSettings()

    def _loadSettings(self):
        """
        Loads the server settings from the persistent settings file.
        """

        local_config = LocalConfig.instance()
        self._settings = local_config.loadSectionSettings("GNS3VM", GNS3_VM_SETTINGS)

        # keep the config file sync
        self._saveSettings()

    def _saveSettings(self):
        """
        Saves the server settings to a persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings("GNS3VM", self._settings)

    def settings(self):
        """
        Returns the GNS3 VM settings.

        :returns: GNS3 VM settings (dict)
        """

        return self._settings

    def setSettings(self, settings):
        """
        Set new GNS3 VM settings.

        :param settings: GNS3 VM settings (dict)
        """

        self._settings.update(settings)
        self._saveSettings()

    def autoStart(self):
        """
        Automatically start the GNS3 VM at startup.

        :returns: boolean
        """

        return self._settings["auto_start"]

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of GNS3VM

        :returns: instance of GNS3VM
        """

        if not hasattr(GNS3VM, "_instance") or GNS3VM._instance is None:
            GNS3VM._instance = GNS3VM()
        return GNS3VM._instance
