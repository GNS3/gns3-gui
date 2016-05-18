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

import logging
import time
from contextlib import contextmanager

from .utils import human_filesize
from .qt import QtCore, QtWidgets, QtNetwork

log = logging.getLogger(__name__)


class Progress(QtCore.QObject):

    """
    Display a progress dialog when something is running
    """

    add_query_signal = QtCore.Signal(str, str, QtNetwork.QNetworkReply)
    remove_query_signal = QtCore.Signal(str)
    progress_signal = QtCore.Signal(str, int, int)

    def __init__(self, parent, min_duration=1000):

        super().__init__(parent)
        self._progress_dialog = None

        # Timer called for refreshing the progress dialog status
        self._rtimer = QtCore.QTimer()
        self._rtimer.timeout.connect(self.update)
        self._rtimer.start(250)

        # When in millisecond we start to show the progress dialog
        self._display_start_time = 0

        self._finished_query_during_display = 0
        self._queries = {}
        # QtCore.Qt.QueuedConnection warranty that we execute the slot
        # in the current thread and not emitter thread.
        # This fix an issue with Qt 5.5
        self.add_query_signal.connect(self._addQuerySlot, QtCore.Qt.QueuedConnection)
        self.remove_query_signal.connect(self._removeQuerySlot, QtCore.Qt.QueuedConnection)
        self.progress_signal.connect(self._progressSlot, QtCore.Qt.QueuedConnection)

        self._minimum_duration = min_duration
        self._cancel_button_text = ""
        self._allow_cancel_query = False
        self._enable = True

    def _addQuerySlot(self, query_id, explanation, response):
        self._queries[query_id] = {"explanation": explanation, "current": 0, "maximum": 0, "response": response}

    def _removeQuerySlot(self, query_id):
        self._finished_query_during_display += 1
        if query_id in self._queries:
            del self._queries[query_id]

    def progress_dialog(self):
        return self._progress_dialog

    def _progressSlot(self, query_id, current, maximum):
        if query_id in self._queries:
            self._queries[query_id]["current"] = current
            self._queries[query_id]["maximum"] = maximum

    def setAllowCancelQuery(self, allow_cancel_query):
        self._allow_cancel_query = allow_cancel_query

    def setCancelButtonText(self, text):
        self._cancel_button_text = text

    def _cancelSlot(self):
        log.debug("User ask for cancel running queries")
        if self._allow_cancel_query:
            log.debug("Cancel running queries")
            for query in self._queries.copy().values():
                query["response"].abort()

    def _rejectSlot(self):
        self._progress_dialog = None
        self._cancelSlot()

    def update(self):
        if len(self._queries) == 0 and (time.time() * 1000) >= self._display_start_time + self._minimum_duration:
            self.hide()
            return
        self.show()

    def show(self):
        if self._progress_dialog is None or self._progress_dialog.wasCanceled():
            progress_dialog = QtWidgets.QProgressDialog("Waiting for server response", None, 0, 0, self.parent())
            progress_dialog.canceled.connect(self._cancelSlot)
            progress_dialog.rejected.connect(self._rejectSlot)
            progress_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            progress_dialog.setWindowTitle("Please wait")
            progress_dialog.setAutoReset(False)
            progress_dialog.setMinimumDuration(self._minimum_duration)

            if len(self._cancel_button_text) > 0:
                progress_dialog.setCancelButtonText(self._cancel_button_text)
            else:
                progress_dialog.setCancelButton(None)

            if len(self._queries) > 0:
                text = list(self._queries.values())[0]["explanation"]
                progress_dialog.setLabelText(text)

            self._progress_dialog = progress_dialog
            self._finished_query_during_display = 0
            self._display_start_time = time.time() * 1000
            self._progress_dialog.show()
        else:
            start_timer = False
            progress_dialog = self._progress_dialog

            if len(self._queries) > 0:
                text = list(self._queries.values())[0]["explanation"]
            else:
                text = None

            # If we have multiple queries running progress show progress of the queries
            # otherwise it's the progress of the current query
            if len(self._queries) + self._finished_query_during_display > 1:
                progress_dialog.setMaximum(len(self._queries) + self._finished_query_during_display)
                progress_dialog.setValue(self._finished_query_during_display)
            elif len(self._queries) == 1:
                query = list(self._queries.values())[0]
                if query["maximum"] == query["current"]:

                    # We animate the bar. In theory Qt should be able to do it but
                    # due to all the manipulation of the dialog he is getting lost
                    bar_speed = 8
                    if progress_dialog.maximum() != bar_speed:
                        progress_dialog.setMaximum(bar_speed)
                        progress_dialog.setValue(0)
                    elif progress_dialog.value() == bar_speed:
                        progress_dialog.setValue(0)
                    else:
                        progress_dialog.setValue(progress_dialog.value() + 1)

                else:
                    progress_dialog.setMaximum(query["maximum"])
                    progress_dialog.setValue(query["current"])

                if text and query["maximum"] > 1000:
                    text += "\n{} / {}".format(human_filesize(query["current"]), human_filesize(query["maximum"]))

            if text:
                progress_dialog.setLabelText(text)

    def hide(self):
        """
        Hide and cancel the progress dialog
        """
        if self._progress_dialog is not None:
            progress_dialog = self._progress_dialog
            self._progress_dialog = None
            progress_dialog.cancel()
            progress_dialog.deleteLater()

    @contextmanager
    def context(self, **kwargs):
        """
        Change the behavior of the progress dialog when in this block
        and restore it at the end of the block.

        :param kwargs: Options to change (possible: min_duration, enable)
        """
        if 'min_duration' in kwargs:
            old_minimum_duration = self._minimum_duration
            self._minimum_duration = kwargs['min_duration']
        if 'enable' in kwargs:
            old_enable = self._enable
            self._enable = kwargs['enable']
        if 'cancel_button_text' in kwargs:
            old_cancel_button_text = self._cancel_button_text
            self._cancel_button_text = kwargs['cancel_button_text']
        if 'allow_cancel_query' in kwargs:
            old_allow_cancel_query = self._allow_cancel_query
            self._allow_cancel_query = kwargs['allow_cancel_query']
        yield
        if 'min_duration' in kwargs:
            self._minimum_duration = old_minimum_duration
        if 'enable' in kwargs:
            self._enable = old_enable
        if 'allow_cancel_query' in kwargs:
            self._allow_cancel_query = old_allow_cancel_query
        if 'cancel_button_text' in kwargs:
            self._cancel_button_text = old_cancel_button_text

    @staticmethod
    def instance(parent=None):
        """
        Singleton to return only one instance of Progress.

        :returns: instance of Progress
        """

        if not hasattr(Progress, "_instance") or Progress._instance is None:
            Progress._instance = Progress(parent)
        return Progress._instance

