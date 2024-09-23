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
Base class for Dynamips router implementation on the client side.
"""

import os
import re

from gns3.node import Node

from ..adapters import ADAPTER_MATRIX
from ..wics import WIC_MATRIX

import logging
log = logging.getLogger(__name__)


class Router(Node):
    """
    Dynamips router (client implementation).

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    :param platform: c7200, c3745, c3725, c3600, c2691, c2600 or c1700
    """

    URL_PREFIX = "dynamips"

    def __init__(self, module, server, project, platform="c7200"):

        super().__init__(module, server, project)
        self._dynamips_id = None

        router_settings = {"platform": platform,
                           "usage": "",
                           "chassis": "",
                           "image": "",
                           "image_md5sum": "",
                           "startup_config": "",
                           "private_config": "",
                           "ram": 128,
                           "nvram": 128,
                           "mmap": True,
                           "sparsemem": True,
                           "clock_divisor": 8,
                           "idlepc": "",
                           "idlemax": 500,
                           "idlesleep": 30,
                           "iomem": 15,
                           "exec_area": 64,
                           "disk0": 0,
                           "disk1": 0,
                           "auto_delete_disks": False,
                           "console_type": "telnet",
                           "console_auto_start": False,
                           "aux": None,
                           "mac_addr": None,
                           "system_id": "FTX0945W0MY",
                           "slot0": None,
                           "slot1": None,
                           "slot2": None,
                           "slot3": None,
                           "slot4": None,
                           "slot5": None,
                           "slot6": None,
                           "wic0": None,
                           "wic1": None,
                           "wic2": None}

        self.settings().update(router_settings)

    def _createCallback(self, result):
        """
        Callback for create.

        :param result: server response
        """

        self._dynamips_id = result.get("dynamips_id")

    def computeIdlepcs(self, callback):
        """
        Get idle-PC proposals.
        """

        log.debug("{} is requesting Idle-PC proposals".format(self.name()))
        self.controllerHttpGet("/nodes/{node_id}/dynamips/idlepc_proposals".format(node_id=self._node_id),
                               callback,
                               timeout=240,
                               context={"router": self},
                               progressText="Computing Idle-PC values, please wait...")

    def computeAutoIdlepc(self, callback):
        """
        Find the best idle-PC value.
        """

        log.debug("{} is requesting Idle-PC proposals".format(self.name()))
        self.controllerHttpGet("/nodes/{node_id}/dynamips/auto_idlepc".format(node_id=self._node_id),
                               callback,
                               timeout=240,
                               context={"router": self},
                               progressText="Computing Idle-PC values, please wait...")

    def idlepc(self):
        """
        Returns the current Idle-PC value for this router.

        :returns: idlepc value (string)
        """

        return self._settings["idlepc"]

    def setIdlepc(self, idlepc):
        """
        Sets a new Idle-PC value for this router.

        :param idlepc: idlepc value (string)
        """

        self.update({"idlepc": idlepc})

    def _slot_info(self):
        """
        Returns information about the slots/ports of this router.

        :returns: formated string
        """

        slots = {}
        slot_info = ""
        for name, value in self._settings.items():
            if name.startswith("slot") and value is not None:
                slots[name] = value

        for name in sorted(slots.keys()):
            slot_number = int(name[-1])
            adapter_name = slots[name]
            nb_ports = ADAPTER_MATRIX[adapter_name]["nb_ports"]
            if nb_ports == 1:
                port_string = "port"
            else:
                port_string = "ports"

            slot_info = slot_info + "    slot {slot_number} hardware is {adapter} with {nb_ports} {port_string}\n".format(slot_number=str(slot_number),
                                                                                                                         adapter=adapter_name,
                                                                                                                         nb_ports=nb_ports,
                                                                                                                         port_string=port_string)

            port_names = {}
            for port in self._ports:
                if port.adapterNumber() == slot_number and port.portNumber() < 16:
                    port_names[port.name()] = port
            sorted_ports = sorted(port_names.keys())

            for port_name in sorted_ports:
                port_info = port_names[port_name]
                if port_info.isFree():
                    slot_info += "      {} is empty\n".format(port_name)
                else:
                    slot_info += "      {port_name} {port_description}\n".format(port_name=port_name,
                                                                                 port_description=port_info.description())

        wic_slots = {}
        for name, value in self._settings.items():
            if name.startswith("wic") and value is not None:
                wic_slots[name] = value

        for name in sorted(wic_slots.keys()):
            wic_slot_number = int(name[-1])
            wic_name = wic_slots[name]
            nb_ports = WIC_MATRIX[wic_name]["nb_ports"]
            if nb_ports == 1:
                port_string = "port"
            else:
                port_string = "ports"

            slot_info = slot_info + "    {wic_name} installed in WIC slot {wic_slot_number} with {nb_ports} {port_string}\n".format(wic_name=wic_name,
                                                                                                                                   wic_slot_number=wic_slot_number,
                                                                                                                                   nb_ports=nb_ports,
                                                                                                                                   port_string=port_string)

            base = 16 * (wic_slot_number + 1)
            port_names = {}
            for port_number in range(0, nb_ports):
                for port in self._ports:
                    if port.adapterNumber() == 0 and port.portNumber() == base + port_number:
                        port_names[port.name()] = port
            sorted_ports = sorted(port_names.keys())

            for port_name in sorted_ports:
                port_info = port_names[port_name]
                if port_info.isFree():
                    slot_info += "      {} is empty\n".format(port_name)
                else:
                    slot_info += "      {port_name} {port_description}\n".format(port_name=port_name,
                                                                                 port_description=port_info.description())

        return slot_info

    def info(self):
        """
        Returns information about this router.

        :returns: formated string
        """

        platform = self._settings["platform"]
        router_specific_info = ""
        if platform == "c7200":
            router_specific_info = "{midplane} {npe}".format(midplane=self._settings["midplane"],
                                                             npe=self._settings["npe"])

            router_specific_info = router_specific_info.upper()

        # get info about Idle-PC
        idlepc_info = "with no idlepc value"
        if self._settings["idlepc"]:
            idlepc_info = "with idlepc value of {idlepc}, idlemax of {idlemax} and idlesleep of {idlesleep} ms".format(idlepc=self._settings["idlepc"],
                                                                                                                       idlemax=self._settings["idlemax"],
                                                                                                                       idlesleep=self._settings["idlesleep"])

        info = """Router {name} is {state}
  Running on server {host} with port {port}
  Local ID is {id} and server ID is {node_id}
  Dynamips ID is {dynamips_id}
  Hardware is Dynamips emulated Cisco {platform} {specific_info} with {ram}MB RAM and {nvram}KB NVRAM
  Console is on port {console} and type is {console_type}, AUX console is on port {aux}
  IOS image is "{image_name}"
  {idlepc_info}
  PCMCIA disks: disk0 is {disk0}MB and disk1 is {disk1}MB
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           dynamips_id=self._dynamips_id,
           state=self.state(),
           platform=platform,
           specific_info=router_specific_info,
           ram=self._settings["ram"],
           nvram=self._settings["nvram"],
           host=self.compute().name(),
           port=self.compute().port(),
           console=self._settings["console"],
           console_type=self._settings["console_type"],
           aux=self._settings["aux"],
           image_name=os.path.basename(self._settings["image"]),
           idlepc_info=idlepc_info,
           disk0=self._settings["disk0"],
           disk1=self._settings["disk1"])

        # gather information about PA, their interfaces and connections
        slot_info = self._slot_info()

        usage = "\n" + self._settings.get("usage")
        return info + slot_info + usage

    def configFiles(self):
        """
        Name of the configuration files
        """

        return ["configs/i{}_startup-config.cfg".format(self._dynamips_id),
                "configs/i{}_private-config.cfg".format(self._dynamips_id)]

    def auxConsole(self):
        """
        Returns the auxiliary console port for this router.

        :returns: port (integer)
        """

        return self._settings["aux"]

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

        :returns: QWidget object
        """

        from ..pages.ios_router_configuration_page import IOSRouterConfigurationPage
        return IOSRouterConfigurationPage

    @staticmethod
    def validateHostname(hostname):
        """
        Checks if the hostname is valid.

        :param hostname: hostname to check

        :returns: boolean
        """

        # IOS names must start with a letter, end with a letter or digit, and
        # have as interior characters only letters, digits, and hyphens.
        # They must be 63 characters or fewer (ARPANET rules).
        if re.search(r"""^(?!-|[0-9])[a-zA-Z0-9-]{1,63}(?<!-)$""", hostname):
            return True
        return False

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this router.

        :returns: symbol path (or resource).
        """

        return ":/symbols/router.svg"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.routers]
