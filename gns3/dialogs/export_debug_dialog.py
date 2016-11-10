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


from zipfile import ZipFile
import platform
import psutil
import os

from gns3.version import __version__
from gns3.qt import QtWidgets, QtCore
from gns3.ui.export_debug_dialog_ui import Ui_ExportDebugDialog
from gns3.local_config import LocalConfig
from gns3.controller import Controller

import logging
log = logging.getLogger(__name__)


class ExportDebugDialog(QtWidgets.QDialog, Ui_ExportDebugDialog):
    """
    This dialog allow user to export useful information
    for remote debugging by a GNS3 developers.
    """

    def __init__(self, parent, project):

        super().__init__(parent)
        self._project = project
        self.setupUi(self)
        self.uiOkButton.clicked.connect(self._okButtonClickedSlot)

    def _okButtonClickedSlot(self):
        if Controller.instance().isRemote():
            QtWidgets.QMessageBox.critical(self, "Debug", "Export debug information from a remote server is not supported")
            self.reject()
            return

        self._path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export debug file", None, "Zip file (*.zip)", "Zip file (*.zip)")

        if len(self._path) == 0:
            self.reject()
            return

        if Controller.instance().connected():
            Controller.instance().post("/debug", self._exportDebugCallback)
        else:
            self._exportDebugCallback({}, error=True)

    def _exportDebugCallback(self, result, error=False, **kwargs):
        log.info("Export debug information to %s", self._path)

        try:
            with ZipFile(self._path, 'w') as zip:
                zip.writestr("debug.txt", self._getDebugData())
                dir = LocalConfig.instance().configDirectory()
                for filename in os.listdir(dir):
                    path = os.path.join(dir, filename)
                    if os.path.isfile(path):
                        zip.write(path, filename)

                dir = os.path.join(LocalConfig.instance().configDirectory(), "debug")
                if os.path.exists(dir):
                    for filename in os.listdir(dir):
                        path = os.path.join(dir, filename)
                        if os.path.isfile(path):
                            zip.write(path, filename)

                if self._project:
                    dir = self._project.filesDir()
                    if dir:
                        for filename in os.listdir(dir):
                            path = os.path.join(dir, filename)
                            if os.path.isfile(path):
                                zip.write(path, filename)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "Debug", "Can't export debug information: {}".format(str(e)))
        self.accept()

    def _getDebugData(self):
        try:
            connections = psutil.net_connections()
        # You need to be root for OSX
        except psutil.AccessDenied:
            connections = None

        try:
            addrs = ["* {}: {}".format(key, val) for key, val in psutil.net_if_addrs().items()]
        except UnicodeDecodeError:
            addrs = ["INVALID ADDR WITH UNICODE CHARACTERS"]

        data = """Version: {version}
OS: {os}
Python: {python}
Qt: {qt}
PyQt: {pyqt}
CPU: {cpu}
Memory: {memory}

Networks:
{addrs}

Open connections:
{connections}

Processus:
""".format(
            version=__version__,
            qt=QtCore.QT_VERSION_STR,
            pyqt=QtCore.PYQT_VERSION_STR,
            os=platform.platform(),
            python=platform.python_version(),
            memory=psutil.virtual_memory(),
            cpu=psutil.cpu_times(),
            connections=connections,
            addrs="\n".join(addrs)
        )
        for proc in psutil.process_iter():
            try:
                psinfo = proc.as_dict(attrs=["name", "exe"])
                data += "* {} {}\n".format(psinfo["name"], psinfo["exe"])
            except psutil.NoSuchProcess:
                pass
        return data

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    print(ExportDebugDialog(None)._getDebugData())
