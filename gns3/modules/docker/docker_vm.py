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
Docker VM implementation.
"""

from gns3.node import Node
from .settings import DOCKER_CONTAINER_SETTINGS

import logging
log = logging.getLogger(__name__)


class DockerVM(Node):
    """
    Docker Image.

    :param module: parent module for this node
    :param server: GNS3 server instance
    """
    URL_PREFIX = "docker"

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        log.info("Docker VM is being created")

        docker_vm_settings = {"image": "",
                              "adapters": DOCKER_CONTAINER_SETTINGS["adapters"],
                              "start_command": DOCKER_CONTAINER_SETTINGS["start_command"],
                              "environment": DOCKER_CONTAINER_SETTINGS["environment"],
                              "console": None,
                              "console_host": None,
                              "aux": None,
                              "console_type": DOCKER_CONTAINER_SETTINGS["console_type"],
                              "console_resolution": DOCKER_CONTAINER_SETTINGS["console_resolution"],
                              "console_http_port": DOCKER_CONTAINER_SETTINGS["console_http_port"],
                              "console_http_path": DOCKER_CONTAINER_SETTINGS["console_http_path"]}

        self.settings().update(docker_vm_settings)

    def create(self, image, name=None, base_name=None, node_id=None, additional_settings={}, default_name_format="{name}-{0}"):
        """Creates this Docker container.

        :param image: image name
        :param name: optional name
        :param additional_settings: additional settings for this VM
        """

        params = {
            "image": image,
            "adapters": self._settings["adapters"]
        }
        params.update(additional_settings)
        if base_name:
            default_name_format = default_name_format.replace('{name}', base_name)
        self._create(name=name, node_id=node_id, params=params, default_name_format=default_name_format, timeout=None)

    def _createCallback(self, result):
        """
        Callback for Docker container creating.

        :param result: server response
        """
        pass

    def update(self, new_settings):
        """
        Updates the settings for this Docker container.

        :param new_settings: settings dictionary
        """

        params = {}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value
        if params:
            self._update(params)

    def info(self):
        """Returns information about this Docker container.

        :returns: formatted string
        :rtype: string
        """
        if self.status() == Node.started:
            state = "started"
        else:
            state = "stopped"

        info = """Docker container {name} is {state}
  Node ID is {id}, server's Docker container ID is {node_id}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           state=state)

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "     {port_name} is empty\n".format(
                    port_name=port.name())
            else:
                port_info += "     {port_name} {port_description}\n".format(
                    port_name=port.name(),
                    port_description=port.description())

        return info + port_info

    def console(self):
        """
        Returns the console port for this Docker VM instance.

        :returns: port (integer)
        """
        return self._settings["console"]

    def consoleHttpPath(self):
        """
        Returns the path of the web ui

        :returns: string
        """
        return self._settings["console_http_path"]

    def auxConsole(self):
        """
        Returns the console port for this Docker VM instance.

        :returns: port (integer)
        """
        return self._settings["aux"]

    def configPage(self):
        """Returns the configuration page widget to be used by the node configurator.

        :returns: QWidget object
        """
        from .pages.docker_vm_configuration_page import DockerVMConfigurationPage
        return DockerVMConfigurationPage

    @staticmethod
    def defaultSymbol():
        """Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """
        return ":/symbols/docker_guest.svg"

    def configFiles(self):
        """
        Return path of the /etc/network/interfaces
        """
        return ["etc/network/interfaces"]

    @staticmethod
    def symbolName():
        return "Docker container"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """
        return [Node.end_devices]

    def __str__(self):
        return "Docker container"
