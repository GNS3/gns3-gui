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


from gns3.node import Node

import logging
log = logging.getLogger(__name__)


class Nat(Node):

    """
    Nat node

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "nat"

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        self.setStatus(Node.started)
        self._always_on = True
        self._nat_settings = {}
        self.settings().update(self._nat_settings)

    def info(self):
        """
        Returns information about this nat.

        :returns: formatted string
        """

        info = """NAT node {name} is always-on
  Running on server {host} with port {port}
""".format(name=self.name(),
           host=self.compute().name(),
           port=self.compute().port())

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "   Port {} is empty\n".format(port.name())
            else:
                port_info += "   Port {name} {description}\n".format(name=port.name(),
                                                                     description=port.description())

        return info + port_info

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this nat.

        :returns: symbol path (or resource).
        """

        return ":/symbols/nat.svg"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.end_devices]

    def __str__(self):

        return "Nat"
