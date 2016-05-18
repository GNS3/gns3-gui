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
Base class for VM classes.
"""

import os
from gns3.servers import Servers
from gns3.packet_capture import PacketCapture
from gns3.qt import QtGui, QtCore

from .node import Node

import logging
log = logging.getLogger(__name__)


class VM(Node):

    def __init__(self, module, server, project):

        super().__init__(module, server, project)

        self._vm_id = None
        self._vm_directory = None
        self._command_line = None

    def consoleCommand(self, console_type=None):
        """
        :returns: The console command for this host
        """
        from .main_window import MainWindow
        general_settings = MainWindow.instance().settings()

        if console_type != "telnet":
            console_type = self.consoleType()
            if console_type == "serial":
                return general_settings["serial_console_command"]
            elif console_type == "vnc":
                return general_settings["vnc_console_command"]
        return general_settings["telnet_console_command"]

    def consoleType(self):
        """
        Get the console type (serial, telnet or VNC)
        """
        console_type = "telnet"
        if hasattr(self, "serialConsole") and self.serialConsole():
            return "serial"
        if "console_type" in self.settings():
            return self.settings()["console_type"]
        return console_type

    def vm_id(self):
        """
        Return the ID of this device

        :returns: identifier (string)
        """

        return self._vm_id

    def vmDir(self):
        """
        Return the working directory of the VM

        :returns: identifier (string)
        """

        return self._vm_directory

    def commandLine(self):
        """
        Return the command line used to run the VM

        :returns: identifier (string)
        """

        return self._command_line

    def delete(self):
        """
        Deletes this VM instance.
        """

        log.debug("{} is being deleted".format(self.name()))
        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        if self._vm_id and self._server.connected():
            self.httpDelete("/{prefix}/vms/{vm_id}".format(prefix=self.URL_PREFIX, vm_id=self._vm_id), self._deleteCallback)
        else:
            self.deleted_signal.emit()
            self._module.removeNode(self)

    def _deleteCallback(self, result, error=False, **kwargs):
        """
        Callback for delete.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        log.info("{} has been deleted".format(self.name()))
        self.deleted_signal.emit()
        self._module.removeNode(self)

    def start(self):
        """
        Starts this VM instance.
        """

        if self.status() == Node.started:
            log.debug("{} is already running".format(self.name()))
            return

        log.debug("{} is starting".format(self.name()))
        self.httpPost("/{prefix}/vms/{vm_id}/start".format(prefix=self.URL_PREFIX, vm_id=self._vm_id), self._startCallback, progressText="{} is starting".format(self.name()))

    def _startCallback(self, result, error=False, **kwargs):
        """
        Callback for start.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while starting {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{} has started".format(self.name()))
            self.setStatus(Node.started)
            if result:
                self._updateCallback(result)

    def _setupCallback(self, result, error=False, **kwargs):
        """
        Callback for setup.

        :param result: server response
        :param error: indicates an error (boolean)
        :returns: Boolean success or not
        """

        if error:
            log.error("error while setting up {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            return False

        self._vm_id = result["vm_id"]
        if not self._vm_id:
            self.error_signal.emit(self.id(), "returned ID from server is null")
            return False

        if "vm_directory" in result:
            self._vm_directory = result["vm_directory"]

        if "command_line" in result:
            self._command_line = result["command_line"]

        # update the settings using the defaults sent by the server
        for name, value in result.items():
            if name in self._settings and self._settings[name] != value:
                log.info("{} setting up and updating {} from '{}' to '{}'".format(self.name(),
                                                                                  name,
                                                                                  self._settings[name],
                                                                                  value))
                self._settings[name] = value
        return True

    def _updateCallback(self, result, error=False, **kwargs):
        """
        Callback for update.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            return False

        if "command_line" in result:
            self._command_line = result["command_line"]

        return True

    def stop(self):
        """
        Stops this VM instance.
        """

        if self.status() == Node.stopped:
            log.debug("{} is already stopped".format(self.name()))
            return

        log.debug("{} is stopping".format(self.name()))
        self.httpPost("/{prefix}/vms/{vm_id}/stop".format(prefix=self.URL_PREFIX, vm_id=self._vm_id), self._stopCallback, progressText="{} is stopping".format(self.name()))

    def _stopCallback(self, result, error=False, **kwargs):
        """
        Callback for stop.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while stopping {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            # To avoid block the client if the node no longer exists or server doesn't answer we consider node as stopped
            if not "status" in result or result["status"] == 404:
                self.setStatus(Node.stopped)
        else:
            log.info("{} has stopped".format(self.name()))
            self.setStatus(Node.stopped)

    def reload(self):
        """
        Reloads this VM instance.
        """

        log.debug("{} is being reloaded".format(self.name()))
        self.httpPost("/{prefix}/vms/{vm_id}/reload".format(prefix=self.URL_PREFIX, vm_id=self._vm_id), self._reloadCallback)

    def _reloadCallback(self, result, error=False, **kwargs):
        """
        Callback for reload.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while suspending {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{} has reloaded".format(self.name()))

    def addNIO(self, port, nio):
        """
        Adds a new NIO on the specified port for this VM instance.

        :param port: Port instance
        :param nio: NIO instance
        """
        params = self.getNIOInfo(nio)
        log.debug("{} is adding an {}: {}".format(self.name(), nio, params))
        self.httpPost("/{prefix}/vms/{vm_id}/adapters/{adapter}/ports/{port}/nio".format(
            adapter=port.adapterNumber(),
            port=port.portNumber(),
            prefix=self.URL_PREFIX,
            vm_id=self._vm_id),
            self._addNIOCallback,
            context={"port_id": port.id()},
            body=params)

    def _addNIOCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for addNIO.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while adding a NIO for {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            self.nio_cancel_signal.emit(self.id())
        else:
            self.nio_signal.emit(self.id(), context["port_id"])

    def deleteNIO(self, port):
        """
        Deletes an NIO from the specified port on this instance

        :param port: Port instance
        """

        log.debug("{} is deleting an NIO".format(self.name()))
        self.httpDelete("/{prefix}/vms/{vm_id}/adapters/{adapter}/ports/{port}/nio".format(
            adapter=port.adapterNumber(),
            prefix=self.URL_PREFIX,
            port=port.portNumber(),
            vm_id=self._vm_id),
            self._deleteNIOCallback)

    def _deleteNIOCallback(self, result, error=False, **kwargs):
        """
        Callback for deleteNIO.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("Error while deleting NIO {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            return

        log.debug("{} has deleted a NIO: {}".format(self.name(), result))

    def _readBaseConfig(self, config_path):
        """
        Returns a base config content.

        :param config_path: path to the configuration file.

        :returns: config content
        """

        if config_path is None or len(config_path.strip()) == 0:
            return None

        if not os.path.isabs(config_path):
            config_path = os.path.join(Servers.instance().localServerSettings()["configs_path"], config_path)

        if not os.path.isfile(config_path):
            return None

        try:
            with open(config_path, "rb") as f:
                log.info("Opening configuration file: {}".format(config_path))
                config = f.read().decode("utf-8")
                config = config.replace('\r', "")
                return config
        except OSError as e:
            self.error_signal.emit(self.id(), "Could not read configuration file {}: {}".format(config_path, e))
            return None
        except UnicodeDecodeError as e:
            self.error_signal.emit(self.id(), "Invalid configuration file {}: {}".format(config_path, e))
            return None
        return ""

    def startPacketCapture(self, port, capture_file_name, data_link_type):
        """
        Starts a packet capture.

        :param port: Port instance
        :param capture_file_name: PCAP capture file path
        :param data_link_type: PCAP data link type (unused by some VM)
        """

        params = {"capture_file_name": capture_file_name,
                  "data_link_type": data_link_type}
        log.debug("{} is starting a packet capture on {}: {}".format(self.name(), port.name(), params))
        self.httpPost("/{prefix}/vms/{vm_id}/adapters/{adapter_number}/ports/{port_number}/start_capture".format(
            vm_id=self._vm_id,
            prefix=self.URL_PREFIX,
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
            PacketCapture.instance().startCapture(self, context["port"], result["pcap_file_path"])

    def stopPacketCapture(self, port):
        """
        Stops a packet capture.

        :param port: Port instance
        """

        log.debug("{} is stopping a packet capture on {}".format(self.name(), port.name()))
        self.httpPost("/{prefix}/vms/{vm_id}/adapters/{adapter_number}/ports/{port_number}/stop_capture".format(
            vm_id=self._vm_id,
            prefix=self.URL_PREFIX,
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
            PacketCapture.instance().stopCapture(self, context["port"])
    def dump(self):
        """
        Returns a representation of this device.
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """

        device = {
            "id": self.id(),
            "type": self.__class__.__name__,
            "description": str(self),
            "properties": {},
            "server_id": self._server.id()
        }

        # add the ports
        if self._ports:
            # In 1.4.2dev1 we track an issue about duplicate port name
            # https://github.com/GNS3/gns3-gui/issues/992
            initialized_port_name = set()

            ports = device["ports"] = []
            for port in self._ports:
                if port.name() in initialized_port_name:
                    msg = "Duplicate port name {} in {}.".format(port.name(), self.name())
                    print(msg)
                    log.error(msg)
                else:
                    ports.append(port.dump())
                    initialized_port_name.add(port.name())

        return device

    def load(self, node_info):
        """
        Loads a device representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        self._loading = True
        self._node_info = node_info
        self.loaded_signal.connect(self._updatePortSettings)

    def openConsole(self, command=None, aux=False):
        if command is None:
            if aux:
                command = self.consoleCommand(console_type="telnet")
            else:
                command = self.consoleCommand()

        console_type = "telnet"
        if hasattr(self, "serialConsole") and self.serialConsole():
            from .serial_console import serialConsole
            serialConsole(self.name(), self.serialPipe(), command)
            return

        if aux:
            console_port = self.auxConsole()
            if console_port is None:
                raise ValueError("AUX console port not allocated for {}".format(self.name()))
            # Aux console is always telnet
            console_type = "telnet"
        else:
            console_port = self.console()
            if "console_type" in self.settings():
                console_type = self.settings()["console_type"]

        if console_type == "telnet":
            from .telnet_console import nodeTelnetConsole
            nodeTelnetConsole(self.name(), self.server(), console_port, command)
        elif console_type == "vnc":
            from .vnc_console import vncConsole
            vncConsole(self.server().host(), console_port, command)
        elif console_type == "http" or console_type == "https":
            QtGui.QDesktopServices.openUrl(QtCore.QUrl("{console_type}://{host}:{port}{path}".format(console_type=console_type, host=self.server().host(), port=console_port, path=self.consoleHttpPath())))

    def _updatePortSettings(self):
        """
        Updates port settings when loading a topology.
        """

        self.loaded_signal.disconnect(self._updatePortSettings)

        # assign the correct names and IDs to the ports
        if "ports" in self._node_info:
            ports = self._node_info["ports"]

            port_initialized = set()

            for topology_port in ports:
                for port in self._ports:
                    if topology_port["port_number"] == port.portNumber():
                        # If the adapter is missing we consider that adapter_number == port_number
                        adapter_number = topology_port.get("adapter_number", topology_port["port_number"])
                        if port.adapterNumber() is None or adapter_number == port.adapterNumber() or topology_port.get("slot_number", None) == port.adapterNumber():

                            if port in port_initialized:
                                msg = "Topology corrupted port {} already exists for {}".format(port, self.name())
                                print(msg)
                                log.error(msg)
                            else:
                                port.setName(topology_port["name"])
                                port.setId(topology_port["id"])
                                port_initialized.add(port)

        # now we can set the node as initialized and trigger the created signal
        self.setInitialized(True)
        log.info("{} has been loaded".format(self.name()))
        self.created_signal.emit(self.id())
        self._module.addNode(self)
        self._loading = False
        self._node_info = None
