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

from gns3.qt import QtWidgets
from gns3.local_config import LocalConfig

from ..module import Module
from .iou_device import IOUDevice
from .settings import IOU_SETTINGS
from .settings import IOU_DEVICE_SETTINGS

import logging
log = logging.getLogger(__name__)


class IOU(Module):
    """
    IOU module.
    """

    def __init__(self):
        super().__init__()
        self._iou_devices = {}
        self._iou_images_cache = {}
        self._loadSettings()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings(self.__class__.__name__, IOU_SETTINGS)
        self._loadIOUDevices()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

    def _loadIOUDevices(self):
        """
        Load the IOU devices from the persistent settings file.
        """

        self._iou_devices = {}
        settings = LocalConfig.instance().settings()
        if "devices" in settings.get(self.__class__.__name__, {}):
            for device in settings[self.__class__.__name__]["devices"]:
                name = device.get("name")
                server = device.get("server")
                key = "{server}:{name}".format(server=server, name=name)
                if key in self._iou_devices or not name or not server:
                    continue
                device_settings = IOU_DEVICE_SETTINGS.copy()
                device_settings.update(device)
                # for backward compatibility before version 1.4
                if "symbol" not in device_settings:
                    device_settings["symbol"] = device_settings["default_symbol"]
                    device_settings["symbol"] = device_settings["symbol"][:-11] + ".svg" if device_settings["symbol"].endswith("normal.svg") else device_settings["symbol"]
                device_settings["startup_config"] = device_settings.get("initial_config", device_settings["startup_config"])
                self._iou_devices[key] = device_settings

    def _saveIOUDevices(self):
        """
        Saves the IOU devices to the persistent settings file.
        """

        self._settings["devices"] = list(self._iou_devices.values())
        self._saveSettings()

    def nodeTemplates(self):
        """
        Returns IOU devices settings.

        :returns: IOU devices settings (dictionary)
        """

        return self._iou_devices

    def setNodeTemplates(self, new_iou_devices):
        """
        Sets IOS devices settings.

        :param new_iou_devices: IOU images settings (dictionary)
        """

        self._iou_devices = new_iou_devices.copy()
        self._saveIOUDevices()

    @staticmethod
    def configurationPage():
        """
        Returns the configuration page for this module.

        :returns: QWidget object
        """

        from .pages.iou_device_configuration_page import iouDeviceConfigurationPage
        return iouDeviceConfigurationPage

    def findAlternativeIOUImage(self, image):
        """
        Tries to find an alternative IOU image

        :param image: path to IOU

        :return: IOU image path
        """

        if image in self._iou_images_cache:
            return self._iou_images_cache[image]

        from gns3.main_window import MainWindow
        mainwindow = MainWindow.instance()
        iou_devices = self.nodeTemplates()
        candidate_iou_images = {}

        alternative_image = image

        # find all images with the same platform and local server
        for iou_device in iou_devices.values():
            if iou_device["server"] == "local":
                candidate_iou_images[iou_device["image"]] = iou_device["path"]

        if candidate_iou_images:
            selection, ok = QtWidgets.QInputDialog.getItem(mainwindow,
                                                           "IOU image", "IOU image {} could not be found\nPlease select an alternative from your existing images:".format(image),
                                                           list(candidate_iou_images.keys()), 0, False)
            if ok:
                iou_image = candidate_iou_images[selection]
                self._iou_images_cache[image] = iou_image
                return iou_image

        # no registered IOU image is used, let's just ask for an IOU image path
        QtWidgets.QMessageBox.critical(mainwindow, "IOU image", "Could not find the {} IOU image \nPlease select a similar IOU image!".format(image))
        from .pages.iou_device_preferences_page import IOUDevicePreferencesPage
        path = IOUDevicePreferencesPage.getIOUImage(mainwindow, None)
        if path:
            alternative_image = path
            self._iou_images_cache[image] = alternative_image
        return alternative_image

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
