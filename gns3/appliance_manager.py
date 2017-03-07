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

from .controller import Controller


import logging
log = logging.getLogger(__name__)


class ApplianceManager:

    def __init__(self):
        self._appliance_templates = []
        self._controller = Controller.instance()
        self._controller.connected_signal.connect(self._controllerConnectedSlot)
        self._controller.disconnected_signal.connect(self._controllerDisconnectedSlot)
        self._controllerConnectedSlot()

    def _controllerConnectedSlot(self):
        if self._controller.connected():
            self._controller.get("/appliances/templates", self._listApplianceTemplateCallback)

    def _controllerDisconnectedSlot(self):
        self._appliance_templates = []

    def appliance_templates(self):
        return self._appliance_templates

    def _listApplianceTemplateCallback(self, result, error=False, **kwargs):
        if error is True:
            log.error("Error while getting appliance list: {}".format(result["message"]))
            return
        self._appliance_templates = result

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of ApplianceManager.
        :returns: instance of ApplianceManager
        """

        if not hasattr(ApplianceManager, '_instance') or ApplianceManager._instance is None:
            ApplianceManager._instance = ApplianceManager()
        return ApplianceManager._instance
