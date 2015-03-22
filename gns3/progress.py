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


class Progress(QtCore.QObject):

    """
    Display a progress dialog when something is running
    """

    add_query_signal = QtCore.Signal(str, str)
    remove_query_signal = QtCore.Signal(str)

    def __init__(self, parent, min_duration=1000):

        super().__init__()
        self._progress_dialog = None
        self._parent = parent
        self._stimer = QtCore.QTimer()
        self._finished_query_during_display = 0
        self._queries = {}
        self.add_query_signal.connect(self._add_query)
        self.remove_query_signal.connect(self._remove_query)
        self._minimum_duration = min_duration

    def _add_query(self, query_id, explanation):

        self._queries[query_id] = explanation
        self.show()

    def _remove_query(self, query_id):

        self._finished_query_during_display += 1
        if query_id in self._queries:
            del self._queries[query_id]

        if len(self._queries) == 0:
            self.hide()
        else:
            self.show()

    def progress_dialog(self):

        return self._progress_dialog

    def show(self):

        if self._progress_dialog is None or self._progress_dialog.wasCanceled():
            progress_dialog = QtGui.QProgressDialog("Waiting for server response", None, 0, 0, self._parent)
            progress_dialog.setModal(True)
            progress_dialog.setCancelButton(None)
            progress_dialog.setWindowTitle("Please wait")
            progress_dialog.setMinimumDuration(self._minimum_duration)
            self._progress_dialog = progress_dialog
            self._stimer.singleShot(self._minimum_duration, self._show_dialog)
            self._finished_query_during_display = 0
        else:
            progress_dialog = self._progress_dialog
            progress_dialog.setMaximum(len(self._queries) + self._finished_query_during_display)
            progress_dialog.setValue(self._finished_query_during_display)

        if len(self._queries) > 0:
            progress_dialog.setLabelText(list(self._queries.values())[0])

    def _show_dialog(self):
        if self._progress_dialog is not None:
            self._progress_dialog.show()

    def hide(self):
        if self._progress_dialog is not None:
            progress_dialog = self._progress_dialog
            self._progress_dialog = None
            progress_dialog.cancel()
