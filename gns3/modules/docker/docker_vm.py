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

        docker_vm_settings = {"image": "",
                              "usage": "",
                              "adapters": DOCKER_CONTAINER_SETTINGS["adapters"],
                              "custom_adapters": DOCKER_CONTAINER_SETTINGS["custom_adapters"],
                              "start_command": DOCKER_CONTAINER_SETTINGS["start_command"],
                              "environment": DOCKER_CONTAINER_SETTINGS["environment"],
                              "aux": None,
                              "console_type": DOCKER_CONTAINER_SETTINGS["console_type"],
                              "console_auto_start": DOCKER_CONTAINER_SETTINGS["console_auto_start"],
                              "console_resolution": DOCKER_CONTAINER_SETTINGS["console_resolution"],
                              "console_http_port": DOCKER_CONTAINER_SETTINGS["console_http_port"],
                              "console_http_path": DOCKER_CONTAINER_SETTINGS["console_http_path"],
                              "extra_hosts": DOCKER_CONTAINER_SETTINGS["extra_hosts"],
                              "extra_volumes": DOCKER_CONTAINER_SETTINGS["extra_volumes"]}

        self.settings().update(docker_vm_settings)

    def info(self):
        """
        Returns information about this Docker container.

        :returns: formatted string
        """

        info = """Docker container {name} is {state}
  Running on server {host} with port {port}
  Local ID is {id} and server ID is {node_id}
  Docker image is "{image}"
  Console is on port {console} and type is {console_type}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           state=self.state(),
           host=self.compute().name(),
           port=self.compute().port(),
           console=self._settings["console"],
           console_type=self._settings["console_type"],
           image=self._settings["image"])

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "     {port_name} is empty\n".format(
                    port_name=port.name())
            else:
                port_info += "     {port_name} {port_description}\n".format(
                    port_name=port.name(),
                    port_description=port.description())

        usage = "\n" + self._settings.get("usage")
        return info + port_info + usage

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
        """
        Returns the configuration page widget to be used by the node configurator.

        :returns: QWidget object
        """
        from .pages.docker_vm_configuration_page import DockerVMConfigurationPage
        return DockerVMConfigurationPage

    @staticmethod
    def validateHostname(hostname):
        """
        Checks if the hostname is valid.

        :param hostname: hostname to check

        :returns: boolean
        """

        return DockerVM.isValidRfc1123Hostname(hostname)

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """
        return ":/symbols/docker_guest.svg"

    def configFiles(self):
        """
        Returns the path of the /etc/network/interfaces
        """
        return ["etc/network/interfaces"]

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """
        return [Node.end_devices]

    def __str__(self):
        return "Docker container"
