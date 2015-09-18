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

"""
Thread to run a command and wait for its completion.
"""

import tempfile
import subprocess
import shlex
from ..qt import QtCore

import logging
log = logging.getLogger(__name__)


class WaitForCommandWorker(QtCore.QObject):

    """
    Thread to wait for a command to be executed.

    :param command: command to execute (list)
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    def __init__(self, command, timeout=120, shell=False):

        super().__init__()
        self._is_running = False
        self._command = command
        self._timeout = timeout
        self._output = b""
        self._shell = shell

    def run(self):
        """
        Worker starting point.
        """

        self._is_running = True

        try:
            self._output = subprocess.check_output(self._command,
                                                   cwd=tempfile.gettempdir(),
                                                   timeout=self._timeout,
                                                   shell=self._shell)
        except (OSError, subprocess.SubprocessError) as e:
            command_string = " ".join(shlex.quote(s) for s in self._command)
            self.error.emit('Could not execute command "{}": {}'.format(command_string, e), True)
            return
        self.finished.emit()

    def output(self):
        """
        Returns the command output.
        """

        return self._output

    def cancel(self):
        """
        Cancel this worker.
        """

        if not self:
            return
        self._is_running = False
