#!/usr/bin/env python
#
# Copyright (C) 2017 GNS3 Technologies Inc.
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

from ..qt import QtCore
from ..controller import Controller

import logging
log = logging.getLogger(__name__)


class CreateSnapshotWorker(QtCore.QObject):
    """
    Export snapshot
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    canceled = QtCore.pyqtSignal()


    def __init__(self, project, snapshot_name):
        super().__init__()
        self._project = project
        self._snapshot_name = snapshot_name

    def run(self):
        if self._project:
            Controller.instance().post(
                "/projects/{}/snapshots".format(self._project.id()),
                self._createSnapshotsCallback,
                {"name": self._snapshot_name},
                timeout=None,
                showProgress=False,
                eventsHandler=self
            )

    def _createSnapshotsCallback(self, content, error=False, server=None, context={}, **kwargs):
        if error:
            if content:
                self.error.emit(content["message"], True)
            else:
                self.error.emit("Cannot create snapshot of project", True)
            self.finished.emit()
            return
        self.finished.emit()

    def cancel(self):
        log.warning("Snapshot `{}` creation has been canceled by user.".format(self._snapshot_name))
        self.canceled.emit()
