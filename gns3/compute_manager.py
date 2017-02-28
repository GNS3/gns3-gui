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

import sys
import copy
import urllib
import datetime


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
        self._controller.disconnected_signal.connect(self._controllerDisconnectedSlot)
        self._controllerConnectedSlot()

        # If we receive fresh data from the notification feed no need to refresh via an API call
        self._last_computes_refresh = datetime.datetime.now().timestamp()

        self._timer = QtCore.QTimer()
        self._timer.setInterval(1000)
        self._refreshingComputes = False
        self._timer.timeout.connect(self._refreshComputesSlot)
        self._timer.start()

    def _refreshComputesSlot(self):
        if self._refreshingComputes:
            return
        if self._controller.connected() and datetime.datetime.now().timestamp() - self._last_computes_refresh > 5:
            self._last_computes_refresh = datetime.datetime.now().timestamp()
            self._refreshingComputes = True
            self._controller.get("/computes", self._listComputesCallback, showProgress=False, timeout=15)

    def _controllerConnectedSlot(self):
        if self._controller.connected():
            self._refreshingComputes = True
            self._controller.get("/computes", self._listComputesCallback, showProgress=False, timeout=15)

    def _controllerDisconnectedSlot(self):
        for compute_id in list(self._computes):
            del self._computes[compute_id]
            self.deleted_signal.emit(compute_id)

    def _listComputesCallback(self, result, error=False, **kwargs):
        self._refreshingComputes = False
        if error is True:
            log.error("Error while getting compute list: {}".format(result["message"]))
            return

        for compute in result:
            self.computeDataReceivedCallback(compute)

    def computeDataReceivedCallback(self, compute):
        """
        Called when we received data from a compute
        node.
        """
        self._last_computes_refresh = datetime.datetime.now().timestamp()

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
        self._computes[compute_id].setCpuUsagePercent(compute["cpu_usage_percent"])
        self._computes[compute_id].setMemoryUsagePercent(compute["memory_usage_percent"])
        self._computes[compute_id].setCapabilities(compute["capabilities"])

        if new_node:
            self.created_signal.emit(compute_id)
        else:
            self.updated_signal.emit(compute_id)

    def computeIsTheRemoteGNS3VM(self, compute):
        """
        :returns: Boolean True if the remote server is the remote GNS3 VM
        """
        if compute.id() != "local" and compute.id() != "vm":
            if self.vmCompute() and "GNS3 VM ({})".format(compute.name()) == self.vmCompute().name():
                return True
        return False

    def computes(self):
        """
        :returns: List of computes nodes
        """
        computes = []
        for compute in self._computes.values():
            # We filter the remote GNS3 VM compute from the computes list
            if not self.computeIsTheRemoteGNS3VM(compute):
                computes.append(compute)
        return computes

    def vmCompute(self):
        """
        :returns: The GNS3 VM compute node or None
        """
        try:
            return self._computes["vm"]
        except KeyError:
            return None

    def localCompute(self):
        """
        :returns: The local compute node or None
        """
        try:
            return self._computes["local"]
        except KeyError:
            return None

    def localPlatform(self):
        """
        Return the platform of the local compute.

        With a remote controller it could be different of our local platform
        """
        c = self.localCompute()
        if c is None:
            return sys.platform
        return c.capabilities().get("platform", sys.platform)

    def remoteComputes(self):
        """
        :returns: List of non local and non VM computes
        """
        return [c for c in self._computes.values() if c.id() != "local" and c.id() != "vm"]

    def getCompute(self, compute_id):
        if compute_id.startswith("http:") or compute_id.startswith("https:"):
            u = urllib.parse.urlsplit(compute_id)
            for compute in self._computes.values():
                if "{}:{}".format(compute.host(), compute.port()) == u.netloc:
                    return compute
            raise KeyError("Compute {} is missing.".format(compute_id))
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
            if compute_id in ["local", "vm"]:
                continue

            if compute_id not in [c.id() for c in computes]:
                log.debug("Delete compute %s", compute_id)
                self.deleteCompute(compute_id)
            else:
                # Update the changed nodes
                for c in computes:
                    if c.id() == compute_id and c != self._computes[compute_id]:
                        log.debug("Update compute %s", compute_id)
                        self._controller.put("/computes/" + compute_id, None, body=c.__json__())
                        self._computes[compute_id] = c
                        self.updated_signal.emit(compute_id)
        # Create the new nodes
        for compute in computes:
            if compute.id() not in self._computes:
                log.debug("Create compute %s", compute.id())
                self._controller.post("/computes", None, body=compute.__json__())
                self._computes[compute.id()] = compute
                self.created_signal.emit(compute.id())

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
