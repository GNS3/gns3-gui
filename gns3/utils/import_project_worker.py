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
import shutil
import uuid
import json
import os


from ..qt import QtCore, QtWidgets
from ..dialogs.new_project_dialog import NewProjectDialog
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

    def __init__(self, parent, source):
        super().__init__(parent)
        self._source = source

    def run(self):
        self._project_uuid = str(uuid.uuid4())

        project_name = os.path.basename(self._source).split('.')[0]
        self._project_dialog = NewProjectDialog(self.parent(), default_project_name=project_name)
        self._project_dialog.show()
        self._project_dialog.accepted.connect(self._newProjectDialodAcceptedSlot)

    def _newProjectDialodAcceptedSlot(self):
        new_project_settings = self._project_dialog.getNewProjectSettings()

        self.updated.emit(25)

        dst = new_project_settings['project_files_dir']
        self._project_file = new_project_settings['project_path']

        try:
            with zipfile.ZipFile(self._source) as myzip:
                myzip.extractall(dst)

            with open(os.path.join(dst, "project.gns3")) as f:
                project = json.load(f)
            project["project_id"] = self._project_uuid

            shutil.move(os.path.join(dst, "project.gns3"), self._project_file)

            self.updated.emit(50)

            if os.path.exists(os.path.join(dst, "servers", "vm")):
                self._zippath = os.path.join(dst, "servers", "vm.zip")
                with zipfile.ZipFile(self._zippath, 'w') as z:
                    for root, dirs, files in os.walk(os.path.join(dst, "servers", "vm")):
                        for file in files:
                            path = os.path.join(root, file)
                            z.write(path, os.path.relpath(path, os.path.join(dst, "servers", "vm")))

                Servers.instance().vmServer().post("/projects/{}/import".format(self._project_uuid), self._importProjectCallback, body=pathlib.Path(self._zippath))
            else:
                self.finished.emit()
                self.imported.emit(self._project_file)
        except OSError as e:
            self.error.emit("Can't write the topology {}: {}".format(self._path, str(e)), True)
            self.finished.emit()
            return

    def _importProjectCallback(self, content, error=False, server=None, context={}, **kwargs):
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
