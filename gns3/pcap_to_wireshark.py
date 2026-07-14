# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 GNS3 Technologies Inc.
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
import time
import shlex
import subprocess

from .qt import QtCore

class PCAPToWireshark(QtCore.QThread):
    error_signal = QtCore.pyqtSignal(str)

    def __init__(self, pcap_path, wireshark_cmd):

        super().__init__()
        self._pcap_path = pcap_path
        self._wireshark_cmd = wireshark_cmd
        self._running = True
        self._wireshark_proc = None

    def run(self):

        if not os.path.exists(self._pcap_path):
            self.error_signal.emit(f"Error: {self._pcap_path} not found.")
            return

        try:
            wireshark_cmd = shlex.split(self._wireshark_cmd)
        except ValueError as e:
            self.error_signal.emit(f"Invalid Wireshark command {self._wireshark_cmd}: {str(e)}")
            return

        try:
            self._wireshark_proc = subprocess.Popen(
                wireshark_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            self.error_signal.emit("Error: Wireshark not found in $PATH")
            return

        with open(self._pcap_path, 'rb') as f:
            #f.seek(0, os.SEEK_END)

            while self._running and self._wireshark_proc.poll() is None:
                chunk = f.read(4096)
                if chunk:
                    try:
                        self._wireshark_proc.stdin.write(chunk)
                        self._wireshark_proc.stdin.flush()
                    except BrokenPipeError:
                        break  # Wireshark has been closed
                else:
                    time.sleep(0.1)

    def stop(self):
        self._running = False
        if self._wireshark_proc:
            try:
                self._wireshark_proc.stdin.close()
                self._wireshark_proc.kill()
            except Exception as e:
                print(e)
                pass
