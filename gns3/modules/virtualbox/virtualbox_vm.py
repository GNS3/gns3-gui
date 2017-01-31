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

import sys
import os
import tempfile

from gns3.node import Node
from .settings import VBOX_VM_SETTINGS

import logging
log = logging.getLogger(__name__)


class VirtualBoxVM(Node):

    """
    VirtualBox VM.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "virtualbox"

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        log.info("VirtualBox VM instance is being created")
        self._linked_clone = False

        virtualbox_vm_settings = {"vmname": "",
                                  "console": None,
                                  "console_host": None,
                                  "adapters": VBOX_VM_SETTINGS["adapters"],
                                  "use_any_adapter": VBOX_VM_SETTINGS["use_any_adapter"],
                                  "adapter_type": VBOX_VM_SETTINGS["adapter_type"],
                                  "ram": VBOX_VM_SETTINGS["ram"],
                                  "headless": VBOX_VM_SETTINGS["headless"],
                                  "acpi_shutdown": VBOX_VM_SETTINGS["acpi_shutdown"],
                                  "port_name_format": "Ethernet0",
                                  "port_segment_size": 0,
                                  "first_port_name": None}

        self.settings().update(virtualbox_vm_settings)

    def create(self, vmname, name=None, node_id=None, port_name_format="Ethernet{0}", port_segment_size=0,
               first_port_name="", linked_clone=False, additional_settings={}, default_name_format=None):
        """
        Creates this VirtualBox VM.

        :param vmname: VM name in VirtualBox
        :param name: optional name
        :param node_id: Node identifier
        :param linked_clone: either the VM is a linked clone
        :param additional_settings: additional settings for this VM
        """

        if not name:
            name = vmname

        self._linked_clone = linked_clone
        params = {"vmname": vmname,
                  "linked_clone": linked_clone,
                  "port_name_format": port_name_format,
                  "port_segment_size": port_segment_size,
                  "first_port_name": first_port_name}
        params.update(additional_settings)
        self._create(name, node_id, params, default_name_format)

    def _createCallback(self, result):
        """
        Callback for create.

        :param result: server response (dict)
        """
        pass

    def update(self, new_settings):
        """
        Updates the settings for this VirtualBox VM.

        :param new_settings: settings (dict)
        """

        params = {}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        if params:
            self._update(params)

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
  Server's node ID is {node_id}
  VirtualBox name is "{vmname}"
  RAM is {ram} MB
  VirtualBox VM's server runs on {host}, console is on port {console}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           state=state,
           vmname=self._settings["vmname"],
           ram=self._settings["ram"],
           host=self.compute().name(),
           console=self._settings["console"])

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "     {port_name} is empty\n".format(port_name=port.name())
            else:
                port_info += "     {port_name} {port_description}\n".format(port_name=port.name(),
                                                                            port_description=port.description())

        return info + port_info

    def console(self):
        """
        Returns the console port for this VirtualBox VM instance.

        :returns: port (integer)
        """
        return self._settings["console"]

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

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

        return ":/symbols/vbox_guest.svg"

    @staticmethod
    def symbolName():

        return "VirtualBox VM"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.end_devices]

    def __str__(self):

        return "VirtualBox VM"
