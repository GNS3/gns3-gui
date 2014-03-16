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
Handles commands typed in the GNS3 console.
"""

import sys
import cmd
import logging
from .version import __version__


class ConsoleCmd(cmd.Cmd):

    def __init__(self):

        cmd.Cmd.__init__(self)

    def do_version(self, args):

        print("GNS3 version {}".format(__version__))

    def do_debug(self, args):
        """
        debug [level] (0 or 1).
        """

        root = logging.getLogger()
        ch = logging.StreamHandler(sys.stdout)

        if len(args) == 1:
            try:
                level = int(args[0])
                if level == 0:
                    print("Deactivating debugging")
                    root.removeHandler(ch)
                else:
                    print("Activating debugging")
                    root.addHandler(ch)
            except:
                print(self.do_debug.__doc__)
        else:
            print(self.do_debug.__doc__)
