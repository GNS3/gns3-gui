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
VirtualBox VM implementation.
"""

from gns3.vm import VM
from gns3.node import Node
from gns3.ports.port import Port
from gns3.ports.ethernet_port import EthernetPort
from .settings import VBOX_VM_SETTINGS

import logging
log = logging.getLogger(__name__)


class VirtualBoxVM(VM):

    """
    VirtualBox VM.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "virtualbox"

    def __init__(self, module, server, project):

        VM.__init__(self, module, server, project)
        log.info("VirtualBox VM instance is being created")
        self._linked_clone = False
        self._export_directory = None
        self._loading = False
        self._ports = []
        self._settings = {"name": "",
                          "vmname": "",
                          "console": None,
                          "adapters": VBOX_VM_SETTINGS["adapters"],
                          "use_any_adapter": VBOX_VM_SETTINGS["use_any_adapter"],
                          "adapter_type": VBOX_VM_SETTINGS["adapter_type"],
                          "ram": VBOX_VM_SETTINGS["ram"],
                          "headless": VBOX_VM_SETTINGS["headless"],
                          "enable_remote_console": VBOX_VM_SETTINGS["enable_remote_console"]}

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
            new_port.setPacketCaptureSupported(True)
            self._ports.append(new_port)
            log.debug("Adapter {} has been added".format(adapter_name))

    def setup(self, vmname, name=None, vm_id=None, linked_clone=False, additional_settings={}):
        """
        Setups this VirtualBox VM.

        :param vmname: VM name in VirtualBox
        :param name: optional name
        :param vm_id: VM identifier
        :param linked_clone: either the VM is a linked clone
        :param additional_settings: additional settings for this VM
        """

        # let's create a unique name if none has been chosen
        if not name:
            if linked_clone:
                name = self.allocateName(vmname + "-")
            else:
                name = vmname
                self.setName(name)

        if not name:
            self.error_signal.emit(self.id(), "could not allocate a name for this VirtualBox VM")
            return

        self._settings["name"] = name
        self._linked_clone = linked_clone
        params = {"name": name,
                  "vmname": vmname,
                  "linked_clone": linked_clone}

        if vm_id:
            params["vm_id"] = vm_id

        params.update(additional_settings)
        self.httpPost("/virtualbox/vms", self._setupCallback, body=params)

    def _setupCallback(self, result, error=False, **kwargs):
        """
        Callback for setup.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while setting up {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            return

        self._vm_id = result["vm_id"]
        # update the settings with what has been sent by the server
        for name, value in result.items():
            if name in self._settings and self._settings[name] != value:
                log.info("VirtualBox VM instance {} setting up and updating {} from '{}' to '{}'".format(self.name(),
                                                                                                         name,
                                                                                                         self._settings[name],
                                                                                                         value))
                self._settings[name] = value

        if self._settings["adapters"] != 0:
            self._addAdapters(self._settings["adapters"])

        if self._loading:
            self.updated_signal.emit()
        else:
            self.setInitialized(True)
            log.info("VirtualBox VM instance {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)

    def update(self, new_settings):
        """
        Updates the settings for this VirtualBox VM.

        :param new_settings: settings (dict)
        """

        if "name" in new_settings and new_settings["name"] != self.name():
            if self.hasAllocatedName(new_settings["name"]):
                self.error_signal.emit(self.id(), 'Name "{}" is already used by another node'.format(new_settings["name"]))
                return
            elif self._linked_clone:
                # forces the update of the VM name in VirtualBox.
                new_settings["vmname"] = new_settings["name"]

        params = {}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        log.debug("{} is updating settings: {}".format(self.name(), params))
        self.httpPut("/virtualbox/vms/{vm_id}".format(vm_id=self._vm_id), self._updateCallback, body=params)

    def _updateCallback(self, result, error=False, **kwargs):
        """
        Callback for update.

        :param result: server response (dict)
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

        if updated or self._loading:
            log.info("VirtualBox VM {} has been updated".format(self.name()))
            self.updated_signal.emit()

    def suspend(self):
        """
        Suspends this VirtualBox VM instance.
        """

        if self.status() == Node.suspended:
            log.debug("{} is already suspended".format(self.name()))
            return

        log.debug("{} is being suspended".format(self.name()))
        self.httpPost("/virtualbox/vms/{vm_id}/suspend".format(vm_id=self._vm_id), self._suspendCallback)

    def _suspendCallback(self, result, error=False, **kwargs):
        """
        Callback for suspend.

        :param result: server response (dict)
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
        :param data_link_type: PCAP data link type (unused)
        """

        params = {"capture_file_name": capture_file_name}
        log.debug("{} is starting a packet capture on {}: {}".format(self.name(), port.name(), params))
        self.httpPost("/virtualbox/vms/{vm_id}/adapters/{adapter_number}/ports/0/start_capture".format(
            vm_id=self._vm_id,
            adapter_number=port.adapterNumber()),
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
        self.httpPost("/virtualbox/vms/{vm_id}/adapters/{adapter_number}/ports/0/stop_capture".format(
            vm_id=self._vm_id,
            adapter_number=port.adapterNumber()),
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

    def info(self):
        """
        Returns information about this VirtualBox VM instance.

        :returns: formated string
        """

        if self.status() == Node.started:
            state = "started"
        else:
            state = "stopped"

        info = """VirtualBox VM {name} is {state}
  Local node ID is {id}
  Server's VirtualBox VM ID is {vm_id}
  VirtualBox name is "{vmname}"
  RAM is {ram} MB
  VirtualBox VM's server runs on {host}:{port}, console is on port {console}
""".format(name=self.name(),
           id=self.id(),
           vm_id=self._vm_id,
           state=state,
           vmname=self._settings["vmname"],
           ram=self._settings["ram"],
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

    def dump(self):
        """
        Returns a representation of this VirtualBox VM instance.
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """

        vbox_vm = {"id": self.id(),
                   "vm_id": self._vm_id,
                   "linked_clone": self._linked_clone,
                   "type": self.__class__.__name__,
                   "description": str(self),
                   "properties": {},
                   "server_id": self._server.id()}

        # add the properties
        for name, value in self._settings.items():
            if name in self._defaults and self._defaults[name] != value:
                vbox_vm["properties"][name] = value

        # add the ports
        if self._ports:
            ports = vbox_vm["ports"] = []
            for port in self._ports:
                ports.append(port.dump())

        return vbox_vm

    def load(self, node_info):
        """
        Loads a VirtualBox VM representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        self.node_info = node_info
        # for backward compatibility
        vm_id = node_info.get("vbox_id")
        if not vm_id:
            vm_id = node_info["vm_id"]
        linked_clone = node_info.get("linked_clone", False)
        settings = node_info["properties"]
        settings["adapters"] = settings.get("adapters", 1)
        name = settings.pop("name")
        vmname = settings.pop("vmname")
        self.updated_signal.connect(self._updatePortSettings)
        # block the created signal, it will be triggered when loading is completely done
        self._loading = True
        log.info("VirtualBox VM {} is loading".format(name))
        self.setName(name)
        self.setup(vmname, name, vm_id, linked_clone, settings)

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
        log.info("VirtualBox VM {} has been loaded".format(self.name()))
        self.created_signal.emit(self.id())
        self._module.addNode(self)
        self._inital_settings = None
        self._loading = False

    def name(self):
        """
        Returns the name of this VirtualBox VM instance.

        :returns: name (string)
        """

        return self._settings["name"]

    def settings(self):
        """
        Returns all this VirtualBox VM instance settings.

        :returns: settings dictionary
        """

        return self._settings

    def ports(self):
        """
        Returns all the ports for this VirtualBox VM instance.

        :returns: list of Port instances
        """

        return self._ports

    def serialConsole(self):
        """
        Returns either the serial console must be used or not.

        :return: boolean
        """

        if self._settings["enable_remote_console"]:
            return False
        return True

    def console(self):
        """
        Returns the console port for this VirtualBox VM instance.

        :returns: port (integer)
        """

        return self._settings["console"]

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node configurator.

        :returns: QWidget object
        """

        from .pages.virtualbox_vm_configuration_page import VirtualBoxVMConfigurationPage
        return VirtualBoxVMConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/vbox_guest.normal.svg"

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when this node is hovered.

        :returns: symbol path (or resource).
        """

        return ":/symbols/vbox_guest.selected.svg"

    @staticmethod
    def symbolName():

        return "VirtualBox VM"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.end_devices]

    def __str__(self):

        return "VirtualBox VM"
