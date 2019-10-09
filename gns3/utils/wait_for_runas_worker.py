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
Thread to run a command with administrator rights on Windows and wait for its completion.
"""

from ..utils import shlex_quote
from ..qt import QtCore

import logging
log = logging.getLogger(__name__)


class WaitForRunAsWorker(QtCore.QObject):

    """
    Thread to wait for a command to be executed.

    :param command: command to execute (list)
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    def __init__(self, command, timeout=300):

        super().__init__()
        self._is_running = False
        self._command = command
        self._timeout = timeout

    def run(self):
        """
        Worker starting point.
        """

        self._is_running = True

        import pywintypes
        import win32con
        import win32event
        import win32process
        from win32com.shell.shell import ShellExecuteEx
        from win32com.shell import shellcon

        program = '"%s"' % self._command[0]
        params = " ".join(['"%s"' % (x,) for x in self._command[1:]])
        try:
            process = ShellExecuteEx(nShow=win32con.SW_SHOWNORMAL,
                                     fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                                     lpVerb="runas",
                                     lpFile=program,
                                     lpParameters=params)
        except pywintypes.error as e:
            command_string = " ".join(shlex_quote(s) for s in self._command)
            self.error.emit('Could not execute command "{}": {}'.format(command_string, e), True)
            return

        handle = process['hProcess']
        win32event.WaitForSingleObject(handle, self._timeout * 1000)
        return_code = win32process.GetExitCodeProcess(handle)
        if return_code != 0:
            self.error.emit("Return code is {}".format(return_code), True)
        else:
            self.finished.emit()

    def cancel(self):
        """
        Cancel this worker.
        """

        if not self:
            return
        self._is_running = False
