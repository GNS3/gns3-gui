# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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

from gns3.qt import QtWidgets
from gns3.controller import Controller
from .settings import SERVERS_SETTINGS
from .local_config import LocalConfig

import logging
log = logging.getLogger(__name__)


class GNS3VM:
    """
    Represents the GNS3 VM.
    """

    def __init__(self):

        self._is_enabled = False
        self._settings = None
        self._loadSettings()
        self._ip_address = None

        from .main_window import MainWindow
        self._main_window = MainWindow.instance()

    def isEnabled(self):

        return self._is_enabled

    def _loadSettings(self):
        """
        Loads the server settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings("Servers", SERVERS_SETTINGS)
        self.update(self._settings["vm"]) # FIXME: don't load settings locally

    def settings(self):
        """
        Returns the GNS3 VM settings.

        :returns: GNS3 VM settings (dict)
        """

        return self._settings["vm"]

    def setSettings(self, settings):
        """
        Set new GNS3 VM settings.

        :param settings: GNS3 VM settings (dict)
        """

        self._settings["vm"].update(settings)
        LocalConfig.instance().saveSectionSettings("Servers", self._settings)

    def _updateGNS3VMCallback(self, result, error=False, **kwargs):
        """
        Callback for ...

        :param progress_dialog: QProgressDialog instance
        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtWidgets.QMessageBox.critical(self._main_window, "GNS3 VM update", "{}".format(result["message"]))
        else:
            print("GNS3 VM successfully updated")

    def _startGNS3VMCallback(self, result, error=False, **kwargs):
        """
        Callback for ...

        :param progress_dialog: QProgressDialog instance
        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtWidgets.QMessageBox.critical(self._main_window, "GNS3 VM start", "{}".format(result["message"]))
        else:
            print("GNS3 VM successfully started")
            self._ip_address = result["ip_address"]

    def ipAddress(self):

        return self._ip_address

    def autoStart(self):

        return self.settings()["auto_start"]

    def start(self):

        Controller.instance().post("/gns3vm/start", self._startGNS3VMCallback, progressText="Starting the GNS3 VM...")

    def update(self, settings):

        self.setSettings(settings)  # FIXME: don't save settings locally
        Controller.instance().put("/gns3vm", self._updateGNS3VMCallback, body=settings, progressText="Updating the GNS3 VM...")

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of GNS3VM

        :returns: instance of GNS3VM
        """

        if not hasattr(GNS3VM, "_instance") or GNS3VM._instance is None:
            GNS3VM._instance = GNS3VM()
        return GNS3VM._instance
