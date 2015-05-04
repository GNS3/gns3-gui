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

import platform
import sys
import struct
import inspect
import datetime
from .topology import Topology
from .version import __version__
from .console_cmd import ConsoleCmd
from .pycutext import PyCutExt
from .modules import MODULES


class ConsoleView(PyCutExt, ConsoleCmd):

    def __init__(self, parent):

        # Set the prompt PyCutExt
        self.prompt = '=> '
        sys.ps1 = '=> '

        # Set introduction message
        bitness = struct.calcsize("P") * 8
        current_year = datetime.date.today().year
        self.intro = "GNS3 management console. Running GNS3 version {} on {} ({}-bit).\n" \
                     "Copyright (c) 2006-{} GNS3 Technologies.".format(__version__, platform.system(), bitness, current_year)

        # Parent class initialization
        try:
            PyCutExt.__init__(self, None, self.intro, parent=parent)

            # dynamically get all the available commands so we can color them
            methods = inspect.getmembers(self, predicate=inspect.ismethod)
            commands = []
            for method in methods:
                method_name = method[0]
                if method_name.startswith("do_"):
                    commands.append(method_name[3:])

            # put our own keywords list
            self.colorizer.keywords = commands
        except Exception as e:
            sys.stderr.write(e)

        for module in MODULES:
            instance = module.instance()
            instance.notification_signal.connect(self.writeNotification)

        # required for Cmd module (do_help etc.)
        self.stdout = sys.stdout
        self._topology = Topology.instance()

    def isatty(self):
        """
        For exception handling purposes
        (see exception hook in the program entry point).
        """

        return False

    def onKeyPress_Tab(self):
        """
        Imitate cmd.Cmd.complete(self, text, state) function.
        """

        line = str(self.line).lstrip()
        cmd = line
        args = ''

        if len(self.line) > 0:
            cmd, args, _ = self.parseline(line)
            if cmd == '':
                compfunc = self.completedefault
            else:
                try:
                    compfunc = getattr(self, 'complete_' + cmd)
                except AttributeError:
                    compfunc = self.completenames
        else:
            compfunc = self.completenames

        self.completion_matches = compfunc(cmd, line, 0, 0)
        if self.completion_matches is not None:
            # Eliminate repeating values
            matches = []
            for m in self.completion_matches:
                try:
                    matches.index(m)
                except ValueError:
                    matches.append(m)

            # Update original list
            self.completion_matches = matches

            # In case we only have one possible value replace it on cmdline
            if len(self.completion_matches) == 1:
                newLine = self.completion_matches[0] + " " + args
                self.line = newLine
                self.point = len(newLine)
            # Else, display possible values
            elif self.completion_matches:
                self.write("\n")
                print(" ".join(self.completion_matches))

        # In any case, reprint prompt + line
        self.write("\n" + sys.ps1 + str(self.line))

    def writeNotification(self, message, details=""):
        """
        Write notification messages coming from the server.

        :param message: notification message
        :param details: details (text)
        """

        text = "Server notification: {}".format(message)
        self.write(text, error=True)
        self.write("\n")
        if details:
            self.write(details)
            self.write("\n")

    def writeError(self, node_id, message):
        """
        Write error messages.

        :param node_id: node identifier
        :param message: error message
        """

        node = Topology.instance().getNode(node_id)
        name = ""
        if node and node.name():
            name = " {}:".format(node.name())

        text = "Error:{name} {message}".format(name=name,
                                               message=message)
        self.write(text, error=True)
        self.write("\n")

    def writeWarning(self, node_id, message):
        """
        Write warning messages.

        :param node_id: node identifier
        :param message: warning message
        """

        node = Topology.instance().getNode(node_id)
        name = ""
        if node and node.name():
            name = " {}:".format(node.name())

        text = "Warning:{name} {message}".format(name=name,
                                                 message=message)
        self.write(text, warning=True)
        self.write("\n")

    def writeServerError(self, node_id, message):
        """
        Write server error messages coming from the server.

        :param node_id: node identifier
        :param code: error code
        :param message: error message
        """

        node = Topology.instance().getNode(node_id)
        server = name = ""
        if node:
            if node.name():
                name = " {}:".format(node.name())
            server = "from {}:{}".format(node.server().host,
                                         node.server().port)

        text = "Server error {server}:{name} {message}".format(server=server,
                                                               name=name,
                                                               message=message)
        self.write(text, error=True)
        self.write("\n")

    def _run(self):
        """
        Runs as command as the cmd.Cmd class would do.
        PyCutExt was originally using as Interpreter to exec user's commands.
        Here we use directly the cmd.Cmd class.
        """

        self.pointer = 0
        if len(self.line):
            self.history.append(self.line)
            try:
                self.lines.append(self.line)
                source = "\n".join(self.lines)
                self.more = self.onecmd(source)
            except Exception as e:
                print("Unknown error: {}".format(e))

        self.write(self.prompt)
        self.lines = []
        self._clearLine()
