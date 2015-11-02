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
            "imagename": "",
            "console": DOCKER_CONTAINER_SETTINGS["console"],
            "adapters": DOCKER_CONTAINER_SETTINGS["adapters"],
            "adapter_type": DOCKER_CONTAINER_SETTINGS["adapter_type"],
            "startcmd": DOCKER_CONTAINER_SETTINGS["startcmd"]
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
            self._ports.append(new_port)
            log.debug("Adapter {} has been added".format(adapter_name))

    def setup(self, imagename, name=None, vm_id=None, additional_settings={}):
        """Sets up this Docker container.

        :param imagename: image name
        :param name: optional name
        :param additional_settings: additional settings for this VM
        """
        # let's create a unique name if none has been chosen
        if not name:
            name = imagename.replace(":", "-").replace("/", "-")
            name = self.allocateName(name + "-")
            self.setName(name)

        if not name:
            self.error_signal.emit(
                self.id(), "could not allocate a name for this container")
            return

        self._settings["name"] = name
        params = {
            "name": name,
            "imagename": imagename
        }
        if vm_id:
            params["id"] = vm_id
        params.update(additional_settings)
        self.httpPost("/docker/images", self._setupCallback, body=params)

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
        Updates the settings for this container.

        :param new_settings: settings dictionary
        """

        updated = False
        if "nios" in new_settings:
            nios = new_settings["nios"]
            # add ports
            for nio in nios:
                if nio in self._settings["nios"]:
                    # port already created for this NIO
                    continue
                nio_object = None
                if nio.lower().startswith("nio_udp"):
                    nio_object = self._createNIOUDP(nio)
                    print("nio_object")
                if nio_object is None:
                    log.error("Could not create NIO object from {}".format(nio))
                    continue
                port = Port(nio, nio_object, stub=True)
                port.setStatus(Port.started)
                self._ports.append(port)
                updated = True
                log.debug("port {} has been added".format(nio))

            # delete ports
            for nio in self._settings["nios"]:
                if nio not in nios:
                    for port in self._ports.copy():
                        if port.name() == nio:
                            self._ports.remove(port)
                            updated = True
                            log.debug("port {} has been deleted".format(nio))
                            break

            self._settings["nios"] = new_settings["nios"].copy()

        if "name" in new_settings and new_settings["name"] != self.name():
            self._settings["name"] = new_settings["name"]
            updated = True

        if updated:
            log.info("cloud {} has been updated".format(self.name()))
            self.updated_signal.emit()

    def suspend(self):
        """Suspends this Docker container."""
        if self.status() == Node.suspended:
            log.debug("{} is already suspended".format(self.name()))
            return
        log.debug("{} is being suspended".format(self.name()))
        self.httpPost("/docker/images/{id}/suspend".format(
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

    def reload(self):
        """Reloads this Docker container."""
        log.debug("{} is being reloaded".format(self.name()))
        self.httpPost("/docker/images/{id}/reload".format(
            id=self._vm_id), self._reloadCallback)

    def _reloadCallback(self, result, error=False, **kwargs):
        """Callback for Docker container reload.

        :param result: server response
        :param error: indicates an error (boolean)
        """
        if error:
            log.error("error while reloading {}: {}".format(
                self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{} has reloaded".format(self.name()))

    def dump(self):
        """
        Returns a representation of this Docker VM instance.
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """
        container = {
            "id": self.id(),
            "vm_id": self._vm_id,
            "type": self.__class__.__name__,
            "description": str(self),
            "properties": {},
            "server_id": self._server.id()
        }

        # add the properties
        for name, value in self._settings.items():
            if value is not None and value != "":
                container["properties"][name] = value

        # add the ports
        if self._ports:
            ports = container["ports"] = []
            for port in self._ports:
                ports.append(port.dump())
        return container

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
        Loads a cloud representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """
        settings = node_info["properties"]
        name = settings.pop("name")
        self.updated_signal.connect(self._updatePortSettings)
        log.info("Docker container {} is loading".format(name))
        self._node_info = node_info
        self.setup(name, settings)

    def _updatePortSettings(self):
        """
        Updates port settings when loading a topology.
        """

        self.updated_signal.disconnect(self._updatePortSettings)
        # update the port with the correct IDs
        if "ports" in self._node_info:
            ports = self._node_info["ports"]
            for topology_port in ports:
                for port in self._ports:
                    if topology_port["name"] == port.name():
                        port.setId(topology_port["id"])
                        if topology_port["name"].startswith("nio_gen_eth") or topology_port["name"].startswith("nio_linux_eth"):
                            # lookup if the interface exists
                            available_interface = False
                            topology_port_name = topology_port["name"].split(':', 1)[1]
                            for interface in self._settings["interfaces"]:
                                if interface["name"] == topology_port_name:
                                    available_interface = True
                                    break
                            if not available_interface:
                                alternative_interface = self._module.findAlternativeInterface(self, topology_port_name)
                                if alternative_interface:
                                    if topology_port["name"] in self._settings["nios"]:
                                        self._settings["nios"].remove(topology_port["name"])
                                    topology_port["name"] = topology_port["name"].replace(topology_port_name, alternative_interface)
                                    port.setName(topology_port["name"])
                                    self._settings["nios"].append(topology_port["name"])

        log.info("cloud {} has been created".format(self.name()))
        self.setInitialized(True)
        self.created_signal.emit(self.id())

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

    def shellExecCmd(self):
        """Returns the execution command.

        :returns: execution cmd for shell console
        :rtype: string
        """
        return "docker exec -it {} bash".format(self._settings['name'])

    def console(self):
        """
        Returns the console port for this Docker VM instance.

        :returns: port (integer)
        """
        return self._settings["console"]

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
        return ":/symbols/docker_guest.normal.svg"

    @staticmethod
    def hoverSymbol():
        """Returns the symbol to use when this node is hovered.

        :returns: symbol path (or resource).
        """
        return ":/symbols/docker_guest.selected.svg"

    @staticmethod
    def symbolName():
        return "Docker image"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """
        return [Node.end_devices]

    def __str__(self):
        return "Docker image"
