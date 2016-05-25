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

from .compute import Compute
from .controller import Controller

import copy
import logging
log = logging.getLogger(__name__)


class ComputeManager(QtCore.QObject):
    created_signal = QtCore.Signal(str)
    updated_signal = QtCore.Signal(str)
    deleted_signal = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self._computes = {}
        self._controller = Controller.instance()
        self._controller.connected_signal.connect(self._controllerConnectedSlot)
        self._controllerConnectedSlot()

    def _controllerConnectedSlot(self):
        if self._controller.connected():
            self._controller.get("/computes", self._listComputesCallback)

    def _listComputesCallback(self, result, error=False, **kwargs):
        if error is True:
            log.error("Error while getting compute list: {}".format(self.name(), result["message"]))
            return

        for compute in result:
            self.computeDataReceivedCallback(compute)

    def computeDataReceivedCallback(self, compute):
        """
        Called when we received data from a compute
        node.
        """
        new_node = False
        compute_id = compute["compute_id"]
        if compute_id not in self._computes:
            new_node = True
            self._computes[compute_id] = Compute(compute_id)

        self._computes[compute_id].setName(compute["name"])
        self._computes[compute_id].setConnected(compute["connected"])
        self._computes[compute_id].setProtocol(compute["protocol"])
        self._computes[compute_id].setHost(compute["host"])
        self._computes[compute_id].setPort(compute["port"])
        self._computes[compute_id].setUser(compute["user"])

        if new_node:
            self.created_signal.emit(compute_id)
        else:
            self.updated_signal.emit(compute_id)

    def computes(self):
        """
        :returns: List of computes nodes
        """
        return self._computes.values()

    def getCompute(self, compute_id):
        if compute_id not in self._computes:
            self._computes[compute_id] = Compute(compute_id)
            self.created_signal.emit(compute_id)
        return self._computes[compute_id]

    def deleteCompute(self, compute_id):
        if compute_id in self._computes:
            compute = self._computes[compute_id]
            del self._computes[compute_id]
            self._controller.delete("/computes/" + compute_id, None)
        self.deleted_signal.emit(compute_id)

    def updateList(self, computes):
        """
        Sync an array of compute server with remote
        """
        for compute_id in copy.copy(self._computes):
            # Delete compute on controller not in the new computes
            if compute_id not in [c.id() for c in computes]:
                self.deleteCompute(compute_id)

    @staticmethod
    def reset():
        ComputeManager._instance = None

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of ComputeManager.
        :returns: instance of ComputeManager
        """

        if not hasattr(ComputeManager, '_instance') or ComputeManager._instance is None:
            ComputeManager._instance = ComputeManager()
        return ComputeManager._instance
