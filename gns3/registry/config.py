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
import shutil


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

        # Raise error if VM already exists
        for item in self._config["Qemu"]["vms"]:
            if item["name"] == new_config["name"]:
                raise ConfigException("{} already exist".format(item["name"]))

        if "qemu" in appliance_config:
            self._add_qemu_config(new_config, appliance_config)
            return
        raise ConfigException("{} not configuration found for Qemu".format(item["name"]))

    def _add_qemu_config(self, new_config, appliance_config):

        new_config["adapter_type"] = appliance_config["qemu"]["adapter_type"]
        new_config["adapters"] = appliance_config["qemu"]["adapters"]
        new_config["cpu_throttling"] = 0
        new_config["ram"] = appliance_config["qemu"]["ram"]
        new_config["console_type"] = appliance_config["qemu"]["console_type"]
        new_config["legacy_networking"] = False
        new_config["process_priority"] = "normal"

        options = appliance_config["qemu"].get("options", "")

        new_config["options"] = options.strip()

        new_config["hda_disk_image"] = appliance_config["qemu"].get("hda_disk_image", "")
        new_config["hdb_disk_image"] = appliance_config["qemu"].get("hdb_disk_image", "")
        new_config["hdc_disk_image"] = appliance_config["qemu"].get("hdc_disk_image", "")
        new_config["hdd_disk_image"] = appliance_config["qemu"].get("hdd_disk_image", "")
        new_config["cdrom_image"] = appliance_config["qemu"].get("cdrom_image", "")
        new_config["initrd_image"] = appliance_config["qemu"].get("initrd_image", "")
        new_config["kernel_command_line"] = appliance_config["qemu"].get("kernel_command_line", "")
        new_config["kernel_image"] = appliance_config["qemu"].get("kernel_image", "")


        new_config["qemu_path"] = "qemu-system-{}".format(appliance_config["qemu"]["arch"])

        if "symbol" in appliance_config:
            new_config["symbol"] = appliance_config["symbol"]
        elif appliance_config["category"] == "guest":
            new_config["symbol"] = ":/symbols/qemu_guest.svg"
        elif appliance_config["category"] == "router":
            new_config["symbol"] = ":/symbols/router.svg"
        elif appliance_config["category"] == "multilayer_switch":
            new_config["symbol"] = ":/symbols/multilayer_switch.svg"
        elif appliance_config["category"] == "multilayer_switch":
            new_config["symbol"] = ":/symbols/multilayer_switch.svg"
        elif appliance_config["category"] == "firewall":
            new_config["symbol"] = ":/symbols/firewall.svg"

        for image in appliance_config["images"]:
            new_config[image["type"]] = self._relative_image_path(image["path"])

        if "boot_priority" in appliance_config:
            new_config["boot_priority"] = appliance_config["boot_priority"]

        self._config["Qemu"]["vms"].append(new_config)

    def _relative_image_path(self, path):
        """
        :returns: Path relative to image directory. Copy the image to the directory if not
        """

        if os.path.abspath(os.path.join(os.path.dirname(path), "..")) == self.images_dir:
            return os.path.basename(path)

        filename = os.path.basename(path)
        self.import_image(path)
        return filename

    def import_image(self, path):
        """
        Copy an image to the image directory.
        """
        filename = os.path.basename(path)
        os.makedirs(os.path.join(self.images_dir, "QEMU"), exist_ok=True)
        dst = os.path.join(self.images_dir, "QEMU", filename)
        shutil.copy(path, dst)

    def save(self):
        """
        Save the configuration file
        """

        with open(self.path, "w+", encoding="utf-8") as f:
            json.dump(self._config, f, indent=4)
