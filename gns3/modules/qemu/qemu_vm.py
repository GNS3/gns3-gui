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
QEMU VM implementation.
"""

from gns3.vm import VM
from gns3.node import Node
from gns3.ports.port import Port
from gns3.ports.ethernet_port import EthernetPort
from .settings import QEMU_VM_SETTINGS

import logging
log = logging.getLogger(__name__)


class QemuVM(VM):

    """
    QEMU VM.

    :param module: parent module for this node
    :param server: GNS3 server instance
    """
    URL_PREFIX = "qemu"

    def __init__(self, module, server, project):
        VM.__init__(self, module, server, project)

        log.info("QEMU VM instance is being created")
        self._defaults = {}
        self._inital_settings = None
        self._export_directory = None
        self._loading = False
        self._module = module
        self._ports = []

        self._settings = {"name": "",
                          "qemu_path": "",
                          "hda_disk_image": "",
                          "hdb_disk_image": "",
                          "hdc_disk_image": "",
                          "hdd_disk_image": "",
                          "options": "",
                          "ram": QEMU_VM_SETTINGS["ram"],
                          "console": None,
                          "adapters": QEMU_VM_SETTINGS["adapters"],
                          "adapter_type": QEMU_VM_SETTINGS["adapter_type"],
                          "legacy_networking": QEMU_VM_SETTINGS["legacy_networking"],
                          "cpu_throttling": QEMU_VM_SETTINGS["cpu_throttling"],
                          "process_priority": QEMU_VM_SETTINGS["process_priority"],
                          "initrd": "",
                          "kernel_image": "",
                          "kernel_command_line": ""}

        self._addAdapters(1)

        # save the default settings
        self._defaults = self._settings.copy()

    def _addAdapters(self, adapters):
        """
        Adds adapters.

        :param adapters: number of adapters
        """

        for adapter_number in range(0, adapters):
            adapter_name = EthernetPort.longNameType() + str(adapter_number)
            short_name = EthernetPort.shortNameType() + str(adapter_number)
            new_port = EthernetPort(adapter_name)
            new_port.setShortName(short_name)
            new_port.setAdapterNumber(adapter_number)
            new_port.setPortNumber(0)
            self._ports.append(new_port)
            log.debug("Adapter {} has been added".format(adapter_name))

    def setup(self, qemu_path, name=None, console=None, vm_id=None, initial_settings={}, base_name=None):
        """
        Setups this QEMU VM.

        :param name: optional name
        :param vm_id: VM identifier
        """

        # let's create a unique name if none has been chosen
        if not name:
            name = self.allocateName(base_name + "-")

        if not name:
            self.error_signal.emit(self.id(), "could not allocate a name for this QEMU VM")
            return

        self._settings["name"] = name
        params = {"name": name,
                  "qemu_path": qemu_path}

        if console:
            params["console"] = self._settings["console"] = console

        if vm_id:
            params["vm_id"] = vm_id

        # other initial settings will be applied when the router has been created
        if initial_settings:
            self._inital_settings = initial_settings

        self.httpPost("/qemu/vms", self._setupCallback, body=params)

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
                log.info("QEMU VM instance {} setting up and updating {} from '{}' to '{}'".format(self.name(),
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
            log.info("QEMU VM instance {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)

    def delete(self):
        """
        Deletes this QEMU VM instance.
        """

        log.debug("QEMU VM instance {} is being deleted".format(self.name()))
        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        if self._vm_id:
            self.httpDelete("/qemu/vms/{vm_id}".format(vm_id=self._vm_id), self._deleteCallback)
        else:
            self.deleted_signal.emit()
            self._module.removeNode(self)

    def _deleteCallback(self, result, error=False, **kwargs):
        """
        Callback for delete.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        log.info("{} has been deleted".format(self.name()))
        self.deleted_signal.emit()
        self._module.removeNode(self)

    def update(self, new_settings):
        """
        Updates the settings for this QEMU VM.

        :param new_settings: settings dictionary
        """

        if "name" in new_settings and new_settings["name"] != self.name() and self.hasAllocatedName(new_settings["name"]):
            self.error_signal.emit(self.id(), 'Name "{}" is already used by another node'.format(new_settings["name"]))
            return

        params = {}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        if "cloud_path" in new_settings:
            params["cloud_path"] = self._settings["cloud_path"] = new_settings.pop("cloud_path")

        log.debug("{} is updating settings: {}".format(self.name(), params))
        self.httpPut("/qemu/vms/{vm_id}".format(vm_id=self._vm_id), self._updateCallback, body=params)

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
                if name == "name":
                    # update the node name
                    self.updateAllocatedName(value)
                if name == "adapters":
                    nb_adapters_changed = True
                self._settings[name] = value

        if nb_adapters_changed:
            log.debug("number of adapters has changed to {}".format(self._settings["adapters"]))
            # TODO: dynamically add/remove adapters
            self._ports.clear()
            self._addAdapters(self._settings["adapters"])

        if self._inital_settings and not self._loading:
            self.setInitialized(True)
            log.info("QEMU VM {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)
            self._inital_settings = None
        elif updated or self._loading:
            log.info("QEMU VM {} has been updated".format(self.name()))
            self.updated_signal.emit()

    def start(self):
        """
        Starts this QEMU VM instance.
        """

        if self.status() == Node.started:
            log.debug("{} is already running".format(self.name()))
            return

        log.debug("{} is starting".format(self.name()))
        self.httpPost("/qemu/vms/{vm_id}/start".format(vm_id=self._vm_id), self._startCallback)

    def _startCallback(self, result, error=False, **kwargs):
        """
        Callback for start.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while starting {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{} has started".format(self.name()))
            self.setStatus(Node.started)
            for port in self._ports:
                # set ports as started
                port.setStatus(Port.started)
            self.started_signal.emit()

    def stop(self):
        """
        Stops this QEMU VM instance.
        """

        if self.status() == Node.stopped:
            log.debug("{} is already stopped".format(self.name()))
            return

        log.debug("{} is stopping".format(self.name()))
        self.httpPost("/qemu/vms/{vm_id}/stop".format(vm_id=self._vm_id), self._stopCallback)

    def _stopCallback(self, result, error=False, **kwargs):
        """
        Callback for stop.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while stopping {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{} has stopped".format(self.name()))
            self.setStatus(Node.stopped)
            for port in self._ports:
                # set ports as stopped
                port.setStatus(Port.stopped)
            self.stopped_signal.emit()

    def suspend(self):
        """
        Suspends this QEMU VM instance.
        """

        if self.status() == Node.suspended:
            log.debug("{} is already suspended".format(self.name()))
            return

        log.debug("{} is being suspended".format(self.name()))
        self.httpPost("/qemu/vms/{vm_id}/suspend".format(vm_id=self._vm_id), self._suspendCallback)

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

    def reload(self):
        """
        Reloads this QEMU VM instance.
        """

        log.debug("{} is being reloaded".format(self.name()))
        self.httpPost("/qemu/vms/{vm_id}/reload".format(vm_id=self._vm_id), self._reloadCallback)

    def _reloadCallback(self, result, error=False, **kwargs):
        """
        Callback for reload.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while reloading {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{} has reloaded".format(self.name()))

    def dump(self):
        """
        Returns a representation of this QEMU VM instance.
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """

        qemu_vm = {"id": self.id(),
                   "vm_id": self._vm_id,
                   "type": self.__class__.__name__,
                   "description": str(self),
                   "properties": {},
                   "server_id": self._server.id()}

        # add the properties
        for name, value in self._settings.items():
            if name in self._defaults and self._defaults[name] != value:
                qemu_vm["properties"][name] = value

        # add the ports
        if self._ports:
            ports = qemu_vm["ports"] = []
            for port in self._ports:
                ports.append(port.dump())

        return qemu_vm

    def info(self):
        """
        Returns information about this QEMU VM instance.

        :returns: formated string
        """

        if self.status() == Node.started:
            state = "started"
        else:
            state = "stopped"

        info = """QEMU VM {name} is {state}
  Node ID is {id}, server's QEMU VM ID is {vm_id}
  QEMU VM's server runs on {host}:{port}, console is on port {console}
""".format(name=self.name(),
           id=self.id(),
           vm_id=self._vm_id,
           state=state,
           host=self._server.host,
           port=self._server.port,
           console=self._settings["console"])

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "     {port_name} is empty\n".format(port_name=port.name())
            else:
                port_info += "     {port_name} {port_description}\n".format(port_name=port.name(),
                                                                            port_description=port.description())

        return info + port_info

    def load(self, node_info):
        """
        Loads a QEMU VM representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        self.node_info = node_info
        # for backward compatibility
        vm_id = node_info.get("qemu_id")
        if not vm_id:
            vm_id = node_info["vm_id"]
        settings = node_info["properties"]
        name = settings.pop("name")
        qemu_path = settings.pop("qemu_path")
        console = settings.pop("console", self._defaults["console"])
        self.updated_signal.connect(self._updatePortSettings)
        # block the created signal, it will be triggered when loading is completely done
        self._loading = True
        log.info("QEMU VM {} is loading".format(name))
        self.setName(name)
        self.setup(qemu_path, name, console, vm_id, settings)

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
                    adapter_number = topology_port.get("adapter_number", topology_port["port_number"])
                    if adapter_number == port.adapterNumber():
                        port.setName(topology_port["name"])
                        port.setId(topology_port["id"])

        # now we can set the node has initialized and trigger the signal
        self.setInitialized(True)
        log.info("QEMU VM {} has been loaded".format(self.name()))
        self.created_signal.emit(self.id())
        self._module.addNode(self)
        self._inital_settings = None
        self._loading = False

    def name(self):
        """
        Returns the name of this QEMU VM instance.

        :returns: name (string)
        """

        return self._settings["name"]

    def settings(self):
        """
        Returns all this QEMU VM instance settings.

        :returns: settings dictionary
        """

        return self._settings

    def ports(self):
        """
        Returns all the ports for this QEMU VM instance.

        :returns: list of Port instances
        """

        return self._ports

    def console(self):
        """
        Returns the console port for this QEMU VM instance.

        :returns: port (integer)
        """

        return self._settings["console"]

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node configurator.

        :returns: QWidget object
        """

        from .pages.qemu_vm_configuration_page import QemuVMConfigurationPage
        return QemuVMConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/qemu_guest.normal.svg"

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when this node is hovered.

        :returns: symbol path (or resource).
        """

        return ":/symbols/qemu_guest.selected.svg"

    @staticmethod
    def symbolName():

        return "QEMU VM"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.end_devices]

    def __str__(self):

        return "QEMU VM"
