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

import shutil
import re
import time
import os

from ..qt import QtCore, QtWidgets
from ..utils.progress_dialog import ProgressDialog
from ..utils.process_files_worker import ProcessFilesWorker
from ..ui.snapshots_dialog_ui import Ui_SnapshotsDialog
from ..topology import Topology
from ..node import Node


class SnapshotsDialog(QtWidgets.QDialog, Ui_SnapshotsDialog):

    """
    Snapshots dialog implementation.

    :param parent: parent widget
    """

    def __init__(self, parent, project_path, project_files_dir):

        super().__init__(parent)
        self.setupUi(self)

        self._project_path = project_path
        self._project_files_dir = os.path.join(project_files_dir, "project-files")

        self.uiCreatePushButton.clicked.connect(self._createSnapshotSlot)
        self.uiDeletePushButton.clicked.connect(self._deleteSnapshotSlot)
        self.uiRestorePushButton.clicked.connect(self._restoreSnapshotSlot)
        self.uiSnapshotsList.itemDoubleClicked.connect(self._snapshotDoubleClickedSlot)
        self._listSnaphosts()

    def _listSnaphosts(self):
        """
        Lists all available snapshots.
        """

        self.uiSnapshotsList.clear()
        snapshot_dir = os.path.join(self._project_files_dir, "snapshots")
        if not os.path.isdir(snapshot_dir):
            return

        snapshots = []
        for snapshot in os.listdir(snapshot_dir):
            match = re.search(r"^(.*)_([0-9]+)_([0-9]+)", snapshot)
            if match:
                snapshot_name = match.group(1)
                snapshot_date = match.group(2)[:2] + '/' + match.group(2)[2:4] + '/' + match.group(2)[4:]
                snapshot_time = match.group(3)[:2] + ':' + match.group(3)[2:4] + ':' + match.group(3)[4:]
                snapshots.append((snapshot_name, snapshot_date, snapshot_time))

        # Sort by date
        snapshots = sorted(snapshots, key=(lambda v: v[1] + v[2]))
        for snapshot_name, snapshot_date, snapshot_time in snapshots:
            item = QtWidgets.QListWidgetItem(self.uiSnapshotsList)
            item.setText("{} on {} at {}".format(snapshot_name, snapshot_date, snapshot_time))
            item.setData(QtCore.Qt.UserRole, os.path.join(snapshot_dir, snapshot))


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
        if ok and snapshot_name:
            from ..main_window import MainWindow
            MainWindow.instance().saveProject(self._project_path)
            snapshot_name = "{name}_{date}".format(name=snapshot_name, date=time.strftime("%d%m%y_%H%M%S"))
            snapshot_dir = os.path.join(self._project_files_dir, "snapshots", snapshot_name)
            worker = ProcessFilesWorker(os.path.dirname(self._project_path), snapshot_dir, skip_dirs=["snapshots"])
            progress_dialog = ProgressDialog(worker, "Creating snapshot", "Copying project files...", "Cancel", parent=self)
            progress_dialog.show()
            progress_dialog.exec_()
            self._listSnaphosts()

    def _deleteSnapshotSlot(self):
        """
        Slot to delete a snapshot.
        """

        item = self.uiSnapshotsList.currentItem()
        if item:
            snapshot_path = item.data(QtCore.Qt.UserRole)
            shutil.rmtree(snapshot_path, ignore_errors=True)
            self._listSnaphosts()

    def _restoreSnapshotSlot(self):
        """
        Slot to restore a snapshot.
        """

        item = self.uiSnapshotsList.currentItem()
        if item:
            snapshot_path = item.data(QtCore.Qt.UserRole)
            self._restoreSnapshot(snapshot_path)

    def _restoreSnapshot(self, snapshot_path):
        """
        Restores a snapshot.

        :param snapshot_path: path to the snapshot
        """

        match = re.search(r"^(.*)_([0-9]+)_([0-9]+)", os.path.basename(snapshot_path))
        if match:
            snapshot_name = match.group(1)
        else:
            snapshot_name = "Unknown"
        reply = QtWidgets.QMessageBox.question(self, "Snapshots", "This will discard any changes made to your project since the snapshot \"{}\" was taken?".format(snapshot_name),
                                               QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
        if reply == QtWidgets.QMessageBox.Cancel:
            return

        # stop all the nodes
        topology = Topology.instance()
        for node in topology.nodes():
            if hasattr(node, "start") and node.status() == Node.started:
                node.stop()

        project_name, _ = os.path.splitext(os.path.basename(self._project_path))
        legacy_project_files_dir = os.path.join(snapshot_path, "{}-files".format(project_name))
        if os.path.exists(legacy_project_files_dir):
            # support for pre 1.3 snapshots
            for root, dirs, _ in os.walk(self._project_files_dir):
                dirs[:] = [d for d in dirs if d not in "snapshots"]
                for project_subdir in dirs:
                    project_subdir_path = os.path.join(root, project_subdir)
                    shutil.rmtree(project_subdir_path, ignore_errors=True)

            dirs = os.listdir(legacy_project_files_dir)
            for snapshot_subdir in dirs:
                snapshot_subdir_path = os.path.join(legacy_project_files_dir, snapshot_subdir)
                worker = ProcessFilesWorker(snapshot_subdir_path, os.path.join(self._project_files_dir, snapshot_subdir))
                progress_dialog = ProgressDialog(worker, "Restoring snapshot", "Copying project files...", "Cancel", parent=self)
                progress_dialog.show()
                progress_dialog.exec_()

            try:
                os.remove(self._project_path)
                shutil.copy(os.path.join(snapshot_path, os.path.basename(self._project_path)), self._project_path)
            except OSError as e:
                QtWidgets.QMessageBox.critical(self, "Restore snapshot", "Cannot restore snapshot: {}".format(e))
        else:
            worker = ProcessFilesWorker(snapshot_path, os.path.dirname(self._project_path), skip_dirs=["snapshots"])
            progress_dialog = ProgressDialog(worker, "Restoring snapshot", "Copying project files...", "Cancel", parent=self)
            progress_dialog.show()
            progress_dialog.exec_()

        from ..main_window import MainWindow
        MainWindow.instance().loadSnapshot(self._project_path)
        self.accept()

    def _snapshotDoubleClickedSlot(self, item):
        """
        Slot to restore a snapshot when it is double clicked.
        """

        snapshot_path = item.data(QtCore.Qt.UserRole)
        self._restoreSnapshot(snapshot_path)
