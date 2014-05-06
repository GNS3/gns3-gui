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

import socket
import base64
import os
from gns3.qt import QtCore, QtGui
from gns3.servers import Servers
from ..module import Module
from ..module_error import ModuleError
from .vpcs_device import VPCSDevice
from .settings import VPCS_SETTINGS, VPCS_SETTING_TYPES

import logging
log = logging.getLogger(__name__)


class VPCS(Module):
    """
    VPCS module.
    """

    def __init__(self):
        Module.__init__(self)

        self._settings = {}
        self._nodes = []
        self._vpcs_images = {}
        self._servers = []
        self._working_dir = ""

        # load the settings
        self._loadSettings()
        self._loadVPCSImages()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in VPCS_SETTINGS.items():
            self._settings[name] = settings.value(name, value, type=VPCS_SETTING_TYPES[name])
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

    def _loadVPCSImages(self):
        """
        Load the VPCS images from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup("VPCSImages")

        # load the VPCS images
        size = settings.beginReadArray("vpcs_image")
        for index in range(0, size):
            settings.setArrayIndex(index)
            path = settings.value("path", "")
            image = settings.value("image", "")
            script_file = settings.value("script_file", "")
            key = "{server}:{image}".format(server=server, image=image)
            self._vpcs_images[key] = {"path": path,
                                     "image": image,
                                     "script_file": script_file}

        settings.endArray()
        settings.endGroup()

    def _saveVPCSImages(self):
        """
        Saves the VPCS images to the persistent settings file.
        """

        # save the settings
        settings = QtCore.QSettings()
        settings.beginGroup("VPCSImages")
        settings.remove("")

        # save the VPCS images
        settings.beginWriteArray("vpcs_image", len(self._vpcs_images))
        index = 0
        for ios_image in self._vpcs_images.values():
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
        log.info("local working directory for VPCS module: {}".format(self._working_dir))

        # update the server with the new working directory / project name
        for server in self._servers:
            if server.connected():
                self._sendSettings(server)

    def addServer(self, server):
        """
        Adds a server to be used by this module.

        :param server: WebSocketClient instance
        """

        log.info("adding server {}:{} to VPCS module".format(server.host, server.port))
        self._servers.append(server)
        self._sendSettings(server)

    def removeServer(self, server):
        """
        Removes a server from being used by this module.

        :param server: WebSocketClient instance
        """

        log.info("removing server {}:{} from VPCS module".format(server.host, server.port))
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

    def vpcsImages(self):
        """
        Returns VPCS images settings.

        :returns: VPCS images settings (dictionary)
        """

        return self._vpcs_images

    def setVPCSImages(self, new_vpcs_images):
        """
        Sets IOS images settings.

        :param new_vpcs_images: IOS images settings (dictionary)
        """

        self._vpcs_images = new_vpcs_images.copy()
        self._saveVPCSImages()

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

        params = {}
        for name, value in settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        if params:
            for server in self._servers:
                # send the local working directory only if this is a local server
                if server.isLocal():
                    params.update({"working_dir": self._working_dir})
                else:
                    project_name = os.path.basename(self._working_dir)
                    if project_name.endswith("-files"):
                        project_name = project_name[:-6]
                    params.update({"project_name": project_name})
                server.send_notification("vpcs.settings", params)

        self._settings.update(settings)
        self._saveSettings()

    def _sendSettings(self, server):
        """
        Sends the module settings to the server.

        :param server: WebSocketClient instance
        """

        log.info("sending VPCS settings to server {}:{}".format(server.host, server.port))
        params = self._settings.copy()

        # send the local working directory only if this is a local server
        if server.isLocal():
            params.update({"working_dir": self._working_dir})
        else:
            project_name = os.path.basename(self._working_dir)
            if project_name.endswith("-files"):
                project_name = project_name[:-6]
            params.update({"project_name": project_name})
        server.send_notification("vpcs.settings", params)

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
        settings = {}

        selected_images = []
        for image, info in self._vpcs_images.items():
            if info["server"] == node.server().host or (node.server().isLocal() and info["server"] == "local"):
                selected_images.append(image)

        if not selected_images:
            raise ModuleError("No VPCS image found for this device")
        elif len(selected_images) > 1:

            from gns3.main_window import MainWindow
            mainwindow = MainWindow.instance()

            (selection, ok) = QtGui.QInputDialog.getItem(mainwindow, "VPCS image", "Please choose an image", selected_images, 0, False)
            if ok:
                vpcsimage = selection
            else:
                raise ModuleError("Please select an VPCS image")

        else:
            vpcsimage = selected_images[0]

        script_file = self._vpcs_images[vpcsimage]["script_file"]
        vpcs_path = self._vpcs_images[vpcsimage]["path"]
        if script_file:
            settings = {"script_file": script_file}
        node.setup(vpcs_path, initial_settings=settings)

    def reset(self):
        """
        Resets the servers.
        """

        log.info("VPCS module reset")
        for server in self._servers:
            if server.connected():
                server.send_notification("vpcs.reset")
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

        return [VPCSDevice]

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        from .pages.vpcs_preferences_page import VPCSPreferencesPage
        from .pages.vpcs_device_preferences_page import VPCSDevicePreferencesPage
        return [VPCSPreferencesPage, VPCSDevicePreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of VPCS module.

        :returns: instance of VPCS
        """

        if not hasattr(VPCS, "_instance"):
            VPCS._instance = VPCS()
        return VPCS._instance
