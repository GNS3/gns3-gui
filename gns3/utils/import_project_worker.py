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


from ..qt import QtCore
from ..servers import Servers


class ImportProjectWorker(QtCore.QObject):
    """
    Import topology shipped in the portable format
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)
    imported = QtCore.pyqtSignal(str)

    def __init__(self, source, new_project_settings):
        super().__init__()
        self._source = source
        self._new_project_settings = new_project_settings
        self._project_uuid = str(uuid.uuid4())

    def run(self):

        self._dst = self._new_project_settings['project_files_dir']
        name = self._new_project_settings['project_name']
        self._project_file = self._new_project_settings['project_path']
        Servers.instance().localServer().post("/projects", self._createProjectCallback,
                                              body={"project_id": self._project_uuid, "name": name, "path": self._dst})

    def _createProjectCallback(self, content, error=False, server=None, context={}, **kwargs):
        if error:
            self.error.emit("Can't import the project", True)
            self.finished.emit()
            return

        self.updated.emit(25)
        if sys.platform.startswith("linux") and Servers.instance().vmServer() is None:
            Servers.instance().localServer().post("/projects/{}/import?gns3vm=0".format(self._project_uuid), self._importProjectCallback, body=pathlib.Path(self._source))
        else:
            Servers.instance().localServer().post("/projects/{}/import?gns3vm=1".format(self._project_uuid), self._importProjectCallback, body=pathlib.Path(self._source))


    def _importProjectCallback(self, content, error=False, server=None, context={}, **kwargs):
        if error:
            self.error.emit("Can't import the project", True)
            self.finished.emit()
            return

        self.updated.emit(50)

        if os.path.exists(os.path.join(self._dst, "servers", "vm")):
            if Servers.instance().vmServer() is None:
                self.error.emit("You must configure the GNS3 VM in order to import this project", True)
                self.finished.emit()
                return

            self._zippath = os.path.join(self._dst, "servers", "vm.zip")
            with zipfile.ZipFile(self._zippath, 'w') as z:
                for root, dirs, files in os.walk(os.path.join(self._dst, "servers", "vm")):
                    for file in files:
                        path = os.path.join(root, file)
                        z.write(path, os.path.relpath(path, os.path.join(self._dst, "servers", "vm")))

            Servers.instance().vmServer().post("/projects/{}/import".format(self._project_uuid), self._importProjectVMCallback, body=pathlib.Path(self._zippath))
        else:
            self.finished.emit()
            self.imported.emit(self._project_file)

    def _importProjectVMCallback(self, content, error=False, server=None, context={}, **kwargs):
        try:
            os.remove(self._zippath)
        except OSError as e:
            self.error.emit("Can't write the topology {}: {}".format(self._path, str(e)), True)
            self.finished.emit()
            return

        if error:
            self.error.emit("Can't import the project", True)
            self.finished.emit()
            return
        self.finished.emit()
        self.imported.emit(self._project_file)

    def cancel(self):
        pass
