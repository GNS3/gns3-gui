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
Base class for Dynamips router implementations on the client side.
Asynchronously sends JSON messages to the GNS3 server and receives responses with callbacks.
"""

from gns3.node import Node
from ..adapters import ADAPTER_MATRIX
from ..wics import WIC_MATRIX

import logging
log = logging.getLogger(__name__)


class Router(Node):
    """
    Dynamips router (client implementation).

    :param server: GNS3 server instance
    :param platform: c7200, c3745, c3725, c3600, c2691, c2600 or c1700
    """

    def __init__(self, server, platform="c7200"):
        Node.__init__(self)

        self._server = server
        self._defaults = {}
        self._ports = []
        self._router_id = None
        self._settings = {"name": "",
                          "platform": platform,
                          "image": "",
                          "ram": 128,
                          "nvram": 128,
                          "mmap": True,
                          "sparsemem": True,
                          "clock_divisor": 8,
                          "idlepc": "",
                          "idlemax": 1500,
                          "idlesleep": 30,
                          "exec_area": None,
                          "jit_sharing_group": None,
                          "disk0": 0,
                          "disk1": 0,
                          "confreg": '0x2102',
                          "console": None,
                          "aux": None,
                          "mac_addr": None,
                          "system_id": None,
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

        #self._ethernet_wic_port_id = 0
        #self._serial_wic_port_id = 0

    def _addAdapterPorts(self, adapter, slot_id):
        """

        :param adapter: adapter name
        :param slot_id: slot identifier (integer)
        """

        nb_ports = ADAPTER_MATRIX[adapter]["nb_ports"]
        for port_id in range(0, nb_ports):
            port = ADAPTER_MATRIX[adapter]["port"]
            if "chassis" in self._settings and self._settings["chassis"] in ("1720", "1721", "1750"):
                # these chassis show their interface without a slot number
                port_name = port.longNameType() + str(port_id)
            else:
                port_name = port.longNameType() + str(slot_id) + "/" + str(port_id)
            new_port = port(port_name)
            new_port.slot = slot_id
            new_port.port = port_id
            self._ports.append(new_port)

    def _removeAdapterPorts(self, slot_id):

        for port in self._ports.copy():
            if port.slot == slot_id:
                self._ports.remove(port)

    def _addWICPorts(self, wic, wic_slot_id):
        """


        :param wic: WIC name
        :param wic_slot_id: WIC slot identifier (integer)
        """

        nb_ports = WIC_MATRIX[wic]["nb_ports"]
        base = 16 * (wic_slot_id + 1)
        for port_id in range(0, nb_ports):
            port = WIC_MATRIX[wic]["port"]
            port_name = port.longNameType() + str(base + port_id)
            new_port = port(port_name)
            # WICs are always in adapter slot 0.
            new_port.slot = 0
            # Dynamips WICs slot IDs start on a multiple of 16.
            new_port.port = base + port_id
            self._ports.append(new_port)

    def _removeWICPorts(self, wic, wic_slot_id):

        wic_ports_to_delete = []
        nb_ports = WIC_MATRIX[wic]["nb_ports"]
        base = 16 * (wic_slot_id + 1)
        for port_id in range(0, nb_ports):
            wic_ports_to_delete.append(base + port_id)
        for port in self._ports.copy():
            if port.slot == 0 and port.port in wic_ports_to_delete:
                self._ports.remove(port)

    def delete(self):
        """
        Deletes this router.
        """

        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        self._server.send_message("dynamips.vm.delete", {"id": self._router_id}, self._deleteCallback)

    def _deleteCallback(self, result, error=False):
        """
        Callback for the delete method.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            log.info("{} has been deleted".format(self.name()))
            self.delete_signal.emit()

    def setup(self, image, ram, name=None):
        """
        Setups this router.

        :param image: IOS image path
        :param ram: amount of RAM
        :param name: optional name for this router
        """

        #self._settings["image"] = ios_image["path"]
        #self._settings["ram"] = ios_image["ram"]
        #self._settings["idlepc"] = ios_image["idlepc"]
        #TODO: handle startup-config
        #if "chassis" in self._settings:
        #    self._settings["chassis"] = ios_image["chassis"]

        platform = self._settings["platform"]
        #image = self._settings["image"]
        #ram = self._settings["ram"]

        # Minimum settings to send to the server in order
        # to create a new router
        params = {"platform": platform,
                  "ram": ram,
                  "image": image}

        # A name for this router is optional, the server
        # will create one if there is no name set.
        if name:
            self._settings["name"] = name
            params["name"] = name

        self._server.send_message("dynamips.vm.create", params, self.setupCallback)

    def setupCallback(self, response, error=False):
        """
        Callback for the setup.

        :param result: server response
        :param error: ..
        """

        if error:
            #TODO: send errors to the GUI using a signal.
            print(response)
            return

        self._router_id = response["id"]

        # update the settings using the defaults sent by the server
        self._defaults = response.copy()
        for name, value in response.items():
            if name in self._settings and self._settings[name] != value:
                log.info("router setting up and updating {} from {} to {}".format(name, self._settings[name], value))
                self._settings[name] = value

        # insert default adapters
        for name, value in self._settings.items():
            if name.startswith("slot") and value:
                slot_id = int(name[-1])
                adapter = value
                self._addAdapterPorts(adapter, slot_id)

        # let the GUI knows about this router name
        self.newname_signal.emit(self._settings["name"])

    def update(self, new_settings):
        """
        Updates the settings for this router.

        :param new_settings: settings dictionary
        """

        params = {"id": self._router_id}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        self._server.send_message("dynamips.vm.update", params, self.updateCallback)

    def _updateWICNumbering(self):

        wic_ethernet_port_count = 0
        wic_serial_port_count = 0
        for wic_slot_id in range(0, 3):
            base = 16 * (wic_slot_id + 1)
            wic_slot = "wic" + str(wic_slot_id)
            if self._settings[wic_slot]:
                wic = self._settings[wic_slot]
                nb_ports = WIC_MATRIX[wic]["nb_ports"]
                for port_id in range(0, nb_ports):
                    for port in self._ports:
                        if port.slot == 0 and port.port == base + port_id:
                            if port.linkType() == "Serial":
                                wic_port_id = wic_serial_port_count
                                wic_serial_port_count += 1
                            else:
                                wic_port_id = wic_ethernet_port_count
                                wic_ethernet_port_count += 1
                            if "chassis" in self._settings and self._settings["chassis"] in ("1720", "1721", "1750"):
                                # these chassis show their interface without a slot number
                                port.name = port.longNameType() + str(wic_port_id)
                            else:
                                port.name = port.longNameType() + "0/" + str(wic_port_id)

    def updateCallback(self, response, error=False):

        for name, value in response.items():
            if name in self._settings and self._settings[name] != value:
                log.info("{}: updating {} from {} to {}".format(self.name(), name, self._settings[name], value))
                if name.startswith("slot"):
                    # add or remove adapters ports
                    slot_id = int(name[-1])
                    if value:
                        adapter = value
                        if adapter != self._settings[name]:
                            self._removeAdapterPorts(slot_id)
                        self._addAdapterPorts(adapter, slot_id)
                    elif self._settings[name]:
                        self._removeAdapterPorts(slot_id)
                if name.startswith("wic"):
                    # create or remove WIC ports
                    wic_slot_id = int(name[-1])
                    if value:
                        wic = value
                        if self._settings[name] and wic != self._settings[name]:
                            self._removeWICPorts(self._settings[name], wic_slot_id)
                        self._addWICPorts(wic, wic_slot_id)
                    elif self._settings[name]:
                        self._removeWICPorts(self._settings[name], wic_slot_id)
                self._settings[name] = value
        self._updateWICNumbering()

    def start(self):
        """
        Starts this router.
        """

        log.debug("{} is starting".format(self.name()))
        self._server.send_message("dynamips.vm.start", {"id": self._router_id}, self._startCallback)

    def _startCallback(self, result, error=False):
        """
        Callback for start.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while starting {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            log.info("{} has started".format(self.name()))
            self.started_signal.emit()

    def stop(self):
        """
        Stops this router.
        """

        log.debug("{} is stopping".format(self.name()))
        self._server.send_message("dynamips.vm.stop", {"id": self._router_id}, self._stopCallback)

    def _stopCallback(self, result, error=False):
        """
        Callback for stop.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while stopping {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            log.info("{} has stopped".format(self.name()))
            self.stopped_signal.emit()

    def suspend(self):
        """
        Suspends this router.
        """

        log.debug("{} is being suspended".format(self.name()))
        self._server.send_message("dynamips.vm.suspend", {"id": self._router_id}, self._suspendCallback)

    def _suspendCallback(self, result, error=False):
        """
        Callback for suspend.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while suspending {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            log.info("{} has suspended".format(self.name()))
            self.suspended_signal.emit()

    def allocateUDPPort(self):
        """
        Requests an UDP port allocation.
        """

        log.debug("{} is requesting an UDP port allocation".format(self.name()))
        self._server.send_message("dynamips.vm.allocate_udp_port", {"id": self._router_id}, self._allocateUDPPortCallback)

    def _allocateUDPPortCallback(self, result, error=False):
        """
        Callback for allocateUDPPort.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while allocating an UDP port for {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            lhost = result["lhost"]
            lport = result["lport"]
            log.info("{} has allocated UDP port {} for host {}".format(self.name(), lport, lhost))
            self.allocate_udp_nio_signal.emit(self.id, lport, lhost)

    def addNIO(self, port, nio):
        """
        Adds a new NIO on the specified port for this router.

        :param port: Port object.
        :param nio: NIO object.
        """

        nio_type = str(nio)
        params = {"id": self._router_id,
                  "nio": nio_type,
                  "slot": port.slot,
                  "port": port.port}

        if nio_type == "NIO_UDP":
            # add NIO UDP params
            params["lport"] = nio.lport
            params["rhost"] = nio.rhost
            params["rport"] = nio.rport

        elif nio_type == "NIO_GenericEthernet":
            # add NIO generic Ethernet param
            params["ethernet_device"] = nio.ethernet_device

        elif nio_type == "NIO_LinuxEthernet":
            # add NIO Linux Ethernet param
            params["ethernet_device"] = nio.ethernet_device

        elif nio_type == "NIO_TAP":
            # add NIO TAP param
            params["tap_device"] = nio.tap_device

        elif nio_type == "NIO_UNIX":
            # add NIO UNIX params
            params["local_file"] = nio.local_file
            params["remote_file"] = nio.remote_file

        elif nio_type == "NIO_VDE":
            # add NIO VDE params
            params["control_file"] = nio.control_file
            params["local_file"] = nio.local_file

        log.debug("{} is adding an {}: {}".format(self.name(), nio_type, params))
        self._server.send_message("dynamips.vm.add_nio", params, self._addNIOCallback)

    def _addNIOCallback(self, result, error=False):
        """
        Callback for addNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while adding an UDP NIO for {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            self.nio_signal.emit(self.id)

    def deleteNIO(self, port):

        params = {"id": self._router_id,
                  "nio": "NIO_UDP",
                  "slot": port.slot,
                  "port": port.port}

        port.nio = None
        self._server.send_message("dynamips.vm.delete_nio", params, self.deleteNIOCallback)

    def deleteNIOCallback(self, result, error=False):

        print("NIO deleted!")
        print(result)

    def name(self):
        """
        Returns the name of this router.

        :returns: name (string)
        """

        return self._settings["name"]

    def settings(self):
        """
        Returns all this router settings.

        :returns: settings dictionary
        """

        return self._settings

    def ports(self):
        """
        Returns all the ports for this router.

        :returns: list of Port objects
        """

        return self._ports

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node configurator.

        :returns: QWidget object.
        """

        from ..pages.router_configuration_page import RouterConfigurationPage
        return RouterConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this router.

        :returns: symbol path (or resource).
        """

        return ":/symbols/router.normal.svg"

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when the router is hovered.

        :returns: symbol path (or resource).
        """

        return ":/symbols/router.selected.svg"
