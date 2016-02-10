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
VPCS device implementation.
"""

import os
from gns3.vm import VM
from gns3.node import Node
from gns3.ports.ethernet_port import EthernetPort
from gns3.utils.normalize_filename import normalize_filename

import logging
log = logging.getLogger(__name__)


class VPCSDevice(VM):

    """
    VPCS device.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """
    URL_PREFIX = "vpcs"

    def __init__(self, module, server, project):
        super().__init__(module, server, project)

        log.info("VPCS instance is being created")
        self._vm_id = None
        self._settings = {"name": "",
                          "startup_script": None,
                          "startup_script_path": None,
                          "console": None}

        port_name = EthernetPort.longNameType() + str(0)
        short_name = EthernetPort.shortNameType() + str(0)

        # VPCS devices have only one fixed Ethernet port
        port = EthernetPort(port_name)
        port.setShortName(short_name)
        port.setAdapterNumber(0)
        port.setPortNumber(0)
        self._ports.append(port)
        log.debug("port {} has been added".format(port_name))

    def setup(self, name=None, vm_id=None, additional_settings={}, default_name_format="PC{0}"):
        """
        Setups this VPCS device.

        :param name: optional name
        :param vm_id: VM identifier
        :param additional_settings: additional settings for this device
        """

        # let's create a unique name if none has been chosen
        if not name:
            name = self.allocateName(default_name_format)

        if not name:
            self.error_signal.emit(self.id(), "could not allocate a name for this VPCS device")
            return

        self._settings["name"] = name
        params = {"name": name}

        if vm_id:
            params["vm_id"] = vm_id

        if "script_file" in additional_settings:
            if os.path.isfile(additional_settings["script_file"]):
                base_config_content = self._readBaseConfig(additional_settings["script_file"])
                if base_config_content is not None:
                    additional_settings["startup_script"] = base_config_content
            del additional_settings["script_file"]

        if "startup_script_path" in additional_settings:
            del additional_settings["startup_script_path"]

        # If we have an vm id that mean the VM already exits and we should not send startup_script
        if "startup_script" in additional_settings and vm_id is not None:
            del additional_settings["startup_script"]

        params.update(additional_settings)
        self.httpPost("/vpcs/vms", self._setupCallback, body=params)

    def _setupCallback(self, result, error=False, **kwargs):
        """
        Callback for setup.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if not super()._setupCallback(result, error=error, **kwargs):
            return

        if self._loading:
            self.loaded_signal.emit()
        else:
            self.setInitialized(True)
            log.info("VPCS instance {} has been created".format(self.name()))
            self.created_signal.emit(self.id())
            self._module.addNode(self)

    def update(self, new_settings):
        """
        Updates the settings for this VPCS device.

        :param new_settings: settings dictionary
        """

        if "name" in new_settings and new_settings["name"] != self.name() and self.hasAllocatedName(new_settings["name"]):
            self.error_signal.emit(self.id(), 'Name "{}" is already used by another node'.format(new_settings["name"]))
            return

        if "script_file" in new_settings:
            if os.path.isfile(new_settings["script_file"]):
                base_config_content = self._readBaseConfig(new_settings["script_file"])
                if base_config_content is not None:
                    new_settings["startup_script"] = base_config_content
            del new_settings["script_file"]

        if "startup_script_path" in new_settings:
            del new_settings["startup_script_path"]

        params = {}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        log.debug("{} is updating settings: {}".format(self.name(), params))
        self.httpPut("/vpcs/vms/{vm_id}".format(project_id=self._project.id(), vm_id=self._vm_id), self._updateCallback, body=params)

    def _updateCallback(self, result, error=False, **kwargs):
        """
        Callback for update.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if not super()._updateCallback(result, error=error, **kwargs):
            return False

        updated = False
        for name, value in result.items():
            if name in self._settings and self._settings[name] != value:
                log.info("{}: updating {} from '{}' to '{}'".format(self.name(), name, self._settings[name], value))
                updated = True
                if name == "name":
                    # update the node name
                    self.updateAllocatedName(value)
                self._settings[name] = value

        if updated:
            log.info("VPCS device {} has been updated".format(self.name()))
            self.updated_signal.emit()

    def info(self):
        """
        Returns information about this VPCS device.

        :returns: formated string
        """

        if self.status() == Node.started:
            state = "started"
        else:
            state = "stopped"

        info = """Device {name} is {state}
  Local node ID is {id}
  Server's VPCS device ID is {vm_id}
  VPCS's server runs on {host}:{port}, console is on port {console}
