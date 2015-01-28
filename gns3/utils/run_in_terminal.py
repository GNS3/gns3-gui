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

import os
import sys
import subprocess
import shlex
import tempfile


def RunInTerminal(command):

    if sys.platform.startswith("win"):
        if "ComSpec" not in os.environ:
            raise OSError("ComSpec environment variable is not set")
        terminal_cmd = "{} /K cd %TEMP% && {}".format(os.environ['ComSpec'], command)
    elif sys.platform.startswith('darwin'):
        terminal_cmd = "/usr/bin/osascript -e 'tell application \"terminal\" to do script with command \"{}; exit\"'".format(command)
        terminal_cmd = shlex.split(terminal_cmd)
    else:
        terminal_cmd = None
        for path in os.environ["PATH"].split(os.pathsep):
            if "xterm" in os.listdir(path) and os.access(os.path.join(path, "xterm"), os.X_OK):
                terminal_cmd = "{} -e '{}'".format(os.path.join(path, "xterm"), command)
                terminal_cmd = shlex.split(terminal_cmd)
                break
        if not terminal_cmd:
            raise OSError("xterm must be installed first")
    subprocess.Popen(terminal_cmd, stdout=subprocess.PIPE, cwd=tempfile.gettempdir())

if __name__ == '__main__':

    cmd = '/usr/local/bin/dynamips -P 3600 -r 128 --idle-pc 0x0 "/path/to/IOS/c3725-advipservicesk9-mz.124-15.T14.image"'
    RunInTerminal(cmd)
