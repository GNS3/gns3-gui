# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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


from gns3.node import Node
from .cloud import Cloud

import logging
log = logging.getLogger(__name__)


class Host(Cloud):

    """
    Pseudo host based on a Dynamips Cloud.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    _name_instance_count = 1

    def __init__(self, module, server, project):
        Cloud.__init__(self, module, server, project)

        log.info("host is being created")
        # create an unique id and name
        self._name_id = Host._name_instance_count
        Host._name_instance_count += 1

        name = "Host{}".format(self._name_id)
        self._settings["name"] = name

    def setup(self, name=None, initial_settings={}):
        """
        Setups this host.

        :param name: optional name for this host
        """

        if name:
            self._settings["name"] = name

        if initial_settings:
            self._initial_settings = initial_settings
        else:
            self.created_signal.connect(self._autoConfigure)

        self._server.get("/interfaces", self._setupCallback)

    def _autoConfigure(self, node_id):
        """
        Auto adds all Ethernet and TAP interfaces.

        :param node_id: ignored
        """

        new_settings = {"nios": []}
        for interface in self._settings["interfaces"]:
            if interface["name"].startswith("tap"):
                new_settings["nios"].append("nio_tap:{}".format(interface["name"]))
            else:
                new_settings["nios"].append("nio_gen_eth:{}".format(interface["name"]))

        self.update(new_settings)

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this host.

        :returns: symbol path (or resource).
        """

        return ":/symbols/computer.normal.svg"

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when the host is hovered.

        :returns: symbol path (or resource).
        """

        return ":/symbols/computer.selected.svg"

    @staticmethod
    def symbolName():

        return "Host"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.end_devices]

    def __str__(self):

        return "Host"
