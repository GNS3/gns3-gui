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
Functions to start VNC console programs.
"""

import sys
import os
import shlex
import subprocess

from .controller import Controller

import logging
log = logging.getLogger(__name__)


def vncConsole(node, port, command):
    """
    Start a VNC console program.

    :param node: Node instance
    :param port: port number
    """

    if len(command.strip(' ')) == 0:
        log.error("VNC client is not configured")
        return

    name = node.name()
    host = node.consoleHost()

    # replace the place-holders by the actual values
    command = command.replace("%h", host)
    command = command.replace("%p", str(port))
    command = command.replace("%D", str(port - 5900))
    command = command.replace("%d", name.replace('"', '\\"'))
    command = command.replace("%P", node.project().name().replace('"', '\\"'))
    command = command.replace("%i", node.project().id())
    command = command.replace("%n", str(node.id()))
    command = command.replace("%c", Controller.instance().httpClient().fullUrl())

    command = command.replace("{host}", host)
    command = command.replace("{port}", str(port))
    command = command.replace("{display}", str(port - 5900))
    command = command.replace("{name}", name.replace('"', '\\"'))
    command = command.replace("{project}", node.project().name().replace('"', '\\"'))
    command = command.replace("{project_id}", node.project().id())
    command = command.replace("{node_id}", str(node.id()))
    command = command.replace("{url}", Controller.instance().httpClient().fullUrl())

    try:
        log.debug('starting VNC program "{}"'.format(command))
        if sys.platform.startswith("win"):
            # use the string on Windows
            subprocess.Popen(command, env=os.environ)
        else:
            # use arguments on other platforms
            args = shlex.split(command)
            subprocess.Popen(args, env=os.environ)
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        log.error("Could not start VNC program with command '{}': {}".format(command, e))
