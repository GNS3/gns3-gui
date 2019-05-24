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

"""
Docker module implementation.
"""

from gns3.local_config import LocalConfig
from gns3.controller import Controller
from gns3.template_manager import TemplateManager
from gns3.template import Template

from ..module import Module
from .docker_vm import DockerVM
from .settings import DOCKER_SETTINGS, DOCKER_CONTAINER_SETTINGS

import logging
log = logging.getLogger(__name__)


class Docker(Module):
    """
    Docker module.
    """

    def __init__(self):
        super().__init__()
        self._loadSettings()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        local_config = LocalConfig.instance()
        self._settings = local_config.loadSectionSettings(self.__class__.__name__, DOCKER_SETTINGS)

        # migrate container settings to the controller (templates are managed on server side starting with version 2.0)
        Controller.instance().connected_signal.connect(self._migrateOldContainers)

    def _migrateOldContainers(self):
        """
        Migrate local container settings to the controller.
        """

        if self._settings.get("containers"):
            templates = []
            for container in self._settings.get("containers"):
                container_settings = DOCKER_CONTAINER_SETTINGS.copy()
                container_settings.update(container)
                templates.append(Template(container_settings))
            TemplateManager.instance().updateList(templates)
            self._settings["containers"] = []
            self._saveSettings()

    @staticmethod
    def configurationPage():
        """
        Returns the configuration page for this module.

        :returns: QWidget object
        """

        from .pages.docker_vm_configuration_page import DockerVMConfigurationPage
        return DockerVMConfigurationPage

    def getDockerImagesFromServer(self, compute_id, callback):
        """
        Gets the Docker images list from a server.

        :param server: server to send the request to
        :param callback: callback for the reply from the server
        """

        Controller.instance().getCompute("/docker/images", compute_id, callback)

    @staticmethod
    def getNodeClass(node_type, platform=None):
        """
        Returns the class corresponding to node type.

        :param node_type: node type (string)
        :param platform: not used

        :returns: class or None
        """

        if node_type == "docker":
            return DockerVM
        return None

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """
        return [DockerVM]

    @staticmethod
    def preferencePages():
        """
        Returns the preference pages for this module.

        :returns: QWidget object list
        """

        from .pages.docker_preferences_page import DockerPreferencesPage
        from .pages.docker_vm_preferences_page import DockerVMPreferencesPage

        return [DockerPreferencesPage, DockerVMPreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of Docker module.

        :returns: instance of Docker
        """

        if not hasattr(Docker, "_instance"):
            Docker._instance = Docker()
        return Docker._instance

    def __str__(self):
        """
        Returns the module name.
        """

        return "docker"
