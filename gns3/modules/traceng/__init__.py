# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 GNS3 Technologies Inc.
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
TraceNG module implementation.
"""

import os
import shutil

from gns3.local_config import LocalConfig
from gns3.local_server_config import LocalServerConfig

from ..module import Module
from .traceng_node import TraceNGNode
from .settings import TRACENG_SETTINGS

import logging
log = logging.getLogger(__name__)


class TraceNG(Module):
    """
    TraceNG module.
    """

    def __init__(self):
        super().__init__()
        self._working_dir = ""
        self._loadSettings()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings(self.__class__.__name__, TRACENG_SETTINGS)
        if not os.path.exists(self._settings["traceng_path"]):
            traceng_path = shutil.which("traceng")
            if traceng_path:
                self._settings["traceng_path"] = os.path.abspath(traceng_path)
            else:
                self._settings["traceng_path"] = ""

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

        server_settings = {}
        if self._settings["traceng_path"]:
            # save some settings to the server config file
            server_settings["traceng_path"] = os.path.normpath(self._settings["traceng_path"])

        config = LocalServerConfig.instance()
        config.saveSettings(self.__class__.__name__, server_settings)

    @staticmethod
    def getNodeClass(node_type, platform=None):
        """
        Returns the class corresponding to node type.

        :param node_type: node type (string)
        :param platform: not used

        :returns: class or None
        """

        if node_type == "traceng":
            return TraceNGNode
        return None

    @staticmethod
    def configurationPage():
        """
        Returns the configuration page for this module.

        :returns: QWidget object
        """

        from .pages.traceng_node_configuration_page import TraceNGNodeConfigurationPage
        return TraceNGNodeConfigurationPage

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [TraceNGNode]

    @staticmethod
    def preferencePages():
        """
        Returns the preference pages for this module.

        :returns: QWidget object list
        """

        from .pages.traceng_preferences_page import TraceNGPreferencesPage
        from .pages.traceng_node_preferences_page import TraceNGNodePreferencesPage
        return [TraceNGPreferencesPage, TraceNGNodePreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of TraceNG module.

        :returns: instance of TraceNG
        """

        if not hasattr(TraceNG, "_instance"):
            TraceNG._instance = TraceNG()
        return TraceNG._instance

    def __str__(self):
        """
        Returns the module name.
        """

        return "traceng"
