# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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

import uuid

from gns3.node import Node
from gns3.ports.port import Port

import logging
log = logging.getLogger(__name__)


class Cloud(Node):

    """
    Cloud node

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "cloud"

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        self.setStatus(Node.started)
        self._always_on = True
        self._interfaces = {}
        self._cloud_settings = {"ports": []}
        self.settings().update(self._cloud_settings)

    def interfaces(self):

        return self._interfaces

    def _isVirtualizationInterface(self, interface):

        for virtualization_interface in ("vmnet", "vboxnet", "docker", "lxcbr", "virbr", "ovs-system"):
            if interface.lower().startswith(virtualization_interface):
                return True
        return False

    def create(self, name=None, node_id=None, ports=None, default_name_format = "Cloud{0}"):
        """
        Creates this cloud.

        :param name: optional name for this cloud
        :param node_id: Node identifier on the server
        :param ports: ports to be automatically added when creating this cloud
        """

        params = {}
        if ports:
            params["ports"] = ports
        self._create(name, node_id, params, default_name_format)

    def _createCallback(self, result):
        """
        Callback for create.

        :param result: server response
        """

        self._interfaces = result["interfaces"].copy()
        if "ports" in result and result["ports"]:
            for port_info in result["ports"]:
                port = Port(port_info["name"])
                port.setAdapterNumber(0)  # adapter number is always 0
                port.setPortNumber(port_info["port_number"])
                port.setStatus(Port.started)
                self._ports.append(port)
                log.debug("port {} has been added".format(port_info["port_number"]))
        else:
            port_number = 1
            settings = {"ports": []}
            for interface in self._interfaces:
                if self._isVirtualizationInterface(interface["name"]):
                    continue
                settings["ports"].append({"name": interface["name"],
                                          "port_number": port_number,
                                          "type": interface["type"],
                                          "interface": interface["name"]})
                port_number += 1
            self.update(settings)

    def update(self, new_settings):
        """
        Updates the settings for this cloud.

        :param new_settings: settings dictionary
        """

        params = {}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value
        if params:
            self._update(params)

    def _updatePort(self, port_name, port_number):

        # update the port if existing
        for port in self._ports:
            if port.portNumber() == port_number:
                port.setName(port_name)
                log.debug("port {} has been updated".format(port_number))
                return

        # otherwise create a new port
        port = Port(port_name)
        port.setAdapterNumber(0)  # adapter number is always 0
        port.setPortNumber(port_number)
        port.setStatus(Port.started)
        self._ports.append(port)
        log.debug("port {} has been added".format(port_number))

    def _updateCallback(self, result):
        """
        Callback for update.

        :param result: server response
        """

        if "ports" in result:
            updated_port_list = []
            # add/update ports
            for port_info in result["ports"]:
                self._updatePort(port_info["name"], port_info["port_number"])
                updated_port_list.append(port_info["port_number"])

            # delete ports
            for port in self._ports.copy():
                if port.isFree() and port.portNumber() not in updated_port_list:
                    self._ports.remove(port)
                    log.debug("port {} has been removed".format(port.portNumber()))

            self._settings["ports"] = result["ports"].copy()

        if "interfaces" in result:
            self._interfaces = result["interfaces"].copy()

    def info(self):
        """
        Returns information about this cloud.

        :returns: formatted string
        """

        info = """Cloud device {name} is always-on
This is a node for external connections
""".format(name=self.name())

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "   Port {} is empty\n".format(port.name())
            else:
                port_info += "   Port {name} {description}\n".format(name=port.name(),
                                                                     description=port.description())

        return info + port_info

    def dump(self):
        """
        Returns a representation of this cloud
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """

        cloud = super().dump()

        # add the ports
        if self._ports:
            ports = cloud["ports"] = []
            for port in self._ports:
                port_info = port.dump()
                if port.portNumber() in self._settings["ports"]:
                    port_info["type"] = self._settings["ports"][port.portNumber()]["type"]
                    if port_info["type"] in ("ethernet", "tap"):
                        port_info["interface"] = self._settings["ports"][port.portNumber()]["interface"]
                    else:
                        # UDP tunnel
                        port_info["lport"] = self._settings["ports"][port.portNumber()]["lport"]
                        port_info["rhost"] = self._settings["ports"][port.portNumber()]["rhost"]
                        port_info["rport"] = self._settings["ports"][port.portNumber()]["rport"]
                ports.append(port_info)
        return cloud

    def load(self, node_info):
        """
        Loads a cloud representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        super().load(node_info)
        properties = node_info["properties"]
        name = properties.pop("name")

        # Clouds do not have an UUID before version 2.0
        node_id = properties.get("node_id", str(uuid.uuid4()))

        ports = []
        # if "ports" in node_info:
        #     for port_info in node_info["ports"]:
        #         ports.append({"port_number": port_info["port_number"],
        #                       "name": port_info["name"],
        #                       "type": port_info.get("type", "access"),
        #                       "vlan": port_info.get("vlan", 1),
        #                       "ethertype": port_info.get("ethertype", "")})

        log.info("Cloud {} is loading".format(name))
        self.create(name, node_id, ports)

    # def _updatePortSettings(self):
    #     """
    #     Updates port settings when loading a topology.
    #     """
    #
    #     self.loaded_signal.disconnect(self._updatePortSettings)
    #
    #     # update the port with the correct IDs
    #     if "ports" in self._node_info:
    #         ports = self._node_info["ports"]
    #         for topology_port in ports:
    #             for port in self._ports:
    #                 if topology_port["name"] == port.name():
    #                     port.setId(topology_port["id"])
    #                     if topology_port["name"].startswith("nio_gen_eth") or topology_port["name"].startswith("nio_linux_eth"):
    #                         # lookup if the interface exists
    #                         available_interface = False
    #                         topology_port_name = topology_port["name"].split(':', 1)[1]
    #                         for interface in self._settings["interfaces"]:
    #                             if interface["name"] == topology_port_name:
    #                                 available_interface = True
    #                                 break
    #                         if not available_interface:
    #                             alternative_interface = self._module.findAlternativeInterface(self, topology_port_name)
    #                             if alternative_interface:
    #                                 if topology_port["name"] in self._settings["nios"]:
    #                                     self._settings["nios"].remove(topology_port["name"])
    #                                 topology_port["name"] = topology_port["name"].replace(topology_port_name, alternative_interface)
    #                                 nio = self._allocateNIO(topology_port["name"])
    #                                 port.setDefaultNio(nio)
    #                                 port.setName(topology_port["name"])
    #                                 self._settings["nios"].append(topology_port["name"])
    #
    #     # now we can set the node as initialized and trigger the created signal
    #     self.setInitialized(True)
    #     log.info("cloud {} has been loaded".format(self.name()))
    #     self.created_signal.emit(self.id())
    #     self._module.addNode(self)
    #     self._loading = False
    #     self._node_info = None

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

        :returns: QWidget object
        """

        from .pages.cloud_configuration_page import CloudConfigurationPage
        return CloudConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this cloud.

        :returns: symbol path (or resource).
        """

        return ":/symbols/cloud.svg"

    @staticmethod
    def symbolName():

        return "Cloud"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.end_devices]

    def __str__(self):

        return "Cloud"
