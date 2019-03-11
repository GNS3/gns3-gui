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

import os
import urllib.request
import shutil
from ssl import CertificateError

from ..controller import Controller
from .config import Config, ConfigException

import logging
log = logging.getLogger(__name__)


class ApplianceToTemplate:
    """
    Appliance installation.
    """

    def new_template(self, appliance_config, server, controller_symbols=None):
        """
        Creates a new template from an appliance.

        :param appliance_config: Dictionary with appliance configuration
        :param server
        """

        new_template = {
            "compute_id": server,
            "name": appliance_config["name"]
        }

        if "usage" in appliance_config:
            new_template["usage"] = appliance_config["usage"]

        if appliance_config["category"] == "multilayer_switch":
            new_template["category"] = "switch"
        else:
            new_template["category"] = appliance_config["category"]

        if "symbol" in appliance_config:
            new_template["symbol"] = self._set_symbol(appliance_config["symbol"], controller_symbols)

        if new_template.get("symbol") is None:
            if appliance_config["category"] == "guest":
                if "docker" in appliance_config:
                    new_template["symbol"] = ":/symbols/docker_guest.svg"
                else:
                    new_template["symbol"] = ":/symbols/qemu_guest.svg"
            elif appliance_config["category"] == "router":
                new_template["symbol"] = ":/symbols/router.svg"
            elif appliance_config["category"] == "switch":
                new_template["symbol"] = ":/symbols/ethernet_switch.svg"
            elif appliance_config["category"] == "multilayer_switch":
                new_template["symbol"] = ":/symbols/multilayer_switch.svg"
            elif appliance_config["category"] == "firewall":
                new_template["symbol"] = ":/symbols/firewall.svg"

        if "qemu" in appliance_config:
            new_template["template_type"] = "qemu"
            self._add_qemu_config(new_template, appliance_config)
        elif "iou" in appliance_config:
            new_template["template_type"] = "iou"
            self._add_iou_config(new_template, appliance_config)
        elif "dynamips" in appliance_config:
            new_template["template_type"] = "dynamips"
            self._add_dynamips_config(new_template, appliance_config)
        elif "docker" in appliance_config:
            new_template["template_type"] = "docker"
            self._add_docker_config(new_template, appliance_config)
        else:
            raise ConfigException("{} no configuration found for known emulators".format(new_template["name"]))

        return new_template

    def _add_qemu_config(self, new_config, appliance_config):

        new_config.update(appliance_config["qemu"])

        # the following properties are not valid for a template
        new_config.pop("kvm", None)
        new_config.pop("path", None)
        new_config.pop("arch", None)

        options = appliance_config["qemu"].get("options", "")
        if appliance_config["qemu"].get("kvm", "allow") == "disable" and "-no-kvm" not in options:
            options += " -no-kvm"
        new_config["options"] = options.strip()

        for image in appliance_config["images"]:
            if image.get("path"):
                new_config[image["type"]] = self._relative_image_path("QEMU", image["path"])

        if "path" in appliance_config["qemu"]:
            new_config["qemu_path"] = appliance_config["qemu"]["path"]
        else:
            new_config["qemu_path"] = "qemu-system-{}".format(appliance_config["qemu"]["arch"])

        if "first_port_name" in appliance_config:
            new_config["first_port_name"] = appliance_config["first_port_name"]

        if "port_name_format" in appliance_config:
            new_config["port_name_format"] = appliance_config["port_name_format"]

        if "port_segment_size" in appliance_config:
            new_config["port_segment_size"] = appliance_config["port_segment_size"]

        if "custom_adapters" in appliance_config:
            new_config["custom_adapters"] = appliance_config["custom_adapters"]

        if "linked_clone" in appliance_config:
            new_config["linked_clone"] = appliance_config["linked_clone"]

    def _add_docker_config(self, new_config, appliance_config):

        new_config.update(appliance_config["docker"])

        if "custom_adapters" in appliance_config:
            new_config["custom_adapters"] = appliance_config["custom_adapters"]

    def _add_dynamips_config(self, new_config, appliance_config):

        new_config.update(appliance_config["dynamips"])

        for image in appliance_config["images"]:
            new_config[image["type"]] = self._relative_image_path("IOS", image["path"])
            new_config["idlepc"] = image.get("idlepc", "")

    def _add_iou_config(self, new_config, appliance_config):

        new_config.update(appliance_config["iou"])
        for image in appliance_config["images"]:
            if "path" not in image:
                raise ConfigException("Disk image is missing")
            new_config[image["type"]] = self._relative_image_path("IOU", image["path"])
        new_config["path"] = new_config["image"]

    def _relative_image_path(self, image_dir_type, path):
        """

        :param image_dir_type: Type of image directory
        :param filename: Filename at the end of the process
        :param path: Full path to the file
        :returns: Path relative to image directory.
        Copy the image to the directory if not already in the directory
        """

        images_dir = os.path.join(Config().images_dir, image_dir_type)
        path = os.path.abspath(path)
        if os.path.commonprefix([images_dir, path]) == images_dir:
            return path.replace(images_dir, '').strip('/\\')

        return os.path.basename(path)

    def _set_symbol(self, symbol_id, controller_symbols):
        """
        Check if exists on controller or download symbol from the web if needed
        """

        # GNS3 builtin symbol
        if symbol_id.startswith(":/symbols/"):
            return symbol_id

        path = os.path.join(Config().symbols_dir, symbol_id)
        if os.path.exists(path):
            return os.path.basename(path)

        if controller_symbols:
            is_symbol_on_controller = len([s for s in controller_symbols if s['symbol_id'] == symbol_id]) > 0

            if is_symbol_on_controller:
                cached = Controller.instance().getStaticCachedPath(symbol_id)
                if os.path.exists(cached):
                    try:
                        shutil.copy(cached, path)
                    except IOError as e:
                        log.warning("Cannot copy cached symbol from `{}` to `{}` due `{}`".format(cached, path, e))
                return symbol_id

        url = "https://raw.githubusercontent.com/GNS3/gns3-registry/master/symbols/{}".format(symbol_id)
        try:
            urllib.request.urlretrieve(url, path)
            controller = Controller.instance()
            controller.clearStaticCache()
            if controller.isRemote():
                controller.uploadSymbol(symbol_id, path)
            return os.path.basename(path)
        except (OSError, CertificateError):
            return None
