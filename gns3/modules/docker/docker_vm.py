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
from gns3.ports.ethernet_port import EthernetPort
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

    def _addAdapters(self, adapters):
        """Adds adapters.

        :param adapters: number of adapters
        """
        for adapter_number in range(0, adapters):
            adapter_name = EthernetPort.longNameType() + str(adapter_number)
            short_name = EthernetPort.shortNameType() + str(adapter_number)
            new_port = EthernetPort(adapter_name)
            new_port.setShortName(short_name)
            new_port.setAdapterNumber(adapter_number)
            new_port.setPortNumber(0)
            new_port.setHotPluggable(False)
            self._ports.append(new_port)
            log.debug("Adapter {} has been added".format(adapter_name))

    def setup(self, image, name=None, base_name=None, node_id=None, additional_settings={}, default_name_format="{name}-{0}"):
        """Sets up this Docker container.

        :param image: image name
        :param name: optional name
        :param additional_settings: additional settings for this VM
        """

        #self._settings["image"] = image
        params = {
            "image": image,
            "adapters": self._settings["adapters"]
        }
        params.update(additional_settings)
        default_name_format = default_name_format.replace('{name}', base_name)
        self._create(name, node_id, params, default_name_format)

    def _setupCallback(self, result):
        """Callback for Docker container setup.

        :param result: server response
        """

        self._addAdapters(self._settings.get("adapters", 0))

    def dump(self):
        """
        Returns a representation of this Docker VM instance.
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """
        docker = super().dump()

        # add the properties
        for name, value in self._settings.items():
            if value is not None and value != "":
                docker["properties"][name] = value

        return docker

    def update(self, new_settings):
        """
        Updates the settings for this VPCS device.

        :param new_settings: settings dictionary
        """

        params = {}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        if params:
            self._update(params)

    def _updateCallback(self, result):
        """
        Callback for update.

        :param result: server response
        """

        nb_adapters_changed = False
        for name, value in result.items():
            if name in self._settings and self._settings[name] != value:
                log.info("{}: updating {} from '{}' to '{}'".format(self.name(), name, self._settings[name], value))
                if name == "name":
                    # update the node name
                    self.updateAllocatedName(value)
                if name == "adapters":
                    nb_adapters_changed = True
                self._settings[name] = value

        if nb_adapters_changed:
            log.debug("number of adapters has changed to {}".format(self._settings["adapters"]))
            # TODO: dynamically add/remove adapters
            self._ports.clear()
            self._addAdapters(self._settings["adapters"])

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

    def load(self, node_info):
        """
        Loads a Docker representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        super().load(node_info)

        settings = node_info["properties"]
        name = settings.pop("name")
        image = settings.pop("image")
        node_id = node_info.get("node_id")
        if not node_id:
            # for backward compatibility
            node_id = node_info.get("vm_id")

        log.info("Docker container {} is loading".format(name))
        self.setup(image, name=name, node_id=node_id, additional_settings=settings)

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

    def networkInterfacesPath(self):
        """
        Return path of the /etc/network/interfaces
        """
        return "/project-files/docker/{}/etc/network/interfaces".format(self._node_id)

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
