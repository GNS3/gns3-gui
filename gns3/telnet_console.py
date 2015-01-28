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
Functions to start external console terminals.
"""

from .qt import QtCore, QtGui

import sys
import shlex
import subprocess
from .main_window import MainWindow

import logging
log = logging.getLogger(__name__)


class ConsoleThread(QtCore.QThread):

    consoleDone = QtCore.pyqtSignal(str, str, int)

    def __init__(self, parent, command, name, host, port):
        super(QtCore.QThread, self).__init__(parent)
        self._command = command
        self._name = name
        self._host = host
        self._port = port

    def exec_command(self):

        if sys.platform.startswith("win"):
            # use the string on Windows
            subprocess.call(self._command)
        else:
            # use arguments on other platforms
            args = shlex.split(self._command)
            subprocess.call(args)

    def run(self):

        try:
            self.exec_command()
        except (OSError, subprocess.SubprocessError) as e:
            pass
            # log.warning('could not start Telnet console "{}": {}'.format(self._command, e))
        finally:
            # emit signal upon completion
            self.consoleDone.emit(self._name, self._host, self._port)


def telnetConsole(name, host, port, callback=None):
    """
    Start a Telnet console program.

    :param host: host or IP address
    :param port: port number
    """

    command = MainWindow.instance().telnetConsoleCommand()
    if not command:
        return

    # replace the place-holders by the actual values
    command = command.replace("%h", host)
    command = command.replace("%p", str(port))
    command = command.replace("%d", name)

    if callback is not None:
        log.info('starting telnet console in thread "{}"'.format(command))
        console_thread = ConsoleThread(MainWindow.instance(), command, name, host, port)
        console_thread.consoleDone.connect(callback)
        console_thread.start()
    else:
        try:
            log.info('starting telnet console "{}"'.format(command))
            if sys.platform.startswith("win"):
                # use the string on Windows
                subprocess.Popen(command)
            else:
                # use arguments on other platforms
                args = shlex.split(command)
                subprocess.Popen(args)
        except (OSError, ValueError, subprocess.SubprocessError) as e:
            log.warning('could not start Telnet console "{}": {}'.format(command, e))
            raise
