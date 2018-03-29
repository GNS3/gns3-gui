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
import copy
import shutil

from gns3.local_config import LocalConfig
from gns3.local_server_config import LocalServerConfig

from ..module import Module
from .traceng_node import TraceNGNode
from .settings import TRACENG_SETTINGS
from .settings import TRACENG_NODES_SETTINGS

import logging
log = logging.getLogger(__name__)


class TraceNG(Module):

    """
    TraceNG module.
    """

    def __init__(self):
        super().__init__()

        self._settings = {}
        self._nodes = []
        self._traceng_nodes = {}
        self._working_dir = ""
        self._loadSettings()

    def configChangedSlot(self):
        # load the settings
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

        self._loadTraceNGNodes()

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

    def _loadTraceNGNodes(self):
        """
        Load the TraceNG nodes from the persistent settings file.
        """

        self._traceng_nodes = {}
        settings = LocalConfig.instance().settings()
        if "nodes" in settings.get(self.__class__.__name__, {}):
            for node in settings[self.__class__.__name__]["nodes"]:
                name = node.get("name")
                server = node.get("server")
                key = "{server}:{name}".format(server=server, name=name)
                if key in self._traceng_nodes or not name or not server:
                    continue
                node_settings = TRACENG_NODES_SETTINGS.copy()
                node_settings.update(node)
                self._traceng_nodes[key] = node_settings

    def _saveTraceNGNodes(self):
        """
        Saves the TraceNG nodes to the persistent settings file.
        """

        self._settings["nodes"] = list(self._traceng_nodes.values())
        self._saveSettings()

    def addNode(self, node):
        """
        Adds a node to this module.

        :param node: Node instance
        """

        self._nodes.append(node)

    def removeNode(self, node):
        """
        Removes a node from this module.

        :param node: Node instance
        """

        if node in self._nodes:
            self._nodes.remove(node)

    def settings(self):
        """
        Returns the module settings

        :returns: module settings (dictionary)
        """

        return self._settings

    def setSettings(self, settings):
        """
        Sets the module settings

        :param settings: module settings (dictionary)
        """

        self._settings.update(settings)
        self._saveSettings()

    def instantiateNode(self, node_class, server, project):
        """
        Instantiate a new node.

        :param node_class: Node object
        :param server: HTTPClient instance
        :param project: Project instance
        """

        # create an instance of the node class
        return node_class(self, server, project)

    def reset(self):
        """
        Resets the module.
        """

        self._nodes.clear()

    @staticmethod
    def getNodeType(name, platform=None):
        if name == "traceng":
            return TraceNGNode
        return None

    @staticmethod
    def vmConfigurationPage():
        from .pages.traceng_node_configuration_page import TraceNGNodeConfigurationPage
        return TraceNGNodeConfigurationPage

    def VMs(self):
        """
        Returns list of TraceNG nodes
        """

        return self._traceng_nodes

    def setVMs(self, new_traceng_nodes):
        """
        Sets TraceNG list

        :param new_traceng_vms: TraceNG node list
        """

        self._traceng_nodes = new_traceng_nodes.copy()
        self._saveTraceNGNodes()

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [TraceNGNode]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        nodes = []

        # Add a default TraceNG not linked to a specific server
        nodes.append(
            {
                "class": TraceNGNode.__name__,
                "name": "TraceNG",
                "categories": [TraceNGNode.end_devices],
                "symbol": TraceNGNode.defaultSymbol(),
                "builtin": True
            }
        )
        return nodes

    @staticmethod
    def preferencePages():
        """
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
