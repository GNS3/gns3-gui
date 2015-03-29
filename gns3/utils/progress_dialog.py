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

from ..qt import QtGui


class ProgressDialog(QtGui.QProgressDialog):

    """
    Progress dialog implementation with thread support.

    :param thread: thread to run
    :param title: window title
    :param label_text: text to describe the progress bar
    :param cancel_button_text: text for the cancel button
    :param busy: if True, the progress bar in "sliding mode"
    to show unknown progress.
    :param parent: parent widget
    """

    def __init__(self, thread, title, label_text, cancel_button_text, busy=False, parent=None):

        minimum = 0
        maximum = 100

        if busy:
            maximum = 0

        QtGui.QProgressDialog.__init__(self, label_text, cancel_button_text, minimum, maximum, parent)

        self.setModal(True)
        self._errors = []
        self.setWindowTitle(title)

        # connect the signals and start the thread
        self._thread = thread
        self._thread.update.connect(self._updateProgress)
        self._thread.completed.connect(self._completed)
        self._thread.error.connect(self._error)
        self._thread.start()

    def _updateProgress(self, value):
        """
        Slot to update the progress bar value.

        :param value: value for the progress bar (integer)
        """

        self.setValue(value)

    def _completed(self):
        """
        Slot to close this dialog when the thread is finished.
        """

        self._thread.wait()
        QtGui.QProgressDialog.accept(self)

    def _error(self, message, stop=False):
        """
        Slot to show an error message sent by the thread.

        :param message: error message
        """

        if stop:
            QtGui.QMessageBox.critical(self, "Error", "{}".format(message))
            self.cancel()
        else:
            self._errors.append(message)

    def errors(self):
        """
        Returns error messages.

        :returns: error message list
        """

        return self._errors

    def done(self, result):
        """
        Stop the thread and close this dialog.
        """

        self._thread.stop()
        if not self._thread.wait(3000):
            self._thread.terminate()
            self._thread.wait()
        QtGui.QProgressDialog.done(self, result)
