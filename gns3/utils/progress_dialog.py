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

from ..qt import sip
from gns3.version import __version__
from ..qt import QtWidgets, QtCore, qslot

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
    :param create_thread: Start the worker in a dedicated thread
    to show unknown progress.
    :param parent: parent widget
    """

    def __init__(self, worker, title, label_text, cancel_button_text, busy=False, parent=None, delay=0, create_thread=True, cancelable=False):

        if "dev" in __version__:
            assert QtCore.QThread.currentThread() == QtWidgets.QApplication.instance().thread()

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
        self._cancelable = cancelable
        self._worker = worker
        self._worker.setObjectName(worker.__class__.__name__)
        if create_thread:
            self._thread = QtCore.QThread()
            if "dev" in __version__:
                assert not self._worker.parent()
            log.debug("Set worker inside a thread {}".format(self._worker.__class__))
            self._worker.moveToThread(self._thread)
        else:
            log.debug("Set worker outside of a thread {}".format(self._worker.__class__))
            self._thread = None
        self._worker.finished.connect(self.accept)
        self._worker.updated.connect(self._updateProgressSlot)
        self._worker.error.connect(self._error)
        if self._thread:
            self._thread.started.connect(self._worker.run)

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

    @qslot
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

        if self._thread:
            self._thread.start()
            log.debug("{} thread started".format(self._worker.objectName()))
        elif self._worker:
            self._worker.run()

    @qslot
    def _canceledSlot(self):
        if self._cancelable and not self._thread:
            self._worker.cancel()
            log.debug("{} worker canceled".format(self._worker.objectName()))

        if self._thread:
            self._worker.cancel()
            log.debug("{} thread canceled".format(self._worker.objectName()))
        self._cleanup()

    @qslot
    def accept(self):
        if self._worker:
            log.debug("{} thread finished".format(self._worker.objectName()))
        self._cleanup()
        super().accept()

    def __del__(self):

        self._cleanup()

    @qslot
    def _cleanup(self):
        """
        Delete the thread.
        """

        if self._countdownTimer:
            self._countdownTimer.stop()

        if self._thread and not sip.isdeleted(self._thread):
            if self._thread.isRunning():
                log.debug("{} thread is being destroyed".format(self._worker.objectName()))
                thread = self._thread
                self._thread = None
                thread.quit()
                if not thread.wait(3000):
                    thread.terminate()
                    thread.wait()
                log.debug("{} thread destroyed".format(self._worker.objectName()))
                thread.deleteLater()
            self._worker = None

    @qslot
    def _updateProgressSlot(self, value):
        """
        Slot to update the progress bar value.

        :param value: value for the progress bar (integer)
        """

        if self._thread:
            # It seems in some cases this is called on a deleted object and crash
            self.setValue(value)

    @qslot
    def _error(self, message, stop=False):
        """
        Slot to show an error message sent by the thread.

        :param message: message
        """

        if stop:
            log.critical("{} thread stopping with an error: {}".format(self._worker.objectName(), message))
            self._canceledSlot()
            QtWidgets.QMessageBox.critical(self.parentWidget(), "Error", "{}".format(message))
        else:
            self._errors.append(message)
            self._cleanup()

    def errors(self):
        """
        Returns error messages.

        :returns: error message list
        """

        return self._errors
