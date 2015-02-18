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

from .qt import QtCore, QtGui


class Progress:

    """
    Display a progress dialog when something is running
    """

    def __init__(self, parent):
        self._progress_dialog = None
        self._parent = parent
        self.stimer = QtCore.QTimer()

    def show(self):
        min_duration = 100  #  Minimum duration before display (ms)

        if self._progress_dialog is None:
            self._progress_dialog = QtGui.QProgressDialog("Waiting for server response", None, 0, 0, self._parent)
            self._progress_dialog.setModal(True)
            self._progress_dialog.setValue(0)
            self._progress_dialog.setWindowTitle("Please wait")
            self._progress_dialog.setMinimumDuration(min_duration)
            self.stimer.singleShot(min_duration, self._show_dialog)

    def _show_dialog(self):
        if self._progress_dialog is not None:
            self._progress_dialog.show()

    def hide(self):
        if self._progress_dialog is not None:
            self._progress_dialog.cancel()
            self._progress_dialog = None
