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

import copy

from .qt import QtCore
from .controller import Controller
from .appliance import Appliance
from .utils.server_select import server_select

import logging
log = logging.getLogger(__name__)


class ApplianceManager(QtCore.QObject):
    """
    Manager for appliances and appliance templates.
    """

    appliances_changed_signal = QtCore.Signal()
    appliance_templates_changed_signal = QtCore.Signal()

    created_signal = QtCore.Signal(str)
    updated_signal = QtCore.Signal(str)
    deleted_signal = QtCore.Signal(str)

    def __init__(self):

        super().__init__()
        self._appliance_templates = []
        self._appliances = {}
        self._controller = Controller.instance()
        self._controller.connected_signal.connect(self.refresh)
        self._controller.disconnected_signal.connect(self._controllerDisconnectedSlot)

    def refresh(self, update=False):
        """
        Gets the appliances and appliance templates from the controller.
        """

        if self._controller.connected():
            if update is True:
                self._controller.get("/appliances/templates?update=yes", self._listApplianceTemplateCallback, progressText="Downloading appliance templates from online registry...")
            else:
                self._controller.get("/appliances/templates", self._listApplianceTemplateCallback)
            self._controller.get("/appliances", self._listAppliancesCallback)

    def _controllerDisconnectedSlot(self):
        """
        Called when the controller has been disconnected.
        """

        self._appliance_templates = []
        self._appliances = {}
        self.appliances_changed_signal.emit()

    def deleteAppliance(self, appliance_id):
        """
        Deletes an appliance on the controller.

        :param appliance_id: appliance identifier
        """

        if appliance_id in self._appliances and not self._appliances[appliance_id].builtin():
            appliance = self._appliances[appliance_id]
            log.debug("Delete appliance '{}' (ID={})".format(appliance.name(), appliance_id))
            self._controller.delete("/appliances/{appliance_id}".format(appliance_id=appliance_id), None)

    def deleteApplianceCallback(self, result, error=False, **kwargs):
        """
        Callback to delete an appliance
        """

        if error is True:
            log.warning("Error while deleting appliance: {}".format(result.get("message", "unknown")))

        appliance_id = result["appliance_id"]
        if appliance_id in self._appliances and not self._appliances[appliance_id].builtin():
            del self._appliances[appliance_id]
            self.deleted_signal.emit(appliance_id)
            self.appliances_changed_signal.emit()

    def updateAppliance(self, appliance):
        """
        Updates an appliance on the controller.

        :param appliance: appliance object.
        """

        log.debug("Update appliance '{}' (ID={})".format(appliance.name(), appliance.id()))
        self._controller.put("/appliances/{appliance_id}".format(appliance_id=appliance.id()), self.applianceDataReceivedCallback, body=appliance.__json__())

    def updateList(self, appliances):
        """
        Sync an array of appliances with the controller.
        """

        for appliance_id in copy.copy(self._appliances):
            # Delete missing appliances
            if appliance_id not in [appliance.id() for appliance in appliances]:
                self.deleteAppliance(appliance_id)
            else:
                # Update the changed appliances
                for appliance in appliances:
                    if appliance.id() == appliance_id and appliance != self._appliances[appliance_id]:
                        self.updateAppliance(appliance)

        # Create the new appliances
        for appliance in appliances:
            if appliance.id() not in self._appliances:
                log.debug("Create appliance '{}' (ID={})".format(appliance.name(), appliance.id()))
                self._controller.post("/appliances", self.applianceDataReceivedCallback, body=appliance.__json__())

    def applianceDataReceivedCallback(self, result, error=False, **kwargs):
        """
        Callback to add or update an appliance
        """

        if error is True:
            log.error("Error while adding/updating appliance: {}".format(result.get("message", "unknown")))
            return

        appliance_id = result["appliance_id"]
        if appliance_id not in self._appliances:
            self._appliances[appliance_id] = Appliance(result)
            self.created_signal.emit(appliance_id)
        else:
            appliance = self._appliances[appliance_id]
            appliance.setSettings(result)
            self.updated_signal.emit(appliance_id)

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

        try:
            return self._appliances[appliance_id]
        except KeyError:
            return None

    def _listAppliancesCallback(self, result, error=False, **kwargs):
        """
        Callback to get the appliances.
        """

        if error is True:
            log.error("Error while getting appliances list: {}".format(result.get("message", "unknown")))
            return

        for appliance in result:
            appliance_id = appliance["appliance_id"]
            if appliance_id not in self._appliances:
                self._appliances[appliance_id] = Appliance(appliance)
                self.created_signal.emit(appliance_id)
        self.appliances_changed_signal.emit()

    def _listApplianceTemplateCallback(self, result, error=False, **kwargs):
        """
        Callback to get the appliance templates.
        """

        if error is True:
            log.error("Error while getting appliance templates list: {}".format(result.get("message", "unknown")))
            return
        self._appliance_templates = result
        self.appliance_templates_changed_signal.emit()

    def createNodeFromApplianceId(self, project, appliance_id, x, y):
        """
        Creates a new node from an appliance.
        """

        for appliance in self._appliances.values():
            if appliance.id() == appliance_id:
                break

        if not self._controller.connected():
            log.error("Cannot create node: not connected to any controller server")
            return

        if not project or not project.id():
            log.error("Cannot create node: please create a project first!")
            return

        params = {"x": int(x), "y": int(y)}
        if appliance.compute_id() is None:
            from .main_window import MainWindow
            server = server_select(MainWindow.instance(), node_type=appliance.appliance_type())
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
