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
Dynamips module implementation.
"""

import os
import glob
from gns3.qt import QtCore, QtGui
from gns3.servers import Servers
from ..module import Module
from ..module_error import ModuleError
from .nodes.router import Router
from .nodes.c1700 import C1700
from .nodes.c2600 import C2600
from .nodes.c2691 import C2691
from .nodes.c3600 import C3600
from .nodes.c3725 import C3725
from .nodes.c3745 import C3745
from .nodes.c7200 import C7200
from .nodes.ethernet_switch import EthernetSwitch
from .nodes.ethernet_hub import EthernetHub
from .nodes.frame_relay_switch import FrameRelaySwitch
from .nodes.atm_switch import ATMSwitch
from .settings import DYNAMIPS_SETTINGS, DYNAMIPS_SETTING_TYPES, PLATFORMS_DEFAULT_RAM

import logging
log = logging.getLogger(__name__)


class Dynamips(Module):
    """
    Dynamips module.
    """

    def __init__(self):
        Module.__init__(self)

        self._settings = {}
        self._ios_images = {}
        self._servers = []
        self._nodes = []
        self._working_dir = ""
        self._images_dir = ""
        self._ios_images_cache = {}

        # load the settings and IOS images.
        self._loadSettings()
        self._loadIOSImages()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in DYNAMIPS_SETTINGS.items():
            self._settings[name] = settings.value(name, value, type=DYNAMIPS_SETTING_TYPES[name])
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

    def _loadIOSImages(self):
        """
        Load the IOS images from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup("IOSImages")

        # load the IOS images
        size = settings.beginReadArray("ios_image")
        for index in range(0, size):
            settings.setArrayIndex(index)
            path = settings.value("path", "")
            image = settings.value("image", "")
            startup_config = settings.value("startup_config", "")
            private_config = settings.value("private_config", "")
            platform = settings.value("platform", "")
            chassis = settings.value("chassis", "")
            idlepc = settings.value("idlepc", "")
            ram = settings.value("ram", 128, type=int)
            server = settings.value("server", "local")

            key = "{server}:{image}".format(server=server, image=image)
            self._ios_images[key] = {"path": path,
                                     "image": image,
                                     "startup_config": startup_config,
                                     "private_config": private_config,
                                     "platform": platform,
                                     "chassis": chassis,
                                     "idlepc": idlepc,
                                     "ram": ram,
                                     "server": server}

        settings.endArray()
        settings.endGroup()

    def _saveIOSImages(self):
        """
        Saves the IOS images to the persistent settings file.
        """

        # save the settings
        settings = QtCore.QSettings()
        settings.beginGroup("IOSImages")
        settings.remove("")

        # save the IOS images
        settings.beginWriteArray("ios_image", len(self._ios_images))
        index = 0
        for ios_image in self._ios_images.values():
            settings.setArrayIndex(index)
            for name, value in ios_image.items():
                settings.setValue(name, value)
            index += 1
        settings.endArray()
        settings.endGroup()

    def _delete_dynamips_files(self):
        """
        Deletes useless local Dynamips files from the working directory
        """

        files = glob.glob(os.path.join(self._working_dir, "dynamips", "*.ghost"))
        files += glob.glob(os.path.join(self._working_dir, "dynamips", "*_lock"))
        files += glob.glob(os.path.join(self._working_dir, "dynamips", "ilt_*"))
        files += glob.glob(os.path.join(self._working_dir, "dynamips", "c[0-9][0-9][0-9][0-9]_*_rommon_vars"))
        files += glob.glob(os.path.join(self._working_dir, "dynamips", "c[0-9][0-9][0-9][0-9]_*_ssa"))
        for file in files:
            try:
                log.debug("deleting file {}".format(file))
                os.remove(file)
            except OSError as e:
                log.warn("could not delete file {}: {}".format(file, e))
                continue

    def setProjectFilesDir(self, path):
        """
        Sets the project files directory path this module.

        :param path: path to the local project files directory
        """

        #self._delete_dynamips_files()  #FIXME: cause issues
        self._working_dir = path
        log.info("local working directory for Dynamips module: {}".format(self._working_dir))

        # update the server with the new working directory / project name
        for server in self._servers:
            if server.connected():
                self._sendSettings(server)

    def setImageFilesDir(self, path):
        """
        Sets the image files directory path this module.

        :param path: path to the local image files directory
        """

        self._images_dir = os.path.join(path, "IOS")

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

        log.info("adding server {}:{} to Dynamips module".format(server.host, server.port))
        self._servers.append(server)
        self._sendSettings(server)

    def removeServer(self, server):
        """
        Removes a server from being used by this module.

        :param server: WebSocketClient instance
        """

        log.info("removing server {}:{} from Dynamips module".format(server.host, server.port))
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

    def iosImages(self):
        """
        Returns IOS images settings.

        :returns: IOS images settings (dictionary)
        """

        return self._ios_images

    def setIOSImages(self, new_ios_images):
        """
        Sets IOS images settings.

        :param new_ios_images: IOS images settings (dictionary)
        """

        self._ios_images = new_ios_images.copy()
        self._saveIOSImages()

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
                if server.isLocal():
                    params.update({"working_dir": self._working_dir})
                else:
                    project_name = os.path.basename(self._working_dir)
                    if project_name.endswith("-files"):
                        project_name = project_name[:-6]
                    params.update({"project_name": project_name})
                server.send_notification("dynamips.settings", params)

        self._settings.update(settings)
        self._saveSettings()

    def _sendSettings(self, server):
        """
        Sends the module settings to the server.

        :param server: WebSocketClient instance
        """

        log.info("sending Dynamips settings to server {}:{}".format(server.host, server.port))
        params = self._settings.copy()
        # send the local working directory only if this is a local server
        if server.isLocal():
            params.update({"working_dir": self._working_dir})
        else:
            project_name = os.path.basename(self._working_dir)
            if project_name.endswith("-files"):
                project_name = project_name[:-6]
            params.update({"project_name": project_name})
        server.send_notification("dynamips.settings", params)

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

    def _allocateIOSImage(self, node):
        """
        Allocates an IOS image to a node

        :param node: Node instance
        """

        platform = node.settings()["platform"]

        selected_images = []
        for ios_image, info in self._ios_images.items():
            if info["platform"] == platform and (info["server"] == node.server().host or (node.server().isLocal() and info["server"] == "local")):
                selected_images.append(ios_image)

        if not selected_images:
            return None
        elif len(selected_images) > 1:

            from gns3.main_window import MainWindow
            mainwindow = MainWindow.instance()

            (selection, ok) = QtGui.QInputDialog.getItem(mainwindow, "IOS image", "Please choose an image", selected_images, 0, False)
            if ok:
                return self._ios_images[selection]
            else:
                raise ModuleError("Please select an IOS image")

        else:
            return self._ios_images[selected_images[0]]

    def setupNode(self, node):
        """
        Setups a node.

        :param node: Node instance
        """

        log.info("configuring node {}".format(node))

        if isinstance(node, Router):
            ios_image = self._allocateIOSImage(node)
            if not ios_image:
                raise ModuleError("No IOS image found for platform {}".format(node.settings()["platform"]))
            settings = {}
            # set initial settings like the chassis or an idle-pc value etc.
            if ios_image["chassis"]:
                settings["chassis"] = ios_image["chassis"]
            if ios_image["idlepc"]:
                settings["idlepc"] = ios_image["idlepc"]
            if ios_image["startup_config"]:
                settings["startup_config"] = ios_image["startup_config"]
            if ios_image["private_config"]:
                settings["private_config"] = ios_image["private_config"]
            node.setup(ios_image["path"], ios_image["ram"], initial_settings=settings)
        else:
            node.setup()

    def updateImageIdlepc(self, image_path, idlepc):
        """
        Updates the idle-pc for an IOS image.

        :param image_path: path to the IOS image
        :param idlepc: idle-pc value
        """

        for ios_image in self._ios_images.values():
            if ios_image["path"] == image_path:
                if ios_image["idlepc"] != idlepc:
                    ios_image["idlepc"] = idlepc
                    self._saveIOSImages()
                break

    def reset(self):
        """
        Resets the servers and nodes.
        """

        log.info("Dynamips module reset")
        for server in self._servers:
            if server.connected():
                server.send_notification("dynamips.reset")
        self._servers.clear()

        for node in self._nodes:
            node.reset()
        self._nodes.clear()

    def notification(self, destination, params):
        """
        To received notifications from the server.

        :param destination: JSON-RPC method
        :param params: JSON-RPC params
        """

        if "devices" in params:
            for node in self._nodes:
                for device in params["devices"]:
                    if node.name() == device:
                        message = "node {}: {}".format(node.name(), params["message"])
                        self.notification_signal.emit(message, params["details"])
                        if hasattr(node, "stop"):
                            node.stop()

    def exportConfigs(self, directory):
        """
        Exports all configs for all nodes to a directory.

        :param directory: destination directory path
        """

        for node in self._nodes:
            if hasattr(node, "exportConfigs") and node.initialized():
                node.exportConfigs(directory)

    def importConfigs(self, directory):
        """
        Imports configs to all nodes from a directory.

        :param directory: source directory path
        """

        for node in self._nodes:
            if hasattr(node, "importConfigs") and node.initialized():
                node.importConfigs(directory)

    def findAlternativeIOSImage(self, image, node):
        """
        Tries to find an alternative IOS image.

        :param image: image name
        :param node: requesting Node instance

        :return: IOS image (dictionary)
        """

        if image in self._ios_images_cache:
            return self._ios_images_cache[image]

        from gns3.main_window import MainWindow
        mainwindow = MainWindow.instance()
        ios_images = self.iosImages()
        candidate_ios_images = {}
        alternative_image = {"path": image,
                             "ram": None,
                             "idlepc": None}

        # find all images with the same platform and local server
        for ios_image in ios_images.values():
            if ios_image["platform"] == node.settings()["platform"] and ios_image["server"] == "local":
                candidate_ios_images[ios_image["image"]] = ios_image

        if candidate_ios_images:
            selection, ok = QtGui.QInputDialog.getItem(mainwindow,
                                                       "IOS image", "IOS image {} could not be found\nPlease select an alternative from your existing images:".format(image),
                                                       list(candidate_ios_images.keys()), 0, False)
            if ok:
                ios_image = candidate_ios_images[selection]
                alternative_image["path"] = ios_image["path"]
                alternative_image["ram"] = ios_image["ram"]
                alternative_image["idlepc"] = ios_image["idlepc"]
                self._ios_images_cache[image] = alternative_image
                return alternative_image

        # no registered IOS image is used, let's just ask for an IOS image path
        QtGui.QMessageBox.critical(mainwindow, "IOS image", "Could not find the {} IOS image \nPlease select a similar IOS image!".format(image))
        from .pages.ios_router_preferences_page import IOSRouterPreferencesPage
        path = IOSRouterPreferencesPage.getIOSImage(mainwindow)
        if path:
            alternative_image["path"] = path
            self._ios_images_cache[image] = alternative_image
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
    def nodes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [C1700, C2600, C2691, C3600, C3725, C3745, C7200, EthernetSwitch, EthernetHub, FrameRelaySwitch, ATMSwitch]

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        from .pages.dynamips_preferences_page import DynamipsPreferencesPage
        from .pages.ios_router_preferences_page import IOSRouterPreferencesPage
        return [DynamipsPreferencesPage, IOSRouterPreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of Dynamips.

        :returns: instance of Dynamips
        """

        if not hasattr(Dynamips, "_instance"):
            Dynamips._instance = Dynamips()
        return Dynamips._instance
