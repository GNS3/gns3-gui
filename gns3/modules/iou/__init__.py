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
        self._nodes = []
        self._iou_images = {}
        self._servers = []
        self._working_dir = ""
        self._images_dir = ""

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
        settings.beginGroup("IOUImages")

        # load the IOU images
        size = settings.beginReadArray("iou_image")
        for index in range(0, size):
            settings.setArrayIndex(index)
            path = settings.value("path", "")
            image = settings.value("image", "")
            initial_config = settings.value("initial_config", "")
            use_default_iou_values = settings.value("use_default_iou_values", True, type=bool)
            ram = settings.value("ram", 256, type=int)
            nvram = settings.value("nvram", 128, type=int)
            server = settings.value("server", "local")
            key = "{server}:{image}".format(server=server, image=image)
            self._iou_images[key] = {"path": path,
                                     "image": image,
                                     "initial_config": initial_config,
                                     "use_default_iou_values": use_default_iou_values,
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
        settings.beginGroup("IOUImages")
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

    def allocateServer(self, node_class):
        """
        Allocates a server.

        :param node_class: Node object

        :returns: allocated server (WebSocketClient instance)
        """

        # allocate a server for the node
        servers = Servers.instance()
        if self._settings["use_local_server"]:
            # use the local server
            server = servers.localServer()
        else:
            # pick up a remote server (round-robin method)
            server = next(iter(servers))
            if not server:
                raise ModuleError("No remote server is configured")
        return server

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

    def setupNode(self, node):
        """
        Setups a node.

        :param node: Node instance
        """

        log.info("configuring node {}".format(node))

        selected_images = []
        for image, info in self._iou_images.items():
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

        initial_config = self._iou_images[iouimage]["initial_config"]
        iou_path = self._iou_images[iouimage]["path"]
        use_default_iou_values = self._iou_images[iouimage]["use_default_iou_values"]
        settings = {}
        if initial_config:
            settings["initial_config"] = initial_config
        settings["use_default_iou_values"] = use_default_iou_values
        if not use_default_iou_values:
            settings["ram"] = self._iou_images[iouimage]["ram"]
            settings["nvram"] = self._iou_images[iouimage]["nvram"]
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
