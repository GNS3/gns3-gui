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

import sys
import os
import shutil

from gns3.qt import QtCore, QtGui
from gns3.local_server_config import LocalServerConfig
from gns3.local_config import LocalConfig

from ..module import Module
from ..module_error import ModuleError
from .iou_device import IOUDevice
from .settings import IOU_SETTINGS, IOU_SETTING_TYPES
from .settings import IOU_DEVICE_SETTINGS, IOU_DEVICE_SETTING_TYPES

import logging
log = logging.getLogger(__name__)


class IOU(Module):

    """
    IOU module.
    """

    def __init__(self):
        Module.__init__(self)

        self._settings = {}
        self._nodes = []
        self._iou_devices = {}
        self._iou_images_cache = {}

        # load the settings
        self._loadSettings()
        self._loadIOUDevices()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        local_config = LocalConfig.instance()

        # restore the IOU settings from QSettings (for backward compatibility)
        legacy_settings = {}
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name in IOU_SETTINGS.keys():
            if settings.contains(name):
                legacy_settings[name] = settings.value(name, type=IOU_SETTING_TYPES[name])
        if "iourc" in legacy_settings:
            legacy_settings["iourc_path"] = legacy_settings["iourc"]
            del legacy_settings["iourc"]
        settings.remove("")
        settings.endGroup()

        if legacy_settings:
            local_config.saveSectionSettings(self.__class__.__name__, legacy_settings)
        self._settings = local_config.loadSectionSettings(self.__class__.__name__, IOU_SETTINGS)

        if sys.platform.startswith("linux") and not os.path.exists(self._settings["iouyap_path"]):
            iouyap_path = shutil.which("iouyap")
            if iouyap_path:
                self._settings["iouyap_path"] = iouyap_path

        # keep the config file sync
        self._saveSettings()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

        # save some settings to the local server config file
        server_settings = {
            "iourc_path": self._settings["iourc_path"],
            "iouyap_path": self._settings["iouyap_path"],
            "license_check": self._settings["license_check"]
        }
        config = LocalServerConfig.instance()
        config.saveSettings(self.__class__.__name__, server_settings)

    def _loadIOUDevices(self):
        """
        Load the IOU devices from the persistent settings file.
        """

        local_config = LocalConfig.instance()

        # restore the VirtualBox settings from QSettings (for backward compatibility)
        iou_devices = []
        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup("IOUDevices")
        # load the IOU devices
        size = settings.beginReadArray("iou_device")
        for index in range(0, size):
            settings.setArrayIndex(index)
            device = {}
            for setting_name, default_value in IOU_DEVICE_SETTINGS.items():
                device[setting_name] = settings.value(setting_name, default_value, IOU_DEVICE_SETTING_TYPES[setting_name])
            iou_devices.append(device)
        settings.endArray()
        settings.remove("")
        settings.endGroup()

        if iou_devices:
            local_config.saveSectionSettings(self.__class__.__name__, {"devices": iou_devices})

        settings = local_config.settings()
        if "devices" in settings.get(self.__class__.__name__, {}):
            for device in settings[self.__class__.__name__]["devices"]:
                name = device.get("name")
                server = device.get("server")
                key = "{server}:{name}".format(server=server, name=name)
                if key in self._iou_devices or not name or not server:
                    continue
                device_settings = IOU_DEVICE_SETTINGS.copy()
                device_settings.update(device)
                self._iou_devices[key] = device_settings

        # keep things sync
        self._saveIOUDevices()

    def _saveIOUDevices(self):
        """
        Saves the IOU devices to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, {"devices": list(self._iou_devices.values())})

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

    def iouDevices(self):
        """
        Returns IOU devices settings.

        :returns: IOU devices settings (dictionary)
        """

        return self._iou_devices

    def setIOUDevices(self, new_iou_devices):
        """
        Sets IOS devices settings.

        :param new_iou_devices: IOU images settings (dictionary)
        """

        self._iou_devices = new_iou_devices.copy()
        self._saveIOUDevices()

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

        log.info("creating node {}".format(node_class))

        if server.isLocal() and (not self._settings["iourc_path"] or not os.path.isfile(self._settings["iourc_path"])):
            raise ModuleError("The path to IOURC must be configured")

        # create an instance of the node class
        return node_class(self, server, project)

    def setupNode(self, node, node_name):
        """
        Setups a node.

        :param node: Node instance
        :param node_name: Node name
        """

        log.info("configuring node {}".format(node))

        iouimage = None
        if node_name:
            for iou_key, info in self._iou_devices.items():
                if node_name == info["name"]:
                    iouimage = iou_key

        if not iouimage:
            selected_images = []
            for image, info in self._iou_devices.items():
                if info["server"] == node.server().host or (node.server().isLocal() and info["server"] == "local"):
                    selected_images.append(image)

            if not selected_images:
                raise ModuleError("No IOU image found for this device")
            elif len(selected_images) > 1:

                from gns3.main_window import MainWindow
                mainwindow = MainWindow.instance()

                (selection, ok) = QtGui.QInputDialog.getItem(mainwindow, "IOU image", "Please choose an image", selected_images, 0, False)
                if ok:
                    iouimage = selection
                else:
                    raise ModuleError("Please select an IOU image")

            else:
                iouimage = selected_images[0]

        name = self._iou_devices[iouimage]["name"]
        initial_config = self._iou_devices[iouimage]["initial_config"]
        iou_path = self._iou_devices[iouimage]["path"]
        use_default_iou_values = self._iou_devices[iouimage]["use_default_iou_values"]
        settings = {}
        if initial_config:
            settings["initial_config"] = initial_config
        settings["use_default_iou_values"] = use_default_iou_values
        if not use_default_iou_values:
            settings["ram"] = self._iou_devices[iouimage]["ram"]
            settings["nvram"] = self._iou_devices[iouimage]["nvram"]
        settings["ethernet_adapters"] = self._iou_devices[iouimage]["ethernet_adapters"]
        settings["serial_adapters"] = self._iou_devices[iouimage]["serial_adapters"]

        if len(self._settings["iourc_path"]) > 0:
            try:
                with open(self._settings["iourc_path"]) as f:
                    settings["iourc_content"] = f.read()
            except OSError as e:
                print("Can't open iourc file {}: {}".format(self._settings["iourc_path"], e))

        if node.server().isCloud():
            settings["cloud_path"] = "images/IOU"
            node.setup(self._iou_devices[iouimage]["image"], initial_settings=settings)
        else:
            node.setup(iou_path, initial_settings=settings)

    def reset(self):
        """
        Resets the servers.
        """

        log.info("IOU module reset")
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
        iou_devices = self.iouDevices()
        candidate_iou_images = {}

        alternative_image = image

        # find all images with the same platform and local server
        for iou_device in iou_devices.values():
            if iou_device["server"] == "local":
                candidate_iou_images[iou_device["image"]] = iou_device["path"]

        if candidate_iou_images:
            selection, ok = QtGui.QInputDialog.getItem(mainwindow,
                                                       "IOU image", "IOU image {} could not be found\nPlease select an alternative from your existing images:".format(image),
                                                       list(candidate_iou_images.keys()), 0, False)
            if ok:
                iou_image = candidate_iou_images[selection]
                self._iou_images_cache[image] = iou_image
                return iou_image

        # no registered IOU image is used, let's just ask for an IOU image path
        QtGui.QMessageBox.critical(mainwindow, "IOU image", "Could not find the {} IOU image \nPlease select a similar IOU image!".format(image))
        from .pages.iou_device_preferences_page import IOUDevicePreferencesPage
        path = IOUDevicePreferencesPage.getIOUImage(mainwindow)
        if path:
            alternative_image = path
            self._iou_images_cache[image] = alternative_image
        return alternative_image

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

        return [IOUDevice]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        nodes = []
        for iou_device in self._iou_devices.values():
            nodes.append(
                {"class": IOUDevice.__name__,
                 "name": iou_device["name"],
                 "server": iou_device["server"],
                 "default_symbol": iou_device["default_symbol"],
                 "hover_symbol": iou_device["hover_symbol"],
                 "categories": [iou_device["category"]]
                 }
            )
        return nodes

    @staticmethod
    def preferencePages():
        """
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
