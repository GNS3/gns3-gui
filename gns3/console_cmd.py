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
import struct
from .qt import sip

from .node import Node
from .qt import QtCore
from .version import __version__

import logging
log = logging.getLogger(__name__)


class ConsoleCmd(cmd.Cmd):

    def do_version(self, args):
        """
        Show the version of GNS3 and its dependencies.
        """

        compiled = ""
        if hasattr(sys, "frozen"):
            compiled = "(compiled)"
        print("GNS3 version is {} {}".format(__version__, compiled))
        print("Python version is {}.{}.{} ({}-bit) with {} encoding".format(sys.version_info[0],
                                                                            sys.version_info[1],
                                                                            sys.version_info[2],
                                                                            struct.calcsize("P") * 8,
                                                                            sys.getdefaultencoding()))
        print("Qt version is {}".format(QtCore.QT_VERSION_STR))

        print("PyQt version is {}".format(QtCore.PYQT_VERSION_STR))
        print("SIP version is {}".format(sip.SIP_VERSION_STR))

    def do_start(self, args):
        """
        Start all or a specific device(s)
        start {/all | device1 [device2] ...}
        """

        if '?' in args or args.strip() == "":
            print(self.do_start.__doc__)
            return

        devices = args.split()
        if '/all' in devices:
            for node in self._topology.nodes():
                if hasattr(node, "start") and node.initialized():
                    node.start()
        else:
            for device in devices:
                for node in self._topology.nodes():
                    if node.name() == device:
                        if hasattr(node, "start") and node.initialized():
                            node.start()
                        else:
                            print("{} cannot be started".format(device))
                        break

    def do_stop(self, args):
        """
        Stop all or a specific device(s)
        stop {/all | device1 [device2] ...}
        """

        if '?' in args or args.strip() == "":
            print(self.do_stop.__doc__)
            return

        devices = args.split()
        if '/all' in devices:
            for node in self._topology.nodes():
                if hasattr(node, "stop") and node.initialized():
                    node.stop()
        else:
            for device in devices:
                for node in self._topology.nodes():
                    if node.name() == device:
                        if hasattr(node, "stop") and node.initialized():
                            node.stop()
                        else:
                            print("{} cannot be stopped".format(device))
                        break

    def do_suspend(self, args):
        """
        Suspend all or a specific device(s)
        suspend {/all | device1 [device2] ...}
        """

        if '?' in args or args.strip() == "":
            print(self.do_suspend.__doc__)
            return

        devices = args.split()
        if '/all' in devices:
            for node in self._topology.nodes():
                if hasattr(node, "suspend") and node.initialized():
                    node.suspend()
        else:
            for device in devices:
                for node in self._topology.nodes():
                    if node.name() == device:
                        if hasattr(node, "suspend") and node.initialized():
                            node.suspend()
                        else:
                            print("{} cannot be suspended".format(device))
                        break

    def do_reload(self, args):
        """
        Reload all or a specific device(s)
        reload {/all | device1 [device2] ...}
        """

        if '?' in args or args.strip() == "":
            print(self.do_reload.__doc__)
            return

        devices = args.split()
        if '/all' in devices:
            for node in self._topology.nodes():
                if hasattr(node, "reload") and node.initialized():
                    node.reload()
        else:
            for device in devices:
                for node in self._topology.nodes():
                    if node.name() == device:
                        if hasattr(node, "reload") and node.initialized():
                            node.reload()
                        else:
                            print("{} cannot be reloaded".format(device))
                        break

    def do_console(self, args):
        """
        Console to all or a specific device(s)
        console {/all | device1 [device2] ...}
        """

        if '?' in args or args.strip() == "":
            print(self.do_console.__doc__)
            return

        devices = args.split()
        if '/all' in devices:
            for node in self._topology.nodes():
                if hasattr(node, "console") and node.initialized() and node.status() == Node.started:
                    self._start_console(node)
        else:
            for device in devices:
                for node in self._topology.nodes():
                    if node.name() == device:
                        if hasattr(node, "console") and node.initialized() and node.status() == Node.started:
                            self._start_console(node)
                        else:
                            print("Cannot console to {}".format(device))
                        break

    def do_log(self, args):
        """
        Log a message

        log level message
        """

        args = args.split()
        if len(args) == 0:
            return
        level = args.pop(0)
        if level == "info":
            log.info(" ".join(args))
        elif level == "warning":
            log.warning(" ".join(args))
        else:
            log.error(" ".join(args))

    def _start_console(self, node):
        """
        Starts a console application for a specific node.

        :param node: Node instance
        """

        console_port = node.console()
        from .telnet_console import nodeTelnetConsole
        nodeTelnetConsole(node, console_port)

    def do_debug(self, args):
        """
        Activate or deactivate debugging messages
        debug [level] (0, 1 or 2).
        """

        if '?' in args or args.strip() == "":
            print(self.do_debug.__doc__)
            return

        root = logging.getLogger()

        if len(args) == 1:
            level = int(args[0])
            if level == 0:
                print("Deactivating debugging")
                root.setLevel(logging.INFO)
            else:
                print("Activating debugging")
                root.setLevel(logging.DEBUG)
            from .main_window import MainWindow
            MainWindow.instance().setSettings({"debug_level": level})
        else:
            print(self.do_debug.__doc__)

    def _show_device(self, params):
        """
        Handles the 'show device' command.

        :param params: list of parameters
        """

        if len(params) == 1:
            # print out all the device info
            for node in self._topology.nodes():
                if hasattr(node, "info"):
                    print(node.info())

        elif len(params) >= 2:
            # this is a 'show device <device_name>'
            params.pop(0)
            for param in params:
                node_name = param
                found = False
                for node in self._topology.nodes():
                    if hasattr(node, "info") and node.name() == node_name:
                        print(node.info())
                        found = True
                        break

                if found is False:
                    print("{}: no such device".format(node_name))
                    continue

    def do_show(self, args):
        """
        Show detail information about every device in current lab:
        show device

        Show detail information about a device:
        show device <device_name>
        """

        if '?' in args or args.strip() == "":
            print(self.do_show.__doc__)
            return

        params = args.split()
        if params[0] == "device":
            self._show_device(params)
        else:
            print(self.do_show.__doc__)

    def do_help(self, args):
        """
        Get help on commands
        'help' or '?' with no arguments prints a list of commands for which help is available
        'help <command>' or '? <command>' gives help on <command>
        """

        cmd.Cmd.do_help(self, args)
