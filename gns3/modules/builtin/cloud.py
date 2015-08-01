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

"""
NIO implementation on the client side (in the form of a pseudo node represented as a cloud).
"""

import re
from gns3.node import Node
from gns3.ports.port import Port
from gns3.nios.nio_generic_ethernet import NIOGenericEthernet
from gns3.nios.nio_linux_ethernet import NIOLinuxEthernet
from gns3.nios.nio_nat import NIONAT
from gns3.nios.nio_udp import NIOUDP
from gns3.nios.nio_tap import NIOTAP
from gns3.nios.nio_unix import NIOUNIX
from gns3.nios.nio_vde import NIOVDE
from gns3.nios.nio_null import NIONull

import logging
log = logging.getLogger(__name__)


class Cloud(Node):

    """
    Dynamips cloud.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    _name_instance_count = 1

    def __init__(self, module, server, project):

        super().__init__(module, server, project)

        log.info("cloud is being created")
        # create an unique id and name
        self._name_id = Cloud._name_instance_count
        Cloud._name_instance_count += 1

        name = "Cloud {}".format(self._name_id)
        self.setStatus(Node.started)  # this is an always-on node
        self._initial_settings = None
        self._settings = {"name": name,
                          "interfaces": {},
                          "nios": []}

    def delete(self):
        """
        Deletes this cloud.
        """

        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        self.deleted_signal.emit()

    def setup(self, name=None, additional_settings={}):
        """
        Setups this cloud.

        :param name: optional name for this cloud
        """

        if name:
            self._settings["name"] = name

        if additional_settings and "nios" in additional_settings:
            self._settings["nios"] = additional_settings["nios"]

        self._server.get("/interfaces", self._setupCallback)

    def _setupCallback(self, result, error=False, **kwargs):
        """
        Callback for setup.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while setting up {}: {}".format(self.name(), result["message"]))
            # a warning message instead of a error is more appropriate here
            self.warning_signal.emit(self.id(), result["message"])
        else:
            self._settings["interfaces"] = result.copy()

        if self._settings["nios"]:
            self._addPorts(self._settings["nios"])

        if self._loading:
            self.loaded_signal.emit()
        else:
            self.setInitialized(True)
            log.info("cloud {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)

    def _createNIOUDP(self, nio):
        """
        Creates a NIO UDP.

        :param nio: nio string
        """

        match = re.search(r"""^nio_udp:(\d+):(.+):(\d+)$""", nio)
        if match:
            lport = int(match.group(1))
            rhost = match.group(2)
            rport = int(match.group(3))
            return NIOUDP(lport, rhost, rport)
        return None

    def _createNIOGenericEthernet(self, nio):
        """
        Creates a NIO Generic Ethernet.

        :param nio: nio string
        """

        match = re.search(r"""^nio_gen_eth:(.+)$""", nio)
        if match:
            ethernet_device = match.group(1)
            return NIOGenericEthernet(ethernet_device)
        return None

    def _createNIOLinuxEthernet(self, nio):
        """
        Creates a NIO Linux Ethernet.

        :param nio: nio string
        """

        match = re.search(r"""^nio_gen_linux:(.+)$""", nio)
        if match:
            linux_device = match.group(1)
            return NIOLinuxEthernet(linux_device)
        return None

    def _createNIONAT(self, nio):
        """
        Creates a NIO NAT.

        :param nio: nio string
        """

        match = re.search(r"""^nio_nat:(.+)$""", nio)
        if match:
            identifier = match.group(1)
            return NIONAT(identifier)
        return None

    def _createNIOTAP(self, nio):
        """
        Creates a NIO TAP.

        :param nio: nio string
        """

        match = re.search(r"""^nio_tap:(.+)$""", nio)
        if match:
            tap_device = match.group(1)
            return NIOTAP(tap_device)
        return None

    def _createNIOUNIX(self, nio):
        """
        Creates a NIO UNIX.

        :param nio: nio string
        """

        match = re.search(r"""^nio_unix:(.+):(.+)$""", nio)
        if match:
            local_file = match.group(1)
            remote_file = match.group(2)
            return NIOUNIX(local_file, remote_file)
        return None

    def _createNIOVDE(self, nio):
        """
        Creates a NIO VDE.

        :param nio: nio string
        """

        match = re.search(r"""^nio_vde:(.+):(.+)$""", nio)
        if match:
            control_file = match.group(1)
            local_file = match.group(2)
            return NIOVDE(control_file, local_file)
        return None

    def _createNIONull(self, nio):
        """
        Creates a NIO Null.

        :param nio: nio string
        """

        match = re.search(r"""^nio_null:(.+)$""", nio)
        if match:
            identifier = match.group(1)
            return NIONull(identifier)
        return None

    def _allocateNIO(self, nio):
        """
        Allocate a new NIO object.

        :param nio: NIO description

        :returns: NIO instance
        """

        nio_object = None
        if nio.lower().startswith("nio_udp"):
            nio_object = self._createNIOUDP(nio)
        if nio.lower().startswith("nio_gen_eth"):
            nio_object = self._createNIOGenericEthernet(nio)
        if nio.lower().startswith("nio_gen_linux"):
            nio_object = self._createNIOLinuxEthernet(nio)
        if nio.lower().startswith("nio_nat"):
            nio_object = self._createNIONAT(nio)
        if nio.lower().startswith("nio_tap"):
            nio_object = self._createNIOTAP(nio)
        if nio.lower().startswith("nio_unix"):
            nio_object = self._createNIOUNIX(nio)
        if nio.lower().startswith("nio_vde"):
            nio_object = self._createNIOVDE(nio)
        if nio.lower().startswith("nio_null"):
            nio_object = self._createNIONull(nio)
        if nio_object is None:
            log.error("Could not create NIO object from {}".format(nio))
        return nio_object

    def _addPorts(self, nios, ignore_existing_nio=False):
        """
        Adds adapters.

        :param adapters: number of adapters
        """

        # add ports
        for nio in nios:
            if ignore_existing_nio and nio in self._settings["nios"]:
                # port already created for this NIO
                continue
            nio_object = self._allocateNIO(nio)
            if nio_object is None:
                continue
            port = Port(nio, nio_object, stub=True)
            port.setStatus(Port.started)
            self._ports.append(port)
            log.debug("port {} has been added".format(nio))

    def update(self, new_settings):
        """
        Updates the settings for this cloud.

        :param new_settings: settings dictionary
        """

        updated = False
        if "nios" in new_settings:
            nios = new_settings["nios"]
            self._addPorts(nios, ignore_existing_nio=True)
            updated = True

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

    def deleteNIO(self, port):

        pass

    def info(self):
        """
        Returns information about this cloud.

        :returns: formated string
        """

        info = """Cloud device {name} is always-on
This is a pseudo-device for external connections
""".format(name=self.name())

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "   Port {} is empty\n".format(port.name())
            else:
                port_info += "   Port {name} {description}\n".format(name=port.name(),
                                                                     description=port.description())

            # add the Windows interface name
            match = re.search(r"""^nio_gen_eth:(\\device\\npf_.+)$""", port.name())
            if match:
                for interface in self._settings["interfaces"]:
                    if interface["name"].lower() == match.group(1):
                        port_info += "      Windows name: {}\n".format(interface["description"])
                        break

        return info + port_info

    def dump(self):
        """
        Returns a representation of this cloud
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """

        cloud = {"id": self.id(),
                 "type": self.__class__.__name__,
                 "description": str(self),
                 "properties": {"name": self.name(),
                                "nios": self._settings["nios"]},
                 "server_id": self._server.id()}

        # add the ports
        if self._ports:
            ports = cloud["ports"] = []
            for port in self._ports:
                ports.append(port.dump())

        return cloud

    def load(self, node_info):
        """
        Loads a cloud representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        settings = node_info["properties"]
        name = settings.pop("name")
        log.info("cloud {} is loading".format(name))
        self.setName(name)
        self._loading = True
        self._node_info = node_info
        self.loaded_signal.connect(self._updatePortSettings)
        self.setup(name, additional_settings=settings)

    def _updatePortSettings(self):
        """
        Updates port settings when loading a topology.
        """

        self.loaded_signal.disconnect(self._updatePortSettings)

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
                                    nio = self._allocateNIO(topology_port["name"])
                                    port.setDefaultNio(nio)
                                    port.setName(topology_port["name"])
                                    self._settings["nios"].append(topology_port["name"])

        # now we can set the node as initialized and trigger the created signal
        self.setInitialized(True)
        log.info("cloud {} has been loaded".format(self.name()))
        self.created_signal.emit(self.id())
        self._module.addNode(self)
        self._loading = False
        self._node_info = None

    def name(self):
        """
        Returns the name of this cloud.

        :returns: name (string)
        """

        return self._settings["name"]

    def settings(self):
        """
        Returns all this cloud settings.

        :returns: settings dictionary
        """

        return self._settings

    def ports(self):
        """
        Returns all the ports for this cloud.

        :returns: list of Port instances
        """

        return self._ports

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

        :returns: list of node category (integer)
        """

        return [Node.end_devices]

    def __str__(self):

        return "Cloud"
