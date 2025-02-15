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

from .qt import QtCore

import os
import sys
import shlex
import subprocess
import psutil
import shutil

from .main_window import MainWindow
from .controller import Controller

import logging
log = logging.getLogger(__name__)

console_mutex = QtCore.QMutex()


def gnome_terminal_env():

    uid = os.getuid()

    # get list of processes of current user
    procs = [p.info for p in psutil.process_iter(
        attrs=['name', 'pid', 'ppid', 'create_time', 'uids']
    ) if p.info['uids'].real == uid]

    # get pid of gnome-terminal-server process
    gnome_terminal_server_pid = [p['pid'] for p in procs if p['name'] == "gnome-terminal-server"]
    if not gnome_terminal_server_pid:
        return {}
    gnome_terminal_server_pid = gnome_terminal_server_pid[0]

    # get subprocesses of gnome-terminal-server
    gnome_terminal_server_children = [p for p in procs if p['ppid'] == gnome_terminal_server_pid]
    gnome_terminal_server_children.sort(key=lambda p: p['create_time'], reverse=True)

    # return the gnome-terminal environment variables of the first subprocess named telnet
    for proc in gnome_terminal_server_children:
        if proc['name'] == "telnet":
            try:
                env = psutil.Process(proc['pid']).environ()
                if 'GNOME_TERMINAL_SERVICE' in env and \
                   'GNOME_TERMINAL_SCREEN' in env:
                    return {'GNOME_TERMINAL_SERVICE': env['GNOME_TERMINAL_SERVICE'],
                            'GNOME_TERMINAL_SCREEN': env['GNOME_TERMINAL_SCREEN']}
            except psutil.Error:
                pass
    return {}


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
            subprocess.Popen(command, env=os.environ)
        else:
            # use arguments on other platforms
            try:
                args = shlex.split(command)
            except ValueError:
                self.consoleError.emit("Syntax error in command: '{}'".format(command))
                return

            env = os.environ.copy()
            # special case to force gnome-terminal to correctly use tabs on Linux
            if sys.platform.startswith("linux") and "gnome-terminal" in args[0] and "--tab" in command:
                # inject gnome-terminal environment variables
                if "GNOME_TERMINAL_SERVICE" not in env or "GNOME_TERMINAL_SCREEN" not in env:
                    env.update(gnome_terminal_env())
            proc = subprocess.Popen(args, env=env)
            if sys.platform.startswith("linux"):
                wmctrl_path = shutil.which("wmctrl")
                if wmctrl_path:
                    proc.wait() # wait for the terminal to open
                    try:
                        # use wmctrl to raise the window based on the node name
                        subprocess.run([wmctrl_path, "-Fa", self._name], env=os.environ)
                    except OSError as e:
                        self.consoleError.emit("Count not focus on terminal window: '{}'".format(e))

    def run(self):

        host = self._host
        port = self._port

        # replace the place-holders by the actual values
        command = self._command.replace("%h", host)
        command = command.replace("%p", str(port))
        command = command.replace("%d", self._name.replace('"', '\\"'))
        command = command.replace("%P", self._node.project().name().replace('"', '\\"'))
        command = command.replace("%i", self._node.project().id())
        command = command.replace("%n", str(self._node.id()))
        command = command.replace("%c", Controller.instance().httpClient().fullUrl())

        command = command.replace("{host}", host)
        command = command.replace("{port}", str(port))
        command = command.replace("{name}", self._name.replace('"', '\\"'))
        command = command.replace("{project}", self._node.project().name().replace('"', '\\"'))
        command = command.replace("{project_id}", self._node.project().id())
        command = command.replace("{node_id}", str(self._node.id()))
        command = command.replace("{url}", Controller.instance().httpClient().fullUrl())

        # If the console use an apple script we lock to avoid multiple console
        # to interact at the same time
        if sys.platform.startswith("darwin") and "osascript" in command:
            console_mutex.lock()

        try:
            self.exec_command(command)
        except (OSError, subprocess.SubprocessError) as e:
            self.consoleError.emit("Could not start Telnet console with command '{}': {}".format(command, e))
        finally:
            log.debug('Telnet console {}:{} closed'.format(host, port))
            if sys.platform.startswith("darwin") and "osascript" in command:
                console_mutex.unlock()


def nodeTelnetConsole(node, port, command=None):
    """
    Start a Telnet console program for a node.

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

    if len(command.strip(' ')) == 0:
        log.warning('Telnet console program is not configured')
        return

    log.debug('Starting telnet console in thread "{}"'.format(command))
    console_thread = ConsoleThread(MainWindow.instance(), command, node, port)
    console_thread.consoleError.connect(_consoleErrorSlot)
    console_thread.start()


def _consoleErrorSlot(message):
    log.error(message)
