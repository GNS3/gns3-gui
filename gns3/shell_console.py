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
Functions to start external shell.
"""

import sys
import shlex
import subprocess
from .main_window import MainWindow

import logging
log = logging.getLogger(__name__)


def shellConsole(name, cmd):
    """Start a terminal on node.

    :param node: Virtual node
    :param cmd: Execution command
    """

    command = MainWindow.instance().shellConsoleCommand()
    if not command:
        return
    command = command.replace("%s", cmd)
    command = command.replace("%d", name)
    log.info('starting shell "{}"'.format(command))

    try:
        if sys.platform.startswith("win"):
            # use the string on Windows
            subprocess.Popen(command)
        else:
            # use arguments on other platforms
            args = shlex.split(command)
            subprocess.Popen(args)
    except (OSError, subprocess.SubprocessError) as e:
        log.warning('could not start shell "{}": {}'.format(command, e))
        raise
