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

import os
import zipfile
import shutil

from ..qt import QtCore
from ..servers import Servers


class ExportProjectWorker(QtCore.QObject):
    """
    Export the current topology to a portable format
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    def __init__(self, project, path, include_images):
        super().__init__()
        self._project = project
        self._include_images = include_images
        self._path = path

    def run(self):

        vm_server = None
        for server in self._project.servers():
            if server.isGNS3VM():
                vm_server = server

        if vm_server:
            self._project.get(vm_server,
                              "/export",
                              self._exportVmReceived,
                              downloadProgressCallback=self._downloadFileProgress)
        else:
            self._project.get(Servers.instance().localServer(),
                              "/export?include_images={}".format(self._include_images),
                              self._exportLocalReceived,
                              downloadProgressCallback=self._downloadFileProgress)

    def _exportVmReceived(self, content, error=False, server=None, context={}, **kwargs):
        if error:
            self.error.emit("Can't export the project from the VM", True)
            self.finished.emit()
            return

        vm_path = os.path.join(self._project.filesDir(), "servers", "vm")
        if os.path.exists(vm_path):
            shutil.rmtree(vm_path, ignore_errors=True)
        try:
            os.makedirs(vm_path, exist_ok=True)
        except OSError as e:
            self.error.emit("Can't create directory {}: {}".format(vm_path, e), True)
            self.finished.emit()
            return

        with zipfile.ZipFile(self._path) as myzip:
            myzip.extractall(vm_path)

        # We reset the content of the file
        try:
            open(self._path, 'wb+').close()
        except OSError as e:
            self.error.emit("Can't write project file {}: {}".format(self._path, e), True)
            self.finished.emit()
            return

        self._project.get(Servers.instance().localServer(), "/export?include_images={}".format(self._include_images), self._exportLocalReceived, downloadProgressCallback=self._downloadFileProgress)

    def _exportLocalReceived(self, content, error=False, server=None, context={}, **kwargs):
        if error:
            self.error.emit("Can't export the project from the local server", True)
            self.finished.emit()
            return
        self.finished.emit()

    def _downloadFileProgress(self, content, server=None, context={}, **kwargs):
        """
        Called for each part of the file
        """
        try:
            with open(self._path, 'ab') as f:
                f.write(content)
        except OSError as e:
            self.error.emit("Can't write project file {}: {}".format(self._path, e), True)
            self.finished.emit()
            return

    def cancel(self):
        pass