""".format(name=self.name(),
           id=self.id(),
           vm_id=self._vm_id,
           state=state,
           host=self._server.host(),
           port=self._server.port(),
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
        Returns a representation of this VPCS device.
        (to be saved in a topology file).

        :returns: representation of the node (dictionary)
        """

        vpcs_device = super().dump()
        vpcs_device["vm_id"] = self._vm_id

        # add the properties
        for name, value in self._settings.items():
            if value is not None and value != "":
                if name != "startup_script":
                    if name == "startup_script_path":
                        value = os.path.basename(value)
                    vpcs_device["properties"][name] = value

        return vpcs_device

    def load(self, node_info):
        """
        Loads a VPCS device representation
        (from a topology file).

        :param node_info: representation of the node (dictionary)
        """

        super().load(node_info)

        # for backward compatibility
        vm_id = node_info.get("vpcs_id")
        if not vm_id:
            vm_id = node_info.get("vm_id")

        # prepare the VM settings
        vm_settings = {}
        for name, value in node_info["properties"].items():
            if name in self._settings:
                vm_settings[name] = value
        name = vm_settings.pop("name")

        log.info("VPCS device {} is loading".format(name))
        self.setName(name)
        self.setup(name, vm_id, vm_settings)

    def exportConfig(self, config_export_path):
        """
        Exports the script file.

        :param config_export_path: export path for the script file
        """

        self.httpGet("/vpcs/vms/{vm_id}".format(vm_id=self._vm_id),
                     self._exportConfigCallback,
                     context={"path": config_export_path})

    def _exportConfigCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for exportConfig.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while exporting {} configs: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        elif "startup_script" in result:
            path = context["path"]
            try:
                with open(path, "wb") as f:
                    log.info("saving {} script file to {}".format(self.name(), path))
                    if result["startup_script"]:
                        f.write(result["startup_script"].encode("utf-8"))
            except OSError as e:
                self.error_signal.emit(self.id(), "could not export the script file to {}: {}".format(path, e))

    def exportConfigToDirectory(self, directory):
        """
        Exports the script-file to a directory.

        :param directory: destination directory path
        """

        self.httpGet("/vpcs/vms/{vm_id}".format(vm_id=self._vm_id),
                     self._exportConfigToDirectoryCallback,
                     context={"directory": directory})

    def _exportConfigToDirectoryCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for exportConfigToDirectory.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while exporting {} configs: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        elif "startup_script" in result:
            export_directory = context["directory"]
            config_path = os.path.join(export_directory, normalize_filename(self.name())) + "_startup.vpc"
            try:
                with open(config_path, "wb") as f:
                    log.info("saving {} script file to {}".format(self.name(), config_path))
                    if result["startup_script"]:
                        f.write(result["startup_script"].encode("utf-8"))
            except OSError as e:
                self.error_signal.emit(self.id(), "could not export the script file to {}: {}".format(config_path, e))

    def importConfig(self, path):
        """
        Imports a script-file.

        :param path: path to the script file
        """

        new_settings = {"script_file": path}
        self.update(new_settings)

    def importConfigFromDirectory(self, directory):
        """
        Imports an initial-config from a directory.

        :param directory: source directory path
        """

        try:
            contents = os.listdir(directory)
        except OSError as e:
            self.warning_signal.emit(self.id(), "Can't list file in {}: {}".format(directory, str(e)))
            return
        script_file = normalize_filename(self.name()) + "_startup.vpc"
        new_settings = {}
        if script_file in contents:
            new_settings["script_file"] = os.path.join(directory, script_file)
        else:
            self.warning_signal.emit(self.id(), "no script file could be found, expected file name: {}".format(script_file))
            return
        self.update(new_settings)

    def name(self):
        """
        Returns the name of this VPCS device.

        :returns: name (string)
        """

        return self._settings["name"]

    def settings(self):
        """
        Returns all this VPCS device settings.

        :returns: settings dictionary
        """

        return self._settings

    def ports(self):
        """
        Returns all the ports for this VPCS device.

        :returns: list of Port instances
        """

        return self._ports

    def console(self):
        """
        Returns the console port for this VPCS device.

        :returns: port (integer)
        """

        return self._settings["console"]

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

        :returns: QWidget object
        """

        from .pages.vpcs_device_configuration_page import VPCSDeviceConfigurationPage
        return VPCSDeviceConfigurationPage

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.

        :returns: symbol path (or resource).
        """

        return ":/symbols/computer.svg"

    @staticmethod
    def symbolName():

        return "VPCS"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node category (integer)
        """

        return [Node.end_devices]

    def __str__(self):

        return "VPCS device"
