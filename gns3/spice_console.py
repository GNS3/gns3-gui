# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 GNS3 Technologies Inc.
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
Functions to start SPICE console programs.
"""

import sys
import os
import shlex
import subprocess

import logging
log = logging.getLogger(__name__)


def spiceConsole(host, port, command):
    """
    Start a SPICE console program.

    :param host: host or IP address
    :param port: port number
    :param command: command to be executed
    """

    if len(command.strip(' ')) == 0:
        log.warning('SPICE client is not configured')
        return

    # ipv6 support
    if ":" in host:
        host = "[{}]".format(host)

    # replace the place-holders by the actual values
    command = command.replace("%h", host)
    command = command.replace("%p", str(port))

    try:
        log.info('starting SPICE program "{}"'.format(command))
        if sys.platform.startswith("win"):
            # use the string on Windows
            subprocess.Popen(command)
        else:
            # use arguments on other platforms
            args = shlex.split(command)
            subprocess.Popen(args, env=os.environ)
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        log.warning('could not start SPICE program "{}": {}'.format(command, e))
        raise
