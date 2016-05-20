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


import re
import uuid

from gns3.node import Node
from gns3.ports.atm_port import ATMPort

import logging
log = logging.getLogger(__name__)


class ATMSwitch(Node):

    """
    ATM switch.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """
    URL_PREFIX = "atm_switch"

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        self.setStatus(Node.started)  # this is an always-on node
        self._ports = []
        self._settings = {"name": "",
                          "mappings": {}}

    def isAlwaysOn(self):
        """
        Indicates that this node is always running and cannot be stopped.

        :returns: boolean
        """

        return True

    def _updatePortsFromMappings(self, mappings):

        ports_to_create = []
        for source, destination in mappings.items():
            source_port = source.split(":")[0]
            destination_port = destination.split(":")[0]
            if source_port not in ports_to_create:
                ports_to_create.append(source_port)
            if destination_port not in ports_to_create:
                ports_to_create.append(destination_port)

        for port in self._ports.copy():
            if port.isFree():
                self._ports.remove(port)
                log.debug("port {} has been removed".format(port.name()))
            else:
                ports_to_create.remove(port.name())

        for port_name in ports_to_create:
            port = ATMPort(port_name)
            port.setAdapterNumber(0)  # adapter number is always 0
            port.setPortNumber(int(port_name))
            port.setStatus(ATMPort.started)
            self._ports.append(port)
            log.debug("port {} has been added".format(port_name))

    def setup(self, name=None, node_id=None, mappings={}, default_name_format="ATM{0}"):
        """
        Setups this ATM switch.

        :param name: optional name for this switch.
        :param node_id: Node identifier on the server
        :param mappings: mappings to be automatically added when creating this ATM switch
        """

        # let's create a unique name if none has been chosen
        if not name:
            name = self.allocateName(default_name_format)

        if not name:
            self.error_signal.emit(self.id(), "could not allocate a name for this ATM switch")
            return

        self._settings["name"] = name
        params = {"name": name}
        if node_id:
            params["node_id"] = node_id
        if mappings:
            params["mappings"] = mappings
        self._create(params)

    def _setupCallback(self, result, error=False, **kwargs):
        """
        Callback for setup.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if not super()._setupCallback(result, error=error, **kwargs):
            return

        if "mappings" in result:
            self._updatePortsFromMappings(result["mappings"])

        if self._loading:
            self.loaded_signal.emit()
        else:
            self.setInitialized(True)
            log.info("ATM switch instance {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)

    def update(self, new_settings):
        """
        Updates the settings for this ATM switch.

        :param new_settings: settings dictionary
        """

        params = {}
        if "mappings" in new_settings:
            params["mappings"] = new_settings["mappings"]

        if "name" in new_settings and new_settings["name"] != self.name():
            if self.hasAllocatedName(new_settings["name"]):
                self.error_signal.emit(self.id(), 'Name "{}" is already used by another node'.format(new_settings["name"]))
                return
            params["name"] = new_settings["name"]

        if params:
            self._update(params)

    def updateCallback(self, result, error=False, **kwargs):
        """
        Callback for update.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if not super().updateCallback(result, error=error, **kwargs):
            return False

        if error:
            log.error("error while updating {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:

            if "mappings" in result:
                self._updatePortsFromMappings(result["mappings"])
                self._settings["mappings"] = result["mappings"].copy()

            if "name" in result:
                self._settings["name"] = result["name"]
                self.updateAllocatedName(result["name"])
            log.info("{} has been updated".format(self.name()))
            self.updated_signal.emit()

    def info(self):
        """
        Returns information about this ATM switch.

        :returns: formatted string
        """

        info = """ATM switch {name} is always-on
  Local node ID is {id}
  Server's Node ID is {node_id}
  Hardware is Dynamips emulated simple ATM switch
  Switch's server runs on {host}:{port}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           host=self._server.host(),
           port=self._server.port())

        port_info = ""
        mapping = re.compile(r"""^([0-9]*):([0-9]*):([0-9]*)$""")
        for port in self._ports:
            if port.isFree():
                port_info += "   Port {} is empty\n".format(port.name())
            else:
                port_info += "   Port {name} {description}\n".format(name=port.name(),
                                                                     description=port.description())

            for source, destination in self._settings["mappings"].items():
                match_source_mapping = mapping.search(source)
                match_destination_mapping = mapping.search(destination)
                if match_source_mapping and match_destination_mapping:
                    source_port, source_vpi, source_vci = match_source_mapping.group(1, 2, 3)
                    destination_port, destination_vpi, destination_vci = match_destination_mapping.group(1, 2, 3)
                else:
                    source_port, source_vpi = source.split(":")
                    destination_port, destination_vpi = destination.split(":")
                    source_vci = destination_vci = 0

                if port.name() == source_port or port.name() == destination_port:
                    if port.name() == source_port:
                        vpi1 = source_vpi
                        vci1 = source_vci
                        port = destination_port
                        vci2 = destination_vci
                        vpi2 = destination_vpi
                    else:
                        vpi1 = destination_vpi
                        vci1 = destination_vci
                        port = source_port
                        vci2 = source_vci
                        vpi2 = source_vpi

                    if vci1 and vci2:
                        port_info += "      incoming VPI {vpi1} and VCI {vci1} is switched to port {port} outgoing VPI {vpi2} and VCI {vci2}\n".format(vpi1=vpi1,
                                                                                                                                                       vci1=vci1,
                                                                                                                                                       port=port,
                                                                                                                                                       vpi2=vpi2,
                                                                                                                                                       vci2=vci2)
                    else:
                        port_info += "      incoming VPI {vpi1} is switched to port {port} outgoing VPI {vpi2}\n".format(vpi1=vpi1,
                                                                                                                         port=port,
                                                                                                                         vpi2=vpi2)

                    break

        return info + port_info

    def dump(self):
        """
        Returns a representation of this ATM switch
        (to be saved in a topology file).

        :returns: dictionary
        """

        atmsw = super().dump()
        atmsw["properties"]["name"] = self.name()

        if self._settings["mappings"]:
            atmsw["properties"]["mappings"] = self._settings["mappings"]

        return atmsw

    def load(self, node_info):
        """
        Loads an ATM switch representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        settings = node_info["properties"]
        name = settings.pop("name")

        # ATM switches do not have an UUID before version 2.0
        node_id = settings.get("node_id", str(uuid.uuid4()))

        mappings = {}
        if "mappings" in settings:
            mappings = settings["mappings"]

        log.info("ATM switch {} is loading".format(name))
        self.setName(name)
        self.setup(name, node_id, mappings)

    def name(self):
        """
        Returns the name of this switch.

        :returns: name (string)
        """

        return self._settings["name"]

    def settings(self):
        """
        Returns all this switch settings.

        :returns: settings dictionary
        """

        return self._settings

    def ports(self):
        """
        Returns all the ports for this switch.

        :returns: list of Port instances
        """

        return self._ports

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

        :returns: QWidget object
        """

        from .pages.atm_switch_configuration_page import ATMSwitchConfigurationPage
        return ATMSwitchConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/atm_switch.svg"

    @staticmethod
    def symbolName():

        return "ATM switch"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.switches]

    def __str__(self):

        return "ATM switch"
