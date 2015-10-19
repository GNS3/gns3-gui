#!/usr/bin/env python
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


import json
import sys
import os
import urllib
import re

from .image import Image

import logging
log = logging.getLogger(__name__)

class ConfigException(Exception):
    pass


class Config:
    """
    GNS3 config file
    """

    def __init__(self, path=None):
        """
        :params path: Path of the configuration file, otherwise detect it on the system
        """

        self.path = path
        if self.path is None:
            self.path = self._get_standard_config_file_path()

        with open(self.path, encoding="utf-8") as f:
            self._config = json.load(f)

    @property
    def images_dir(self):
        """
        :returns: Location of the images directory on the server
        """
        return self._config["Servers"]["local_server"]["images_path"]

    @property
    def symbols_dir(self):
        """
        :returns: Location of the symbols directory
        """
        return self._config["Servers"]["local_server"]["symbols_path"]

    @property
    def servers(self):
        """
        :returns: List of server present in the configuration file as strings
        """

        servers = ["local"]
        if "vm" in self._config["Servers"] and self._config["Servers"]["vm"].get("auto_start", False):
            servers.append("vm")
        if "remote_servers" in self._config["Servers"]:
            for server in self._config["Servers"]["remote_servers"]:
                if "url" in server:
                    servers.append(server["url"])
        return servers

    def _get_standard_config_file_path(self):

        if sys.platform.startswith("win"):
            filename = "gns3_gui.ini"
        else:
            filename = "gns3_gui.conf"

        appname = "GNS3"

        if sys.platform.startswith("win"):
            appdata = os.path.expandvars("%APPDATA%")
            return os.path.join(appdata, appname, filename)
        else:
            home = os.path.expanduser("~")
            return os.path.join(home, ".config", appname, filename)

    def add_appliance(self, appliance_config, server):
        """
        Add appliance to the user configuration

        :param appliance_config: Dictionary with appliance configuration
        :param server
        """

        new_config = {
            "server": server,
            "name": appliance_config["name"]
        }
        if appliance_config["category"] == "guest":
            new_config["category"] = 2
        elif appliance_config["category"] == "router":
            new_config["category"] = 0
        elif appliance_config["category"] == "firewall":
            new_config["category"] = 3
        elif appliance_config["category"] == "switch":
            new_config["category"] = 1
        elif appliance_config["category"] == "multilayer_switch":
            new_config["category"] = 1

        # Raise error if VM already exists
        for item in self._config["Qemu"]["vms"]:
            if item["name"] == new_config["name"]:
                raise ConfigException("{} already exists".format(item["name"]))

        if "qemu" in appliance_config:
            self._add_qemu_config(new_config, appliance_config)
            return
        raise ConfigException("{} not configuration found for Qemu".format(item["name"]))

    def _add_qemu_config(self, new_config, appliance_config):

        new_config["adapter_type"] = appliance_config["qemu"]["adapter_type"]
        new_config["adapters"] = appliance_config["qemu"]["adapters"]
        new_config["cpu_throttling"] = appliance_config["qemu"].get("cpu_throttling", 0)
        new_config["ram"] = appliance_config["qemu"]["ram"]
        new_config["console_type"] = appliance_config["qemu"]["console_type"]
        new_config["legacy_networking"] = False
        new_config["process_priority"] = appliance_config["qemu"].get("process_priority", "normal")

        options = appliance_config["qemu"].get("options", "")
        if "-nographic" not in options:
            options += " -nographic"
        new_config["options"] = options.strip()

        new_config["hda_disk_image"] = appliance_config["qemu"].get("hda_disk_image", "")
        new_config["hdb_disk_image"] = appliance_config["qemu"].get("hdb_disk_image", "")
        new_config["hdc_disk_image"] = appliance_config["qemu"].get("hdc_disk_image", "")
        new_config["hdd_disk_image"] = appliance_config["qemu"].get("hdd_disk_image", "")
        new_config["cdrom_image"] = appliance_config["qemu"].get("cdrom_image", "")
        new_config["initrd"] = appliance_config["qemu"].get("initrd", "")
        new_config["kernel_command_line"] = appliance_config["qemu"].get("kernel_command_line", "")
        new_config["kernel_image"] = appliance_config["qemu"].get("kernel_image", "")


        new_config["qemu_path"] = "qemu-system-{}".format(appliance_config["qemu"]["arch"])

        if "symbol" in appliance_config:
            new_config["symbol"] = self._set_symbol(appliance_config["symbol"])

        if new_config.get("symbol") is None:
            if appliance_config["category"] == "guest":
                new_config["symbol"] = ":/symbols/qemu_guest.svg"
            elif appliance_config["category"] == "router":
                new_config["symbol"] = ":/symbols/router.svg"
            elif appliance_config["category"] == "switch":
                new_config["symbol"] = ":/symbols/ethernet_switch.svg"
            elif appliance_config["category"] == "multilayer_switch":
                new_config["symbol"] = ":/symbols/multilayer_switch.svg"
            elif appliance_config["category"] == "firewall":
                new_config["symbol"] = ":/symbols/firewall.svg"

        for image in appliance_config["images"]:
            new_config[image["type"]] = self._relative_image_path(image["filename"], image["path"])

        if "boot_priority" in appliance_config:
            new_config["boot_priority"] = appliance_config["boot_priority"]

        if "first_port_name" in appliance_config:
            new_config["first_port_name"] = appliance_config["first_port_name"]

        if "port_name_format" in appliance_config:
            new_config["port_name_format"] = appliance_config["port_name_format"]

        if "port_segment_size" in appliance_config:
            new_config["port_segment_size"] = appliance_config["port_segment_size"]

        if "linked_base" in appliance_config:
            new_config["linked_base"] = appliance_config["linked_base"]

        log.debug("Add appliance QEMU: %s", str(new_config))
        self._config["Qemu"]["vms"].append(new_config)

    def _set_symbol(self, symbol):
        """
        Download symbol for the web if need
        """

        # GNS3 builtin symbol
        if symbol.startswith(":/symbols/"):
            return symbol

        path = os.path.join(self.symbols_dir, symbol)
        if os.path.exists(path):
            return path

        url = "https://raw.githubusercontent.com/GNS3/gns3-registry/master/symbols/{}".format(symbol)
        try:
            urllib.request.urlretrieve(url, path)
            return path
        except OSError:
            return None

    def _relative_image_path(self, filename, path):
        """
        :returns: Path relative to image directory.
        Copy the image to the directory if not already in the directory
        """

        images_dir = os.path.join(self.images_dir, "QEMU")
        path = os.path.abspath(path)
        if os.path.commonprefix([images_dir, path]) == images_dir:
            return path.replace(images_dir, '').strip('/\\')

        if '/' in filename or '\\' in filename:
            # In case of OVA we want to update the OVA name
            base_file = re.split(r'[/\\]', filename)[0]
        else:
            base_file = filename
        Image(path).copy(os.path.join(self.images_dir, "QEMU"), base_file)
        return filename

    def save(self):
        """
        Save the configuration file
        """

        with open(self.path, "w+", encoding="utf-8") as f:
            json.dump(self._config, f, indent=4)
