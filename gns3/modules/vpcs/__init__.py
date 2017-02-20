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
import copy
import shutil

from gns3.qt import QtWidgets
from gns3.local_config import LocalConfig
from gns3.local_server_config import LocalServerConfig
from gns3.utils.get_default_base_config import get_default_base_config
from gns3.utils.get_resource import get_resource

from ..module import Module
from ..module_error import ModuleError
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

        self._settings = {}
        self._nodes = []
        self._vpcs_nodes = {}
        self._working_dir = ""
        self._loadSettings()

    def configChangedSlot(self):
        # load the settings
        self._loadSettings()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        # Copy the default base config in the final location
        get_default_base_config(get_resource(os.path.join("configs", "vpcs_base_config.txt")))

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

        server_settings = copy.copy(self._settings)
        if server_settings["vpcs_path"]:
            # save some settings to the server config file
            server_settings["vpcs_path"] = os.path.normpath(server_settings["vpcs_path"])
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

    def createNode(self, node, node_name):
        """
        Creates a node.

        :param node: Node instance
        :param node_name: Node name
        """

        log.info("creating node {}".format(node))

        if node_name:
            for node_key, info in self._vpcs_nodes.items():
                if node_name == info["name"]:
                    vm_settings = {}
                    for setting_name, value in self._vpcs_nodes[node_key].items():

                        if setting_name in node.settings() and setting_name != "name" and value != "" and value is not None:
                            vm_settings[setting_name] = value

                    node.create(default_name_format=info["default_name_format"], additional_settings=vm_settings)
                    return

        vm_settings = {
            "base_script_file": self._settings.get("base_script_file", get_default_base_config(get_resource(os.path.join("configs", "vpcs_base_config.txt"))))
        }
        node.create(additional_settings=vm_settings)

    def reset(self):
        """
        Resets the module.
        """

        self._nodes.clear()

    def exportConfigs(self, directory):
        """
        Exports all configs for all nodes to a directory.

        :param directory: destination directory path
        """

        for node in self._nodes:
            if node.initialized():
                node.exportConfigToDirectory(directory)

    def importConfigs(self, directory):
        """
        Imports configs to all nodes from a directory.

        :param directory: source directory path
        """

        for node in self._nodes:
            if node.initialized():
                node.importConfigFromDirectory(directory)

    @staticmethod
    def getNodeClass(name):
        """
        Returns the object with the corresponding name.

        :param name: object name
        """

        if name in globals():
            return globals()[name]
        return None

    @staticmethod
    def getNodeType(name, platform=None):
        if name == "vpcs":
            return VPCSNode
        return None

    @staticmethod
    def vmConfigurationPage():
        from .pages.vpcs_node_configuration_page import VPCSNodeConfigurationPage
        return VPCSNodeConfigurationPage

    def VMs(self):
        """
        Returns list of VPCS nodes
        """

        return self._vpcs_nodes

    def setVMs(self, new_vpcs_nodes):
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

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        nodes = []

        # Add a default VPCS not linked to a specific server
        nodes.append(
            {
                "class": VPCSNode.__name__,
                "name": "VPCS",
                "categories": [VPCSNode.end_devices],
                "symbol": VPCSNode.defaultSymbol(),
                "builtin": True
            }
        )

        for node in self._vpcs_nodes.values():
            nodes.append(
                {"class": VPCSNode.__name__,
                 "name": node["name"],
                 "server": node["server"],
                 "symbol": node["symbol"],
                 "categories": [node["category"]]
                 }
            )
        return nodes

    @staticmethod
    def preferencePages():
        """
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
