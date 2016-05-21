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


from gns3.servers import Servers
from gns3.local_config import LocalConfig
from gns3.utils.get_resource import get_resource
from gns3.utils.get_default_base_config import get_default_base_config
from gns3.local_server_config import LocalServerConfig
from gns3.gns3_vm import GNS3VM

from ..module import Module
from .vpcs_device import VPCSDevice
from .settings import VPCS_SETTINGS

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
        self._working_dir = ""

        self._vpcs_multi_host_process = None
        self._vpcs_multi_host_port = 0

        self._loadSettings()

    def configChangedSlot(self):
        # load the settings
        self._loadSettings()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings(self.__class__.__name__, VPCS_SETTINGS)

        if not self._settings["base_script_file"]:
            self._settings["base_script_file"] = get_default_base_config(get_resource(os.path.join("configs", "vpcs_base_config.txt")))

        if not os.path.exists(self._settings["vpcs_path"]):
            vpcs_path = shutil.which("vpcs")
            if vpcs_path:
                self._settings["vpcs_path"] = os.path.abspath(vpcs_path)
            else:
                self._settings["vpcs_path"] = ""

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

        if self._settings["vpcs_path"]:
            # save some settings to the server config file
            server_settings = {
                "vpcs_path": os.path.normpath(self._settings["vpcs_path"]),
            }
            config = LocalServerConfig.instance()
            config.saveSettings(self.__class__.__name__, server_settings)

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

    def createNode(self, node_class, server, project):
        """
        Creates a new node.

        :param node_class: Node object
        :param server: HTTPClient instance
        :param project: Project instance
        """

        log.info("Creating node {}".format(node_class))

        # create an instance of the node class
        return node_class(self, server, project)

    def setupNode(self, node, node_name):
        """
        Setups a node.

        :param node: Node instance
        :param node_name: Node name
        """

        log.info("configuring node {}".format(node))
        vm_settings = {}

        script_file = self._settings["base_script_file"]
        if script_file:
            vm_settings["script_file"] = script_file

        default_name_format = VPCS_SETTINGS["default_name_format"]
        if self._settings["default_name_format"]:
            default_name_format = self._settings["default_name_format"]

        node.setup(additional_settings=vm_settings, default_name_format=default_name_format)

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
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [VPCSDevice]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        if self._settings["use_local_server"]:
            server = "local"
        elif GNS3VM.instance().isRunning():
            server = "vm"
        else:
            remote_server = next(iter(Servers.instance()))
            if remote_server:
                server = remote_server.url()
            else:
                # If user has no server configured and has uncheck the checkbox
                # it's a mistake. We use the GNS3VM in order to show a correct
                # error message
                server = "vm"

        nodes = []
        for node_class in VPCS.classes():
            nodes.append(
                {"class": node_class.__name__,
                 "name": node_class.symbolName(),
                 "server": server,
                 "categories": [self._settings["category"]],
                 "symbol": self._settings["symbol"]}
            )
        return nodes

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        from .pages.vpcs_preferences_page import VPCSPreferencesPage
        return [VPCSPreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of VPCS module.

        :returns: instance of VPCS
        """

        if not hasattr(VPCS, "_instance"):
            VPCS._instance = VPCS()
        return VPCS._instance
