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

from ..local_config import LocalConfig
from ..controller import Controller

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

        self._path = path
        if self._path is None:
            self._path = LocalConfig.instance().configFilePath()

        with open(self._path, encoding="utf-8") as f:
            self._config = json.load(f)

    @property
    def path(self):
        return self._path

    @property
    def images_dir(self):
        """
        :returns: Location of the images directory on the server
        """
        return Controller.instance().settings()["images_path"]

    @property
    def appliances_dir(self):
        """
        :returns: Location of the images directory on the server
        """
        return Controller.instance().settings()["appliances_path"]

    @property
    def symbols_dir(self):
        """
        :returns: Location of the symbols directory
        """
        return Controller.instance().settings()["symbols_path"]

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

    def save(self):
        """
        Save the configuration file
        """
        LocalConfig.instance().setSettings(self._config)
