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

import socket
import base64
import os
from gns3.qt import QtCore
from gns3.servers import Servers
from ..module import Module
from ..module_error import ModuleError
from .iou_device import IOUDevice
from .settings import IOU_SETTINGS, IOU_SETTING_TYPES

import logging
log = logging.getLogger(__name__)


class IOU(Module):
    """
    IOU module.
    """

    def __init__(self):
        Module.__init__(self)

        self._settings = {}
        self._iou_images = {}
        self._servers = []
        self._working_dir = ""

        # load the settings
        self._loadSettings()
        self._loadIOUImages()

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

    def _loadIOUImages(self):
        """
        Load the IOU images from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup("IOUs")

        # load the IOU images
        size = settings.beginReadArray("iou_image")
        for index in range(0, size):
            settings.setArrayIndex(index)
            path = settings.value("path", "")
            image = settings.value("image", "")
            startup_config = settings.value("startup_config", "")
            ram = settings.value("ram", 256, type=int)
            nvram = settings.value("nvram", 128, type=int)
            server = settings.value("server", "local")

            key = "{server}:{image}".format(server=server, image=image)
            self._iou_images[key] = {"path": path,
                                     "image": image,
                                     "startup_config": startup_config,
                                     "ram": ram,
                                     "nvram": nvram,
                                     "server": server}

        settings.endArray()
        settings.endGroup()

    def _saveIOUImages(self):
        """
        Saves the IOU images to the persistent settings file.
        """

        # save the settings
        settings = QtCore.QSettings()
        settings.beginGroup("IOUs")
        settings.remove("")

        # save the IOU images
        settings.beginWriteArray("iou_image", len(self._iou_images))
        index = 0
        for ios_image in self._iou_images.values():
            settings.setArrayIndex(index)
            for name, value in ios_image.items():
                settings.setValue(name, value)
            index += 1
        settings.endArray()
        settings.endGroup()

    def setLocalBaseWorkingDir(self, path):
        """
        Sets the local base working directory for this module.

        :param path: path to the local working directory
        """

        self._working_dir = os.path.join(path, "iou")
        if not os.path.exists(self._working_dir):
            try:
                os.makedirs(self._working_dir)
            except EnvironmentError as e:
                raise ModuleError("{}".format(e))

        log.info("local working directory for IOU module: {}".format(self._working_dir))
        servers = Servers.instance()
        server = servers.localServer()
        if server.connected():
            self._sendSettings(server)

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

    def iouImages(self):
        """
        Returns IOU images settings.

        :returns: IOU images settings (dictionary)
        """

        return self._iou_images

    def setIOUImages(self, new_iou_images):
        """
        Sets IOS images settings.

        :param new_iou_images: IOS images settings (dictionary)
        """

        self._iou_images = new_iou_images.copy()
        self._saveIOUImages()

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
            with open(iourc_path, "r") as f:
                log.info("opening iourc file: {}".format(iourc_path))
                config = f.read()
                encoded = ("").join(base64.encodestring(config.encode("utf-8")).decode("utf-8").split())
                return encoded
        except EnvironmentError as e:
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
        servers = Servers.instance()
        if server == servers.localServer():
            params.update({"working_dir": self._working_dir})
        server.send_notification("iou.settings", params)

    def createNode(self, node_class, server=None):
        """
        Creates a new node.

        :param node_class: Node object
        :param server: optional  WebSocketClient instance
        """

        log.info("creating node {}".format(node_class))

        if not self._settings["iourc"] or not os.path.exists(self._settings["iourc"]):
            raise ModuleError("The path to IOURC must be configured")

        # allocate a server for the node if none is given
        servers = Servers.instance()
        if self._settings["use_local_server"] and not server:
            # use the local server
            server = servers.localServer()
        elif not server:
            # pick up a remote server (round-robin method)
            server = next(iter(servers))
            if not server:
                raise ModuleError("No remote server is configured")

        if not server.connected():
            try:
                log.info("reconnecting to server {}:{}".format(server.host, server.port))
                server.reconnect()
                self._sendSettings(server)
            except socket.error as e:
                raise ModuleError("Could not connect to server {}:{}: {}".format(server.host,
                                                                                 server.port,
                                                                                 e))
        if server not in self._servers:
            self.addServer(server)

        # create an instance of the node class
        return node_class(self, server)

    def setupNode(self, node):
        """
        Setups a node.

        :param node: Node instance
        """

        log.info("configuring node {}".format(node))
        if not self._iou_images:
            raise ModuleError("No IOU image found for this device")

        settings = {}
        #FIXME: for now use the fist available image
        iouimage = list(self._iou_images.keys())[0]
        startup_config = self._iou_images[iouimage]["startup_config"]
        iou_path = self._iou_images[iouimage]["path"]
        if startup_config:
            settings = {"startup_config": startup_config}
        node.setup(iou_path, initial_settings=settings)

    def reset(self):
        """
        Resets the servers.
        """

        log.info("IOU module reset")
        for server in self._servers:
            if server.connected():
                server.send_notification("iou.reset")

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
    def nodes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [IOUDevice]

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
