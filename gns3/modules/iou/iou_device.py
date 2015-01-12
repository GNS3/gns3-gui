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
IOU device implementation.
"""

import os
import re
import base64
from gns3.node import Node
from gns3.ports.port import Port
from gns3.ports.ethernet_port import EthernetPort
from gns3.ports.serial_port import SerialPort
from gns3.utils.normalize_filename import normalize_filename
from .settings import IOU_DEVICE_SETTINGS

import logging
log = logging.getLogger(__name__)


class IOUDevice(Node):
    """
    IOU device.

    :param module: parent module for this node
    :param server: GNS3 server instance
    """

    def __init__(self, module, server):
        Node.__init__(self, server)

        log.info("IOU instance is being created")
        self._iou_id = None
        self._defaults = {}
        self._inital_settings = None
        self._loading = False
        self._module = module
        self._export_directory = None
        self._ports = []
        self._settings = {"name": "",
                          "path": "",
                          "initial_config": "",
                          "l1_keepalives": False,
                          "use_default_iou_values": IOU_DEVICE_SETTINGS["use_default_iou_values"],
                          "ram": IOU_DEVICE_SETTINGS["ram"],
                          "nvram": IOU_DEVICE_SETTINGS["nvram"],
                          "ethernet_adapters": IOU_DEVICE_SETTINGS["ethernet_adapters"],
                          "serial_adapters": IOU_DEVICE_SETTINGS["serial_adapters"],
                          "console": None}

        #self._occupied_slots = []
        self._addAdapters(2, 2)

        # save the default settings
        self._defaults = self._settings.copy()

    def _addAdapters(self, nb_ethernet_adapters, nb_serial_adapters):
        """
        Adds ports based on what adapter is inserted in which slot.

        :param adapter: adapter name
        :param slot_number: slot number (integer)
        """

        nb_adapters = nb_ethernet_adapters + nb_serial_adapters
        for slot_number in range(0, nb_adapters):
#             if slot_number in self._occupied_slots:
#                 continue
            for port_number in range(0, 4):
                if slot_number < nb_ethernet_adapters:
                    port = EthernetPort
                else:
                    port = SerialPort
                port_name = port.longNameType() + str(slot_number) + "/" + str(port_number)
                short_name = port.shortNameType() + str(slot_number) + "/" + str(port_number)
                new_port = port(port_name)
                new_port.setShortName(short_name)
                new_port.setPortNumber(port_number)
                new_port.setSlotNumber(slot_number)
                new_port.setPacketCaptureSupported(True)
                #self._occupied_slots.append(slot_number)
                self._ports.append(new_port)
                log.debug("port {} has been added".format(port_name))

    def _removeAdapters(self, nb_ethernet_adapters, nb_serial_adapters):
        """
        Removes ports when an adapter is removed from a slot.

        :param slot_number: slot number (integer)
        """

        for port in self._ports.copy():
            if (port.slotNumber() >= nb_ethernet_adapters and port.linkType() == "Ethernet") or \
                (port.slotNumber() >= nb_serial_adapters and port.linkType() == "Serial"):
                #self._occupied_slots.remove(port.slotNumber())
                self._ports.remove(port)
                log.info("port {} has been removed".format(port.name()))

    def setup(self, iou_path, name=None, console=None, iou_id=None, initial_settings={}, base_name="IOU"):
        """
        Setups this IOU device.

        :param iou_path: path to an IOU image
        :param name: optional name
        :param console: optional TCP console port
        """

        # let's create a unique name if none has been chosen
        if not name:
            name = self.allocateName(base_name)

        if not name:
            self.error_signal.emit(self.id(), "could not allocate a name for this IOU device")
            return

        params = {"name": name,
                  "path": iou_path}

        if iou_id:
            params["iou_id"] = iou_id

        if console:
            params["console"] = self._settings["console"] = console

        if "cloud_path" in initial_settings:
            params["cloud_path"] = self._settings["cloud_path"] = initial_settings.pop("cloud_path")

        # other initial settings will be applied when the router has been created
        if initial_settings:
            self._inital_settings = initial_settings

        self._server.send_message("iou.create", params, self._setupCallback)

    def _setupCallback(self, result, error=False):
        """
        Callback for setup.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while setting up {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
            return

        self._iou_id = result["id"]
        if not self._iou_id:
            self.error_signal.emit(self.id(), "returned ID from server is null")
            return

        # update the settings using the defaults sent by the server
        for name, value in result.items():
            if name in self._settings and self._settings[name] != value:
                log.info("IOU instance setting up and updating {} from '{}' to '{}'".format(name, self._settings[name], value))
                self._settings[name] = value

        # update the node with setup initial settings if any
        if self._inital_settings:
            self.update(self._inital_settings)
        elif self._loading:
            self.updated_signal.emit()
        else:
            self.setInitialized(True)
            log.info("IOU instance {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)

    def delete(self):
        """
        Deletes this IOU instance.
        """

        log.debug("IOU device {} is being deleted".format(self.name()))
        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        if self._iou_id:
            self._server.send_message("iou.delete", {"id": self._iou_id}, self._deleteCallback)
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
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        log.info("{} has been deleted".format(self.name()))
        self.deleted_signal.emit()
        self._module.removeNode(self)

    def _base64Config(self, config_path):
        """
        Get the base64 encoded config from a file.

        :param config_path: path to the configuration file.

        :returns: base64 encoded string
        """

        try:
            with open(config_path, "r", errors="replace") as f:
                log.info("opening configuration file: {}".format(config_path))
                config = f.read()
                config = '!\n' + config.replace('\r', "")
                encoded = "".join(base64.encodestring(config.encode("utf-8")).decode("utf-8").split())
                return encoded
        except OSError as e:
            log.warn("could not base64 encode {}: {}".format(config_path, e))
            return ""

    def update(self, new_settings):
        """
        Updates the settings for this IOU device.

        :param new_settings: settings dictionary
        """

        if "name" in new_settings and new_settings["name"] != self.name() and self.hasAllocatedName(new_settings["name"]):
            self.error_signal.emit(self.id(), 'Name "{}" is already used by another node'.format(new_settings["name"]))
            return

        params = {"id": self._iou_id}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        if "initial_config" in new_settings and self._settings["initial_config"] != new_settings["initial_config"] \
        and not self.server().isLocal() and os.path.isfile(new_settings["initial_config"]):
            params["initial_config_base64"] = self._base64Config(new_settings["initial_config"])

        log.debug("{} is updating settings: {}".format(self.name(), params))
        self._server.send_message("iou.update", params, self._updateCallback)

    def _updateCallback(self, result, error=False):
        """
        Callback for update.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
            return

        updated = False
        nb_adapters_changed = False
        for name, value in result.items():
            if name in self._settings and self._settings[name] != value:
                log.info("{}: updating {} from '{}' to '{}'".format(self.name(), name, self._settings[name], value))
                updated = True
                if name == "ethernet_adapters" or name == "serial_adapters":
                    nb_adapters_changed = True
                if name == "name":
                    # update the node name
                    self.updateAllocatedName(value)
                self._settings[name] = value

        if nb_adapters_changed:
            log.debug("number of adapters has changed: Ethernet={} Serial={}".format(self._settings["ethernet_adapters"], self._settings["serial_adapters"]))
            #TODO: dynamically add/remove adapters
            self._ports.clear()
            self._addAdapters(self._settings["ethernet_adapters"], self._settings["serial_adapters"])

        if self._inital_settings and not self._loading:
            self.setInitialized(True)
            log.info("IOU device {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)
            self._inital_settings = None
        elif updated or self._loading:
            log.info("IOU device {} has been updated".format(self.name()))
            self.updated_signal.emit()

    def start(self):
        """
        Starts this IOU instance.
        """

        if self.status() == Node.started:
            log.debug("{} is already running".format(self.name()))
            return

        log.debug("{} is starting".format(self.name()))
        self._server.send_message("iou.start", {"id": self._iou_id}, self._startCallback)

    def _startCallback(self, result, error=False):
        """
        Callback for start.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while starting {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:
            log.info("{} has started".format(self.name()))
            self.setStatus(Node.started)
            for port in self._ports:
                # set ports as started
                port.setStatus(Port.started)
            self.started_signal.emit()

    def stop(self):
        """
        Stops this IOU instance.
        """

        if self.status() == Node.stopped:
            log.debug("{} is already stopped".format(self.name()))
            return

        log.debug("{} is stopping".format(self.name()))
        self._server.send_message("iou.stop", {"id": self._iou_id}, self._stopCallback)

    def _stopCallback(self, result, error=False):
        """
        Callback for stop.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while stopping {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:
            log.info("{} has stopped".format(self.name()))
            self.setStatus(Node.stopped)
            for port in self._ports:
                # set ports as stopped
                port.setStatus(Port.stopped)
            self.stopped_signal.emit()

    def reload(self):
        """
        Reloads this IOU instance.
        """

        log.debug("{} is being reloaded".format(self.name()))
        self._server.send_message("iou.reload", {"id": self._iou_id}, self._reloadCallback)

    def _reloadCallback(self, result, error=False):
        """
        Callback for reload.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while suspending {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:
            log.info("{} has reloaded".format(self.name()))

    def allocateUDPPort(self, port_id):
        """
        Requests an UDP port allocation.

        :param port_id: port identifier
        """

        log.debug("{} is requesting an UDP port allocation".format(self.name()))
        self._server.send_message("iou.allocate_udp_port", {"id": self._iou_id, "port_id": port_id}, self._allocateUDPPortCallback)

    def _allocateUDPPortCallback(self, result, error=False):
        """
        Callback for allocateUDPPort.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while allocating an UDP port for {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:
            port_id = result["port_id"]
            lport = result["lport"]
            log.debug("{} has allocated UDP port {}".format(self.name(), port_id, lport))
            self.allocate_udp_nio_signal.emit(self.id(), port_id, lport)

    def addNIO(self, port, nio):
        """
        Adds a new NIO on the specified port for this IOU instance.

        :param port: Port instance
        :param nio: NIO instance
        """

        params = {"id": self._iou_id,
                  "slot": port.slotNumber(),
                  "port": port.portNumber(),
                  "port_id": port.id()}

        params["nio"] = self.getNIOInfo(nio)
        log.debug("{} is adding an {}: {}".format(self.name(), nio, params))
        self._server.send_message("iou.add_nio", params, self._addNIOCallback)

    def _addNIOCallback(self, result, error=False):
        """
        Callback for addNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while adding an UDP NIO for {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
            self.nio_cancel_signal.emit(self.id())
        else:
            self.nio_signal.emit(self.id(), result["port_id"])

    def deleteNIO(self, port):
        """
        Deletes an NIO from the specified port on this IOU instance

        :param port: Port instance
        """

        params = {"id": self._iou_id,
                  "port": port.portNumber(),
                  "slot": port.slotNumber()}

        log.debug("{} is deleting an NIO: {}".format(self.name(), params))
        self._server.send_message("iou.delete_nio", params, self._deleteNIOCallback)

    def _deleteNIOCallback(self, result, error=False):
        """
        Callback for deleteNIO.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting NIO {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
            return

        log.debug("{} has deleted a NIO: {}".format(self.name(), result))

    def startPacketCapture(self, port, capture_file_name, data_link_type):
        """
        Starts a packet capture.

        :param port: Port instance
        :param capture_file_name: PCAP capture file path
        :param data_link_type: PCAP data link type
        """

        params = {"id": self._iou_id,
                  "port_id": port.id(),
                  "port": port.portNumber(),
                  "slot": port.slotNumber(),
                  "capture_file_name": capture_file_name,
                  "data_link_type": data_link_type}

        log.debug("{} is starting a packet capture on {}: {}".format(self.name(), port.name(), params))
        self._server.send_message("iou.start_capture", params, self._startPacketCaptureCallback)

    def _startPacketCaptureCallback(self, result, error=False):
        """
        Callback for starting a packet capture.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while starting capture {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:
            for port in self._ports:
                if port.id() == result["port_id"]:
                    log.info("{} has successfully started capturing packets on {}".format(self.name(), port.name()))
                    try:
                        port.startPacketCapture(result["capture_file_path"])
                    except OSError as e:
                        self.error_signal.emit(self.id(), "could not start the packet capture reader: {}: {}".format(e, e.filename))
                    self.updated_signal.emit()
                    break

    def stopPacketCapture(self, port):
        """
        Stops a packet capture.

        :param port: Port instance
        """

        params = {"id": self._iou_id,
                  "port_id": port.id(),
                  "port": port.portNumber(),
                  "slot": port.slotNumber()}

        log.debug("{} is stopping a packet capture on {}: {}".format(self.name(), port.name(), params))
        self._server.send_message("iou.stop_capture", params, self._stopPacketCaptureCallback)

    def _stopPacketCaptureCallback(self, result, error=False):
        """
        Callback for stopping a packet capture.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while stopping capture {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:
            for port in self._ports:
                if port.id() == result["port_id"]:
                    log.info("{} has successfully stopped capturing packets on {}".format(self.name(), port.name()))
                    port.stopPacketCapture()
                    self.updated_signal.emit()
                    break

    def info(self):
        """
        Returns information about this IOU device.

        :returns: formated string
        """

        if self.status() == Node.started:
            state = "started"
        else:
            state = "stopped"

        if self._settings["use_default_iou_values"]:
            memories_info = "default RAM and NVRAM IOU values"
        else:
            memories_info = "{ram} MB RAM and {nvram} KB NVRAM".format(ram=self._settings["ram"],
                                                                       nvram=self._settings["nvram"])

        info = """Device {name} is {state}
  Node ID is {id}, server's IOU device ID is {iou_id}
  Hardware is Cisco IOU generic device with {memories_info}
  Device's server runs on {host}:{port}, console is on port {console}
  Image is {image_name}
  {nb_ethernet} Ethernet adapters and {nb_serial} serial adapters installed
""".format(name=self.name(),
           id=self.id(),
           iou_id=self._iou_id,
           state=state,
           memories_info=memories_info,
           host=self._server.host,
           port=self._server.port,
           console=self._settings["console"],
           image_name=os.path.basename(self._settings["path"]),
           nb_ethernet=self._settings["ethernet_adapters"],
           nb_serial=self._settings["serial_adapters"])

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "     {port_name} is empty\n".format(port_name=port.name())
            else:
                port_info += "     {port_name} {port_description}\n".format(port_name=port.name(),
                                                                            port_description=port.description())

        return info + port_info

    def dump(self):
        """
        Returns a representation of this IOU device.
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """

        iou = {"id": self.id(),
               "iou_id": self._iou_id,
               "type": self.__class__.__name__,
               "description": str(self),
               "properties": {},
               "server_id": self._server.id()}

        # add the properties
        for name, value in self._settings.items():
            if name in self._defaults and self._defaults[name] != value:
                iou["properties"][name] = value

        # add the ports
        if self._ports:
            ports = iou["ports"] = []
            for port in self._ports:
                ports.append(port.dump())

        # make the IOU path relative
        image_path = iou["properties"]["path"]
        if self.server().isLocal():
            if os.path.commonprefix([image_path, self._module.imageFilesDir()]) == self._module.imageFilesDir():
                # save only the image name if it is stored the images directory
                iou["properties"]["path"] = os.path.basename(image_path)
        else:
            iou["properties"]["path"] = image_path

        return iou

    def load(self, node_info):
        """
        Loads an IOU device representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        self.node_info = node_info
        iou_id = node_info.get("iou_id")
        settings = node_info["properties"]
        name = settings.pop("name")
        path = settings.pop("path")

        if self.server().isLocal():
            # check and update the path to use the image in the images directory
            updated_path = os.path.join(self._module.imageFilesDir(), path)
            if os.path.isfile(updated_path):
                path = updated_path
            elif not os.path.isfile(path):
                path = self._module.findAlternativeIOUImage(path)

        console = settings.pop("console")
        self.updated_signal.connect(self._updatePortSettings)
        # block the created signal, it will be triggered when loading is completely done
        self._loading = True
        log.info("iou device {} is loading".format(name))
        self.setName(name)
        self.setup(path, name, console, iou_id, settings)

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
                    if topology_port["port_number"] == port.portNumber() and topology_port["slot_number"] == port.slotNumber():
                        port.setName(topology_port["name"])
                        port.setId(topology_port["id"])

        # now we can set the node has initialized and trigger the signal
        self.setInitialized(True)
        log.info("IOU device {} has been loaded".format(self.name()))
        self.created_signal.emit(self.id())
        self._module.addNode(self)
        self._inital_settings = None
        self._loading = False

    def exportConfig(self, config_export_path):
        """
        Exports the initial-config

        :param config_export_path: export path for the initial-config
        """

        self._config_export_path = config_export_path
        self._server.send_message("iou.export_config", {"id": self._iou_id}, self._exportConfigCallback)

    def _exportConfigCallback(self, result, error=False):
        """
        Callback for exportConfig.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while exporting {} initial-config: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:

            if "initial_config_base64" in result and self._config_export_path:
                config = base64.decodebytes(result["initial_config_base64"].encode("utf-8"))
                try:
                    with open(self._config_export_path, "wb") as f:
                        log.info("saving {} initial-config to {}".format(self.name(), self._config_export_path))
                        f.write(config)
                except OSError as e:
                    self.error_signal.emit(self.id(), "could not export initial-config to {}: {}".format(self._config_export_path, e))

    def exportConfigToDirectory(self, directory):
        """
        Exports the initial-config to a directory.

        :param directory: destination directory path
        """

        self._export_directory = directory
        self._server.send_message("iou.export_config", {"id": self._iou_id}, self._exportConfigToDirectoryCallback)

    def _exportConfigToDirectoryCallback(self, result, error=False):
        """
        Callback for exportConfigToDirectory.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while exporting {} initial-config: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["code"], result["message"])
        else:

            if "initial_config_base64" in result:
                config_path = os.path.join(self._export_directory, normalize_filename(self.name())) + "_initial-config.cfg"
                config = base64.decodebytes(result["initial_config_base64"].encode("utf-8"))
                try:
                    with open(config_path, "wb") as f:
                        log.info("saving {} initial-config to {}".format(self.name(), config_path))
                        f.write(config)
                except OSError as e:
                    self.error_signal.emit(self.id(), "could not export initial-config to {}: {}".format(config_path, e))

            self._export_directory = None

    def importConfig(self, path):
        """
        Imports an initial-config.

        :param path: path to the initial config
        """

        new_settings = {"initial_config": path}
        self.update(new_settings)

    def importConfigFromDirectory(self, directory):
        """
        Imports an initial-config from a directory.

        :param directory: source directory path
        """

        contents = os.listdir(directory)
        initial_config = normalize_filename(self.name()) + "_initial-config.cfg"
        new_settings = {}
        if initial_config in contents:
            new_settings["initial_config"] = os.path.join(directory, initial_config)
        else:
            self.warning_signal.emit(self.id(), "no initial-config file could be found, expected file name: {}".format(initial_config))
        if new_settings:
            self.update(new_settings)

    def name(self):
        """
        Returns the name of this IOU device.

        :returns: name (string)
        """

        return self._settings["name"]

    def settings(self):
        """
        Returns all this IOU device settings.

        :returns: settings dictionary
        """

        return self._settings

    def ports(self):
        """
        Returns all the ports for this IOU device.

        :returns: list of Port instances
        """

        return self._ports

    def console(self):
        """
        Returns the console port for this IOU device.

        :returns: port (integer)
        """

        return self._settings["console"]

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node configurator.

        :returns: QWidget object
        """

        from .pages.iou_device_configuration_page import iouDeviceConfigurationPage
        return iouDeviceConfigurationPage

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
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/multilayer_switch.normal.svg"

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when this node is hovered.

        :returns: symbol path (or resource).
        """

        return ":/symbols/multilayer_switch.selected.svg"

    @staticmethod
    def symbolName():

        return "IOU device"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.routers, Node.switches]

    def __str__(self):

        return "IOU device"
