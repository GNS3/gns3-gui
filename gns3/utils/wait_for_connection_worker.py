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
Thread to repeatedly try to connect to a network resource.
"""

import socket
import time
from ..qt import QtCore


class WaitForConnectionWorker(QtCore.QObject):

    """
    Thread to wait for a connection.

    :param host: destination host or IP address
    :param port: destination port
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    def __init__(self, host, port):

        super().__init__()
        self._is_running = False
        self._host = host
        self._port = port

    def run(self):
        """
        Worker starting point.
        """

        self._is_running = True
        connection_success = False
        begin = time.time()

        # try to connect for 30 seconds
        while time.time() - begin < 30.0:
            if not self._is_running:
                return
            time.sleep(0.01)
            sock = None
            try:
                sock = socket.create_connection((self._host, self._port), timeout=10)
            except OSError as e:
                last_exception = e
                continue
            finally:
                if sock:
                    sock.close()
            connection_success = True
            break

        if not self._is_running:
            return

        if not connection_success:

            # let the GUI know about the connection was unsuccessful
            self.error.emit("Could not connect to {} on port {}: {}".format(self._host,
                                                                            self._port,
                                                                            last_exception), True)
            return

        # connection has been successful, let's inform the GUI
        self.finished.emit()

    def cancel(self):
        """
        Cancel this worker.
        """

        if not self:
            return
        self._is_running = False
