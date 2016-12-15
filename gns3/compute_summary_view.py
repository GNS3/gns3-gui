# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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

"""
Compute summary view that list all the compute, their status.
"""

import sip

from .qt import QtGui, QtCore, QtWidgets
from .compute_manager import ComputeManager

import logging
log = logging.getLogger(__name__)


class ComputeItem(QtWidgets.QTreeWidgetItem):

    """
    Custom item for the QTreeWidget instance
    (topology summary view).

    :param parent: parent widget
    :param compute: Compute instance
    """

    def __init__(self, parent, compute):

        super().__init__(parent)
        self._compute = compute
        self._parent = parent
        self._status = "unknown"

        self._refreshStatusSlot()

    def _refreshStatusSlot(self):
        """
        Changes the icon to show the node status (started, stopped etc.)
        """

        if self is None:
            return

        usage = None
        text = self._compute.name()

        if self._compute.cpuUsagePercent() is not None:
            text = "{} CPU {}%, RAM {}%".format(text, self._compute.cpuUsagePercent(), self._compute.memoryUsagePercent())

        self.setText(0, text)
        self.setToolTip(0, text + " on " + self._compute.capabilities().get("platform", ""))

        if self._compute.connected():
            self._status = "connected"
            if usage is None or (self._compute.cpuUsagePercent() < 90 and self._compute.memoryUsagePercent() < 90):
                self.setIcon(0, QtGui.QIcon(':/icons/led_green.svg'))
            else:
                self.setIcon(0, QtGui.QIcon(':/icons/led_yellow.svg'))
        else:
            if self._status == "unknown":
                self.setIcon(0, QtGui.QIcon(':/icons/led_gray.svg'))
            else:
                self._status = "stopped"
                self.setIcon(0, QtGui.QIcon(':/icons/led_red.svg'))
        self._parent.sortItems(0, QtCore.Qt.AscendingOrder)


class ComputeSummaryView(QtWidgets.QTreeWidget):

    """
    Compute summary view implementation.

    :param parent: parent widget
    """

    def __init__(self, parent):

        super().__init__(parent)

        self._computes = {}

        ComputeManager.instance().created_signal.connect(self._computeAddedSlot)
        ComputeManager.instance().updated_signal.connect(self._computeUpdatedSlot)
        ComputeManager.instance().deleted_signal.connect(self._computeRemovedSlot)
        for compute in ComputeManager.instance().computes():
            self._computeAddedSlot(compute.id())

    def _computeAddedSlot(self, compute_id):
        """
        Called when a compute is added to the list of computes

        :params url: URL of the compute
        """

        compute = ComputeManager.instance().getCompute(compute_id)
        if ComputeManager.instance().computeIsTheRemoteGNS3VM(compute):
            return
        self._computes[compute_id] = ComputeItem(self, compute)

    def _computeUpdatedSlot(self, compute_id):
        """
        Called when a compute is updated

        :params url: URL of the compute
        """

        if compute_id in self._computes:
            compute = ComputeManager.instance().getCompute(compute_id)
            # We hide the remote GNS3 VM
            if ComputeManager.instance().computeIsTheRemoteGNS3VM(compute):
                self._computeRemovedSlot(compute_id)
            else:
                self._computes[compute_id]._refreshStatusSlot()
        else:
            self._computeAddedSlot(compute_id)

    def _computeRemovedSlot(self, compute_id):
        """
        Called when a compute is removed to the list of computes

        :params url: URL of the compute
        """

        if compute_id in self._computes:
            self.takeTopLevelItem(self.indexOfTopLevelItem(self._computes[compute_id]))
            del self._computes[compute_id]
