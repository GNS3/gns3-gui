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
import shutil
import copy

import psutil

from .qt import QtCore, QtWidgets
from .version import __version__, __version_info__
from .utils import parse_version
from .local_server_config import LocalServerConfig
from .settings import LOCAL_SERVER_SETTINGS

import logging
log = logging.getLogger(__name__)


class LocalConfig(QtCore.QObject):

    """
    Handles the local GUI settings.
    """

    config_changed_signal = QtCore.Signal()

    def __init__(self, config_file=None):
        """
        :param config_file: Path to the config file (override all other config, useful for tests)
        """

        super().__init__()
        self._profile = None
        self._config_file = config_file
        self._migrateOldConfigPath()
        self._resetLoadConfig()

    def _resetLoadConfig(self):
        """
        Reload the config from scratch everything is clean

        """
        self._settings = {}
        self._last_config_changed = None
        if sys.platform.startswith("win"):
            filename = "gns3_gui.ini"
        else:
            filename = "gns3_gui.conf"

        appname = "GNS3"

        if sys.platform.startswith("win"):
            # On windows, the system wide configuration file location is %COMMON_APPDATA%/GNS3/gns3_gui.conf
            common_appdata = os.path.expandvars("%COMMON_APPDATA%")
            system_wide_config_file = os.path.join(common_appdata, appname, filename)
        else:
            # On UNIX-like platforms, the system wide configuration file location is /etc/xdg/GNS3/gns3_gui.conf
            system_wide_config_file = os.path.join("/etc/xdg", appname, filename)

        if not self._config_file:
            self._config_file = os.path.join(self.configDirectory(), filename)

        # First load system wide settings
        if os.path.exists(system_wide_config_file):
            self._readConfig(system_wide_config_file)

        config_file_in_cwd = os.path.join(os.getcwd(), filename)
        if os.path.exists(config_file_in_cwd):
            # use any config file present in the current working directory
            self._config_file = config_file_in_cwd
        elif not os.path.exists(self._config_file):
            try:
                # create the config file if it doesn't exist
                os.makedirs(os.path.dirname(self._config_file), exist_ok=True)

                if sys.platform.startswith("win"):
                    old_config_path = os.path.join(os.path.expandvars("%APPDATA%"), "GNS3", filename)
                else:
                    old_config_path = os.path.join(os.path.expanduser("~"), ".config", "GNS3", filename)

                # TODO: migrate versioned config file from a previous version of GNS3 (for instance 2.2 -> 2.3) + support profiles
                if os.path.exists(old_config_path):
                    # migrate post version 2.2.0 configuration file
                    shutil.copyfile(old_config_path, self._config_file)
                    # reset the local server path and ubridge path
                    settings = LocalServerConfig.instance().loadSettings("Server", LOCAL_SERVER_SETTINGS)
                    settings["path"] = ""
                    settings["ubridge_path"] = ""
                    LocalServerConfig.instance().saveSettings("Server", settings)
                else:
                    # create a new config
                    with open(self._config_file, "w", encoding="utf-8") as f:
                        json.dump({"version": __version__, "type": "settings"}, f)
            except OSError as e:
                log.error("Could not create the config file {}: {}".format(self._config_file, e))

        user_settings = self._readConfig(self._config_file)
        # overwrite system wide settings with user specific ones
        self._settings.update(user_settings)
        self._migrateOldConfig()
        self.writeConfig()

    def profile(self):
        """
        :returns: Current settings profile
        """
        return self._profile

    def setProfile(self, profile):
        previous_profile = self._profile
        if profile == "default":
            self._profile = None
        else:
            self._profile = profile
        if previous_profile != self._profile:
            self._config_file = None
            self._resetLoadConfig()

    def configDirectory(self):
        """
        Get the configuration directory
        """

        version = "{}.{}".format(__version_info__[0], __version_info__[1])
        if sys.platform.startswith("win"):
            appdata = os.path.expandvars("%APPDATA%")
            path = os.path.join(appdata, "GNS3", version)
        else:
            home = os.path.expanduser("~")
            path = os.path.join(home, ".config", "GNS3", version)

        if self._profile is not None:
            path = os.path.join(path, "profiles", self._profile)

        return os.path.normpath(path)

    def runAsRootPath(self):
        """
        Gets run as root filename
        :return: string
        """
        return os.path.join(self.configDirectory(), "run_as_root")

    def _migrateOldConfigPath(self):
        """
        Migrate pre 1.4 config path
        """

        # In < 1.4 on Mac the config was in a gns3.net directory
        # We have move to same location as Linux
        if sys.platform.startswith("darwin"):
            version = "{}.{}".format(__version_info__[0], __version_info__[1])
            old_path = os.path.join(os.path.expanduser("~"), ".config", "gns3.net")
            new_path = os.path.join(os.path.expanduser("~"), ".config", "GNS3", version)
            if os.path.exists(old_path) and not os.path.exists(new_path):
                try:
                    shutil.copytree(old_path, new_path)
                except OSError as e:
                    log.error("Can't copy the old config: %s", str(e))

    def _migrateOldConfig(self):
        """
        Migrate config from a previous version.
        """

        # Display an error if settings come from a more recent version of GNS3
        # patch level version are compatible (ex 1.5.3 and 1.5.2). But if you open
        # settings from 1.6.1 with 1.5.1 you will have an error
        if "version" in self._settings:
            if parse_version(self._settings["version"])[:2] > parse_version(__version__)[:2]:
                app = QtWidgets.QApplication(sys.argv)  # We need to create an application because settings are loaded before Qt init
                error_message = "Settings are for version {} of GNS3. It is not possible to use a previous version of GNS3 without risking losing data. Delete the settings in '{}' to start GNS3".format(self._settings["version"], self.configDirectory())
                QtWidgets.QMessageBox.critical(False, "Version error", error_message)
                # Exit immediately not clean but we want to avoid any side effect that could corrupt the file
                QtCore.QTimer.singleShot(0, app.quit)
                app.exec_()
                sys.exit(1)

        if "version" not in self._settings or parse_version(self._settings["version"]) < parse_version("1.4.0alpha1"):

             servers = self._settings.get("Servers", {})

             if "LocalServer" in self._settings:
                servers["local_server"] = copy.copy(self._settings["LocalServer"])

                 # We migrate the server binary for OSX due to the change from py2app to CX freeze
                if servers["local_server"]["path"] == "/Applications/GNS3.app/Contents/Resources/server/Contents/MacOS/gns3server":
                    servers["local_server"]["path"] = "gns3server"

             if "RemoteServers" in self._settings:
                servers["remote_servers"] = copy.copy(self._settings["RemoteServers"])

             self._settings["Servers"] = servers

             if "GUI" in self._settings:
                main_window = self._settings.get("MainWindow", {})
                main_window["hide_getting_started_dialog"] = self._settings["GUI"].get("hide_getting_started_dialog", False)
                self._settings["MainWindow"] = main_window

        if "version" not in self._settings or parse_version(self._settings["version"]) < parse_version("1.4.1dev2"):
            if sys.platform.startswith("darwin"):
                from .settings import PRECONFIGURED_TELNET_CONSOLE_COMMANDS, DEFAULT_TELNET_CONSOLE_COMMAND

                if "MainWindow" in self._settings:
                    if self._settings["MainWindow"].get("telnet_console_command") not in PRECONFIGURED_TELNET_CONSOLE_COMMANDS.values():
                        self._settings["MainWindow"]["telnet_console_command"] = DEFAULT_TELNET_CONSOLE_COMMAND

         # Migrate 1.X to 2.0
        if "version" not in self._settings or parse_version(self._settings["version"]) < parse_version("2.0.0"):
            if "Qemu" in self._settings:
                # The internet VM is replaced by the nat Node
                # we remove it from the list of available VM
                vms = []
                for vm in self._settings["Qemu"].get("vms", []):
                    if vm.get("hda_disk_image") != "core-linux-6.4-internet-0.1.img":
                        vms.append(vm)
                self._settings["Qemu"]["vms"] = vms

         # Starting with 2.0.0dev5 IOU licence is stored in the settings
        if "version" not in self._settings or parse_version(self._settings["version"]) < parse_version("2.0.0"):
            if "IOU" in self._settings and "iourc_path" in self._settings["IOU"] and "iourc_content" not in self._settings["IOU"]:
                try:
                    with open(self._settings["IOU"]["iourc_path"], "r", encoding="utf-8") as f:
                        self._settings["IOU"]["iourc_content"] = f.read().replace("\r\n", "\n")
                        del self._settings["IOU"]["iourc_path"]
                except OSError as e:
                    log.warning("Can't import IOU licence {}: {}".format(self._settings["IOU"]["iourc_path"], str(e)))
                except UnicodeDecodeError as e:
                    log.warning("Non ascii characters in iourc file {}, please remove them: {}".format(self._settings["IOU"]["iourc_path"], str(e)))

    def _readConfig(self, config_path):
        """
        Read the configuration file.
        """

        log.debug("Load config from %s", config_path)
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._last_config_changed = os.stat(config_path).st_mtime
                config = json.load(f)
                self._settings.update(config)
        except (ValueError, OSError) as e:
            log.error("Could not read the config file {}: {}".format(self._config_file, e))

        # Update already loaded section
        for section in self._settings.keys():
            if isinstance(self._settings[section], dict):
                self.loadSectionSettings(section, self._settings[section])

        return dict()

    def writeConfig(self):
        """
        Write the configuration file.
        """

        self._settings["version"] = __version__
        try:
            temporary = os.path.join(os.path.dirname(self._config_file), "gns3_gui.tmp")
            with open(temporary, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, sort_keys=True, indent=4)
            shutil.move(temporary, self._config_file)
            log.debug("Configuration save to %s", self._config_file)
            self._last_config_changed = os.stat(self._config_file).st_mtime
        except (ValueError, OSError) as e:
            log.error("Could not write the config file {}: {}".format(self._config_file, e))

    def checkConfigChanged(self):

        try:
            if self._last_config_changed and self._last_config_changed < os.stat(self._config_file).st_mtime:
                log.debug("Client config has changed, reloading it...")
                self._readConfig(self._config_file)
                self.config_changed_signal.emit()
        except OSError as e:
            log.error("Error when checking for changes {}: {}".format(self._config_file, str(e)))

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

        self._config_file = config_file
        self._resetLoadConfig()

    def settings(self):
        """
        Get the settings.

        :returns: settings (dict)
        """

        return copy.deepcopy(self._settings)

    def setSettings(self, settings):
        """
        Save the settings.

        :param settings: settings to save (dict)
        """

        if self._settings != settings:
            self._settings.update(settings)
            self.writeConfig()
            self.config_changed_signal.emit()

    def loadSectionSettings(self, section, default_settings):
        """
        Get all the settings from a given section.

        :param default_settings: setting names and default values (dict)

        :returns: settings (dict)
        """

        settings = self.settings().get(section, dict())
        changed = False

        def _copySettings(local, default):
            """
            Copy only existing settings, ignore the other.
            Add default values if require.
            """
            nonlocal changed

            # use default values for missing settings
            for name, value in default.items():
                if name not in local:
                    local[name] = value
                    changed = True
                elif isinstance(value, dict):
                    local[name] = _copySettings(local[name], default[name])
            return local

        settings = _copySettings(settings, default_settings)
        self._settings[section] = settings

        if changed:
            log.debug("Section %s has missing default values. Adding keys %s Saving configuration", section, ','.join(set(default_settings.keys()) - set(settings.keys())))
            self.writeConfig()
        return copy.deepcopy(settings)

    def saveSectionSettings(self, section, settings):
        """
        Save all the settings in a given section.

        :param section: section name
        :param settings: settings to save (dict)
        """

        if section not in self._settings:
            self._settings[section] = {}

        if self._settings[section] != settings:
            self._settings[section].update(copy.deepcopy(settings))
            log.debug("Section %s has changed. Saving configuration", section)
            self.writeConfig()
        else:
            log.debug("Section %s has not changed. Skip saving configuration", section)

    def experimental(self):
        """
        :returns: Boolean. True if experimental features allowed
        """

        from gns3.settings import GENERAL_SETTINGS
        return self.loadSectionSettings("MainWindow", GENERAL_SETTINGS)["experimental_features"]

    def hdpi(self):
        """
        :returns: Boolean. True if hdpi is allowed
        """

        from gns3.settings import GENERAL_SETTINGS
        return self.loadSectionSettings("MainWindow", GENERAL_SETTINGS)["hdpi"]

    def multiProfiles(self):
        """
        :returns: Boolean. True if multi_profiles is enabled
        """

        from gns3.settings import GENERAL_SETTINGS
        return self.loadSectionSettings("MainWindow", GENERAL_SETTINGS)["multi_profiles"]

    def setMultiProfiles(self, value):
        from gns3.settings import GENERAL_SETTINGS
        settings = self.loadSectionSettings("MainWindow", GENERAL_SETTINGS)
        settings["multi_profiles"] = value
        self.saveSectionSettings("MainWindow", settings)

    def directFileUpload(self):
        """
        :returns: Boolean. True if direct_file_upload is enabled
        """

        from gns3.settings import GENERAL_SETTINGS
        return self.loadSectionSettings("MainWindow", GENERAL_SETTINGS)["direct_file_upload"]

    def setDirectFileUpload(self, value):
        from gns3.settings import GENERAL_SETTINGS
        settings = self.loadSectionSettings("MainWindow", GENERAL_SETTINGS)
        settings["direct_file_upload"] = value
        self.saveSectionSettings("MainWindow", settings)

    def showInterfaceLabelsOnNewProject(self):
        """
        :returns: Boolean. True if show_interface_labels_on_new_project is enabled
        """

        from gns3.settings import GRAPHICS_VIEW_SETTINGS
        return self.loadSectionSettings("GraphicsView", GRAPHICS_VIEW_SETTINGS).get("show_interface_labels_on_new_project", False)

    def setShowInterfaceLabelsOnNewProject(self, value):
        from gns3.settings import GRAPHICS_VIEW_SETTINGS
        settings = self.loadSectionSettings("GraphicsView", GRAPHICS_VIEW_SETTINGS)
        settings["show_interface_labels_on_new_project"] = value
        self.saveSectionSettings("GraphicsView", settings)

    def showGridOnNewProject(self):
        """
        :returns: Boolean. True if show_grid_on_new_project is enabled
        """

        from gns3.settings import GRAPHICS_VIEW_SETTINGS
        return self.loadSectionSettings("GraphicsView", GRAPHICS_VIEW_SETTINGS).get("show_grid_on_new_project", False)

    def snapToGridOnNewProject(self):
        """
        :returns: Boolean. True if snap_to_grid_on_new_project is enabled
        """

        from gns3.settings import GRAPHICS_VIEW_SETTINGS
        return self.loadSectionSettings("GraphicsView", GRAPHICS_VIEW_SETTINGS).get("snap_to_grid_on_new_project", False)

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of LocalConfig.

        :returns: instance of LocalConfig
        """

        if not hasattr(LocalConfig, "_instance") or LocalConfig._instance is None:
            LocalConfig._instance = LocalConfig()
        return LocalConfig._instance

    @staticmethod
    def isMainGui():
        """
        :returns: Return true if we are the main gui (first gui to start)
        """

        my_pid = os.getpid()
        pid_path = os.path.join(LocalConfig.instance().configDirectory(), "gns3_gui.pid")

        if os.path.exists(pid_path):
            try:
                with open(pid_path) as f:
                    pid = int(f.read())
                    if pid != my_pid:
                        try:
                            process = psutil.Process(pid=pid)
                            ps_name = process.name().lower()
                        except (OSError, psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                        else:
                            if "gns3" in ps_name or "python" in ps_name:
                                # Process run under the same user id
                                if sys.platform.startswith("win") or process.uids()[0] == os.getuid():
                                    return False
                    else:
                        return True
            except (OSError, ValueError) as e:
                log.critical("Can't read pid file %s: %s", pid_path, str(e))
                return False

        try:
            with open(pid_path, 'w+') as f:
                f.write(str(my_pid))
        except OSError as e:
            log.critical("Can't write pid file %s: %s", pid_path, str(e))
            return False
        return True
