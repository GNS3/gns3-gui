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

from .qt import QtCore, QtWidgets

import os
import sys
import shlex
import subprocess
from .main_window import MainWindow
from .controller import Controller

import logging
log = logging.getLogger(__name__)

console_mutex = QtCore.QMutex()


class ConsoleThread(QtCore.QThread):

    consoleError = QtCore.pyqtSignal(str)

    def __init__(self, parent, command, node, port):
        super().__init__(parent)

        self._command = command
        self._name = node.name()
        self._host = node.consoleHost()
        assert self._host
        self._port = port
        self._node = node

    def exec_command(self, command):

        if sys.platform.startswith("win"):
            # use the string on Windows
            subprocess.call(command)
        else:
            # use arguments on other platforms
            try:
                args = shlex.split(command)
            except ValueError:
                self.consoleError.emit("Syntax error in command: {}".format(command))
                return
            subprocess.call(args, env=os.environ)

    def run(self):

        host = self._host
        port = self._port

        # replace the place-holders by the actual values
        command = self._command.replace("%h", host)
        command = command.replace("%p", str(port))
        command = command.replace("%d", self._name)
        command = command.replace("%i", self._node.project().id())
        command = command.replace("%n", str(self._node.id()))
        command = command.replace("%c", Controller.instance().httpClient().fullUrl())

        # If the console use an apple script we lock to avoid multiple console
        # to interact at the same time
        if sys.platform.startswith("darwin") and "osascript" in command:
            console_mutex.lock()

        try:
            self.exec_command(command)
        except (OSError, subprocess.SubprocessError) as e:
            pass
            # log.warning('could not start Telnet console "{}": {}'.format(self._command, e))
        finally:
            log.debug('Telnet console {}:{} closed'.format(host, port))
            if sys.platform.startswith("darwin") and "osascript" in command:
                console_mutex.unlock()


def nodeTelnetConsole(node, port, command=None):
    """
    Start a Telnet console program for a topology node.

    :param node: The node
    :param command: Console command
    """

    if not node.isStarted():
        return

    if command is None:
        general_settings = MainWindow.instance().settings()
        command = general_settings["telnet_console_command"]
        if not command:
            return

    log.debug('Starting telnet console in thread "{}"'.format(command))
    console_thread = ConsoleThread(MainWindow.instance(), command, node, port)
    console_thread.consoleError.connect(_consoleErrorSlot)
    console_thread.start()


def _consoleErrorSlot(message):
    QtWidgets.QMessageBox.critical(MainWindow.instance(), "Error", message)
