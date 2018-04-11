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
from .utils.server_select import server_select

import logging
log = logging.getLogger(__name__)


class ApplianceManager(QtCore.QObject):
    """
    Manager for appliances and appliance templates.
    """

    appliances_changed_signal = QtCore.Signal()

    def __init__(self):

        super().__init__()
        self._appliance_templates = []
        self._appliances = []
        self._controller = Controller.instance()
        self._controller.connected_signal.connect(self.refresh)
        self._controller.disconnected_signal.connect(self._controllerDisconnectedSlot)
        self.refresh()

    def refresh(self):
        """
        Gets the appliances and appliance templates from the controller.
        """

        if self._controller.connected():
            self._controller.get("/appliances/templates", self._listApplianceTemplateCallback)
            self._controller.get("/appliances", self._listAppliancesCallback)

    def _controllerDisconnectedSlot(self):
        """
        Called when the controller has been disconnected.
        """

        self._appliance_templates = []
        self._appliances = []
        self.appliances_changed_signal.emit()

    def applianceTemplates(self):
        """
        Returns the appliance templates.

        :returns: array of appliance templates
        """

        return self._appliance_templates

    def appliances(self):
        """
        Returns the appliances

        :returns: array of appliances
        """

        return self._appliances

    def getAppliance(self, appliance_id):
        """
        Look for an appliance by appliance ID.

        :param appliance_id: appliance identifier
        :returns: appliance or None
        """

        for appliance in self._appliances:
            if appliance["appliance_id"] == appliance_id:
                return appliance
        return None

    def _listAppliancesCallback(self, result, error=False, **kwargs):
        """
        Callback to get the appliances.
        """

        if error is True:
            log.error("Error while getting the appliances list: {}".format(result["message"]))
            return
        self._appliances = result
        self.appliances_changed_signal.emit()

    def _listApplianceTemplateCallback(self, result, error=False, **kwargs):
        """
        Callback to get the appliance templates.
        """

        if error is True:
            log.error("Error while getting appliance templates list: {}".format(result["message"]))
            return
        self._appliance_templates = result
        self.appliances_changed_signal.emit()

    def createNodeFromApplianceId(self, project, appliance_id, x, y):
        """
        Creates a new node from an appliance.
        """

        for appliance in self._appliances:
            if appliance["appliance_id"] == appliance_id:
                break

        params = {"x": int(x), "y": int(y)}
        if appliance.get("compute_id") is None:
            from .main_window import MainWindow
            server = server_select(MainWindow.instance(), node_type=appliance["node_type"])
            if server is None:
                return False
            params["compute_id"] = server.id()

        self._controller.post("/projects/{project_id}/appliances/{appliance_id}".format(project_id=project.id(), appliance_id=appliance_id),
                              self._createNodeFromApplianceCallback,
                              params,
                              timeout=None)
        return True

    def _createNodeFromApplianceCallback(self, result, error=False, **kwargs):
        """
        Callback to create node from appliance (for errors only).
        """

        if error and "message" in result:
            log.error("Error while creating node: {}".format(result["message"]))
            return

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of ApplianceManager.
        :returns: instance of ApplianceManager
        """

        if not hasattr(ApplianceManager, '_instance') or ApplianceManager._instance is None:
            ApplianceManager._instance = ApplianceManager()
        return ApplianceManager._instance
