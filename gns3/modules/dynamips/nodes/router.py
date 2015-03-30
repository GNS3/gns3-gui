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

from gns3.vm import VM
from gns3.node import Node
from gns3.ports.port import Port
from gns3.servers import Servers
from gns3.utils.normalize_filename import normalize_filename

from ..settings import PLATFORMS_DEFAULT_RAM
from ..adapters import ADAPTER_MATRIX
from ..wics import WIC_MATRIX

import logging
log = logging.getLogger(__name__)


class Router(VM):

    """
    Dynamips router (client implementation).

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    :param platform: c7200, c3745, c3725, c3600, c2691, c2600 or c1700
    """

    URL_PREFIX = "dynamips"

    def __init__(self, module, server, project, platform="c7200"):

        VM.__init__(self, module, server, project)
        log.info("Router {} is being created".format(platform))
        self._ports = []
        self._dynamips_id = None
        self._loading = False
        self._export_directory = None
        self._defaults = {}
        self._settings = {"name": "",
                          "platform": platform,
                          "image": "",
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
                          "exec_area": 64,
                          "disk0": 0,
                          "disk1": 0,
                          "console": None,
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

    def _addAdapterPorts(self, adapter, slot_number):
        """
        Adds ports based on what adapter is inserted in which slot.

        :param adapter: adapter name
        :param slot_number: slot number (integer)
        """

        nb_ports = ADAPTER_MATRIX[adapter]["nb_ports"]
        for port_number in range(0, nb_ports):
            port = ADAPTER_MATRIX[adapter]["port"]
            if "chassis" in self._settings and self._settings["chassis"] in ("1720", "1721", "1750"):
                # these chassis show their interface without a slot number
                port_name = port.longNameType() + str(port_number)
                short_name = port.shortNameType() + str(port_number)
            else:
                port_name = port.longNameType() + str(slot_number) + "/" + str(port_number)
                short_name = port.shortNameType() + str(slot_number) + "/" + str(port_number)
            new_port = port(port_name)
            new_port.setShortName(short_name)
            new_port.setPortNumber(port_number)
            new_port.setAdapterNumber(slot_number)
            new_port.setPacketCaptureSupported(True)
            self._ports.append(new_port)
            log.debug("port {} has been added".format(port_name))

    def _removeAdapterPorts(self, slot_number):
        """
        Removes ports when an adapter is removed from a slot.

        :param slot_number: slot number (integer)
        """

        for port in self._ports.copy():
            if port.adapterNumber() == slot_number:
                self._ports.remove(port)
                log.debug("port {} has been removed".format(port.name()))

    def _addWICPorts(self, wic, wic_slot_number):
        """
        Adds ports based on what WIC is inserted in which slot.

        :param wic: WIC name
        :param wic_slot_number: WIC slot number (integer)
        """

        nb_ports = WIC_MATRIX[wic]["nb_ports"]
        base = 16 * (wic_slot_number + 1)
        for port_number in range(0, nb_ports):
            port = WIC_MATRIX[wic]["port"]
            # Dynamips WICs port number start on a multiple of 16.
            port_name = port.longNameType() + str(base + port_number)
            short_name = port.shortNameType() + str(base + port_number)
            new_port = port(port_name)
            new_port.setShortName(short_name)
            new_port.setPortNumber(base + port_number)
            # WICs are always in adapter slot 0.
            new_port.setAdapterNumber(0)
            new_port.setPacketCaptureSupported(True)
            self._ports.append(new_port)
            log.debug("port {} has been added".format(port_name))

    def _removeWICPorts(self, wic, wic_slot_number):
        """
        Removes ports when a WIC is removed from a slot.

        :param wic_slot_number: WIC slot identifier (integer)
        """

        wic_ports_to_delete = []
        nb_ports = WIC_MATRIX[wic]["nb_ports"]
        base = 16 * (wic_slot_number + 1)
        for port_number in range(0, nb_ports):
            wic_ports_to_delete.append(base + port_number)
        for port in self._ports.copy():
            if port.adapterNumber() == 0 and port.portNumber() in wic_ports_to_delete:
                self._ports.remove(port)
                log.debug("port {} has been removed".format(port.name()))

    def _updateWICNumbering(self):
        """
        Updates the port names that are located on a WIC adapter
        (based on the number of WICs and their slot number).
        """

        wic_ethernet_port_count = 0
        wic_serial_port_count = 0
        for wic_slot_number in range(0, 3):
            base = 16 * (wic_slot_number + 1)
            wic_slot = "wic" + str(wic_slot_number)
            if self._settings[wic_slot]:
                wic = self._settings[wic_slot]
                nb_ports = WIC_MATRIX[wic]["nb_ports"]
                for port_number in range(0, nb_ports):
                    for port in self._ports:
                        if port.adapterNumber() == 0 and port.portNumber() == base + port_number:
                            if port.linkType() == "Serial":
                                wic_port_number = wic_serial_port_count
                                wic_serial_port_count += 1
                            else:
                                wic_port_number = wic_ethernet_port_count
                                wic_ethernet_port_count += 1
                            old_name = port.name()
                            if "chassis" in self._settings and self._settings["chassis"] in ("1720", "1721", "1750"):
                                # these chassis show their interface without a slot number
                                port.setName(port.longNameType() + str(wic_port_number))
                                port.setShortName(port.shortNameType() + str(wic_port_number))
                            else:
                                port.setName(port.longNameType() + "0/" + str(wic_port_number))
                                port.setShortName(port.shortNameType() + "0/" + str(wic_port_number))
                            log.debug("port {} renamed to {}".format(old_name, port.name()))

    def setup(self, image, ram, name=None, vm_id=None, dynamips_id=None, additional_settings={}, base_name="R"):
        """
        Setups this router.

        :param image: IOS image path
        :param ram: amount of RAM
        :param name: optional name for this router
        :param vm_id: VM identifier on the server
        :param dynamips_id: Dynamips identifier on the server
        :param additional_settings: other additional and not mandatory settings
        """

        # let's create a unique name if none has been chosen
        if not name:
            name = self.allocateName(base_name)

        if not name:
            self.error_signal.emit(self.id(), "could not allocate a name for this router")
            return

        # keep the default settings
        self._defaults = self._settings.copy()
        platform = self._settings["platform"]

        self._settings["name"] = name
        # Minimum settings to send to the server in order to create a new router
        params = {"name": name,
                  "platform": platform,
                  "ram": ram,
                  "image": image}

        # FIXME: cloud support
        # if self.server().isCloud():
        #     initial_settings["cloud_path"] = "images/IOS"
        #     params["image"] = os.path.basename(params["image"])

        if vm_id:
            params["vm_id"] = vm_id

        if dynamips_id:
            params["dynamips_id"] = dynamips_id

        # push the startup-config
        if not vm_id and "startup_config" in additional_settings and os.path.isfile(additional_settings["startup_config"]):
            params["startup_config_content"] = self._readBaseConfig(additional_settings["startup_config"])

        # push the private-config
        if not vm_id and "private_config" in additional_settings and os.path.isfile(additional_settings["private_config"]):
            params["private_config_content"] = self._readBaseConfig(additional_settings["private_config"])

        # add some initial settings
        # if "console" in initial_settings:
        #     params["console"] = self._settings["console"] = initial_settings.pop("console")
        # if "aux" in initial_settings:
        #     params["aux"] = self._settings["aux"] = initial_settings.pop("aux")
        # if "mac_addr" in initial_settings:
        #     params["mac_addr"] = self._settings["mac_addr"] = initial_settings.pop("mac_addr")
        # if "chassis" in initial_settings:
        #     params["chassis"] = self._settings["chassis"] = initial_settings.pop("chassis")
        # if "cloud_path" in initial_settings:
        #     params["cloud_path"] = self._settings["cloud_path"] = initial_settings.pop("cloud_path")

        params.update(additional_settings)
        self.httpPost("/dynamips/vms", self._setupCallback, body=params)

    def _setupCallback(self, result, error=False, **kwargs):
        """
        Callback for setup.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while setting up {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            return

        self._vm_id = result["vm_id"]
        self._dynamips_id = result["dynamips_id"]

        # update the settings using the defaults sent by the server
        for name, value in result.items():
            if name in self._settings and self._settings[name] != value:
                log.info("Router {} setting up and updating {} from '{}' to '{}'".format(self.name(),
                                                                                         name,
                                                                                         self._settings[name],
                                                                                         value))
                self._settings[name] = value

        # insert default adapters
        for name, value in self._settings.items():
            if name.startswith("slot") and value:
                slot_number = int(name[-1])
                adapter = value
                self._addAdapterPorts(adapter, slot_number)
            if name.startswith("wic") and value:
                wic_slot_number = int(name[-1])
                wic = value
                self._addWICPorts(wic, wic_slot_number)
        self._updateWICNumbering()

        if self._loading:
            self.updated_signal.emit()
        else:
            self.setInitialized(True)
            log.debug("router {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)

    def update(self, new_settings):
        """
        Updates the settings for this router.

        :param new_settings: settings dictionary
        """

        if "name" in new_settings and new_settings["name"] != self.name() and self.hasAllocatedName(new_settings["name"]):
            self.error_signal.emit(self.id(), 'Name "{}" is already used by another node'.format(new_settings["name"]))
            return

        params = {}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        if "startup_config" in new_settings and self._settings["startup_config"] != new_settings["startup_config"]:
            params["startup_config_content"] = self._readBaseConfig(new_settings["startup_config"])
            del params["startup_config"]

        if "private_config" in new_settings and self._settings["private_config"] != new_settings["private_config"]:
            params["private_config_content"] = self._readBaseConfig(new_settings["private_config"])
            del params["private_config"]

        log.debug("{} is updating settings: {}".format(self.name(), params))
        self.httpPut("/dynamips/vms/{vm_id}".format(vm_id=self._vm_id), self._updateCallback, body=params)

    def _updateCallback(self, result, error=False, **kwargs):
        """
        Callback for update.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            return

        updated = False
        for name, value in result.items():
            if name in self._settings and self._settings[name] != value:
                log.info("{}: updating {} from '{}' to '{}'".format(self.name(), name, self._settings[name], value))
                updated = True
                if name == "name":
                    # update the node name
                    self.updateAllocatedName(value)
                if name.startswith("slot"):
                    # add or remove adapters ports
                    slot_number = int(name[-1])
                    if value:
                        adapter = value
                        if adapter != self._settings[name]:
                            self._removeAdapterPorts(slot_number)
                        self._addAdapterPorts(adapter, slot_number)
                    elif self._settings[name]:
                        self._removeAdapterPorts(slot_number)
                if name.startswith("wic"):
                    # create or remove WIC ports
                    wic_slot_number = int(name[-1])
                    if value:
                        wic = value
                        if self._settings[name] and wic != self._settings[name]:
                            self._removeWICPorts(self._settings[name], wic_slot_number)
                        self._addWICPorts(wic, wic_slot_number)
                    elif self._settings[name]:
                        self._removeWICPorts(self._settings[name], wic_slot_number)
                self._settings[name] = value
        self._updateWICNumbering()

        if updated or self._loading:
            log.info("router {} has been updated".format(self.name()))
            self.updated_signal.emit()

    def suspend(self):
        """
        Suspends this router.
        """

        if self.status() == Node.suspended:
            log.debug("{} is already suspended".format(self.name()))
            return

        log.debug("{} is being suspended".format(self.name()))
        self.httpPost("/dynamips/vms/{vm_id}/suspend".format(vm_id=self._vm_id), self._suspendCallback)

    def _suspendCallback(self, result, error=False, **kwargs):
        """
        Callback for suspend.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while suspending {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{} has suspended".format(self.name()))
            self.setStatus(Node.suspended)
            for port in self._ports:
                # set ports as suspended
                port.setStatus(Port.suspended)
            self.suspended_signal.emit()

    def startPacketCapture(self, port, capture_file_name, data_link_type):
        """
        Starts a packet capture.

        :param port: Port instance
        :param capture_file_name: PCAP capture file path
        :param data_link_type: PCAP data link type
        """

        params = {"capture_file_name": capture_file_name,
                  "data_link_type": data_link_type}
        log.debug("{} is starting a packet capture on {}: {}".format(self.name(), port.name(), params))
        self.httpPost("/dynamips/vms/{vm_id}/adapters/{adapter_number}/ports/{port_number}/start_capture".format(
            vm_id=self._vm_id,
            adapter_number=port.adapterNumber(),
            port_number=port.portNumber()),
            self._startPacketCaptureCallback,
            context={"port": port},
            body=params)

    def _startPacketCaptureCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for starting a packet capture.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while starting capture {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            port = context["port"]
            log.info("{} has successfully started capturing packets on {}".format(self.name(), port.name()))
            try:
                port.startPacketCapture(result["pcap_file_path"])
            except OSError as e:
                self.error_signal.emit(self.id(), "could not start the packet capture reader: {}: {}".format(e, e.filename))
            self.updated_signal.emit()

    def stopPacketCapture(self, port):
        """
        Stops a packet capture.

        :param port: Port instance
        """

        log.debug("{} is stopping a packet capture on {}".format(self.name(), port.name()))
        self.httpPost("/dynamips/vms/{vm_id}/adapters/{adapter_number}/ports/{port_number}/stop_capture".format(
            vm_id=self._vm_id,
            adapter_number=port.adapterNumber(),
            port_number=port.portNumber()),
            self._stopPacketCaptureCallback,
            context={"port": port})

    def _stopPacketCaptureCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for stopping a packet capture.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while stopping capture {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            port = context["port"]
            log.info("{} has successfully stopped capturing packets on {}".format(self.name(), port.name()))
            port.stopPacketCapture()
            self.updated_signal.emit()

    def computeIdlepcs(self, callback):
        """
        Get idle-PC proposals.
        """

        log.debug("{} is requesting Idle-PC proposals".format(self.name()))
        self.httpGet("/dynamips/vms/{vm_id}/idlepc_proposals".format(
            vm_id=self._vm_id),
            callback,
            context={"router": self})

    def computeAutoIdlepc(self, callback):
        """
        Find the best idle-PC value.
        """

        log.debug("{} is requesting Idle-PC proposals".format(self.name()))
        self.httpGet("/dynamips/vms/{vm_id}/auto_idlepc".format(
            vm_id=self._vm_id),
            callback,
            context={"router": self})

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
        self._module.updateImageIdlepc(self._settings["image"], idlepc)

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

            slot_info = slot_info + "   slot {slot_number} hardware is {adapter} with {nb_ports} {port_string}\n".format(slot_number=str(slot_number),
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
                    slot_info += "     {} is empty\n".format(port_name)
                else:
                    slot_info += "     {port_name} {port_description}\n".format(port_name=port_name,
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

            slot_info = slot_info + "   {wic_name} installed in WIC slot {wic_slot_number} with {nb_ports} {port_string}\n".format(wic_name=wic_name,
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
                    slot_info += "     {} is empty\n".format(port_name)
                else:
                    slot_info += "     {port_name} {port_description}\n".format(port_name=port_name,
                                                                                port_description=port_info.description())

        return slot_info

    def info(self):
        """
        Returns information about this router.

        :returns: formated string
        """

        if self.status() == Node.started:
            state = "started"
        elif self.status() == Node.suspended:
            state = "suspended"
        else:
            state = "stopped"

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
  Local node ID is {id}
  Server's VM ID is {vm_id}
  Dynamips ID is {dynamips_id}
  Hardware is Dynamips emulated Cisco {platform} {specific_info} with {ram} MB RAM and {nvram} KB NVRAM
  Router's server runs on {host}:{port}, console is on port {console}, aux is on port {aux}
  Image is {image_name}
  {idlepc_info}
  {disk0} MB disk0 size, {disk1} MB disk1 size
""".format(name=self.name(),
           id=self.id(),
           vm_id=self._vm_id,
           dynamips_id=self._dynamips_id,
           state=state,
           platform=platform,
           specific_info=router_specific_info,
           ram=self._settings["ram"],
           nvram=self._settings["nvram"],
           host=self._server.host,
           port=self._server.port,
           console=self._settings["console"],
           aux=self._settings["aux"],
           image_name=os.path.basename(self._settings["image"]),
           idlepc_info=idlepc_info,
           disk0=self._settings["disk0"],
           disk1=self._settings["disk1"])

        # gather information about PA, their interfaces and connections
        slot_info = self._slot_info()
        return info + slot_info

    def dump(self):
        """
        Returns a representation of this router
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """

        router = {"id": self.id(),
                  "vm_id": self._vm_id,
                  "dynamips_id": self._dynamips_id,
                  "type": self.__class__.__name__,
                  "description": str(self),
                  "properties": {},
                  "server_id": self._server.id()}

        # add the properties
        for name, value in self._settings.items():
            if name in self._defaults and self._defaults[name] != value:
                router["properties"][name] = value

        # add the ports
        if self._ports:
            ports = router["ports"] = []
            for port in self._ports:
                ports.append(port.dump())

        return router

    def _imageFilesDir(self):
        """
        Returns the location of IOS images.
        """

        servers = Servers.instance()
        local_server = servers.localServerSettings()
        return os.path.join(local_server["images_path"], "IOS")

    def load(self, node_info):
        """
        Loads a router representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        self.node_info = node_info
        router_id = node_info.get("router_id")
        # for backward compatibility
        vm_id = dynamips_id = node_info.get("router_id")
        if not vm_id:
            vm_id = node_info["vm_id"]
            dynamips_id = node_info["dynamips_id"]
        settings = node_info["properties"]
        name = settings.pop("name")
        ram = settings.get("ram", PLATFORMS_DEFAULT_RAM[self._settings["platform"]])
        image = settings.pop("image")

        if self.server().isLocal():
            # check and update the path to use the image in the images directory
            updated_image_path = os.path.join(self._imageFilesDir(), image)
            if os.path.isfile(updated_image_path):
                image = updated_image_path
            elif not os.path.isfile(image):
                alternative_image = self._module.findAlternativeIOSImage(image, self)
                image = alternative_image["image"]
                if alternative_image["ram"]:
                    ram = alternative_image["ram"]
                if alternative_image["idlepc"]:
                    settings["idlepc"] = alternative_image["idlepc"]

        self.updated_signal.connect(self._updatePortSettings)
        # block the created signal, it will be triggered when loading is completely done
        self._loading = True
        log.info("router {} is loading".format(name))
        self.setName(name)
        self.setup(image, ram, name, vm_id, dynamips_id, settings)

    def _updatePortSettings(self):
        """
        Updates port settings when loading a topology.
        """

        self.updated_signal.disconnect(self._updatePortSettings)
        # update the port with the correct names and IDs
        if "ports" in self.node_info:
            ports = self.node_info["ports"]
            for topology_port in ports:
                for port in self._ports:
                    if topology_port["port_number"] == port.portNumber() and (topology_port.get("adapter_number", None) == port.adapterNumber() or topology_port.get("slot_number", None) == port.adapterNumber()):
                        port.setName(topology_port["name"])
                        port.setId(topology_port["id"])

        # now we can set the node has initialized and trigger the signal
        self.setInitialized(True)
        log.info("router {} has been loaded".format(self.name()))
        self.created_signal.emit(self.id())
        self._module.addNode(self)
        self._inital_settings = None
        self._loading = False

    def saveConfig(self):
        """
        Save the configs
        """

        self.httpPost("/dynamips/vms/{vm_id}/configs/save".format(vm_id=self._vm_id), self._saveConfigCallback)

    def _saveConfigCallback(self, result, error=False, context={}, **kwargs):

        if error:
            log.error("error while saving {} configs: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{}: configs have been saved".format(self.name()))

    def exportConfig(self, startup_config_export_path, private_config_export_path):
        """
        Exports the startup-config and private-config.

        :param startup_config_export_path: export path for the startup-config
        :param private_config_export_path: export path for the private-config
        """

        self.httpGet("/dynamips/vms/{vm_id}/configs".format(
            vm_id=self._vm_id,
        ),
            self._exportConfigCallback,
            context={
            "startup_config_path": startup_config_export_path,
            "private_config_path": private_config_export_path
        })

    def _exportConfigCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for exportConfig.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while exporting {} configs: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            startup_config_path = context["startup_config_path"]
            private_config_path = context["private_config_path"]

            if "startup_config_content" in result is not None:
                try:
                    with open(startup_config_path, "wb") as f:
                        log.info("Saving {} startup-config to {}".format(self.name(), startup_config_path))
                        f.write(result["startup_config_content"].encode("utf-8"))
                except OSError as e:
                    self.error_signal.emit(self.id(), "Could not export startup-config to {}: {}".format(startup_config_path, e))

            if "private_config_content" in result is not None:
                try:
                    with open(private_config_path, "wb") as f:
                        log.info("Saving {} private-config to {}".format(self.name(), private_config_path))
                        f.write(result["private_config_content"].encode("utf-8"))
                except OSError as e:
                    self.error_signal.emit(self.id(), "Could not export private-config to {}: {}".format(private_config_path, e))

    def exportConfigToDirectory(self, directory):
        """
        Exports the startup-config and private-config to a directory.

        :param directory: destination directory path
        """

        self.httpGet("/dynamips/vms/{vm_id}/configs".format(
            vm_id=self._vm_id,
        ),
            self._exportConfigToDirectoryCallback,
            context={
            "directory": directory
        })

    def _exportConfigToDirectoryCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for exportConfigToDirectory.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while exporting {} configs: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            directory = context["directory"]
            if "startup_config_content" in result:
                config_path = os.path.join(directory, normalize_filename(self.name())) + "_startup-config.cfg"
                try:
                    with open(config_path, "wb") as f:
                        log.info("saving {} startup-config to {}".format(self.name(), config_path))
                        f.write(result["startup_config_content"].encode("utf-8"))
                except OSError as e:
                    self.error_signal.emit(self.id(), "Could not export startup-config to {}: {}".format(config_path, e))
            if "private_config_content" in result:
                config_path = os.path.join(directory, normalize_filename(self.name())) + "_private-config.cfg"
                try:
                    with open(config_path, "wb") as f:
                        log.info("saving {} private-config to {}".format(self.name(), config_path))
                        f.write(result["private_config_content"].encode("utf-8"))
                except OSError as e:
                    self.error_signal.emit(self.id(), "Could not export private-config to {}: {}".format(config_path, e))

    def importConfig(self, path):
        """
        Imports a startup-config.

        :param path: path to the startup-config
        """

        new_settings = {"startup_config": path}
        self.update(new_settings)

    def importPrivateConfig(self, path):
        """
        Imports a private-config.

        :param path: path to the private-config
        """

        new_settings = {"private_config": path}
        self.update(new_settings)

    def importConfigFromDirectory(self, directory):
        """
        Imports a startup-config and a private-config from a directory.

        :param directory: source directory path
        """

        contents = os.listdir(directory)
        startup_config = normalize_filename(self.name()) + "_startup-config.cfg"
        private_config = normalize_filename(self.name()) + "_private-config.cfg"
        new_settings = {}
        if startup_config in contents:
            new_settings["startup_config"] = os.path.join(directory, startup_config)
        else:
            self.warning_signal.emit(self.id(), "no startup-config file could be found, expected file name: {}".format(startup_config))
        if private_config in contents:
            new_settings["private_config"] = os.path.join(directory, private_config)
        else:
            self.warning_signal.emit(self.id(), "no private-config file could be found, expected file name: {}".format(private_config))
        if new_settings:
            self.update(new_settings)

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

        :returns: list of Port instances
        """

        return self._ports

    def console(self):
        """
        Returns the console port for this router.

        :returns: port (integer)
        """

        return self._settings["console"]

    def auxConsole(self):
        """
        Returns the auxiliary console port for this router.

        :returns: port (integer)
        """

        return self._settings["aux"]

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node configurator.

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
        # They must be 63 characters or fewer.
        if re.search(r"""^[\-\w]+$""", hostname) and len(hostname) <= 63:
            return True
        return False

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

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.routers]
