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

import logging
log = logging.getLogger(__name__)


class FrameRelaySwitch(Node):

    """
    Frame-Relay switch.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "frame_relay_switch"

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        # this is an always-on node
        self.setStatus(Node.started)
        self._always_on = True
        self.settings().update({"mappings": {}})

    def create(self, name=None, node_id=None, mappings={}, default_name_format="FR{0}"):
        """
        Creates this Frame Relay switch.

        :param name: name for this switch.
        :param node_id: node identifier on the server
        :param mappings: mappings to be automatically added when creating this Frame relay switch
        """

        params = {}
        if mappings:
            params["mappings"] = mappings
        self._create(name, node_id, params, default_name_format)

    def _createCallback(self, result):
        """
        Callback for create.

        :param result: server response (dict)
        """
        self.settings()["mappings"] = result["mappings"]

    def update(self, new_settings):
        """
        Updates the settings for this Frame Relay switch.

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
        self.settings()["mappings"] = result["mappings"]

    def info(self):
        """
        Returns information about this Frame Relay switch.

        :returns: formatted string
        """

        info = """Frame relay switch {name} is always-on
  Local node ID is {id}
  Server's Node ID is {node_id}
  Hardware is Dynamips emulated simple Frame relay switch
  Switch's server runs on {host}:{port}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           host=self._compute.host(),
           port=self._compute.port())

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "   Port {} is empty\n".format(port.name())
            else:
                port_info += "   Port {name} {description}\n".format(name=port.name(),
                                                                     description=port.description())

            for source, destination in self._settings["mappings"].items():
                source_port, source_dlci = source.split(":")
                destination_port, destination_dlci = destination.split(":")

                if port.name() == source_port or port.name() == destination_port:
                    if port.name() == source_port:
                        dlci1 = source_dlci
                        port = destination_port
                        dlci2 = destination_dlci
                    else:
                        dlci1 = destination_dlci
                        port = source_port
                        dlci2 = source_dlci
                    port_info += "      incoming DLCI {dlci1} is switched to port {port} outgoing DLCI {dlci2}\n".format(dlci1=dlci1,
                                                                                                                         port=port,
                                                                                                                         dlci2=dlci2)
                    break

        return info + port_info

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

        :returns: QWidget object
        """

        from .pages.frame_relay_switch_configuration_page import FrameRelaySwitchConfigurationPage
        return FrameRelaySwitchConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/frame_relay_switch.svg"

    @staticmethod
    def symbolName():

        return "Frame Relay switch"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.switches]

    def __str__(self):

        return "Frame Relay switch"
