# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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

"""
Progress dialog that blocking tasks (file operations, network connections etc.)
"""

import sip
from ..qt import QtWidgets, QtCore

import logging
log = logging.getLogger(__name__)


class ProgressDialog(QtWidgets.QProgressDialog):

    """
    Progress dialog implementation with thread support.

    :param thread: thread to run
    :param title: window title
    :param label_text: text to describe the progress bar
    :param cancel_button_text: text for the cancel button
    :param busy: if True, the progress bar in "sliding mode"
    :param delay: Countdown in seconds before starting the worker
    to show unknown progress.
    :param parent: parent widget
    """

    def __init__(self, worker, title, label_text, cancel_button_text, busy=False, parent=None, delay=0):

        minimum = 0
        maximum = 100

        if busy:
            maximum = 0

        super().__init__(label_text, cancel_button_text, minimum, maximum, parent)


        self.setModal(True)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self._errors = []
        self.setWindowTitle(title)
        self.canceled.connect(self._canceledSlot)
        self.destroyed.connect(self._cleanup)

        self._thread = QtCore.QThread(self.parent())

        self._worker = worker
        self._worker.finished.connect(self.accept)
        self._worker.updated.connect(self._updateProgress)
        self._worker.error.connect(self._error)
        self._worker.moveToThread(self._thread)

        self._countdownTimer = None
        if delay == 0:
            self._start()
        else:
            self._delay = delay
            self._countdownTimer = QtCore.QTimer()
            self._countdownTimer.setInterval(self._delay * 100)
            self._countdownTimer.timeout.connect(self._updateCountdownSlot)
            self._countdownTimer.start()
            self._updateCountdownSlot()

    def _updateCountdownSlot(self):
        """
        Called every second for countdown before
        starting the worker
        """
        if self._delay <= 0:
            self.setCancelButtonText("Cancel")
            self._countdownTimer.stop()
            self._start()
        else:
            self.setCancelButtonText("Cancel start ({} seconds)".format(self._delay))
            self._delay -= 1

    def _start(self):
        #  connect the thread signals and start the thread
        self._thread.started.connect(self._worker.run)
        self._thread.start()

    def _canceledSlot(self):

        self._worker.cancel()
        self._cleanup()

    def __del__(self):

        self._cleanup()

    def _cleanup(self):
        """
        Delete the thread.
        """

        if not self or sip.isdeleted(self):
            return

        if self._countdownTimer:
            self._countdownTimer.stop()

        if self._thread:
            if not sip.isdeleted(self._thread):
                if self._thread.isRunning():
                    thread = self._thread
                    self._thread = None
                    thread.quit()
                    if not thread.wait(3000):
                        thread.terminate()
                        thread.wait()
                    thread.deleteLater()

    def _updateProgress(self, value):
        """
        Slot to update the progress bar value.

        :param value: value for the progress bar (integer)
        """

        if self is not None and self._thread is not None:
            # It seem in some cases this is called on a deleted object and crash
            if not sip.isdeleted(self):
                self.setValue(value)

    def _error(self, message, stop=False):
        """
        Slot to show an error message sent by the thread.

        :param message: message
        """
        if self is None or sip.isdeleted(self):
            return

        if stop:
            log.critical(message)
            QtWidgets.QMessageBox.critical(self.parentWidget(), "Error", "{}".format(message))
            self._canceledSlot()
        else:
            self._errors.append(message)
            self._cleanup()

    def errors(self):
        """
        Returns error messages.

        :returns: error message list
        """

        return self._errors
