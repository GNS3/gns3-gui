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
Dialog to manage the snapshots.
"""

from ..qt import QtCore, QtWidgets
from ..ui.snapshots_dialog_ui import Ui_SnapshotsDialog
from ..controller import Controller

from datetime import datetime

import logging
log = logging.getLogger(__name__)


class SnapshotsDialog(QtWidgets.QDialog, Ui_SnapshotsDialog):

    """
    Snapshots dialog implementation.

    :param parent: parent widget
    """

    def __init__(self, parent, project):

        super().__init__(parent)
        self.setupUi(self)

        self._project = project

        self.uiCreatePushButton.clicked.connect(self._createSnapshotSlot)
        self.uiDeletePushButton.clicked.connect(self._deleteSnapshotSlot)
        self.uiRestorePushButton.clicked.connect(self._restoreSnapshotSlot)
        self.uiSnapshotsList.itemDoubleClicked.connect(self._snapshotDoubleClickedSlot)
        self._listSnapshots()

    def _listSnapshots(self):
        """
        Lists all available snapshots.
        """

        self.uiSnapshotsList.clear()
        if self._project:
            Controller.instance().get("/projects/{}/snapshots".format(self._project.id()), self._listSnapshotsCallback)

    def _listSnapshotsCallback(self, result, error=False, server=None, context={}, **kwargs):
        if error:
            if result:
                log.error(result["message"])
            return

        for snapshot in result:
            item = QtWidgets.QListWidgetItem(self.uiSnapshotsList)
            item.setText("{} on {}".format(snapshot["name"], datetime.fromtimestamp(snapshot["created_at"]).strftime("%d/%m/%y at %H:%M:%S")))
            item.setData(QtCore.Qt.UserRole, snapshot["snapshot_id"])

        if self.uiSnapshotsList.count():
            self.uiSnapshotsList.setCurrentRow(0)
            self.uiDeletePushButton.setEnabled(True)
            self.uiRestorePushButton.setEnabled(True)
        else:
            self.uiDeletePushButton.setEnabled(False)
            self.uiRestorePushButton.setEnabled(False)

    def _createSnapshotSlot(self):
        """
        Slot to create a snapshot.
        """

        snapshot_name, ok = QtWidgets.QInputDialog.getText(self, "Snapshot", "Snapshot name:", QtWidgets.QLineEdit.Normal, "Unnamed")
        if ok and snapshot_name and self._project:
            Controller.instance().post("/projects/{}/snapshots".format(self._project.id()),
                                       self._createSnapshotsCallback,
                                       {"name": snapshot_name},
                                       progressText="Creation of snapshot '{}' in progress...".format(snapshot_name),
                                       timeout=None)

    def _createSnapshotsCallback(self, result, error=False, server=None, context={}, **kwargs):
        if error:
            if result:
                log.error(result["message"])
            else:
                log.error("Cannot create snapshot of project")
            return
        self._listSnapshots()

    def _deleteSnapshotSlot(self):
        """
        Slot to delete a snapshot.
        """

        item = self.uiSnapshotsList.currentItem()
        if item:
            snapshot_id = item.data(QtCore.Qt.UserRole)
            Controller.instance().delete("/projects/{}/snapshots/{}".format(self._project.id(), snapshot_id), self._deleteSnapshotsCallback)

    def _deleteSnapshotsCallback(self, result, error=False, server=None, context={}, **kwargs):

        if error:
            if result:
                log.error(result["message"])
            return
        self._listSnapshots()

    def _restoreSnapshotSlot(self):
        """
        Slot to restore a snapshot.
        """

        item = self.uiSnapshotsList.currentItem()
        if item:
            snapshot_id = item.data(QtCore.Qt.UserRole)
            self._restoreSnapshot(snapshot_id)

    def _restoreSnapshot(self, snapshot_id):
        """
        Restores a snapshot.

        :param snapshot_id: id of the snapshot
        """

        reply = QtWidgets.QMessageBox.question(self, "Snapshots", "This will discard any changes made to your project since the snapshot was taken, would you like to proceed?", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
        if reply == QtWidgets.QMessageBox.Cancel:
            return

        Controller.instance().post("/projects/{}/snapshots/{}/restore".format(self._project.id(), snapshot_id),
                                   self._restoreSnapshotsCallback, progressText="Restoring snapshot...", timeout=None)

    def _restoreSnapshotsCallback(self, result, error=False, server=None, context={}, **kwargs):

        if error:
            if result:
                log.error(result["message"])
            return
        self.accept()

    def _snapshotDoubleClickedSlot(self, item):
        """
        Slot to restore a snapshot when it is double clicked.
        """

        snapshot_id = item.data(QtCore.Qt.UserRole)
        self._restoreSnapshot(snapshot_id)
