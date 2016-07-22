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

import pathlib
import zipfile
import uuid
import os
import sys


from ..controller import Controller
from ..qt import QtCore


class ImportProjectWorker(QtCore.QObject):
    """
    Import topology shipped in the portable format
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)
    imported = QtCore.pyqtSignal(str)

    def __init__(self, source):
        super().__init__()
        self._source = source
        self._project_uuid = str(uuid.uuid4())

    def run(self):
        Controller.instance().post("/projects/{}/import".format(self._project_uuid), self._importProjectCallback, body=pathlib.Path(self._source), timeout=None)
        self.updated.emit(25)

    def _importProjectCallback(self, content, error=False, server=None, context={}, **kwargs):
        if error:
            if content:
                self.error.emit(content["message"], True)
            else:
                self.error.emit("Can't import the project on the server", True)
            self.finished.emit()
            return

        self.updated.emit(50)

        self.finished.emit()
        self.imported.emit(self._project_uuid)

    def cancel(self):
        pass

