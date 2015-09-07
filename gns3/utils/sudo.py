#!/usr/bin/env python
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


import subprocess


from ..qt import QtWidgets
from ..main_window import MainWindow
from .run_in_terminal import RunInTerminal


def SudoRunInTerminal(command):
    """
    Run a command in the terminal as root
    """

    while True:
        password, ok = QtWidgets.QInputDialog.getText(MainWindow.instance(), "Run as root", "Password for sudo:", QtWidgets.QLineEdit.Password, "")
        if not ok:
            return False
        with subprocess.Popen(["sudo", "-S", "id"], stdout=subprocess.PIPE, stdin=subprocess.PIPE) as proc:
            proc.communicate(input=(password + "\n").encode())
        ret = proc.wait(timeout=0.5)
        if ret == 0:
            break
    RunInTerminal("sudo {}".format(command))
    return True

