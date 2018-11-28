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
IOU module implementation.
"""

from gns3.local_config import LocalConfig
from gns3.controller import Controller
from gns3.template_manager import TemplateManager
from gns3.template import Template

from ..module import Module
from .iou_device import IOUDevice
from .settings import IOU_SETTINGS, IOU_DEVICE_SETTINGS

import logging
log = logging.getLogger(__name__)


class IOU(Module):
    """
    IOU module.
    """

    def __init__(self):
        super().__init__()
        self._loadSettings()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings(self.__class__.__name__, IOU_SETTINGS)

        # migrate devices settings to the controller (templates are managed on server side starting with version 2.0)
        Controller.instance().connected_signal.connect(self._migrateOldDevices)

    def _migrateOldDevices(self):
        """
        Migrate local device settings to the controller.
        """

        if self._settings.get("devices"):
            templates = []
            for device in self._settings.get("devices"):
                device_settings = IOU_DEVICE_SETTINGS.copy()
                device_settings.update(device)
                templates.append(Template(device_settings))
            TemplateManager.instance().updateList(templates)
            self._settings["devices"] = []
            self._saveSettings()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

    @staticmethod
    def configurationPage():
        """
        Returns the configuration page for this module.

        :returns: QWidget object
        """

        from .pages.iou_device_configuration_page import iouDeviceConfigurationPage
        return iouDeviceConfigurationPage

    @staticmethod
    def getNodeClass(node_type, platform=None):
        """
        Returns the class corresponding to node type.

        :param node_type: node type (string)
        :param platform: not used

        :returns: class or None
        """

        if node_type == "iou":
            return IOUDevice
        return None

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [IOUDevice]

    @staticmethod
    def preferencePages():
        """
        Returns the preference pages for this module.

        :returns: QWidget object list
        """

        from .pages.iou_preferences_page import IOUPreferencesPage
        from .pages.iou_device_preferences_page import IOUDevicePreferencesPage
        return [IOUPreferencesPage, IOUDevicePreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of IOU module.

        :returns: instance of IOU
        """

        if not hasattr(IOU, "_instance"):
            IOU._instance = IOU()
        return IOU._instance

    def __str__(self):
        """
        Returns the module name.
        """

        return "iou"
