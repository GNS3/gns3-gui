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

    @staticmethod
    def isSpecialInterface(interface):

        for special_interface in ("lo", "vmnet", "vboxnet", "docker", "lxcbr", "virbr", "ovs-system", "veth", "fw", "p2p"):
            if interface.lower().startswith(special_interface):
                return True
        return False

    def create(self, name=None, node_id=None, ports=None, default_name_format="Cloud{0}"):
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

    def _createCallback(self, result, error=False, **kwargs):
        """
        Callback for create.

        :param result: server response
        """

        if error:
            log.error("Error while creating cloud: {}".format(result["message"]))
            return

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
                if self.isSpecialInterface(interface["name"]):
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
