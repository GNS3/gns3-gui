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

from gns3.local_config import LocalConfig

from ..module import Module
from .cloud import Cloud
from .nat import Nat
from .ethernet_hub import EthernetHub
from .ethernet_switch import EthernetSwitch
from .frame_relay_switch import FrameRelaySwitch
from .atm_switch import ATMSwitch
from .settings import BUILTIN_SETTINGS

import logging
log = logging.getLogger(__name__)


class Builtin(Module):

    """
    Built-in module.
    """

    def __init__(self):
        super().__init__()
        self._loadSettings()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

        # FIXME: handle server side config
        # server_settings = {}
        # config = LocalServerConfig.instance()
        # if self._settings["default_nat_interface"]:
        #     # save some settings to the local server config file
        #     server_settings["default_nat_interface"] = self._settings["default_nat_interface"]
        #     config.saveSettings(self.__class__.__name__, server_settings)
        # else:
        #     config.deleteSetting(self.__class__.__name__, "default_nat_interface")

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        local_config = LocalConfig.instance()
        self._settings = local_config.loadSectionSettings(self.__class__.__name__, BUILTIN_SETTINGS)

    @staticmethod
    def configurationPage(node_type):
        """
        Returns the configuration page for this module.

        :returns: QWidget object
        """

        from .pages.ethernet_hub_configuration_page import EthernetHubConfigurationPage
        from .pages.ethernet_switch_configuration_page import EthernetSwitchConfigurationPage
        from .pages.cloud_configuration_page import CloudConfigurationPage
        if node_type == "ethernet_hub":
            return EthernetHubConfigurationPage
        elif node_type == "ethernet_switch":
            return EthernetSwitchConfigurationPage
        elif node_type == "cloud":
            return CloudConfigurationPage
        return None

    @staticmethod
    def getNodeClass(node_type, platform=None):
        """
        Returns the class corresponding to node type.

        :param node_type: node type (string)
        :param platform: not used

        :returns: class or None
        """

        if node_type == "cloud":
            return Cloud
        elif node_type == "nat":
            return Nat
        elif node_type == "ethernet_hub":
            return EthernetHub
        elif node_type == "ethernet_switch":
            return EthernetSwitch
        elif node_type == "frame_relay_switch":
            return FrameRelaySwitch
        elif node_type == "atm_switch":
            return ATMSwitch
        return None

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [Nat, Cloud, EthernetHub, EthernetSwitch, FrameRelaySwitch, ATMSwitch]

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

    def __str__(self):
        """
        Returns the module name.
        """

        return "builtin"
