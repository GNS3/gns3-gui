#!/usr/bin/env python
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

from .qt import QtCore
from .controller import Controller
from .local_config import LocalConfig
from .settings import GENERAL_SETTINGS
from .http_client_error import HttpClientError


import logging
log = logging.getLogger(__name__)


class ApplianceManager(QtCore.QObject):
    """
    Manager for appliances.
    """

    appliances_changed_signal = QtCore.Signal()

    def __init__(self):

        super().__init__()
        self._appliances = []
        self._controller = Controller.instance()
        self._controller.connected_signal.connect(self.refresh)
        self._controller.disconnected_signal.connect(self._controllerDisconnectedSlot)

    def refresh(self, update=False):
        """
        Gets the appliances from the controller.
        """

        if self._controller.connected():
            settings = LocalConfig.instance().loadSectionSettings("MainWindow", GENERAL_SETTINGS)
            symbol_theme = settings["symbol_theme"]
            if update is True:
                try:
                    self._controller.get(
                        "/appliances?update=yes&symbol_theme={}".format(symbol_theme),
                        self._listAppliancesCallback,
                        progress_text="Downloading appliances from online registry...",
                        wait=True,
                        timeout=300
                    )
                except HttpClientError as e:
                    log.error(f"Error while getting appliances list: {e}")
                    return
            else:
                self._controller.get("/appliances?symbol_theme={}".format(symbol_theme), self._listAppliancesCallback)

    def _controllerDisconnectedSlot(self):
        """
        Called when the controller has been disconnected.
        """

        self._appliances = []
        self.appliances_changed_signal.emit()

    def appliances(self):
        """
        Returns the appliances.

        :returns: array of appliances
        """

        return self._appliances

    def _listAppliancesCallback(self, result, error=False, **kwargs):
        """
        Callback to get the appliances.
        """

        if error is True:
            log.error("Error while getting appliances list: {}".format(result.get("message", "unknown")))
            return
        self._appliances = result
        self.appliances_changed_signal.emit()

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of ApplianceManager.
        :returns: instance of ApplianceManager
        """

        if not hasattr(ApplianceManager, '_instance') or ApplianceManager._instance is None:
            ApplianceManager._instance = ApplianceManager()
        return ApplianceManager._instance
