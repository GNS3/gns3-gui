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

import os
import base64
from gns3.node import Node
from gns3.ports.port import Port

from ..settings import PLATFORMS_DEFAULT_RAM
from ..adapters import ADAPTER_MATRIX
from ..wics import WIC_MATRIX

import logging
log = logging.getLogger(__name__)


class Router(Node):
    """
    Dynamips router (client implementation).

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param platform: c7200, c3745, c3725, c3600, c2691, c2600 or c1700
    """

    def __init__(self, module, server, platform="c7200"):
        Node.__init__(self, server)

        log.info("router {} is being created".format(platform))
        self._defaults = {}
        self._ports = []
        self._router_id = None
        self._inital_settings = None
        self._idlepcs = []
        self._module = module
        self._loading = False
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
                          "jit_sharing_group": None,
                          "disk0": 0,
                          "disk1": 0,
                          "confreg": '0x2102',
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
            else:
                port_name = port.longNameType() + str(slot_number) + "/" + str(port_number)
            new_port = port(port_name)
            new_port.setPortNumber(port_number)
            new_port.setSlotNumber(slot_number)
            self._ports.append(new_port)
            log.debug("port {} has been added".format(port_name))

    def _removeAdapterPorts(self, slot_number):
        """
        Removes ports when an adapter is removed from a slot.

        :param slot_number: slot number (integer)
        """

        for port in self._ports.copy():
            if port.slotNumber() == slot_number:
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
            new_port = port(port_name)
            new_port.setPortNumber(base + port_number)
            # WICs are always in adapter slot 0.
            new_port.setslotNumber(0)
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
            if port.slotNumber() == 0 and port.portNumber() in wic_ports_to_delete:
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
                        if port.slotNumber() == 0 and port.portNumber() == base + port_number:
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
                            else:
                                port.setName(port.longNameType() + "0/" + str(wic_port_number))
                            log.debug("port {} renamed to {}".format(old_name, port.name()))

    def delete(self):
        """
        Deletes this router.
        """

        log.debug("router {} is being deleted".format(self.name()))
        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        if self._router_id and self._server.connected():
            self._server.send_message("dynamips.vm.delete", {"id": self._router_id}, self._deleteCallback)
        else:
            self.deleted_signal.emit()
            self._module.removeNode(self)

    def _deleteCallback(self, result, error=False):
        """
        Callback for delete.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        log.info("router {} has been deleted".format(self.name()))
        self.deleted_signal.emit()
        self._module.removeNode(self)

    def setup(self, image, ram, name=None, initial_settings={}):
        """
        Setups this router.

        :param image: IOS image path
        :param ram: amount of RAM
        :param name: optional name for this router
        :param initial_settings: other additional and not mandatory settings
        """

        platform = self._settings["platform"]

        # Minimum settings to send to the server in order
        # to create a new router
        params = {"platform": platform,
                  "ram": ram,
                  "image": image}

        # add some initial settings
        if "console" in initial_settings:
            params["console"] = self._settings["console"] = initial_settings.pop("console")
        if "aux" in initial_settings:
            params["aux"] = self._settings["aux"] = initial_settings.pop("aux")
        if "mac_addr" in initial_settings:
            params["mac_addr"] = self._settings["mac_addr"] = initial_settings.pop("mac_addr")
        if "chassis" in initial_settings:
            params["chassis"] = self._settings["chassis"] = initial_settings.pop("chassis")

        # other initial settings will be applied when the router has been created
        if initial_settings:
            self._inital_settings = initial_settings

        # a name for this router is optional, the server
        # will create one if there is no name set.
        if name:
            params["name"] = self._settings["name"] = name

        self._server.send_message("dynamips.vm.create", params, self._setupCallback)

    def _setupCallback(self, result, error=False):
        """
        Callback for setup.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while setting up {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
            return

        self._router_id = result["id"]

        # update the settings using the defaults sent by the server
        for name, value in result.items():
            if name in self._settings and self._settings[name] != value:
                log.info("router setting up and updating {} from '{}' to '{}'".format(name, self._settings[name], value))
                self._settings[name] = value

        # insert default adapters
        for name, value in self._settings.items():
            if name.startswith("slot") and value:
                slot_number = int(name[-1])
                adapter = value
                self._addAdapterPorts(adapter, slot_number)

        # update the node with setup initial settings if any
        if self._inital_settings:
            self.update(self._inital_settings)
        elif self._loading:
            self.updated_signal.emit()
        else:
            self.setInitialized(True)
            log.debug("router {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)

    def _base64Config(self, config_path):
        """
        Get the base64 encoded config from a file.

        :param config_path: path to the configuration file.

        :returns: base64 encoded string
        """

        try:
            with open(config_path, "r") as f:
                log.info("opening configuration file: {}".format(config_path))
                config = f.read()
                config = '!\n' + config.replace('\r', "")
                encoded = ("").join(base64.encodestring(config.encode("utf-8")).decode("utf-8").split())
                return encoded
        except EnvironmentError as e:
            log.warn("could not base64 encode {}: {}".format(config_path, e))
            return ""

    def update(self, new_settings):
        """
        Updates the settings for this router.

        :param new_settings: settings dictionary
        """

        params = {"id": self._router_id}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        # push the startup-config
        if "startup_config" in new_settings and self._settings["startup_config"] != new_settings["startup_config"] \
        and os.path.exists(new_settings["startup_config"]):
            params["startup_config_base64"] = self._base64Config(new_settings["startup_config"])

        # push the private-config
        if "private_config" in new_settings and self._settings["private_config"] != new_settings["private_config"] \
        and os.path.exists(new_settings["private_config"]):
            params["private_config_base64"] = self._base64Config(new_settings["private_config"])

        log.debug("{} is updating settings: {}".format(self.name(), params))
        self._server.send_message("dynamips.vm.update", params, self._updateCallback)

    def _updateCallback(self, result, error=False):
        """
        Callback for update.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
            return

        updated = False
        for name, value in result.items():
            if name in self._settings and self._settings[name] != value:
                log.info("{}: updating {} from '{}' to '{}'".format(self.name(), name, self._settings[name], value))
                updated = True
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

        if self._inital_settings and not self._loading:
            self.setInitialized(True)
            log.info("router {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)
            self._inital_settings = None
        elif updated:
            log.info("router {} has been updated".format(self.name()))
            self.updated_signal.emit()

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
            self.setStatus(Node.started)
            for port in self._ports:
                # set ports as started
                port.setStatus(Port.started)
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
            self.setStatus(Node.stopped)
            for port in self._ports:
                # set ports as stopped
                port.setStatus(Port.stopped)
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
            self.setStatus(Node.suspended)
            for port in self._ports:
                # set ports as suspended
                port.setStatus(Port.suspended)
            self.suspended_signal.emit()

    def reload(self):
        """
        Reloads this router.
        """

        log.debug("{} is being reloaded".format(self.name()))
        self._server.send_message("dynamips.vm.reload", {"id": self._router_id}, self._reloadCallback)

    def _reloadCallback(self, result, error=False):
        """
        Callback for reload.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while suspending {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            log.info("{} has reloaded".format(self.name()))

    def computeIdlepcs(self):
        """
        Get idle-pc proposals
        """

        log.debug("{} is requesting idle-pc proposals".format(self.name()))
        self._server.send_message("dynamips.vm.idlepcs", {"id": self._router_id}, self._computeIdlepcsCallback)

    def _computeIdlepcsCallback(self, result, error=False):
        """
        Callback for computeIdlepc.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while computing idle-pc proposals {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            log.info("{} has received idle-pc proposals".format(self.name()))
            self._idlepcs = result["idlepcs"]
            self.idlepc_signal.emit()

    def idlepcs(self):
        """
        Returns previously computed idle-pc values.

        :returns: idle-pc values (list)
        """

        return self._idlepcs

    def idlepc(self):
        """
        Returns the current idle-pc value for this router.

        :returns: idlepc value (string)
        """

        return self._settings["idlepc"]

    def setIdlepc(self, idlepc):
        """
        Sets a new idle-pc value for this router.

        :param idlepc: idlepc value (string)
        """

        params = {"id": self._router_id,
                  "idlepc": idlepc}
        log.debug("{} is updating settings: {}".format(self.name(), params))
        self._server.send_message("dynamips.vm.update", params, self._updateCallback)
        self._module.updateImageIdlepc(self._settings["image"], idlepc)

    def allocateUDPPort(self, port_id):
        """
        Requests an UDP port allocation.

        :param port_id: port identifier
        """

        log.debug("{} is requesting an UDP port allocation".format(self.name()))
        self._server.send_message("dynamips.vm.allocate_udp_port", {"id": self._router_id, "port_id": port_id}, self._allocateUDPPortCallback)

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
            port_id = result["port_id"]
            lhost = result["lhost"]
            lport = result["lport"]
            log.debug("{} has allocated UDP port {} for host {}".format(self.name(), lport, lhost))
            self.allocate_udp_nio_signal.emit(self.id(), port_id, lport, lhost)

    def addNIO(self, port, nio):
        """
        Adds a new NIO on the specified port for this router.

        :param port: Port instance
        :param nio: NIO instance
        """

        nio_type = str(nio)
        params = {"id": self._router_id,
                  "nio": nio_type,
                  "slot": port.slotNumber(),
                  "port": port.portNumber(),
                  "port_id": port.id()}

        self.addNIOInfo(nio, params)
        log.debug("{} is adding an {}: {}".format(self.name(), nio_type, params))
        self._server.send_message("dynamips.vm.add_nio", params, self._addNIOCallback)

    def _addNIOCallback(self, result, error=False):
        """
        Callback for addNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while adding a NIO for {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
        else:
            log.debug("{} has added a new NIO: {}".format(self.name(), result))
            self.nio_signal.emit(self.id(), result["port_id"])

    def deleteNIO(self, port):
        """
        Deletes an NIO from the specified port on this router.

        :param port: Port instance
        """

        params = {"id": self._router_id,
                  "slot": port.slotNumber(),
                  "port": port.portNumber()}

        log.debug("{} is deleting an NIO: {}".format(self.name(), params))
        if self._server.connected():
            self._server.send_message("dynamips.vm.delete_nio", params, self._deleteNIOCallback)

    def _deleteNIOCallback(self, result, error=False):
        """
        Callback for deleteNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting NIO {}: {}".format(self.name(), result["message"]))
            self.error_signal.emit(self.name(), result["code"], result["message"])
            return

        log.debug("{} has deleted a NIO: {}".format(self.name(), result))

    def _saveConfig(self):
        """
        Tells the server to save the router configurations (startup-config and private-config).
        """

        params = {"id": self._router_id}
        log.debug("{} is saving his configuration: {}".format(self.name(), params))
        self._server.send_notification("dynamips.vm.save_config", params)

    def _slot_info(self):
        """
        Returns information about the slots/ports of this router.

        :returns: formated string
        """

        slot_info = ""
        for name, value in self._settings.items():
            if name.startswith("slot") and value != None:
                slot_number = int(name[-1])
                adapter_name = value
                nb_ports = ADAPTER_MATRIX[adapter_name]["nb_ports"]
                if nb_ports == 1:
                    port_string = ' port\n'
                else:
                    port_string = ' ports\n'

                slot_info = slot_info + '   slot ' + str(slot_number) + ' hardware is ' + adapter_name + ' with ' + str(nb_ports) + port_string

                port_names = {}
                for port in self._ports:
                    if port.slotNumber() == slot_number and port.portNumber() < 16:
                        port_names[port.name()] = port
                sorted_ports = sorted(port_names.keys())

                for port_name in sorted_ports:
                    port_info = port_names[port_name]
                    if port_info.isFree():
                        slot_info += '     ' + port_name + ' is empty\n'
                    else:
                        slot_info += '     ' + port_name + ' ' + port_info.description() + '\n'

            if name.startswith("wic") and value != None:
                wic_slot_number = int(name[-1])
                wic_name = value
                nb_ports = WIC_MATRIX[wic_name]["nb_ports"]
                if nb_ports == 1:
                    port_string = ' port\n'
                else:
                    port_string = ' ports\n'

                slot_info = slot_info + "   " + wic_name + " installed in WIC slot " + str(wic_slot_number) + " with " + str(nb_ports) + port_string

                base = 16 * (wic_slot_number + 1)
                port_names = {}
                for port_number in range(0, nb_ports):
                    for port in self._ports:
                        if port.slotNumber() == 0 and port.portNumber() == base + port_number:
                            port_names[port.name()] = port
                sorted_ports = sorted(port_names.keys())

                for port_name in sorted_ports:
                    port_info = port_names[port_name]
                    if port_info.isFree():
                        slot_info += '     ' + port_name + ' is empty\n'
                    else:
                        slot_info += '     ' + port_name + ' ' + port_info.description() + '\n'

        return slot_info

    def info(self):
        """
        Returns information about this router.

        :returns: formated string
        """

        platform = self._settings["platform"]
        router_specific_info = ""
        if platform == "c7200":
            router_specific_info = self._settings["midplane"] + " " + self._settings["npe"]
            router_specific_info = router_specific_info.upper()

        #get info about image and ghostios
        image_info = '\n  Image is '
#         if self.ghost_status == 2:
#             #we are running on ghost IOS
#             image_info = image_info + 'shared ' + self.ghost_file
#         else:
        image_info = image_info + self._settings["image"]

        jitsharing_group_info = '  JIT blocks sharing group is '
        if self._settings["jit_sharing_group"] != None:
            jitsharing_group_info = jitsharing_group_info + str(self._settings["jit_sharing_group"])
        else:
            jitsharing_group_info = '  No JIT blocks sharing enabled'

        #get info about idle-pc value
        idlepc_info = ""
        if not self._settings["idlepc"]:
            idlepc_info = ' with no idlepc value'
        else:
            idlepc_info = ' with idlepc value of ' + self._settings["idlepc"]# + '\n  idlemax value is ' + str(self.idlemax) + ', idlesleep is ' + str(self.idlesleep) + ' ms'

        #gather information about PA, their interfaces and connections
        slot_info = self._slot_info()

#         # Uptime of the router.
#         def utimetotxt(utime):
#             (zmin, zsec) = divmod(utime, 60)
#             (zhur, zmin) = divmod(zmin, 60)
#             (zday, zhur) = divmod(zhur, 24)
#             utxt = ('%d %s, ' % (zday, 'days'  if (zday != 1) else 'day')  if (zday > 0) else '') + \
#                    ('%d %s, ' % (zhur, 'hours' if (zhur != 1) else 'hour') if ((zhur > 0) or (zday > 0)) else '') + \
#                    ('%d %s' % (zmin, 'mins'  if (zmin != 1) else 'min'))
#             return utxt
# 
#         if (self.state == 'running'):
#             txtuptime = '  Router running time is ' + utimetotxt((int(time.time()) - self.starttime) - self.waittime) + '\n'
#         elif (self.state == 'suspended'):
#             txtuptime = '  Router suspended time is ' + utimetotxt(int(time.time()) - self.suspendtime) + '\n'
#         elif (self.state == 'stopped'):
#             txtuptime = '  Router stopped time is ' + utimetotxt(int(time.time()) - self.stoptime) + '\n'
#         else:
        txtuptime = '  Router uptime is unknown\n'

        self.state = "stopped"

        #create final output, with proper indentation
        return 'Router ' + self.name() + ' is ' + self.state + '\n' + '  Hardware is Dynamips emulated Cisco ' + platform + router_specific_info + ' with ' + \
               str(self._settings["ram"]) + ' MB RAM\n' + txtuptime + '  Router\'s server runs on ' + self._server.host + ":" + str(self._server.port) + \
               ', console is on port ' + str(self._settings["console"]) + ', aux is on port ' + str(self._settings["aux"]) + image_info + idlepc_info + '\n' + \
               jitsharing_group_info + '\n  ' + str(self._settings["nvram"]) + ' KB NVRAM, ' + str(self._settings["disk0"]) + \
               ' MB disk0 size, ' + str(self._settings["disk1"]) + ' MB disk1 size' + '\n' + slot_info

    def dump(self):
        """
        Returns a representation of this router
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """

        # tell the server to save the startup-config and
        # private-config
        self._saveConfig()

        router = {"id": self.id(),
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

        #TODO: handle the image path
        # router["properties"]["image"]

        return router

    def load(self, node_info):
        """
        Loads a router representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        self.node_info = node_info
        settings = node_info["properties"]
        name = settings.pop("name")
        image = settings.pop("image")
        ram = settings.get("ram", PLATFORMS_DEFAULT_RAM[self._settings["platform"]])
        self.updated_signal.connect(self._updatePortSettings)
        # block the created signal, it will be triggered when loading is completely done
        self._loading = True
        log.info("router {} is loading".format(name))
        self.setup(image, ram, name, settings)

    def _updatePortSettings(self):
        """
        Updates port settings when loading a topology.
        """

        # update the port with the correct names and IDs
        if "ports" in self.node_info:
            ports = self.node_info["ports"]
            for topology_port in ports:
                for port in self._ports:
                    if topology_port["port_number"] == port.portNumber() and topology_port["slot_number"] == port.slotNumber():
                        port.setName(topology_port["name"])
                        port.setId(topology_port["id"])

        # now we can set the node has initialized and trigger the signal
        self.setInitialized(True)
        log.info("router {} has been loaded".format(self.name()))
        self.created_signal.emit(self.id())
        self._module.addNode(self)
        self._inital_settings = None
        self._loading = False

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

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.routers]
