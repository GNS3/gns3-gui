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

    def __init__(self):

        appname = "GNS3"

        self._config = configparser.RawConfigParser()
        if sys.platform.startswith("win"):
            filename = "gns3_server.ini"
        else:
            filename = "gns3_server.conf"

        if sys.platform.startswith("win"):
            appdata = os.path.expandvars("%APPDATA%")
            self._config_file = os.path.join(appdata, appname, filename)
        else:
            home = os.path.expanduser("~")
            self._config_file = os.path.join(home, ".config", appname, filename)

        try:
            # create the config file if it doesn't exist
            open(self._config_file, "a").close()
        except OSError as e:
            log.error("Could not create the local server configuration {}: {}".format(self._config_file, e))
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

    def loadSettings(self, section, default_settings, types):
        """
        Get all the settings from a given section.

        :param section: section name
        :param default_settings: setting names and default values (dict)
        :param types: setting types (dict)

        :returns: settings (dict)
        """

        if section not in self._config:
            self._config[section] = {}

        settings = {}
        for name, default in default_settings.items():
            if types[name] is int:
                settings[name] = self._config[section].getint(name, default)
            elif types[name] is bool:
                settings[name] = self._config[section].getboolean(name, default)
            elif types[name] is float:
                settings[name] = self._config[section].getfloat(name, default)
            else:
                settings[name] = self._config[section].get(name, default)

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
