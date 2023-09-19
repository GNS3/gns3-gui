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
import shutil
from ssl import CertificateError

from ..qt import QtCore, QtWidgets, QtNetwork
from ..controller import Controller
from .config import Config, ConfigException


import logging
log = logging.getLogger(__name__)


class ApplianceToTemplate:
    """
    Appliance installation.
    """

    def new_template(self, appliance_config, server, appliance_version=None, controller_symbols=None, parent=None):
        """
        Creates a new template from an appliance.

        :param appliance_config: Dictionary with appliance configuration
        :param server
        """

        self._parent = parent
        self._registry_version = appliance_config["registry_version"]
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

        if self._registry_version >= 8:
            if appliance_version:
                for version in appliance_config["versions"]:
                    if appliance_version and version["name"] == appliance_version:
                        # inject "usage", "category" and "symbol" specified at the version
                        # level into the template properties
                        usage = version.get("usage")
                        if usage:
                            new_template["usage"] = usage
                        new_template["symbol"] = version.get("symbol", new_template["symbol"])
                        new_template["category"] = version.get("category", new_template["category"])
                        settings = self._get_settings(appliance_config, version.get("settings"))
                        template_type = settings["template_type"]
                        if template_type == "qemu":
                            self._add_qemu_config(new_template, settings["template_properties"], appliance_config)
                        elif template_type == "iou":
                            self._add_iou_config(new_template, settings["template_properties"], appliance_config)
                        elif template_type == "dynamips":
                            self._add_dynamips_config(new_template, settings["template_properties"], appliance_config)
            else:
                # docker appliances have no version
                settings = self._get_settings(appliance_config)
                if settings["template_type"] == "docker":
                    self._add_docker_config(new_template, settings["template_properties"], appliance_config)
        else:
            if "qemu" in appliance_config:
                self._add_qemu_config(new_template, appliance_config["qemu"], appliance_config)
            elif "iou" in appliance_config:
                self._add_iou_config(new_template, appliance_config["iou"], appliance_config)
            elif "dynamips" in appliance_config:
                self._add_dynamips_config(new_template, appliance_config["dynamips"], appliance_config)
            elif "docker" in appliance_config:
                self._add_docker_config(new_template, appliance_config["docker"], appliance_config)
            else:
                raise ConfigException("{} no configuration found for known emulators".format(new_template["name"]))

        return new_template

    def _get_settings(self, appliance_config, settings_name=None):

        default_settings = None
        # first look for default settings, if any ('default' = true, first set that has it)
        for settings in appliance_config["settings"]:
            if settings.get("default", False):
                default_settings = settings
                break

        # then look for specific settings set if a name is provided
        if settings_name:
            for settings in appliance_config["settings"]:
                if settings.get("name") == settings_name:
                    if settings.get("inherit_default_properties", True) and \
                            default_settings and default_settings["template_type"] == settings["template_type"]:
                        default_settings["template_properties"].update(settings["template_properties"])
                        return default_settings
                    return settings
            raise ConfigException("Settings '{}' cannot be found in the appliance file", settings_name)
        elif default_settings:
            return default_settings

        if not appliance_config.get("settings"):
            raise ConfigException("No settings found in the appliance file")

        # if no default settings are specified, use the first available settings set
        return appliance_config["settings"][0]

    def _add_qemu_config(self, new_config, template_properties, appliance_config):

        new_config["template_type"] = "qemu"
        new_config.update(template_properties)

        # the following properties are not valid for a template
        new_config.pop("kvm", None)  # To check KVM setting against the server capabilities
        new_config.pop("path", None)  # Qemu binary selected in previous step
        new_config.pop("arch", None)  # Used for selecting the Qemu binary

        options = template_properties.get("options", "")
        if template_properties.get("kvm", "allow") == "disable" and "-machine accel=tcg" not in options:
            options += " -machine accel=tcg"
        options = options.strip()
        if options:
            new_config["options"] = options

        for image in appliance_config["images"]:
            if image.get("path"):
                new_config[image["type"]] = self._relative_image_path("QEMU", image["path"])

        if "path" in template_properties:
            new_config["qemu_path"] = template_properties["path"]
        else:
            if self._registry_version >= 8:
                # the "arch" field was replaced by the "platform" field in registry version 8
                new_config["qemu_path"] = "qemu-system-{}".format(template_properties["platform"])
            else:
                new_config["qemu_path"] = "qemu-system-{}".format(template_properties["arch"])

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

    def _add_docker_config(self, new_config, template_properties, appliance_config):

        new_config["template_type"] = "docker"
        new_config.update(template_properties)

        if "custom_adapters" in appliance_config:
            new_config["custom_adapters"] = appliance_config["custom_adapters"]

    def _add_dynamips_config(self, new_config, template_properties, appliance_config):

        new_config["template_type"] = "dynamips"
        new_config.update(template_properties)

        for image in appliance_config["images"]:
            new_config[image["type"]] = self._relative_image_path("IOS", image["path"])
            if self._registry_version < 8:
                new_config["idlepc"] = image.get("idlepc", "")

    def _add_iou_config(self, new_config, template_properties, appliance_config):

        new_config["template_type"] = "iou"
        new_config.update(template_properties)
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

        controller = Controller.instance()
        path = os.path.join(Config().symbols_dir, symbol_id)
        if not controller.isRemote() and os.path.exists(path):
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
            if not self._downloadApplianceSymbol(url, path):
                return None
            controller.clearStaticCache()
            if controller.isRemote():
                controller.uploadSymbol(symbol_id, path)
            return os.path.basename(path)
        except (OSError, CertificateError):
            return None

    def _downloadApplianceSymbol(self, url, path, timeout=30):
        """
        Download an appliance symbol in a synchronous way.
        """

        network_manager = QtNetwork.QNetworkAccessManager()
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        request.setRawHeader(b'User-Agent', b'GNS3 symbol downloader')
        reply = network_manager.get(request)
        progress_dialog = QtWidgets.QProgressDialog("Downloading '{}' appliance symbol...".format(os.path.basename(path)), "Cancel", 0, 0, self._parent)
        progress_dialog.setMinimumDuration(0)
        reply.finished.connect(progress_dialog.close)
        QtCore.QTimer.singleShot(timeout * 1000, progress_dialog.close)
        log.debug("Downloading appliance symbol from '{}'".format(url))
        progress_dialog.show()
        progress_dialog.exec_()
        status = reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
        if reply.error() == QtNetwork.QNetworkReply.NoError and status == 200:
            try:
                with open(path, 'wb+') as f:
                    f.write(reply.readAll())
            except OSError as e:
                log.debug("Error while saving appliance symbol to '{}': {}".format(path, e))
                raise
            log.debug("Appliance symbol downloaded and saved to '{}'".format(path))
            return True
        else:
            log.error("Error when downloading appliance symbol from '{}': {}".format(url, reply.errorString()))
        return False
