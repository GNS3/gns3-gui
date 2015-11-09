# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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

"""Docker module implementation."""

from gns3.qt import QtWidgets
from gns3.local_config import LocalConfig

from ..module import Module
from ..module_error import ModuleError
from .docker_vm import DockerVM
from .settings import DOCKER_SETTINGS, DOCKER_CONTAINER_SETTINGS

import logging
log = logging.getLogger(__name__)


class Docker(Module):
    """Docker module."""

    def __init__(self):
        super().__init__()

        self._settings = {}
        self._docker_images = {}
        self._nodes = []

        # load the settings
        self._loadSettings()
        self._loadDockerImages()

    def configChangedSlot(self):
        # load the settings
        self._loadSettings()

    def _loadSettings(self):
        """Loads the settings from the persistent settings file."""
        local_config = LocalConfig.instance()
        self._settings = local_config.loadSectionSettings(
            self.__class__.__name__, DOCKER_SETTINGS)

    def _saveSettings(self):
        """Saves the settings to the persistent settings file."""
        LocalConfig.instance().saveSectionSettings(
            self.__class__.__name__, self._settings)

    def _loadDockerImages(self):
        """Load the Docker images from the persistent settings file."""

        local_config = LocalConfig.instance()
        settings = local_config.settings()
        if "images" in settings.get(self.__class__.__name__, {}):
            for image in settings[self.__class__.__name__]["images"]:
                name = image.get("name")
                server = image.get("server")
                key = "{server}:{name}".format(server=server, name=name)
                if key in self._docker_images or not name or not server:
                    continue
                container_settings = DOCKER_CONTAINER_SETTINGS.copy()
                container_settings.update(image)
                self._docker_images[key] = container_settings

    def _saveDockerImages(self):
        """Saves the Docker images to the persistent settings file."""

        self._settings["images"] = list(self._docker_images.values())
        self._saveSettings()

    def dockerImages(self):
        """
        Returns Docker images settings.

        :returns: Docker images settings
        :rtype: dict
        """

        return self._docker_images

    def setDockerImages(self, new_docker_images):
        """Sets Docker image settings.

        :param new_iou_images: Docker images settings (dictionary)
        """
        self._docker_images = new_docker_images.copy()
        self._saveDockerImages()

    def addNode(self, node):
        """Adds a node to this module.

        :param node: Node instance
        """
        self._nodes.append(node)

    def removeNode(self, node):
        """Removes a node from this module.

        :param node: Node instance
        """
        if node in self._nodes:
            self._nodes.remove(node)

    def settings(self):
        """
        Returns the module settings

        :returns: module settings (dictionary)
        """
        return self._settings

    def setSettings(self, settings):
        """Sets the module settings

        :param settings: module settings (dictionary)
        """
        self._settings.update(settings)
        self._saveSettings()

    def createNode(self, node_class, server, project):
        """Creates a new node.

        :param node_class: Node object
        :param server: HTTPClient instance
        """
        log.info("creating node {}".format(node_class))
        # create an instance of the node class
        return node_class(self, server, project)

    def setupNode(self, node, node_name):
        """Sets up a node.

        :param node: Node instance
        :param node_name: Node name
        """
        log.info("configuring node {} with id {}".format(node, node.id()))

        image = None
        if node_name:
            for image_key, info in self._docker_images.items():
                if node_name == info["imagename"]:
                    image = image_key
        if not image:
            selected_images = []
            for image, info in self._docker_images.items():
                if info["server"] == node.server().host() or (
                        node.server().isLocal() and info["server"] == "local"):
                    selected_images.append(image)

            if not selected_images:
                raise ModuleError("No Docker VM on server {}".format(
                    node.server().url()))
            elif len(selected_images) > 1:
                from gns3.main_window import MainWindow
                mainwindow = MainWindow.instance()

                (selection, ok) = QtWidgets.QInputDialog.getItem(
                    mainwindow, "Docker Image", "Please choose an image",
                    selected_images, 0, False)
                if ok:
                    image = selection
                else:
                    raise ModuleError("Please select a Docker Image")
            else:
                image = selected_images[0]

        image_settings = {}
        for setting_name, value in self._docker_images[image].items():
            if setting_name in node.settings() and value != "" and value is not None:
                image_settings[setting_name] = value
        imagename = self._docker_images[image]["imagename"]
        node.setup(imagename, additional_settings=image_settings)

    def reset(self):
        """Resets the servers."""
        log.info("Docker module reset")
        self._nodes.clear()

    def getDockerImagesFromServer(self, server, callback):
        """Gets the Docker images list from a server.

        :param server: server to send the request to
        :param callback: callback for the reply from the server
        """
        server.get("/docker/images", callback)

    @staticmethod
    def getNodeClass(name):
        """
        Returns the object with the corresponding name.

        :param name: object name
        """
        if name in globals():
            return globals()[name]

    @staticmethod
    def classes():
        """Returns all the node classes supported by this module.

        :returns: list of classes
        """
        return [DockerVM]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """
        nodes = []
        for docker_image in self._docker_images.values():
            nodes.append({
                "class": DockerVM.__name__,
                "name": docker_image["imagename"],
                "server": docker_image["server"],
                "symbol": docker_image["symbol"],
                "categories": [docker_image["category"]]
            })
        return nodes

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """
        from .pages.docker_preferences_page import DockerPreferencesPage
        from .pages.docker_vm_preferences_page import DockerVMPreferencesPage

        from gns3.local_config import LocalConfig
        if not LocalConfig.instance().experimental():
            return []

        return [DockerPreferencesPage, DockerVMPreferencesPage]

    @staticmethod
    def instance():
        """Singleton to return only one instance of Docker module.

        :returns: instance of Docker"""
        if not hasattr(Docker, "_instance"):
            Docker._instance = Docker()
        return Docker._instance
