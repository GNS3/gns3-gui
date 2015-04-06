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
from gns3.vm import VM
from gns3.node import Node
from gns3.servers import Servers
from gns3.ports.ethernet_port import EthernetPort
from gns3.ports.serial_port import SerialPort
from gns3.utils.normalize_filename import normalize_filename
from .settings import IOU_DEVICE_SETTINGS

import logging
log = logging.getLogger(__name__)


class IOUDevice(VM):

    """
    IOU device.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "iou"

    def __init__(self, module, server, project):
        VM.__init__(self, server, server, project)

        log.info("IOU instance is being created")
        self._vm_id = None
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
                          "console": None,
                          "iourc_content": None}

        # self._occupied_slots = []
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
                new_port.setAdapterNumber(slot_number)
                new_port.setPacketCaptureSupported(True)
                # self._occupied_slots.append(slot_number)
                self._ports.append(new_port)
                log.debug("port {} has been added".format(port_name))

    def _removeAdapters(self, nb_ethernet_adapters, nb_serial_adapters):
        """
        Removes ports when an adapter is removed from a slot.

        :param slot_number: slot number (integer)
        """

        for port in self._ports.copy():
            if (port.adapterNumber() >= nb_ethernet_adapters and port.linkType() == "Ethernet") or \
                    (port.adapterNumber() >= nb_serial_adapters and port.linkType() == "Serial"):
                # self._occupied_slots.remove(port.adapterNumber())
                self._ports.remove(port)
                log.info("port {} has been removed".format(port.name()))

    def setup(self, iou_path, name=None, console=None, vm_id=None, initial_settings={}, base_name="IOU", initial_config=None):
        """
        Setups this IOU device.

        :param iou_path: path to an IOU image
        :param name: optional name
        :param console: optional TCP console port
        :param initial_config: path to initial configuration file
        """

        # let's create a unique name if none has been chosen
        if not name:
            name = self.allocateName(base_name)

        if not name:
            self.error_signal.emit(self.id(), "could not allocate a name for this IOU device")
            return

        self._settings["name"] = name
        params = {"name": name,
                  "path": iou_path}

        if vm_id:
            params["vm_id"] = vm_id

        if console:
            params["console"] = self._settings["console"] = console

        if "cloud_path" in initial_settings:
            params["cloud_path"] = self._settings["cloud_path"] = initial_settings.pop("cloud_path")

        # other initial settings will be applied when the router has been created
        if initial_settings:
            self._inital_settings = initial_settings
        else:
            self._inital_settings = {}

        if initial_config:
            params["initial_config_content"] = self._readBaseConfig(initial_config)

        if len(self._module._settings["iourc_path"]) > 0:
            try:
                with open(self._module._settings["iourc_path"], 'rb') as f:
                    self._inital_settings["iourc_content"] = f.read().decode("utf-8")
            except OSError as e:
                print("Can't open iourc file {}: {}".format(self._module._settings["iourc_path"], e))
        self.httpPost("/iou/vms", self._setupCallback, body=params)

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
        if not self._vm_id:
            self.error_signal.emit(self.id(), "returned ID from server is null")
            return

        # update the settings using the defaults sent by the server
        for name, value in result.items():
            if name in self._settings and self._settings[name] != value:
                log.info("IOU instance {} setting up and updating {} from '{}' to '{}'".format(self.name(),
                                                                                               name,
                                                                                               self._settings[name],
                                                                                               value))
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

    def update(self, new_settings):
        """
        Updates the settings for this IOU device.

        :param new_settings: settings dictionary
        """

        if "name" in new_settings and new_settings["name"] != self.name() and self.hasAllocatedName(new_settings["name"]):
            self.error_signal.emit(self.id(), 'Name "{}" is already used by another node'.format(new_settings["name"]))
            return

        params = {}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        if "initial_config" in new_settings and self._settings["initial_config"] != new_settings["initial_config"]:
            params["initial_config_content"] = self._readBaseConfig(new_settings["initial_config"])
            del params["initial_config"]

        log.debug("{} is updating settings: {}".format(self.name(), params))
        self.httpPut("/iou/vms/{vm_id}".format(vm_id=self._vm_id), self._updateCallback, body=params)

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
            # TODO: dynamically add/remove adapters
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
        self.httpPost("/iou/vms/{vm_id}/adapters/{adapter_number}/ports/{port_number}/start_capture".format(
            vm_id=self._vm_id,
            adapter_number=port.adapterNumber(),
            port_number=port.portNumber()
        ),
            self._startPacketCaptureCallback,
            body=params,
            context={
            "port": port
        })

    def _startPacketCaptureCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for starting a packet capture.

        :param result: server response
        :param error: indicates an error (boolean)
        :param context: Pass a context to the response callback
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
        self.httpPost("/iou/vms/{vm_id}/adapters/{adapter_number}/ports/{port_number}/stop_capture".format(
            vm_id=self._vm_id,
            adapter_number=port.adapterNumber(),
            port_number=port.portNumber()
        ),
            self._stopPacketCaptureCallback,
            context={
            "port": port
        })

    def _stopPacketCaptureCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for stopping a packet capture.

        :param result: server response
        :param error: indicates an error (boolean)
        :param context: Pass a context to the response callback
        """

        if error:
            log.error("error while stopping capture {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            port = context["port"]
            log.info("{} has successfully stopped capturing packets on {}".format(self.name(), port.name()))
            port.stopPacketCapture()
            self.updated_signal.emit()

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
  Node ID is {id}, server's IOU device ID is {vm_id}
  Hardware is Cisco IOU generic device with {memories_info}
  Device's server runs on {host}:{port}, console is on port {console}
  Image is {image_name}
  {nb_ethernet} Ethernet adapters and {nb_serial} serial adapters installed
""".format(name=self.name(),
           id=self.id(),
           vm_id=self._vm_id,
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
               "vm_id": self._vm_id,
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

        return iou

    def _imageFilesDir(self):
        """
        Returns the location of IOU images.
        """

        servers = Servers.instance()
        local_server = servers.localServerSettings()
        return os.path.join(local_server["images_path"], "IOU")

    def load(self, node_info):
        """
        Loads an IOU device representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        self.node_info = node_info
        # for backward compatibility
        vm_id = node_info.get("iou_id")
        if not vm_id:
            vm_id = node_info["vm_id"]
        settings = node_info["properties"]
        name = settings.pop("name")
        path = settings.pop("path")

        if self.server().isLocal():
            # check and update the path to use the image in the images directory
            updated_path = os.path.join(self._imageFilesDir(), path)
            if os.path.isfile(updated_path):
                path = updated_path
            elif not os.path.isfile(path):
                path = self._module.findAlternativeIOUImage(path)

        console = settings.pop("console", None)
        self.updated_signal.connect(self._updatePortSettings)
        # block the created signal, it will be triggered when loading is completely done
        self._loading = True
        log.info("iou device {} is loading".format(name))
        self.setName(name)
        self.setup(path, name, console, vm_id, settings)

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

        self.httpGet("/iou/vms/{vm_id}/initial_config".format(
            vm_id=self._vm_id,
        ),
            self._exportConfigCallback,
            context={
            "path": config_export_path
        })

    def _exportConfigCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for exportConfig.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        path = context["path"]
        if error:
            log.error("error while exporting {} initial-config: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            if "content" in result is not None:
                try:
                    with open(path, "wb") as f:
                        log.info("saving {} initial-config to {}".format(self.name(), path))
                        f.write(result["content"].encode("utf-8"))
                except OSError as e:
                    self.error_signal.emit(self.id(), "Could not export initial-config to {}: {}".format(path, e))

    def exportConfigToDirectory(self, directory):
        """
        Exports the initial-config to a directory.

        :param directory: destination directory path
        """

        self.httpGet("/iou/vms/{vm_id}/initial_config".format(
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

        export_directory = context["directory"]
        if error:
            log.error("error while exporting {} initial-config: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:

            if "content" in result:
                config_path = os.path.join(export_directory, normalize_filename(self.name())) + "_initial-config.cfg"
                try:
                    with open(config_path, "wb") as f:
                        log.info("saving {} initial-config to {}".format(self.name(), config_path))
                        f.write(result["content"].encode("utf-8"))
                except OSError as e:
                    self.error_signal.emit(self.id(), "could not export initial-config to {}: {}".format(config_path, e))

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
