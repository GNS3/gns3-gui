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

import sys
from .qt import sip
import struct
import inspect
import datetime
import platform

from .qt import QtCore, QtWidgets
from .topology import Topology
from .version import __version__
from .console_cmd import ConsoleCmd
from .pycutext import PyCutExt
from .modules import MODULES
from .local_config import LocalConfig

import logging
log = logging.getLogger(__name__)


class ConsoleLogHandler(logging.StreamHandler):
    """
    Display log event to the console
    """

    def emit(self, record):
        if sip.isdeleted(self._console_view):
            return

        message = self.format(record)
        level_no = record.levelno
        if level_no >= logging.ERROR:
            self._console_view.write_message_signal.emit("{}\n".format(message), "error")
        elif level_no >= logging.WARNING:
            self._console_view.write_message_signal.emit("{}\n".format(message), "warning")
        elif level_no >= logging.INFO:
            # To avoid noise on console we display all event only if log level is debug
            # or if we force the display in the log record
            if "show" in record.__dict__ or logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                self._console_view.write_message_signal.emit("{}\n".format(message), "debug")
        elif level_no >= logging.DEBUG:
            self._console_view.write_message_signal.emit("{}\n".format(message), "debug")


class ConsoleView(PyCutExt, ConsoleCmd):

    # Emit this signal to write a message on console
    write_message_signal = QtCore.Signal(str, str)

    def __init__(self, parent):

        # Set the prompt PyCutExt
        self.prompt = '=> '
        sys.ps1 = '=> '

        # Set introduction message
        bitness = struct.calcsize("P") * 8
        current_year = datetime.date.today().year
        self.intro = "GNS3 management console.\nRunning GNS3 version {} on {} ({}-bit) with Python {} Qt {} and PyQt {}.\n" \
                     "Copyright (c) 2006-{} GNS3 Technologies.\n" \
                     "Use Help -> GNS3 Doctor to detect common issues." \
                     "".format(__version__, platform.system(), bitness, platform.python_version(), QtCore.QT_VERSION_STR, QtCore.PYQT_VERSION_STR, current_year)

        # Parent class initialization
        try:
            super().__init__(None, self.intro, parent=parent)

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

        self._handleLogs()

        if LocalConfig.instance().experimental():
            log.warning("WARNING: Experimental features enable. You can use some unfinished features and lost data.")

        for module in MODULES:
            instance = module.instance()
            instance.notification_signal.connect(self.writeNotification)

        self.write_message_signal.connect(self._writeMessageSlot)

        # required for Cmd module (do_help etc.)
        self.stdout = sys.stdout
        self._topology = Topology.instance()

    def contextMenuEvent(self, event):
        """
        Handles all context menu events.

        :param event: QContextMenuEvent instance
        """

        menu = self.createStandardContextMenu()
        delete_all_action = QtWidgets.QAction("Delete All", menu)
        delete_all_action.triggered.connect(self._deleteAllActionSlot)
        menu.addAction(delete_all_action)
        menu.exec_(event.globalPos());

    def _deleteAllActionSlot(self):
        """
        Delete all action slot
        """

        self.clear()
        self.write(self.prompt)
        self.lines = []
        self._clearLine()

    def _writeMessageSlot(self, message, level):
        """
        Write a message in the console.
        """
        if level == "error":
            self.write(message, error=True)
        elif level == "warning":
            self.write(message, warning=True)
        else:
            self.write(message)

    def _handleLogs(self):
        """
        Catch log message and display them
        """

        log = logging.getLogger()
        log_handler = ConsoleLogHandler()
        log_handler._console_view = self
        log.addHandler(log_handler)

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
            if cmd is None or cmd == '':
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
        if details:
            text += "\n" + details
        self.write_message_signal.emit(text, "info")

    def writeError(self, base_node_id, message):
        """
        Write error messages.

        :param base_node_id: base node identifier
        :param message: error message
        """

        node = Topology.instance().getNode(base_node_id)
        name = ""
        if node and node.name():
            name = " {}:".format(node.name())

        text = "Error:{name} {message}".format(name=name,
                                               message=message)
        self.write_message_signal.emit(text, "error")

    def writeWarning(self, base_node_id, message):
        """
        Write warning messages.

        :param base_node_id: base node identifier
        :param message: warning message
        """

        node = Topology.instance().getNode(base_node_id)
        name = ""
        if node and node.name():
            name = " {}:".format(node.name())

        text = "Warning:{name} {message}".format(name=name,
                                                 message=message)
        self.write_message_signal.emit(text, "warning")

    def writeServerError(self, base_node_id, message):
        """
        Write server error messages coming from the server.

        :param base_node_id: Base node identifier
        :param code: error code
        :param message: error message
        """

        node = Topology.instance().getNode(base_node_id)
        server = name = ""
        if node:
            if node.name():
                name = " {}:".format(node.name())
            server = "from {}".format(node.compute().name())

        text = "Server error {server}:{name} {message}".format(server=server,
                                                               name=name,
                                                               message=message)
        self.write_message_signal.emit(text.strip(), "error")

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
