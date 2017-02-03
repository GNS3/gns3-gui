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
Built-in module implementation.
"""

from gns3.qt import QtWidgets
from gns3.local_config import LocalConfig

from ..module import Module
from .cloud import Cloud
from .nat import Nat
from .ethernet_hub import EthernetHub
from .ethernet_switch import EthernetSwitch
from .frame_relay_switch import FrameRelaySwitch
from .atm_switch import ATMSwitch

from .settings import (
    BUILTIN_SETTINGS,
    CLOUD_SETTINGS,
    NAT_SETTINGS,
    ETHERNET_HUB_SETTINGS,
    ETHERNET_SWITCH_SETTINGS
)

import logging
log = logging.getLogger(__name__)


class Builtin(Module):

    """
    Built-in module.
    """

    def __init__(self):
        super().__init__()

        self._settings = {}
        self._nodes = []
        self._cloud_nodes = {}
        self._nat_nodes = {}
        self._ethernet_hubs = {}
        self._ethernet_switches = {}

        # load the settings
        self._loadSettings()

    def configChangedSlot(self):

        pass

    def settings(self):
        """
        Returns the module settings

        :returns: module settings (dictionary)
        """

        return self._settings

    def setSettings(self, settings):
        """Sets the module settings

        :param settings: module settings (dictionary)
        """

        self._settings.update(settings)
        self._saveSettings()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        local_config = LocalConfig.instance()
        self._settings = local_config.loadSectionSettings(self.__class__.__name__, BUILTIN_SETTINGS)
        self._loadNodes()

    def _loadBuilinNodesPerType(self, node_dict, node_type, default_settings):

        settings = LocalConfig.instance().settings()
        if node_type in settings.get(self.__class__.__name__, {}):
            for device in settings[self.__class__.__name__][node_type]:
                name = device.get("name")
                server = device.get("server")
                key = "{server}:{name}".format(server=server, name=name)
                if key in node_dict or not name or not server:
                    continue
                node_settings = default_settings.copy()
                node_settings.update(device)
                node_dict[key] = node_settings

    def _loadNodes(self):
        """
        Load the built-in nodes from the persistent settings file.
        """

        self._loadBuilinNodesPerType(self._cloud_nodes, "cloud_nodes", CLOUD_SETTINGS)
        self._loadBuilinNodesPerType(self._ethernet_hubs, "ethernet_hubs", ETHERNET_HUB_SETTINGS)
        self._loadBuilinNodesPerType(self._ethernet_switches, "ethernet_switches", ETHERNET_SWITCH_SETTINGS)

    def _saveNodes(self):
        """
        Saves the built-in nodes to the persistent settings file.
        """

        self._settings["cloud_nodes"] = list(self._cloud_nodes.values())
        self._settings["ethernet_hubs"] = list(self._ethernet_hubs.values())
        self._settings["ethernet_switches"] = list(self._ethernet_switches.values())
        self._saveSettings()

    def cloudNodes(self):
        """
        Returns cloud nodes settings.

        :returns: Cloud nodes settings (dictionary)
        """

        return self._cloud_nodes

    def setCloudNodes(self, new_cloud_nodes):
        """
        Sets cloud nodes settings.

        :param new_cloud_nodes: cloud nodes settings (dictionary)
        """

        self._cloud_nodes = new_cloud_nodes.copy()
        self._saveNodes()

    def ethernetHubs(self):
        """
        Returns Ethernet hubs settings.

        :returns: Ethernet hubs settings (dictionary)
        """

        return self._ethernet_hubs

    def setEthernetHubs(self, new_ethernet_hubs):
        """
        Sets Ethernet hubs settings.

        :param new_ethernet_hubs: Ethernet hubs settings (dictionary)
        """

        self._ethernet_hubs = new_ethernet_hubs.copy()
        self._saveNodes()

    def ethernetSwitches(self):
        """
        Returns Ethernet switches settings.

        :returns: Ethernet switches settings (dictionary)
        """

        return self._ethernet_switches

    def setEthernetSwitches(self, new_ethernet_switches):
        """
        Sets Ethernet switches settings.

        :param new_ethernet_switches: Ethernet switches settings (dictionary)
        """

        self._ethernet_switches = new_ethernet_switches.copy()
        self._saveNodes()

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

    def reset(self):
        """
        Resets the module.
        """

        self._nodes.clear()

    def instantiateNode(self, node_class, server, project):
        """
        Instantiate a new node.

        :param node_class: Node object
        :param server: HTTPClient instance
        :param project: Project instance
        """

        log.info("instantiating node {}".format(node_class))
        # create an instance of the node class
        return node_class(self, server, project)

    def createNode(self, node, node_name):
        """
        Creates a node.

        :param node: Node instance
        :param node_name: Node name
        """

        log.info("creating node {}".format(node))
        if isinstance(node, Cloud):
            for key, info in self._cloud_nodes.items():
                if node_name == info["name"]:
                    default_name_format = info["default_name_format"].replace('{name}', node_name)
                    node.create(ports=info["ports_mapping"], default_name_format=default_name_format)
                    return
        elif isinstance(node, Nat):
            for key, info in self._nat_nodes.items():
                if node_name == info["name"]:
                    default_name_format = info["default_name_format"].replace('{name}', node_name)
                    node.create(default_name_format=default_name_format)
                    return
        elif isinstance(node, EthernetHub):
            for key, info in self._ethernet_hubs.items():
                if node_name == info["name"]:
                    default_name_format = info["default_name_format"].replace('{name}', node_name)
                    node.create(ports=info["ports_mapping"], default_name_format=default_name_format)
                    return
        elif isinstance(node, EthernetSwitch):
            for key, info in self._ethernet_switches.items():
                if node_name == info["name"]:
                    default_name_format = info["default_name_format"].replace('{name}', node_name)
                    node.create(ports=info["ports_mapping"], default_name_format=default_name_format)
                    return
        node.create()

    @staticmethod
    def findAlternativeInterface(node, missing_interface):

        from gns3.main_window import MainWindow
        mainwindow = MainWindow.instance()

        available_interfaces = []
        for interface in node.settings()["interfaces"]:
            available_interfaces.append(interface["name"])

        if available_interfaces:
            selection, ok = QtWidgets.QInputDialog.getItem(mainwindow,
                                                           "Cloud interfaces", "Interface {} could not be found\nPlease select an alternative from your existing interfaces:".format(missing_interface),
                                                           available_interfaces, 0, False)
            if ok:
                return selection
            QtWidgets.QMessageBox.warning(mainwindow, "Cloud interface", "No alternative interface chosen to replace {} on this host, this may lead to issues".format(missing_interface))
            return None
        else:
            QtWidgets.QMessageBox.critical(mainwindow, "Cloud interface", "Could not find interface {} on this host".format(missing_interface))
            return missing_interface

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
        if name == "cloud":
            return Cloud
        elif name == "nat":
            return Nat
        elif name == "ethernet_hub":
            return EthernetHub
        elif name == "ethernet_switch":
            return EthernetSwitch
        elif name == "frame_relay_switch":
            return FrameRelaySwitch
        elif name == "atm_switch":
            return ATMSwitch
        return None

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [Nat, Cloud, EthernetHub, EthernetSwitch, FrameRelaySwitch, ATMSwitch]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        nodes = []
        for node_class in Builtin.classes():
            nodes.append(
                {"class": node_class.__name__,
                 "name": node_class.symbolName(),
                 "categories": node_class.categories(),
                 "symbol": node_class.defaultSymbol(),
                 "builtin": True,
                 "node_type": node_class.URL_PREFIX
                 }
            )

        # add custom cloud node templates
        for cloud_node in self._cloud_nodes.values():
            nodes.append(
                {"class": Cloud.__name__,
                 "name": cloud_node["name"],
                 "server": cloud_node["server"],
                 "symbol": cloud_node["symbol"],
                 "categories": [cloud_node["category"]]
                 }
            )

        # add custom Ethernet hub templates
        for hub in self._ethernet_hubs.values():
            nodes.append(
                {"class": EthernetHub.__name__,
                 "name": hub["name"],
                 "server": hub["server"],
                 "symbol": hub["symbol"],
                 "categories": [hub["category"]]
                 }
            )

        # add custom Ethernet switch templates
        for switch in self._ethernet_switches.values():
            nodes.append(
                {"class": EthernetSwitch.__name__,
                 "name": switch["name"],
                 "server": switch["server"],
                 "symbol": switch["symbol"],
                 "categories": [switch["category"]]
                 }
            )

        return nodes

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        from .pages.builtin_preferences_page import BuiltinPreferencesPage
        from .pages.cloud_preferences_page import CloudPreferencesPage
        from .pages.ethernet_hub_preferences_page import EthernetHubPreferencesPage
        from .pages.ethernet_switch_preferences_page import EthernetSwitchPreferencesPage

        return [BuiltinPreferencesPage, EthernetHubPreferencesPage, EthernetSwitchPreferencesPage, CloudPreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of built-in module.

        :returns: instance of Builtin
        """

        if not hasattr(Builtin, "_instance"):
            Builtin._instance = Builtin()
        return Builtin._instance
