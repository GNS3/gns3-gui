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
Functions to start external serial console terminals.
"""

import re
import os
import sys
import shlex
import subprocess
import tempfile
from .main_window import MainWindow

import logging
log = logging.getLogger(__name__)


# TODO: support more than just Vbox (Qemu maybe?)
def serialConsole(vmname):
    """
    :param vmname: Virtual machine name.

    Start a Serial console program.
    """

    command = MainWindow.instance().serialConsoleCommand()
    if not command:
        return

    p = re.compile('\s+', re.UNICODE)
    pipe_name = p.sub("_", vmname)
    if sys.platform.startswith('win'):
        pipe_name = r"\\.\pipe\VBOX\{}".format(pipe_name)
    else:
        pipe_name = os.path.join(tempfile.gettempdir(), "pipe_{}".format(pipe_name))

    # replace the place-holders by the actual values
    command = command.replace("%s", pipe_name)
    command = command.replace("%d", vmname)
    log.info('starting serial console "{}"'.format(command))

    try:
        if sys.platform.startswith("win"):
            # use the string on Windows
            subprocess.Popen(command)
        else:
            # use arguments on other platforms
            args = shlex.split(command)
            subprocess.Popen(args)
    except (OSError, subprocess.SubprocessError) as e:
        log.warning('could not start serial console "{}": {}'.format(command, e))
        raise
