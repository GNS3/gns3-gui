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
from PyQt4.QtCore import QThread, pyqtSignal

import sys
import shlex
import subprocess
from .main_window import MainWindow

import logging
log = logging.getLogger(__name__)


class ConsoleThread(QThread):
    """

    """
    consoleDone = pyqtSignal(str, str, int)

    def __init__(self, parent, command, name, host, port):
        super(QThread, self).__init__(parent)
        self._command = command
        self._name = name
        self._host = host
        self._port = port

    def run(self):
        try:
            if sys.platform.startswith("win"):
                # use the string on Windows
                subprocess.call(self._command)
            else:
                # use arguments on other platforms
                args = shlex.split(self._command)
                subprocess.call(args)

            # emit signal upon completion
            self.consoleDone.emit(self._name, self._host, self._port)

        except (OSError, ValueError) as e:
            log.warning('could not start Telnet console "{}": {}'.format(self._command, e))
            raise


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
    log.info('starting telnet console "{}"'.format(command))

    console_thread = ConsoleThread(MainWindow.instance(), command, name, host, port)
    if callback is not None:
        console_thread.consoleDone.connect(callback)

    console_thread.start()
