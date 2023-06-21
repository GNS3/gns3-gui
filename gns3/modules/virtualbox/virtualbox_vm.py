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

from gns3.node import Node
from gns3.utils.bring_to_front import bring_window_to_front_from_process_name
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
        self._linked_clone = False

        virtualbox_vm_settings = {"vmname": "",
                                  "usage": "",
                                  "adapters": VBOX_VM_SETTINGS["adapters"],
                                  "use_any_adapter": VBOX_VM_SETTINGS["use_any_adapter"],
                                  "adapter_type": VBOX_VM_SETTINGS["adapter_type"],
                                  "ram": VBOX_VM_SETTINGS["ram"],
                                  "headless": VBOX_VM_SETTINGS["headless"],
                                  "on_close": VBOX_VM_SETTINGS["on_close"],
                                  "console_type": VBOX_VM_SETTINGS["console_type"],
                                  "console_auto_start": VBOX_VM_SETTINGS["console_auto_start"],
                                  "custom_adapters": VBOX_VM_SETTINGS["custom_adapters"],
                                  "port_name_format": "Ethernet0",
                                  "port_segment_size": 0,
                                  "first_port_name": None}

        self.settings().update(virtualbox_vm_settings)

    def info(self):
        """
        Returns information about this VirtualBox VM instance.

        :returns: formatted string
        """

        info = """VirtualBox VM {name} is {state}
  Running on server {host} with port {port}
  Local ID is {id} and node ID is {node_id}
  VirtualBox's name is "{vmname}"
  Amount of memory is {ram}MB
  Console is on port {console} and type is {console_type}
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           state=self.state(),
           vmname=self._settings["vmname"],
           ram=self._settings["ram"],
           host=self.compute().name(),
           port=self.compute().port(),
           console=self._settings["console"],
           console_type=self._settings["console_type"])

        port_info = ""
        for port in self._ports:
            if port.isFree():
                port_info += "     {port_name} is empty\n".format(port_name=port.name())
            else:
                port_info += "     {port_name} {port_description}\n".format(port_name=port.name(),
                                                                            port_description=port.description())

        usage = "\n" + self._settings.get("usage")
        return info + port_info + usage

    def bringToFront(self):
        """
        Bring the VM window to front.
        """

        if self.status() == Node.started:
            # try 2 different window title formats
            bring_window_to_front_from_process_name("VirtualBox.exe", title="{} [".format(self._settings["vmname"]))
            bring_window_to_front_from_process_name("VirtualBox.exe", title="{} (".format(self._settings["vmname"]))

        # bring any console to front
        return Node.bringToFront(self)

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
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.end_devices]

    def __str__(self):

        return "VirtualBox VM"
