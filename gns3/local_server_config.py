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
import sys
import configparser


import logging
log = logging.getLogger(__name__)


class LocalServerConfig:

    """
    Local server configuration.
    """

    def __init__(self, config_file=None):

        appname = "GNS3"

        self._config = configparser.RawConfigParser()

        if config_file:
            self._config_file = config_file
        else:
            if sys.platform.startswith("win"):
                filename = "gns3_server.ini"
            else:
                filename = "gns3_server.conf"

            from .local_config import LocalConfig
            if sys.platform.startswith("win"):
                self._config_file = os.path.join(LocalConfig.instance().configDirectory(), filename)
            else:
                self._config_file = os.path.join(LocalConfig.instance().configDirectory(), filename)

        try:
            # create the config file if it doesn't exist
            open(self._config_file, "a").close()
        except OSError as e:
            log.error("Could not create the local server configuration {}: {}".format(self._config_file, e))
        self.readConfig()

    def setConfigFile(self, path):
        """
        Change the location of the server config (use for test)
        """
        self._config = configparser.RawConfigParser()
        self._config_file = path
        self.readConfig()

    def readConfig(self):
        """
        Read the configuration file.
        """

        try:
            self._config.read(self._config_file, encoding="utf-8")
        except (OSError, configparser.Error, UnicodeEncodeError, UnicodeDecodeError) as e:
            log.error("Could not read the local server configuration {}: {}".format(self._config_file, e))

    def writeConfig(self):
        """
        Write the configuration file.
        """

        try:
            log.debug("Write configuration file %s", self._config_file)
            with open(self._config_file, "w", encoding="utf-8") as fp:
                self._config.write(fp)
        except (OSError, configparser.Error) as e:
            log.error("Could not write the local server configuration {}: {}".format(self._config_file, e))

    def loadSettings(self, section, default_settings):
        """
        Get all the settings from a given section.

        :param section: section name
        :param default_settings: setting names and default values (dict)

        :returns: settings (dict)
        """

        if section not in self._config:
            self._config[section] = {}

        settings = {}
        for name, default in default_settings.items():
            if isinstance(default, bool):
                settings[name] = self._config[section].getboolean(name, default)
            elif isinstance(default, int):
                settings[name] = self._config[section].getint(name, default)
            elif isinstance(default, float):
                settings[name] = self._config[section].getfloat(name, default)
            else:
                settings[name] = self._config[section].get(name, default)
                if settings[name] == "None":
                    settings[name] = None

        # sync with the config file
        self.saveSettings(section, settings)
        return settings

    def saveSettings(self, section, settings):
        """
        Save all the settings in a given section.

        :param section: section name
        :param settings: settings to save (dict)
        """

        changed = False
        if section not in self._config:
            self._config[section] = {}
            changed = True

        for name, value in settings.items():
            if name not in self._config[section] or self._config[section][name] != str(value):
                self._config[section][name] = str(value)
                changed = True

        if changed:
            self.writeConfig()

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of LocalServerConfig.

        :returns: instance of Config
        """

        if not hasattr(LocalServerConfig, "_instance"):
            LocalServerConfig._instance = LocalServerConfig()
        return LocalServerConfig._instance
