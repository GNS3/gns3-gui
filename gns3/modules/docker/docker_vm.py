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

from gns3.vm import VM
from gns3.node import Node
from gns3.ports.port import Port
from gns3.ports.ethernet_port import EthernetPort
from gns3.nios.nio_generic_ethernet import NIOGenericEthernet
from gns3.nios.nio_linux_ethernet import NIOLinuxEthernet
from gns3.nios.nio_udp import NIOUDP
from .settings import DOCKER_CONTAINER_SETTINGS

import logging
import re
log = logging.getLogger(__name__)


class DockerVM(VM):
    """
    Docker Image.

    :param module: parent module for this node
    :param server: GNS3 server instance
    """
    URL_PREFIX = "docker"

    def __init__(self, module, server, project):
        super().__init__(module, server, project)

        log.info("Docker image instance is being created")
        self._settings = {
            "name": "",
            "image": "",
            "adapters": DOCKER_CONTAINER_SETTINGS["adapters"],
            "start_command": DOCKER_CONTAINER_SETTINGS["start_command"],
            "environment": DOCKER_CONTAINER_SETTINGS["environment"],
            "console": None,
            "aux": None,
            "console_type": DOCKER_CONTAINER_SETTINGS["console_type"],
            "console_resolution": DOCKER_CONTAINER_SETTINGS["console_resolution"],
            "console_http_port": DOCKER_CONTAINER_SETTINGS["console_http_port"],
            "console_http_path": DOCKER_CONTAINER_SETTINGS["console_http_path"]
        }

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
            new_port.setPacketCaptureSupported(True)
            self._ports.append(new_port)
            log.debug("Adapter {} has been added".format(adapter_name))

    def setup(self, image, name=None, base_name=None, vm_id=None, additional_settings={}, default_name_format="{name}-{0}"):
        """Sets up this Docker container.

        :param image: image name
        :param name: optional name
        :param additional_settings: additional settings for this VM
        """
        # let's create a unique name if none has been chosen
        if not name:
            name = self.allocateName(default_name_format.replace('{name}', base_name))

        if not name:
            self.error_signal.emit(self.id(), "could not allocate a name for this container")
            return

        self.setName(name)
        self._settings["name"] = name
        self._settings["image"] = image
        params = {
            "name": name,
            "image": image,
            "adapters": self._settings["adapters"]
        }
        if vm_id:
            params["vm_id"] = vm_id
        params.update(additional_settings)

        self.httpPost("/docker/vms", self._setupCallback, body=params, timeout=None)

    def _setupCallback(self, result, error=False, **kwargs):
        """Callback for Docker container setup.

        :param result: server response
        :param error: indicates an error (boolean)
        """
        if not super()._setupCallback(result, error=error, **kwargs):
            return

        self._addAdapters(self._settings.get("adapters", 0))

        if self._loading:
            self.loaded_signal.emit()
        else:
            self.setInitialized(True)
            log.info(
                "Docker container {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)

    def _updateCallback(self, result, error=False, **kwargs):
        """
        Callback for update.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            return

        updated = False
        nb_adapters_changed = False
        for name, value in result.items():
            if name in self._settings and self._settings[name] != value:
                log.info("{}: updating {} from '{}' to '{}'".format(self.name(), name, self._settings[name], value))
                updated = True
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

        if updated:
            log.info("Docker VM {} has been updated".format(self.name()))
            self.updated_signal.emit()

    def update(self, new_settings):
        """
        Updates the settings for this VPCS device.

        :param new_settings: settings dictionary
        """

        if "name" in new_settings and new_settings["name"] != self.name() and self.hasAllocatedName(new_settings["name"]):
            self.error_signal.emit(self.id(), 'Name "{}" is already used by another node'.format(new_settings["name"]))
            return

        params = {}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        log.debug("{} is updating settings: {}".format(self.name(), params))
        self.httpPut("/docker/vms/{vm_id}".format(project_id=self._project.id(), vm_id=self._vm_id), self._updateCallback, body=params)

    def suspend(self):
        """Suspends this Docker container."""
        if self.status() == Node.suspended:
            log.debug("{} is already suspended".format(self.name()))
            return
        log.debug("{} is being suspended".format(self.name()))
        self.httpPost("/docker/vms/{id}/suspend".format(
            id=self._vm_id), self._suspendCallback)

    def _suspendCallback(self, result, error=False, **kwargs):
        """Callback for container suspend.

        :param result: server response
        :param error: indicates an error (boolean)
        """
        if error:
            log.error("error while suspending {}: {}".format(
                self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{} has suspended".format(self.name()))
            self.setStatus(Node.suspended)
            for port in self._ports:
                # set ports as suspended
                port.setStatus(Port.suspended)
            self.suspended_signal.emit()

    def dump(self):
        """
        Returns a representation of this Docker VM instance.
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """
        docker = super().dump()
        docker["id"] = self.id()
        docker["vm_id"] = self._vm_id

        # add the properties
        for name, value in self._settings.items():
            if value is not None and value != "":
                docker["properties"][name] = value

        # add the ports
        if self._ports:
            ports = docker["ports"] = []
            for port in self._ports:
                ports.append(port.dump())
        return docker

    def info(self):
        """Returns information about this Docker container.

        :returns: formated string
        :rtype: string
        """
        if self.status() == Node.started:
            state = "started"
        else:
            state = "stopped"

        info = """Docker container {name} is {state}
  Node ID is {id}, server's Docker container ID is {vm_id}
""".format(name=self.name(),
           id=self.id(),
           vm_id=self._vm_id,
           state=state
           )

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
        vm_id = node_info["vm_id"]
        log.info("Docker container {} is loading".format(name))
        self.setup(image, name=name, vm_id=vm_id, additional_settings=settings)

    def _updatePortSettings(self):
        """
        Updates port settings when loading a topology.
        """

        self.loaded_signal.disconnect(self._updatePortSettings)

        # assign the correct names and IDs to the ports
        if "ports" in self._node_info:
            ports = self._node_info["ports"]
            for topology_port in ports:
                for port in self._ports:
                    adapter_number = topology_port.get("adapter_number")
                    if adapter_number == port.adapterNumber():
                        port.setName(topology_port["name"])
                        port.setId(topology_port["id"])

        # now we can set the node as initialized and trigger the created signal
        self.setInitialized(True)
        log.info("Docker container {} has been loaded".format(self.name()))
        self.created_signal.emit(self.id())
        self._module.addNode(self)
        self._loading = False
        self._node_info = None

    def name(self):
        """
        Returns the name of this Docker container.

        :returns: name (string)
        """
        return self._settings["name"]

    def settings(self):
        """
        Returns all settings of this Docker container.

        :returns: settings
        :rtype: dict
        """
        return self._settings

    def ports(self):
        """
        Returns all the ports for this Docker VM instance.

        :returns: list of Port instances
        """
        return self._ports

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
        return "/project-files/docker/{}/etc/network/interfaces".format(self._vm_id)

    @staticmethod
    def symbolName():
        return "Docker container"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """
        return [Node.end_devices]

    def __str__(self):
        return "Docker container"


