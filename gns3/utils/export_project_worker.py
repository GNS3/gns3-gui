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

from ..qt import QtCore, QtWidgets
from ..servers import Servers
from ..topology import Topology


class ExportProjectWorker(QtCore.QObject):
    """
    Export the current topology to a portable format
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    def __init__(self, parent, project):
        super().__init__(parent)
        self._project = project

    def run(self):
        if self._project.temporary():
            self.error.emit("You cannot export a temporary project", True)
            self.finished.emit()
            return

        topology = Topology.instance()
        for node in topology.nodes():

            if node.__class__.__name__ in ["VirtualBoxVM", "VMwareVM"]:
                self.error.emit("You cannot export a project including VMware or VirtualBox VM because the data are managed by this software.", True)
                self.finished.emit()
                return

        reply = QtWidgets.QMessageBox.question(self.parent(), "Include image", "Would you like to include the base image in the export?.\n\nThe topology will require no additional download but will be much bigger.\n\nAll the images need to be available on your local computer.", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        self._include_images = int(reply == QtWidgets.QMessageBox.Yes)


        if not os.path.exists(self._project.readmePathFile()):
            text, ok = QtWidgets.QInputDialog.getMultiLineText(self.parent(), "Readme", "Please provide a description for the topology if you want to share it with the public. \nThis will be save in the file README.txt in the project and use for all project exports", "Topology title\n\nAuthor: Grace Hopper <grace@hopper>\n\nThis topology...")
            if not ok:
                self.finished.emit()
                return
            with open(self._project.readmePathFile(), 'w+') as f:
                f.write(text)

        for server in self._project.servers():
            if not server.isLocal() and not server.isGNS3VM():
                self.error.emit("Project from remote server can not be exported. Only project for local and GNS3 VM are supported.", True)
                self.finished.emit()
                return


        QtWidgets.QMessageBox.information(self.parent(), "Export", "Remember to check the licence of the material used in the topology before sharing it with someone else.", QtWidgets.QMessageBox.Ok)

        self._path, _ = QtWidgets.QFileDialog.getSaveFileName(self.parent(), "Export project", None, "GNS3 Topology (*.gns3project)", "GNS3 Topology (*.gns3project)")
        if self._path is None or len(self._path) == 0:
            self.finished.emit()
            return

        try:
            open(self._path, 'wb+').close()
        except OSError as e:
            self.error.emit("Can't write the topology {}: {}".format(self._path, str(e)), True)
            self.finished.emit()
            return

        vm_server = None
        for server in self._project.servers():
            if server.isGNS3VM():
                vm_server = server

        if vm_server:
            self._project.get(vm_server, "/export", self._exportVmReceived, downloadProgressCallback=self._downloadFileProgress)
        else:
            self._project.get(Servers.instance().localServer(), "/export?include_images={}".format(self._include_images), self._exportLocalReceived, downloadProgressCallback=self._downloadFileProgress)

    def _exportVmReceived(self, content, error=False, server=None, context={}, **kwargs):
        if error:
            self.error.emit("Can't export the project from the VM", True)
            self.finished.emit()
            return

        vm_path = os.path.join(self._project.filesDir(), "servers", "vm")
        if os.path.exists(vm_path):
            shutil.rmtree(vm_path)
        os.makedirs(vm_path, exist_ok=True)
        with zipfile.ZipFile(self._path) as myzip:
            myzip.extractall(vm_path)

        # We reset the content of the file
        try:
            open(self._path, 'wb+').close()
        except OSError as e:
            self.error.emit("Can't write the topology {}: {}".format(self._path, str(e)), True)
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
            self.error.emit("Can't write the topology {}: {}".format(self._path, str(e)), True)
            self.finished.emit()
            return

    def cancel(self):
        pass
