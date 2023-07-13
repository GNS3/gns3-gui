#!/usr/bin/env python
#
# Copyright (C) 2021 GNS3 Technologies Inc.
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
import copy
import stat
import shlex
import socket
import shutil
import struct
import psutil
import signal
import subprocess


from gns3.qt import QtWidgets, QtCore, qslot
from gns3.settings import DEFAULT_CONTROLLER_HOST
from gns3.local_config import LocalConfig
from gns3.http_client import HTTPClient
from gns3.utils.wait_for_connection_worker import WaitForConnectionWorker
from gns3.utils.progress_dialog import ProgressDialog
from gns3.utils.sudo import sudo
from gns3.controller import Controller


import logging
log = logging.getLogger(__name__)


class StopLocalServerWorker(QtCore.QObject):
    """
    Worker for displaying a progress dialog when closing
    the server
    """
    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    def __init__(self, local_server_process):
        super().__init__()
        self._local_server_process = local_server_process
        self._precision = 100  # In MS
        self._remaining_trial = int(10 * (1000 / self._precision))

    @qslot
    def _callbackSlot(self, *params):
        self._local_server_process.poll()
        if self._local_server_process.returncode is None and self._remaining_trial > 0:
            self._remaining_trial -= 1
            QtCore.QTimer.singleShot(self._precision, self._callbackSlot)
        else:
            self.finished.emit()

    def run(self):
        QtCore.QTimer.singleShot(1000, self._callbackSlot)

    def cancel(self):
        return


