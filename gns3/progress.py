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

import time

from .utils.progress_dialog import ProgressDialog
from .qt import QtCore


class ProgressDialogThread(QtCore.QThread):
    error = QtCore.pyqtSignal(str, bool)
    completed = QtCore.pyqtSignal()
    update = QtCore.pyqtSignal(int)

    def run(self):
        """
        Thread starting point.
        """

        self._is_running = True

        while True:
            if not self._is_running:
                self.completed.emit()
                return
            time.sleep(0.01)

    def stop(self):
        """
        Stops this thread as soon as possible.
        """

        self._is_running = False


class Progress:

    """
    Display a progress dialog when something is running
    """

    def __init__(self, parent):
        self._progress_dialog = None
        self._parent = parent

    def show(self):
        if self._progress_dialog is None:
            self._progress_dialog = ProgressDialogThread()
            pd = ProgressDialog(self._progress_dialog,
                                "Waiting server",
                                "Waiting",
                                "Cancel", busy=True, parent=self._parent)
            pd.show()

    def hide(self):
        if self._progress_dialog is not None:
            self._progress_dialog.stop()
            self._progress_dialog = None
