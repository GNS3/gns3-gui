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
VPCS module implementation.
"""

import os
import shutil

from gns3.local_config import LocalConfig
from gns3.local_server_config import LocalServerConfig

from ..module import Module
from .vpcs_node import VPCSNode
from .settings import VPCS_SETTINGS
from .settings import VPCS_NODES_SETTINGS

import logging
log = logging.getLogger(__name__)


class VPCS(Module):
    """
    VPCS module.
    """

    def __init__(self):
        super().__init__()
        self._vpcs_nodes = {}
        self._working_dir = ""
        self._loadSettings()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings(self.__class__.__name__, VPCS_SETTINGS)
        if not os.path.exists(self._settings["vpcs_path"]):
            vpcs_path = shutil.which("vpcs")
            if vpcs_path:
                self._settings["vpcs_path"] = os.path.abspath(vpcs_path)
            else:
                self._settings["vpcs_path"] = ""

        self._loadVPCSNodes()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

        server_settings = {}
        if self._settings["vpcs_path"]:
            # save some settings to the server config file
            server_settings["vpcs_path"] = os.path.normpath(self._settings["vpcs_path"])
        config = LocalServerConfig.instance()
        config.saveSettings(self.__class__.__name__, server_settings)

    def _loadVPCSNodes(self):
        """
        Load the VPCS nodes from the persistent settings file.
        """

        self._vpcs_nodes = {}
        settings = LocalConfig.instance().settings()
        if "nodes" in settings.get(self.__class__.__name__, {}):
            for node in settings[self.__class__.__name__]["nodes"]:
                name = node.get("name")
                server = node.get("server")
                key = "{server}:{name}".format(server=server, name=name)
                if key in self._vpcs_nodes or not name or not server:
                    continue
                node_settings = VPCS_NODES_SETTINGS.copy()
                node_settings.update(node)
                self._vpcs_nodes[key] = node_settings

    def _saveVPCSNodes(self):
        """
        Saves the VPCS nodes to the persistent settings file.
        """

        self._settings["nodes"] = list(self._vpcs_nodes.values())
        self._saveSettings()

    @staticmethod
    def getNodeClass(node_type, platform=None):
        """
        Returns the class corresponding to node type.

        :param node_type: name of the node
        :param platform: not used

        :returns: class or None
        """

        if node_type == "vpcs":
            return VPCSNode
        return None

    @staticmethod
    def configurationPage():
        """
        Returns the configuration page for this module.

        :returns: QWidget object
        """

        from .pages.vpcs_node_configuration_page import VPCSNodeConfigurationPage
        return VPCSNodeConfigurationPage

    def nodeTemplates(self):
        """
        Returns list of VPCS nodes
        """

        return self._vpcs_nodes

    def setNodeTemplates(self, new_vpcs_nodes):
        """
        Sets VPCS list

        :param new_vpcs_vms: VPCS node list
        """

        self._vpcs_nodes = new_vpcs_nodes.copy()
        self._saveVPCSNodes()

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [VPCSNode]

    @staticmethod
    def preferencePages():
        """
        Returns the preference pages for this module.

        :returns: QWidget object list
        """

        from .pages.vpcs_preferences_page import VPCSPreferencesPage
        from .pages.vpcs_node_preferences_page import VPCSNodePreferencesPage
        return [VPCSPreferencesPage, VPCSNodePreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of VPCS module.

        :returns: instance of VPCS
        """

        if not hasattr(VPCS, "_instance"):
            VPCS._instance = VPCS()
        return VPCS._instance
