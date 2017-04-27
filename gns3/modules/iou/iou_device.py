# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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
from gns3.node import Node
from gns3.utils.normalize_filename import normalize_filename
from .settings import IOU_DEVICE_SETTINGS

import logging
log = logging.getLogger(__name__)


class IOUDevice(Node):

    """
    IOU device.

    :param module: parent module for this node
    :param server: GNS3 server instance
    :param project: Project instance
    """

    URL_PREFIX = "iou"

    def __init__(self, module, server, project):
        super().__init__(module, server, project)

        iou_device_settings = {"path": "",
                               "md5sum": "",
                               "startup_config": "",
                               "private_config": "",
                               "l1_keepalives": False,
                               "use_default_iou_values": IOU_DEVICE_SETTINGS["use_default_iou_values"],
                               "ram": IOU_DEVICE_SETTINGS["ram"],
                               "nvram": IOU_DEVICE_SETTINGS["nvram"],
                               "ethernet_adapters": IOU_DEVICE_SETTINGS["ethernet_adapters"],
                               "serial_adapters": IOU_DEVICE_SETTINGS["serial_adapters"],
                               "console": None,
                               "console_host": None}

        self.settings().update(iou_device_settings)

    def _createCallback(self, result):
        """
        Callback for create.

        :param result: server response
        """
        pass

    def start(self):
        """
        Starts this VM instance.
        """

        if self.status() == Node.started:
            log.debug("{} is already running".format(self.name()))
            return

        log.debug("{} is starting".format(self.name()))
        self.controllerHttpPost("/nodes/{node_id}/start".format(node_id=self._node_id), self._startCallback, progressText="{} is starting".format(self.name()))

    def update(self, new_settings):
        """
        Updates the settings for this IOU device.

        :param new_settings: settings dictionary
        """

        params = {}
        for name, value in new_settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        if params:
            self._update(params)

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
  Node ID is {id}, server's IOU device ID is {node_id}
  Hardware is Cisco IOU generic device with {memories_info}
  Device's server runs on {host}, console is on port {console}
  Image is {image_name}
  {nb_ethernet} Ethernet adapters and {nb_serial} serial adapters installed
""".format(name=self.name(),
           id=self.id(),
           node_id=self._node_id,
           state=state,
           memories_info=memories_info,
           host=self.compute().name(),
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

    def configFiles(self):
        """
        Name of the configuration files
        """
        return ["startup-config.cfg", "private-config.cfg"]

    def console(self):
        """
        Returns the console port for this IOU device.

        :returns: port (integer)
        """

        return self._settings["console"]

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node properties dialog.

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

        return ":/symbols/multilayer_switch.svg"

    @staticmethod
    def symbolName():

        return "IOU device"

    @staticmethod
    def categories():
        """
        Returns the node categories the node is part of (used by the device panel).

        :returns: list of node categories
        """

        return [Node.routers, Node.switches]

    def __str__(self):

        return "IOU device"
