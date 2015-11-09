# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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

from ..qt import QtCore
from ..utils import md5_hash_file

import logging
log = logging.getLogger(__name__)


class DownloadProjectWorker(QtCore.QObject):

    """
    Downloads project from cloud storage
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)
    file_downloaded = QtCore.pyqtSignal()
    file_list_received = QtCore.pyqtSignal()

    def __init__(self, parent, project, servers):
        self._is_running = False
        self._project = project
        self._servers = servers
        self._files_to_download = []
        self._get_file_lists = 0  # Counter to know how many file list remain to download
        self._total_files_to_download = 0
        super().__init__(parent)

    def run(self):
        self.updated.emit(0)
        self._is_running = True

        try:
            if self._servers.vmServer():
                self._project.get(self._servers.vmServer(), "/files", self._fileListReceived)
                self._get_file_lists += 1
            for server in self._servers.remoteServers().values():
                self._project.get(server, "/files", self._fileListReceived)
                self._get_file_lists += 1
        except Exception as e:
            self.error.emit("Error importing project: {}".format(e), True)

        if self._get_file_lists == 0:
            self._is_running = False

    def _fileListReceived(self, result, error=False, server=None, **kwargs):
        self._get_file_lists -= 1
        if error:
            msg = "Error while downloading project {}".format(result["message"])
            log.error(msg)
            self.error.emit(msg, True)
            return

        for file in result:
            file["server"] = server
            self._files_to_download.append(file)
            self._total_files_to_download += 1

        if self._get_file_lists <= 0:
            self._downloadNextFile()
        else:
            self._is_running = False
            self.finished.emit()

    def _downloadNextFile(self):
        if not self._is_running:
            return

        try:
            file_to_download = self._files_to_download.pop()
        except IndexError:
            self.finished.emit()
            return

        file_path = os.path.join(self._project.filesDir(), file_to_download["path"])

        self.updated.emit(round(100.0 / self._total_files_to_download * (self._total_files_to_download - (len(self._files_to_download) + 1))))

        try:
            if os.path.dirname(file_path) is not None:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

            if os.path.exists(file_path):
                if md5_hash_file(file_path) == file_to_download["md5sum"]:
                    self._downloadNextFile()
                    return

            f = open(file_path, "wb+")
        except OSError as e:
            self.error.emit("Could not write file {}: {}".format(file_path, e), False)
            return
        self._project.get(file_to_download["server"], "/files/{}".format(file_to_download["path"]), self._downloadFileReceived, context={"fd": f, "file_path": file_path}, downloadProgressCallback=self._downloadFileProgress)

    def _downloadFileReceived(self, content, error=False, server=None, context={}):
        """
        Called when download finish
        """
        context["fd"].close()
        self._downloadNextFile()

    def _downloadFileProgress(self, content, server=None, context={}):
        """
        Called for each part of the file
        """
        try:
            context["fd"].write(content)
        except OSError as e:
            self.error.emit("Could not write file {}: {}".format(context["file_path"], e), False)

    def cancel(self):
        """
        Cancel this worker.
        """

        if not self:
            return
        self._is_running = False
