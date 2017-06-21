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


import os
import uuid
import pathlib
from gns3.local_server import LocalServer
from gns3.controller import Controller
from gns3.ports.ethernet_port import EthernetPort
from gns3.ports.serial_port import SerialPort
from gns3.qt import QtGui, QtCore

from .base_node import BaseNode

import logging
log = logging.getLogger(__name__)


class Node(BaseNode):

    def __init__(self, module, compute, project):

        super().__init__(module, compute, project)

        self._node_id = str(uuid.uuid4())

        self._node_directory = None
        self._command_line = None
        self._always_on = False

        # minimum required base settings
        self._settings = {"name": "", "x": None, "y": None, "z": 1}

    def get(self, path, *args, **kwargs):
        return self.controllerHttpGet("/nodes/{node_id}{path}".format(node_id=self._node_id, path=path), *args, **kwargs)

    def post(self, path, *args, **kwargs):
        return self.controllerHttpPost("/nodes/{node_id}{path}".format(node_id=self._node_id, path=path), *args, **kwargs)

    def importFile(self, path, source_path):
        self.post("/files/{path}".format(path=path), self._importFileCallback, body=pathlib.Path(source_path), timeout=None)

    def _importFileCallback(self, result, error=False, **kwargs):
        if error:
            log.error("Error while importing file: {}".format(result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            return False

    def exportFile(self, path, output_path):
        self.get("/files/{path}".format(path=path), self._exportFileCallback, context={"path": output_path}, raw=True)

    def _exportFileCallback(self, result, error=False, raw_body=None, context={}, **kwargs):
        if not error:
            try:
                with open(context["path"], "wb+") as f:
                    f.write(raw_body)
            except OSError as e:
                log.erro("Can't write %s: %s", context["path"], str(e))


    def creator(self):
        return self._creator

    def settings(self):
        return self._settings

    def setSettingValue(self, key, value):
        """
        Set settings
        """
        self._settings[key] = value

    def setGraphics(self, node_item):
        """
        Sync the remote object with the node_item
        """

        data = {
            "x": int(node_item.pos().x()),
            "y": int(node_item.pos().y()),
            "z": int(node_item.zValue()),
            "symbol": node_item.symbol()
        }
        if node_item.label() is not None:
            data["label"] = node_item.label().dump()

        # Send the change of if stuff changed
        changed = False
        for key in data:
            if key not in self._settings or self._settings[key] != data[key]:
                changed = True
        if not changed:
            return

        # If it's the initialization we don't resend it
        # to the server
        if self._settings["x"] is not None:
            self._update(data)
        else:
            self._settings.update(data)

    def setSymbol(self, symbol):
        self._settings["symbol"] = symbol

    def symbol(self):
        return self._settings["symbol"]

    def setPos(self, x, y):
        self._settings["x"] = int(x)
        self._settings["y"] = int(y)

    def x(self):
        return self._settings["x"]

    def y(self):
        return self._settings["y"]

    def z(self):
        return self._settings["z"]

    def isAlwaysOn(self):
        """
        Whether the node is always on.

        :returns: boolean
        """

        return self._always_on

    def consoleCommand(self, console_type=None):
        """
        :returns: The console command for this host
        """

        from .main_window import MainWindow
        general_settings = MainWindow.instance().settings()

        if console_type != "telnet":
            console_type = self.consoleType()
            if console_type == "vnc":
                return general_settings["vnc_console_command"]
        return general_settings["telnet_console_command"]

    def consoleType(self):
        """
        Get the console type (serial, telnet or VNC)
        """
        console_type = "telnet"
        if "console_type" in self.settings():
            return self.settings()["console_type"]
        return console_type

    def consoleHost(self):

        host = self.settings()["console_host"]
        if host is None or host == "::" or host == "0.0.0.0":
            host = Controller.instance().host()
        return host

    def node_id(self):
        """
        Return the ID of this device

        :returns: identifier (string)
        """

        return self._node_id

    def nodeDir(self):
        """
        Return the working directory of this node

        :returns: identifier (string)
        """

        return self._node_directory

    def commandLine(self):
        """
        Return the command line used to run this node

        :returns: identifier (string)
        """

        return self._command_line

    def _prepareBody(self, params):
        """
        :returns: Body for Create and update
        """
        assert self._node_id is not None
        body = {"properties": {},
                "node_type": self.URL_PREFIX,
                "node_id": self._node_id,
                "compute_id": self._compute.id()}

        # We have two kind of properties. The general properties common to all
        # nodes and the specific that we need to put in the properties field
        node_general_properties = ("name", "console", "console_type", "x", "y", "z", "symbol", "label", "port_name_format", "port_segment_size", "first_port_name")
        # No need to send this back to the server because it's read only
        ignore_properties = ("console_host", "symbol_url", "width", "height", "node_id")
        for key, value in params.items():
            if key in node_general_properties:
                body[key] = value
            elif key in ignore_properties:
                pass
            else:
                body["properties"][key] = value

        return body

    def _create(self, name=None, node_id=None, params=None, default_name_format="Node{0}", timeout=120):
        """
        Create the node on the controller
        """

        self._creator = True
        if params is None:
            params = {}

        if "symbol" in self._settings:
            params["symbol"] = self._settings["symbol"]
            params["x"] = self._settings["x"]
            params["y"] = self._settings["y"]
            if "label" in self._settings:
                params["label"] = self._settings["label"]

        if not name:
            # use the default name format if no name is provided
            name = default_name_format

        params["name"] = name
        if node_id is not None:
            self._node_id = node_id

        body = self._prepareBody(params)
        self.controllerHttpPost("/nodes", self.createNodeCallback, body=body, timeout=timeout)

    def createNodeCallback(self, result, error=False, **kwargs):
        """
        Callback for create.

        :param result: server response
        :param error: indicates an error (boolean)
        :returns: Boolean success or not
        """
        if error:
            self.server_error_signal.emit(self.id(), "Error while setting up node: {}".format(result["message"]))
            self.deleted_signal.emit()
            self._module.removeNode(self)
            return False

        result = self._parseResponse(result)
        self._created = True
        self._createCallback(result)

        if self._loading:
            self.loaded_signal.emit()
        else:
            self.setInitialized(True)
            log.info("Node instance {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)

    def _createCallback(self, result):
        """
        Create callback compatible with the compute api.
        """

        pass

    def _update(self, params, timeout=60):
        """
        Update the node on the controller
        """

        if self.initialized():
            log.debug("{} is updating settings: {}".format(self.name(), params))
            body = self._prepareBody(params)
            self.controllerHttpPut("/nodes/{node_id}".format(node_id=self._node_id), self.updateNodeCallback, body=body, timeout=timeout)

    def updateNodeCallback(self, result, error=False, **kwargs):
        """
        Callback for update.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while updating {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            return False

        result = self._parseResponse(result)

        self._updateCallback(result)
        self.updated_signal.emit()
        return True

    def _parseResponse(self, result):
        """
        Parse node object from API
        """
        if "node_id" in result:
            self._node_id = result["node_id"]

        if "name" in result:
            self.setName(result["name"])

        if "command_line" in result:
            self._command_line = result["command_line"]

        if "node_directory" in result:
            self._node_directory = result["node_directory"]

        if "status" in result:
            if result["status"] == "started":
                self.setStatus(Node.started)
            elif result["status"] == "stopped":
                self.setStatus(Node.stopped)
            elif result["status"] == "suspended":
                self.setStatus(Node.suspended)

        if "ports" in result:
            self._updatePorts(result["ports"])

        if "properties" in result:
            for name, value in result["properties"].items():
                if name in self._settings and self._settings[name] != value:
                    log.debug("{} setting up and updating {} from '{}' to '{}'".format(self.name(), name, self._settings[name], value))
                    self._settings[name] = value

            result.update(result["properties"])
            del result["properties"]

        # Update common element of all nodes
        for key in ["x", "y", "z", "symbol", "label", "console_host", "console", "console_type"]:
            if key in result:
                self._settings[key] = result[key]

        return result

    def _updatePorts(self, ports):
        self._settings["ports"] = ports
        old_ports = self._ports.copy()
        self._ports = []
        for port in ports:
            new_port = None

            # Update port if already exist
            for old_port in old_ports:
                if old_port.adapterNumber() == port["adapter_number"] and old_port.portNumber() == port["port_number"] and old_port.name() == port["name"]:
                    new_port = old_port
                    old_ports.remove(old_port)
                    break

            if new_port is None:
                if port["link_type"] == "serial":
                    new_port = SerialPort(port["name"])
                else:
                    new_port = EthernetPort(port["name"])
            new_port.setShortName(port["short_name"])
            new_port.setAdapterNumber(port["adapter_number"])
            new_port.setPortNumber(port["port_number"])
            new_port.setDataLinkTypes(port["data_link_types"])
            new_port.setStatus(self.status())
            self._ports.append(new_port)

    def _updateCallback(self, result):
        """
        Update callback compatible with the compute api.
        """

        pass

    def delete(self, skip_controller=False):
        """
        Deletes this node instance.

        :param skip_controller: True to not delete on the controller (often it's when it's already deleted on the server)
        """

        log.info("{} is being deleted".format(self.name()))
        if not skip_controller:
            self.controllerHttpDelete("/nodes/{node_id}".format(node_id=self._node_id), self._deleteCallback)
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
            return
        log.info("{} has been deleted".format(self.name()))
        self.deleted_signal.emit()
        self._module.removeNode(self)

    def isStarted(self):
        """
        :returns: Boolean True if started
        """
        return self.status() == Node.started

    def start(self):
        """
        Starts this node instance.
        """

        if self.isStarted():
            log.debug("{} is already running".format(self.name()))
            return

        log.debug("{} is starting".format(self.name()))
        self.controllerHttpPost("/nodes/{node_id}/start".format(node_id=self._node_id), self._startCallback, timeout=None, progressText="{} is starting".format(self.name()))

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
            self._parseResponse(result)

    def stop(self):
        """
        Stops this node instance.
        """

        if self.status() == Node.stopped:
            log.debug("{} is already stopped".format(self.name()))
            return

        log.debug("{} is stopping".format(self.name()))
        self.controllerHttpPost("/nodes/{node_id}/stop".format(node_id=self._node_id), self._stopCallback, progressText="{} is stopping".format(self.name()), timeout=None)

    def _stopCallback(self, result, error=False, **kwargs):
        """
        Callback for stop.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while stopping {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            # To avoid blocking the client we consider node as stopped if the node no longer exists or server doesn't answer
            if "status" not in result or result["status"] == 404:
                self.setStatus(Node.stopped)
        else:
            self._parseResponse(result)

    def suspend(self):
        """
        Suspends this router.
        """

        if self.status() == Node.suspended:
            log.debug("{} is already suspended".format(self.name()))
            return

        log.debug("{} is being suspended".format(self.name()))
        self.controllerHttpPost("/nodes/{node_id}/suspend".format(node_id=self._node_id), self._suspendCallback, timeout=None)

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
            self._parseResponse(result)

    def reload(self):
        """
        Reloads this node instance.
        """

        log.debug("{} is being reloaded".format(self.name()))
        self.controllerHttpPost("/nodes/{node_id}/reload".format(node_id=self._node_id), self._reloadCallback, timeout=None)

    def _reloadCallback(self, result, error=False, **kwargs):
        """
        Callback for reload.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while reloading {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{} has reloaded".format(self.name()))

    def _readBaseConfig(self, config_path):
        """
        Returns a base config content.

        :param config_path: path to the configuration file.

        :returns: config content
        """

        if config_path is None or len(config_path.strip()) == 0:
            return None

        if not os.path.isabs(config_path):
            config_path = os.path.join(LocalServer.instance().localServerSettings()["configs_path"], config_path)

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

    def openConsole(self, command=None, aux=False):
        if command is None:
            if aux:
                command = self.consoleCommand(console_type="telnet")
            else:
                command = self.consoleCommand()

        console_type = "telnet"

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
            nodeTelnetConsole(self, console_port, command)
        elif console_type == "vnc":
            from .vnc_console import vncConsole
            vncConsole(self.consoleHost(), console_port, command)
        elif console_type == "http" or console_type == "https":
            QtGui.QDesktopServices.openUrl(QtCore.QUrl("{console_type}://{host}:{port}{path}".format(console_type=console_type, host=self.consoleHost(), port=console_port, path=self.consoleHttpPath())))

    def setName(self, name):
        """
        Set a name for a node.

        :param name: node name
        """

        self._settings["name"] = name

    def name(self):
        """
        Returns the name of this node.

        :returns: name (string)
        """

        return self._settings["name"]
