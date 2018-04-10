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
Base class (interface) for modules.
"""

from ..qt import QtCore
from ..local_config import LocalConfig

import logging
log = logging.getLogger(__name__)


class Module(QtCore.QObject):
    """
    Module interface.
    """

    notification_signal = QtCore.Signal(str, str)

    def __init__(self):

        super().__init__()
        self._settings = {}
        self._nodes = []
        LocalConfig.instance().config_changed_signal.connect(self._configChangedSlot)

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

        # create an instance of the node class
        return node_class(self, server, project)

    def _configChangedSlot(self):
        """
        Called when the configuration file has changed.
        """

        self._loadSettings()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        Must be overloaded.
        """

        raise NotImplementedError()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        Must be overloaded.
        """

        raise NotImplementedError()

    @staticmethod
    def getNodeClass(node_type, platform=None):
        """
        Returns the class corresponding to node type.
        Must be overloaded.

        :param node_type: name of the node
        :param platform: platform (for Dynamips only)

        :returns: class or None
        """

        raise NotImplementedError()

    @staticmethod
    def preferencePages():
        """
        Returns all the preference pages used by this module.
        Must be overloaded.

        :returns: list of preference page classes
        """

        raise NotImplementedError()

    def exportConfigs(self, directory):
        """
        Exports all configs for all nodes to a directory.

        :param directory: destination directory path
        """

        for node in self._nodes:
            if hasattr(node, "initialized") and node.initialized():
                node.exportConfigsToDirectory(directory)

    def importConfigs(self, directory):
        """
        Imports configs to all nodes from a directory.

        :param directory: source directory path
        """

        for node in self._nodes:
            if hasattr(node, "initialized") and node.initialized():
                node.importConfigsFromDirectory(directory)
