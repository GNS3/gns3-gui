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

import sys
import os
import json
from .version import __version__

import logging
log = logging.getLogger(__name__)


class LocalConfig:

    """
    Handles the local GUI settings.
    """

    def __init__(self):

        self._settings = {}

        if sys.platform.startswith("win"):
            filename = "gns3_gui.ini"
        else:
            filename = "gns3_gui.conf"

        if sys.platform.startswith("darwin"):
            appname = "gns3.net"
        else:
            appname = "GNS3"

        if sys.platform.startswith("win"):

            # On windows, the system wide configuration file location is %COMMON_APPDATA%/GNS3/gns3_gui.conf
            common_appdata = os.path.expandvars("%COMMON_APPDATA%")
            system_wide_config_file = os.path.join(common_appdata, appname, filename)

            # On windows, the user specific configuration file location is %APPDATA%/GNS3/gns3_gui.conf
            appdata = os.path.expandvars("%APPDATA%")
            self._config_file = os.path.join(appdata, appname, filename)

        else:

            # On UNIX-like platforms, the system wide configuration file location is /etc/xdg/GNS3/gns3_gui.conf
            system_wide_config_file = os.path.join("/etc/xdg", appname, filename)

            # On UNIX-like platforms, the user specific configuration file location is /etc/xdg/GNS3/gns3_gui.conf
            home = os.path.expanduser("~")
            self._config_file = os.path.join(home, ".config", appname, filename)

        # First load system wide settings
        if os.path.exists(system_wide_config_file):
            self._settings = self._readConfig(system_wide_config_file)
            if not self._settings:
                log.warning("No system wide settings loaded from {}".format(system_wide_config_file))

        config_file_in_cwd = os.path.join(os.getcwd(), filename)
        if os.path.exists(config_file_in_cwd):
            # use any config file present in the current working directory
            self._config_file = config_file_in_cwd
        elif not os.path.exists(self._config_file):
            try:
                # create the config file if it doesn't exist
                os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
                with open(self._config_file, "w") as f:
                    json.dump({"version": __version__, "type": "settings"}, f)
            except OSError as e:
                log.error("Could not create the config file {}: {}".format(self._config_file, e))

        user_settings = self._readConfig(self._config_file)
        # overwrite system wide settings with user specific ones
        self._settings.update(user_settings)
        self._writeConfig()

    def _readConfig(self, config_path):
        """
        Read the configuration file.
        """

        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except (ValueError, OSError) as e:
            log.error("Could not read the config file {}: {}".format(self._config_file, e))

        return dict()

    def _writeConfig(self):
        """
        Write the configuration file.
        """

        try:
            with open(self._config_file, "w") as f:
                json.dump(self._settings, f, sort_keys=True, indent=4)
        except (ValueError, OSError) as e:
            log.error("Could not write the config file {}: {}".format(self._config_file, e))

    def configFilePath(self):
        """
        Returns the config file path.

        :returns: path to the config file.
        """

        return self._config_file

    def setConfigFilePath(self, config_file):
        """
        Set a new config file

        :returns: path to the config file.
        """

        self._settings = self._readConfig(self._config_file)
        self._config_file = config_file

    def settings(self):
        """
        Get the settings.

        :returns: settings (dict)
        """

        return self._readConfig(self._config_file)

    def setSettings(self, settings):
        """
        Save the settings.

        :param settings: settings to save (dict)
        """

        self._settings.update(settings)
        self._writeConfig()

    def loadSectionSettings(self, section, default_settings):
        """
        Get all the settings from a given section.

        :param default_settings: setting names and default values (dict)

        :returns: settings (dict)
        """

        settings = self.settings().get(section, dict())

        # use default values for missing settings
        for name, value in default_settings.items():
            if name not in settings:
                settings[name] = value

        if section not in self._settings:
            self._settings[section] = {}
        self._settings[section].update(settings)
        return settings

    def saveSectionSettings(self, section, settings):
        """
        Save all the settings in a given section.

        :param section: section name
        :param settings: settings to save (dict)
        """

        if section not in self._settings:
            self._settings[section] = {}
        self._settings[section].update(settings)
        self._writeConfig()

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of LocalConfig.

        :returns: instance of LocalConfig
        """

        if not hasattr(LocalConfig, "_instance"):
            LocalConfig._instance = LocalConfig()
        return LocalConfig._instance