class LocalServer(QtCore.QObject):
    """
    Manage the local server process
    """

    def __init__(self, parent=None):
        # Remember if the server was started by us or not
        self._server_started_by_me = False
        self._local_server_path = ""
        self._local_server_process = None

        super().__init__()
        self._parent = parent
        self._config_directory = LocalConfig.instance().configDirectory()
        self._settings = {}
        self.localServerSettings()
        self._port = self._settings.get("port", 3080)
        self._stopping = False
        self._timer = QtCore.QTimer()
        self._timer.setInterval(5000)
        self._timer.timeout.connect(self._checkLocalServerRunningSlot)
        self._timer.start()

    def _pid_path(self):
        """
        :returns: Path of the PID file
        """
        return os.path.join(self._config_directory, "gns3_server.pid")

    def parent(self):
        """
        Parent window
        """
        if self._parent is None:
            from gns3.main_window import MainWindow
            return MainWindow.instance()
        return self._parent

    def _checkUbridgePermissions(self):
        """
        Checks that uBridge can interact with network interfaces.
        """

        path = os.path.abspath(self._settings["ubridge_path"])

        if not path or len(path) == 0 or not os.path.exists(path) or not os.path.isfile(path):
            return False

        if sys.platform.startswith("win"):
            # do not check anything on Windows
            return True

        if os.geteuid() == 0:
            # we are root, so we should have privileged access.
            return True

        request_setuid = False
        if sys.platform.startswith("linux"):
            # test if the executable has the CAP_NET_RAW capability (Linux only)
            try:
                # test the 2nd byte and check if the 13th bit (CAP_NET_RAW) is set
                if "security.capability" not in os.listxattr(path) or not struct.unpack("<IIIII", os.getxattr(path, "security.capability"))[1] & 1 << 13:
                    proceed = QtWidgets.QMessageBox.question(
                        self.parent(),
                        "uBridge",
                        "uBridge requires CAP_NET_RAW capability to interact with network interfaces. Set the capability to uBridge? All users on the system will be able to read packet from the network interfaces.",
                        QtWidgets.QMessageBox.Yes,
                        QtWidgets.QMessageBox.No)
                    if proceed == QtWidgets.QMessageBox.Yes:
                        sudo(["setcap", "cap_net_admin,cap_net_raw=ep", path])
            except AttributeError:
                # Due to a Python bug, os.listxattr could be missing: https://github.com/GNS3/gns3-gui/issues/2010
                log.warning("Could not determine if CAP_NET_RAW capability is set for uBridge (Python bug)")
                return True
            except OSError as e:
                QtWidgets.QMessageBox.critical(self.parent(), "uBridge", "Can't set CAP_NET_RAW capability to uBridge {}: {}".format(path, str(e)))
                request_setuid = True

        if sys.platform.startswith("darwin") or request_setuid:
            try:
                if os.stat(path).st_uid != 0 or not os.stat(path).st_mode & stat.S_ISUID:
                    proceed = QtWidgets.QMessageBox.question(
                        self.parent(),
                        "uBridge",
                        "uBridge requires root permissions to interact with network interfaces. Set root permissions to uBridge? All admin users on the system will be able to read packet from the network interfaces.",
                        QtWidgets.QMessageBox.Yes,
                        QtWidgets.QMessageBox.No)
                    if proceed == QtWidgets.QMessageBox.Yes:
                        from gns3.utils.macos_ubridge_setuid import macos_ubridge_setuid
                        if sys.platform.startswith("darwin") and hasattr(sys, "frozen"):
                            macos_ubridge_setuid()
                        else:
                            sudo(["chown", "root:admin", path], ["chmod", "4750", path])
            except OSError as e:
                QtWidgets.QMessageBox.critical(self.parent(), "uBridge", "Can't set root permissions to uBridge {}: {}".format(path, str(e)))
                return False
        return True

    def localServerSettings(self):
        """
        Returns the local server settings.

        :returns: local server settings (dict)
        """

        settings = Controller.instance().settings()
        self._settings = copy.copy(settings)

        # local GNS3 server path
        local_server_path = shutil.which(settings["path"].strip())
        if local_server_path is None:
            default_server_path = shutil.which("gns3server")
            if default_server_path is not None:
                settings["path"] = os.path.abspath(default_server_path)
        else:
            settings["path"] = os.path.abspath(local_server_path)

        # uBridge path
        ubridge_path = shutil.which(settings["ubridge_path"].strip())
        if ubridge_path is None:
            default_ubridge_path = shutil.which("ubridge")
            if default_ubridge_path is not None:
                settings["ubridge_path"] = os.path.abspath(default_ubridge_path)
        else:
            settings["ubridge_path"] = os.path.abspath(ubridge_path)

        if self._settings != settings:
            self.updateLocalServerSettings(settings)
        return settings

    def updateLocalServerSettings(self, new_settings):
        """
        Update the local server settings. Keep the key not in new_settings
        """

        if "host" in new_settings and new_settings["host"] is None:
            new_settings["host"] = DEFAULT_CONTROLLER_HOST
        old_settings = copy.copy(self._settings)
        if not self._settings:
            self._settings = new_settings
        else:
            self._settings.update(new_settings)
        self._port = self._settings["port"]
        Controller.instance().setSettings(self._settings)

        # Settings have changed we need to restart the server
        if old_settings != self._settings:
            if self._settings["auto_start"]:
                # We restart the local server only if we really need. Auth can be hot change
                settings_require_restart = ('host', 'port', 'path')
                need_restart = False
                for s in settings_require_restart:
                    if old_settings.get(s) != self._settings.get(s):
                        need_restart = True

                if need_restart:
                    self.stopLocalServer(wait=True)

                self.localServerAutoStartIfRequired()
            # If the controller is remote:
            else:
                self.stopLocalServer(wait=True)

    def shouldLocalServerAutoStart(self):
        """
        Returns either the local server
        is automatically started on startup.

        :returns: boolean
        """

        return self._settings["auto_start"] and self._settings["host"] is not None

    def localServerPath(self):
        """
        Returns the local server path.

        :returns: path to local server program.
        """

        return self._settings["path"]

    def _killAlreadyRunningServer(self):
        """
        Kill a running zombie server (started by a gui that no longer exists)
        This will not kill server started by hand.
        """
        try:
            if os.path.exists(self._pid_path()):
                with open(self._pid_path()) as f:
                    pid = int(f.read())
                process = psutil.Process(pid=pid)
                log.info("Kill already running server with PID %d", pid)
                process.kill()
        except (OSError, ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
            # Permission issue, or process no longer exists, or file is empty
            return

    def localServerAutoStartIfRequired(self):
        """
        Try to start the embedded gns3 server.
        """

        local_server_already_running = self.isLocalServerRunning()
        if local_server_already_running and self._server_started_by_me:
            return True

        # We check if two gui are not launched at the same time
        # to avoid killing the server of the other GUI
        if not LocalConfig.isMainGui():
            log.info("Not the main GUI, will not auto start the server")
            Controller.instance().connect()
            return True

        if local_server_already_running:
            log.debug("A local server already running on this host")
            # Try to kill the server. The server can be still running after
            # if the server was started by hand
            self._killAlreadyRunningServer()

        if not local_server_already_running:
            if not self.initLocalServer():
                QtWidgets.QMessageBox.critical(self.parent(), "Local server", "Could not start the local server process: {}".format(self._settings["path"]))
                return False
            if not self.startLocalServer():
                QtWidgets.QMessageBox.critical(self.parent(), "Local server", "Could not start the local server process: {}".format(self._settings["path"]))
                return False

        if self.parent():
            worker = WaitForConnectionWorker(self._settings["host"], self._port)
            progress_dialog = ProgressDialog(worker,
                                             "Local controller",
                                             "Starting local controller {} on port {}...".format(self._settings["host"], self._port),
                                             "Cancel", busy=True, parent=self.parent())
            progress_dialog.show()
            if not progress_dialog.exec_():
                return False
        self._server_started_by_me = True
        Controller.instance().connect()
        return True

    def initLocalServer(self):
        """
        Initialize the local server.
        """

        self._checkUbridgePermissions()
        self._port = self._settings["port"]
        # check the local server path
        local_server_path = self.localServerPath()
        if not local_server_path:
            log.warning("No local server is configured")
            return False
        if not os.path.isfile(local_server_path):
            QtWidgets.QMessageBox.critical(self.parent(), "Local server", "Could not find local server {}".format(local_server_path))
            return False
        elif not os.access(local_server_path, os.X_OK):
            QtWidgets.QMessageBox.critical(self.parent(), "Local server", "{} is not an executable".format(local_server_path))
            return False

        try:
            # check if the local address still exists
            for res in socket.getaddrinfo(self._settings["host"], 0, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
                af, socktype, proto, _, sa = res
                with socket.socket(af, socktype, proto) as sock:
                    sock.bind(sa)
                    break
        except OSError as e:
            QtWidgets.QMessageBox.critical(self.parent(), "Local server", "Could not bind with {}: {} (please check your host binding setting in the preferences)".format(self._settings["host"], e))
            return False

        try:
            # check if the port is already taken
            find_unused_port = False
            for res in socket.getaddrinfo(self._settings["host"], self._port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
                af, socktype, proto, _, sa = res
                with socket.socket(af, socktype, proto) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(sa)
                    break
        except OSError as e:
            log.warning("Could not use socket {}:{} {}".format(self._settings["host"], self._port, e))
            find_unused_port = True

        if find_unused_port:
            # find an alternate port for the local server
            old_port = self._port
            try:
                self._port = self._findUnusedLocalPort(self._settings["host"])
            except OSError as e:
                QtWidgets.QMessageBox.critical(self.parent(), "Local server", "Could not find an unused port for the local server: {}".format(e))
                return False
            log.warning("The server port {} is already in use, fallback to port {}".format(old_port, self._port))
        return True

    def _findUnusedLocalPort(self, host):
        """
        Find an unused port.

        :param host: server hosts

        :returns: port number
        """

        with socket.socket() as s:
            s.bind((host, 0))
            return s.getsockname()[1]

    def startLocalServer(self):
        """
        Starts the local server process.
        """

        self._stopping = False
        path = self.localServerPath()
        command = '"{executable}" --local'.format(executable=path)

        if LocalConfig.instance().profile():
            command += " --profile {}".format(LocalConfig.instance().profile())

        if self._settings["allow_console_from_anywhere"]:
            # allow connections to console from remote addresses
            command += " --allow"

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            command += " --debug"

        settings_dir = self._config_directory
        if os.path.isdir(settings_dir):
            # save server logging info to a file in the settings directory
            logpath = os.path.join(settings_dir, "gns3_server.log")
            if os.path.isfile(logpath):
                # delete the previous log file
                try:
                    os.remove(logpath)
                except FileNotFoundError:
                    pass
                except OSError as e:
                    log.warning("could not delete server log file {}: {}".format(logpath, e))
            command += ' --logfile="{}" --pid="{}"'.format(logpath, self._pid_path())

        log.debug("Starting local server process with {}".format(command))
        try:
            if sys.platform.startswith("win"):
                # use the string on Windows
                self._local_server_process = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP, stderr=subprocess.PIPE)
            else:
                # use arguments on other platforms
                args = shlex.split(command)
                self._local_server_process = subprocess.Popen(args, stderr=subprocess.PIPE)
        except (OSError, subprocess.SubprocessError) as e:
            log.warning('Could not start local server "{}": {}'.format(command, e))
            return False

        log.debug("Local server process has started (PID={})".format(self._local_server_process.pid))
        return True

    def _checkLocalServerRunningSlot(self):
        if self._local_server_process and not self._stopping:
            if not self.localServerProcessIsRunning():
                log.error("Local server process has stopped")
                try:
                    log.error(self._local_server_process.stderr.read().decode())
                except (OSError, UnicodeDecodeError):
                    pass
                self._local_server_process = None

    def localServerProcessIsRunning(self):
        """
        Returns either the local server is running.

        :returns: boolean
        """

        try:
            if self._local_server_process and self._local_server_process.poll() is None:
                return True
        except OSError:
            pass
        return False

    def isLocalServerRunning(self):
        """
        Synchronous check if a server is already running on this host.

        :returns: boolean
        """

        http_client = HTTPClient(self._settings)
        return http_client.checkServerRunning()

    def stopLocalServer(self, wait=False):
        """
        Stops the local server.

        :param wait: wait for the server to stop
        """

        if self.localServerProcessIsRunning():
            self._stopping = True
            log.debug("Stopping local controller (PID={})".format(self._local_server_process.pid))
            # local server is running, let's stop it
            http_client = Controller.instance().httpClient()
            if http_client:
                http_client.shutdown()
            if wait:
                worker = StopLocalServerWorker(self._local_server_process)
                progress_dialog = ProgressDialog(worker, "Local server", "Waiting for the local controller to stop...", None, busy=True, parent=self.parent())
                progress_dialog.show()
                progress_dialog.exec_()
                if self._local_server_process.returncode is None:
                    self._killLocalServer()
            self._server_started_by_me = False

    def _killLocalServer(self):
        # the local server couldn't be stopped with the normal procedure
        try:
            if sys.platform.startswith("win"):
                self._local_server_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                self._local_server_process.send_signal(signal.SIGINT)
        # If the process is already dead we received a permission error
        # it's a race condition between the timeout and send signal
        except (PermissionError, SystemError):
            pass
        try:
            # wait for the server to stop for maximum x seconds
            self._local_server_process.wait(timeout=60)
        except subprocess.TimeoutExpired:
            proceed = QtWidgets.QMessageBox.question(self.parent(),
                                                     "Local controller",
                                                     "The local controller cannot be stopped, would you like to kill it?",
                                                     QtWidgets.QMessageBox.Yes,
                                                     QtWidgets.QMessageBox.No)

            if proceed == QtWidgets.QMessageBox.Yes:
                self._local_server_process.kill()

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of LocalServer.
        :returns: instance of LocalServer
        """

        if not hasattr(LocalServer, '_instance') or LocalServer._instance is None:
            LocalServer._instance = LocalServer()
        return LocalServer._instance


def main():
    import pprint

    pp = pprint.PrettyPrinter(indent=4)
    print("Local server config")
    local_server = LocalServer(False)
    pp.pprint(local_server.localServerSettings())
    local_server.localServerAutoStart()
    local_server.stopLocalServer()


if __name__ == '__main__':
    main()
