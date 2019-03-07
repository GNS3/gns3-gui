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

from ..qt import QtCore


class ExportProjectWorker(QtCore.QObject):
    """
    Export the current project to a portable format
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    def __init__(self, project, path, include_images, compression):
        super().__init__()
        self._project = project
        self._include_images = include_images
        self._path = path
        self._compression = compression

    def run(self):
        if self._project:
            self._project.get("/export?include_images={}&compression={}".format(self._include_images, self._compression),
                              self._exportReceived,
                              downloadProgressCallback=self._downloadFileProgress,
                              timeout=None)

    def _exportReceived(self, content, error=False, server=None, context={}, **kwargs):
        if error:
            if content:
                self.error.emit(content["message"], True)
            else:
                self.error.emit("Can't export the project from the server", True)
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
