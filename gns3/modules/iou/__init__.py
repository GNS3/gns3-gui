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

import base64
import os

from gns3.qt import QtCore, QtGui
from gns3.node import Node

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
        self._servers = []
        self._working_dir = ""
        self._images_dir = ""
        self._iou_images_cache = {}

        # load the settings
        self._loadSettings()
        self._loadIOUDevices()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in IOU_SETTINGS.items():
            self._settings[name] = settings.value(name, value, type=IOU_SETTING_TYPES[name])
        settings.endGroup()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in self._settings.items():
            settings.setValue(name, value)
        settings.endGroup()

    def _loadIOUDevices(self):
        """
        Load the IOU devices from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup("IOUDevices")

        # load the IOU images
        size = settings.beginReadArray("iou_device")
        for index in range(0, size):
            settings.setArrayIndex(index)
            name = settings.value("name")
            server = settings.value("server")
            key = "{server}:{name}".format(server=server, name=name)
            if key in self._iou_devices or not name or not server:
                continue
            self._iou_devices[key] = {}
            for setting_name, default_value in IOU_DEVICE_SETTINGS.items():
                self._iou_devices[key][setting_name] = settings.value(setting_name, default_value, IOU_DEVICE_SETTING_TYPES[setting_name])

        settings.endArray()
        settings.endGroup()

    def _saveIOUDevices(self):
        """
        Saves the IOU devices to the persistent settings file.
        """

        # save the settings
        settings = QtCore.QSettings()
        settings.beginGroup("IOUDevices")
        settings.remove("")

        # save the IOU images
        settings.beginWriteArray("iou_device", len(self._iou_devices))
        index = 0
        for ios_image in self._iou_devices.values():
            settings.setArrayIndex(index)
            for name, value in ios_image.items():
                settings.setValue(name, value)
            index += 1
        settings.endArray()
        settings.endGroup()

    def setProjectFilesDir(self, path):
        """
        Sets the project files directory path this module.

        :param path: path to the local project files directory
        """

        self._working_dir = path
        log.info("local working directory for IOU module: {}".format(self._working_dir))

        # update the server with the new working directory / project name
        for server in self._servers:
            if server.connected():
                self._sendSettings(server)

    def setImageFilesDir(self, path):
        """
        Sets the image files directory path this module.

        :param path: path to the local image files directory
        """

        self._images_dir = os.path.join(path, "IOU")

    def imageFilesDir(self):
        """
        Returns the files directory path this module.

        :returns: path to the local image files directory
        """

        return self._images_dir

    def addServer(self, server):
        """
        Adds a server to be used by this module.

        :param server: WebSocketClient instance
        """

        log.info("adding server {}:{} to IOU module".format(server.host, server.port))
        self._servers.append(server)
        self._sendSettings(server)

    def removeServer(self, server):
        """
        Removes a server from being used by this module.

        :param server: WebSocketClient instance
        """

        log.info("removing server {}:{} from IOU module".format(server.host, server.port))
        self._servers.remove(server)

    def servers(self):
        """
        Returns all the servers used by this module.

        :returns: list of WebSocketClient instances
        """

        return self._servers

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

    def _base64iourc(self, iourc_path):
        """
        Get the content of the IOURC file base64 encoded.

        :param config_path: path to the iourc file.

        :returns: base64 encoded string
        """

        try:
            with open(iourc_path, "r", errors="replace") as f:
                log.info("opening iourc file: {}".format(iourc_path))
                config = f.read()
                encoded = "".join(base64.encodestring(config.encode("utf-8")).decode("utf-8").split())
                return encoded
        except OSError as e:
            log.warn("could not base64 encode {}: {}".format(iourc_path, e))
            return ""

    def setSettings(self, settings):
        """
        Sets the module settings

        :param settings: module settings (dictionary)
        """

        params = {}
        for name, value in settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        if params:
            if "iourc" in params:
                # encode the iourc file in base64
                params["iourc"] = self._base64iourc(params["iourc"])
            for server in self._servers:
                # send the local working directory only if this is a local server
                if server.isLocal():
                    params.update({"working_dir": self._working_dir})
                else:
                    if "iouyap" in params:
                        del params["iouyap"]  # do not send iouyap path to remote servers
                    project_name = os.path.basename(self._working_dir)
                    if project_name.endswith("-files"):
                        project_name = project_name[:-6]
                    params.update({"project_name": project_name})
                server.send_notification("iou.settings", params)

        self._settings.update(settings)
        self._saveSettings()

    def _sendSettings(self, server):
        """
        Sends the module settings to the server.

        :param server: WebSocketClient instance
        """

        log.info("sending IOU settings to server {}:{}".format(server.host, server.port))
        params = self._settings.copy()

        # encode the iourc file in base64
        params["iourc"] = self._base64iourc(params["iourc"])

        # send the local working directory only if this is a local server
        if server.isLocal():
            params.update({"working_dir": self._working_dir})
        else:
            if "iouyap" in params:
                del params["iouyap"]  # do not send iouyap path to remote servers
            project_name = os.path.basename(self._working_dir)
            if project_name.endswith("-files"):
                project_name = project_name[:-6]
            params.update({"project_name": project_name})
        server.send_notification("iou.settings", params)

    def createNode(self, node_class, server):
        """
        Creates a new node.

        :param node_class: Node object
        :param server: WebSocketClient instance
        """

        log.info("creating node {}".format(node_class))

        if not self._settings["iourc"] or not os.path.isfile(self._settings["iourc"]):
            raise ModuleError("The path to IOURC must be configured")

        if not server.connected():
            try:
                log.info("reconnecting to server {}:{}".format(server.host, server.port))
                server.reconnect()
            except OSError as e:
                raise ModuleError("Could not connect to server {}:{}: {}".format(server.host,
                                                                                 server.port,
                                                                                 e))
        if server not in self._servers:
            self.addServer(server)

        # create an instance of the node class
        return node_class(self, server)

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
        for server in self._servers:
            if server.connected():
                server.send_notification("iou.reset")
        self._servers.clear()
        self._nodes.clear()

    def notification(self, destination, params):
        """
        To received notifications from the server.

        :param destination: JSON-RPC method
        :param params: JSON-RPC params
        """

        if "id" in params:
            for node in self._nodes:
                if node.id() == params["id"]:
                    message = "node {}: {}".format(node.name(), params["message"])
                    self.notification_signal.emit(message, params["details"])
                    node.stop()

    def exportConfigs(self, directory):
        """
        Exports all configs for all nodes to a directory.

        :param directory: destination directory path
        """

        for node in self._nodes:
            if hasattr(node, "exportConfig") and node.initialized():
                node.exportConfig(directory)

    def importConfigs(self, directory):
        """
        Imports configs to all nodes from a directory.

        :param directory: source directory path
        """

        for node in self._nodes:
            if hasattr(node, "importConfig") and node.initialized():
                node.importConfig(directory)

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
