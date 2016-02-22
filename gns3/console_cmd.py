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
import struct
import sip
import json
from .qt import QtCore
from .node import Node
from .version import __version__
try:
    from gns3converter import __version__ as gns3converter_version
except ImportError:
    gns3converter_version = "Not installed"


class ConsoleCmd(cmd.Cmd):

    def do_version(self, args):
        """
        Show the version of GNS3 and its dependencies.
        """

        compiled = ""
        if hasattr(sys, "frozen"):
            compiled = "(compiled)"
        print("GNS3 version is {} {}".format(__version__, compiled))
        print("GNS3 Converter version is {}".format(gns3converter_version))
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

    def _start_console(self, node):
        """
        Starts a console application for a specific node.

        :param node: Node instance
        """

        name = node.name()
        console_port = node.console()
        console_host = node.server().host()
        try:
            from .telnet_console import telnetConsole
            telnetConsole(name, console_host, console_port)
        except (OSError, ValueError) as e:
            print("Cannot start console application: {}".format(e))

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
                for handler in root.handlers:
                    if isinstance(handler, logging.StreamHandler):
                        root.removeHandler(handler)
                root.setLevel(logging.INFO)
            else:
                root.addHandler(logging.StreamHandler(sys.stdout))
                if level == 1:
                    print("Activating debugging")
                else:
                    print("Activating full debugging")
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

    def _show_run(self, params):
        """
        Handles the 'show run' command.

        :param params: list of parameters
        """

        if self._topology.project is None:
            print("Sorry, the project hasn't been saved yet")
            return

        topology = self._topology.dump()
        if len(params) == 1:
            # print out whole topology
            print(json.dumps(topology, sort_keys=True, indent=4))
        elif len(params) >= 2:
            # this is a 'show run <device_name>'
            params.pop(0)
            for param in params:
                node_name = param
                node_id = None

                # get the node ID
                for node in self._topology.nodes():
                    if node.name() == node_name:
                        node_id = node.id()
                        break

                if node_id is None:
                    print("{}: no such device".format(node_name))
                    continue

                if "nodes" in topology["topology"]:
                    for node in topology["topology"]["nodes"]:
                        if node["id"] == node_id:
                            print(json.dumps(node, sort_keys=True, indent=4))
                            break

    def _show_gnsvm(self, params):
        """
        Handles the 'show gns3vm' command.

        :param params: list of parameters
        """
        from gns3.gns3_vm import GNS3VM
        vm = GNS3VM.instance()
        print("Running: {}".format(vm.isRunning()))
        print("Settings: {}".format(vm.settings()))

    def do_show(self, args):
        """
        Show detail information about every device in current lab:
        show device

        Show detail information about a device:
        show device <device_name>

        Show the whole topology:
        show run

        Show topology info of a device:
        show run <device_name>

        Show the GNS3 VM status
        show gns3vm
        """

        if '?' in args or args.strip() == "":
            print(self.do_show.__doc__)
            return

        params = args.split()
        if params[0] == "device":
            self._show_device(params)
        elif params[0] == "run":
            self._show_run(params)
        elif params[0] == "gns3vm":
            self._show_gnsvm(params)
        else:
            print(self.do_show.__doc__)

    def do_help(self, args):
        """
        Get help on commands
        'help' or '?' with no arguments prints a list of commands for which help is available
        'help <command>' or '? <command>' gives help on <command>
        """

        cmd.Cmd.do_help(self, args)
