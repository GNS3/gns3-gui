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
from ...controller import Controller

import logging
log = logging.getLogger(__name__)


class Docker(Module):
    """Docker module."""

    def __init__(self):
        super().__init__()

        self._settings = {}
        self._docker_containers = {}
        self._nodes = []

        # load the settings
        self._loadSettings()

    def configChangedSlot(self):
        # load the settings
        self._loadSettings()

    def _saveSettings(self):
        """Saves the settings to the persistent settings file."""
        LocalConfig.instance().saveSectionSettings(
            self.__class__.__name__, self._settings)

    def _loadSettings(self):
        """Loads the settings from the persistent settings file."""
        local_config = LocalConfig.instance()
        self._settings = local_config.loadSectionSettings(
            self.__class__.__name__, DOCKER_SETTINGS)

        self._docker_containers = {}
        if "containers" in self._settings:
            for image in self._settings["containers"]:
                name = image.get("name")
                server = image.get("server")
                key = "{server}:{name}".format(server=server, name=name)
                if key in self._docker_containers or not name or not server:
                    continue
                container_settings = DOCKER_CONTAINER_SETTINGS.copy()
                container_settings.update(image)
                self._docker_containers[key] = container_settings

    def _saveDockerImages(self):
        """Saves the Docker containers to the persistent settings file."""

        self._settings["containers"] = list(self._docker_containers.values())
        self._saveSettings()

    def VMs(self):
        """
        Returns Docker images settings.

        :returns: Docker images settings
        :rtype: dict
        """

        return self._docker_containers

    def setVMs(self, new_docker_containers):
        """Sets Docker image settings.

        :param new_iou_images: Docker images settings (dictionary)
        """
        self._docker_containers = new_docker_containers.copy()
        self._saveDockerImages()

    @staticmethod
    def vmConfigurationPage():
        from .pages.docker_vm_configuration_page import DockerVMConfigurationPage
        return DockerVMConfigurationPage

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

    def instantiateNode(self, node_class, server, project):
        """
        Instantiate a new node.

        :param node_class: Node object
        :param server: HTTPClient instance
        """
        log.info("instantiating node {}".format(node_class))
        # create an instance of the node class
        return node_class(self, server, project)

    def createNode(self, node, node_name):
        """
        Creates a node.

        :param node: Node instance
        :param node_name: Node name
        """
        log.info("creating node {} with id {}".format(node, node.id()))

        image = None
        if node_name:
            for image_key, info in self._docker_containers.items():
                if node_name == info["name"]:
                    image = image_key
        if not image:
            selected_images = []
            for image, info in self._docker_containers.items():
                if info["server"] == node.compute().id():
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
        for setting_name, value in self._docker_containers[image].items():
            if setting_name in node.settings() and value != "" and value is not None:
                if setting_name not in ['name', 'image']:
                    image_settings[setting_name] = value

        default_name_format = DOCKER_CONTAINER_SETTINGS["default_name_format"]
        if self._docker_containers[image]["default_name_format"]:
            default_name_format = self._docker_containers[image]["default_name_format"]

        image = self._docker_containers[image]["image"]
        node.create(image, base_name=node_name, additional_settings=image_settings, default_name_format=default_name_format)

    def reset(self):
        """Resets the servers."""
        self._nodes.clear()

    def getDockerImagesFromServer(self, compute_id, callback):
        """Gets the Docker images list from a server.

        :param server: server to send the request to
        :param callback: callback for the reply from the server
        """
        Controller.instance().getCompute("/docker/images", compute_id, callback)

    @staticmethod
    def getNodeClass(name):
        """
        Returns the object with the corresponding name.

        :param name: object name
        """
        if name in globals():
            return globals()[name]

    @staticmethod
    def getNodeType(name, platform=None):
        if name == "docker":
            return DockerVM
        return None

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
        for docker_image in self._docker_containers.values():
            nodes.append({
                "class": DockerVM.__name__,
                "name": docker_image["name"],
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

        return [DockerPreferencesPage, DockerVMPreferencesPage]

    @staticmethod
    def instance():
        """Singleton to return only one instance of Docker module.

        :returns: instance of Docker"""
        if not hasattr(Docker, "_instance"):
            Docker._instance = Docker()
        return Docker._instance
