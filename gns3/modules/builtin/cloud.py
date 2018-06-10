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
from .settings import CLOUD_SETTINGS

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
        # this is an always-on node
        self.setStatus(Node.started)
        self._always_on = True
        self._interfaces = {}
        self._cloud_settings = {"ports_mapping": [],
                                "remote_console_host": CLOUD_SETTINGS["remote_console_host"],
                                "remote_console_port": CLOUD_SETTINGS["remote_console_port"],
                                "remote_console_type": CLOUD_SETTINGS["remote_console_type"],
                                "remote_console_http_path": CLOUD_SETTINGS["remote_console_http_path"]
                                }
        self.settings().update(self._cloud_settings)

    def interfaces(self):

        return self._interfaces

    def _createCallback(self, result):
        """
        Callback for create.

        :param result: server response
        """

        if "interfaces" in result:
            self._interfaces = result["interfaces"].copy()

    def _updateCallback(self, result):
        """
        Callback for update.

        :param result: server response
        """

        if "interfaces" in result:
            self._interfaces = result["interfaces"].copy()

    def consoleType(self):
        """
        Get the console type.
        """

        return self.settings()["remote_console_type"]

    def consoleHost(self):
        """
        Returns the host to connect to the console.

        :returns: host (string)
        """

        return self.settings()["remote_console_host"]

    def console(self):
        """
        Returns the console port number of this node

        :returns: port number
        """

        return self.settings()["remote_console_port"]

    def consoleHttpPath(self):
        """
        Returns the path of the web ui

        :returns: string
        """
        return self._settings["remote_console_http_path"]

    def info(self):
        """
        Returns information about this cloud.

        :returns: formatted string
        """

        info = """Cloud {name} is always-on
  Running on server {host} with port {port}
""".format(name=self.name(),
           host=self.compute().name(),
           port=self.compute().port())

        if self.consoleType() != "none":
            info += """   Remote console is {console_host} on port {console} and type is {console_type}
""".format(console_host=self.consoleHost(),
           console=self.console(),
           console_type=self.consoleType())
            if self.consoleType() in ("http", "https"):
                info += """   Remote console HTTP path is '{console_http_path}'
""".format(console_http_path=self.consoleHttpPath())
        else:
            info += """   No remote console configured
"""

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
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.end_devices]

    def __str__(self):

        return "Cloud"
