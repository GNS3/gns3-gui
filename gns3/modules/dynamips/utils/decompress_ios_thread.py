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
Thread to wait for an IOS image to be decompressed.
"""

from gns3.qt import QtCore
from .decompress_ios import decompressIOS


class DecompressIOSThread(QtCore.QThread):

    """
    Thread to decompress an IOS image.

    :param ios_image: IOS image path
    :param destination_file: destination path for the decompressed IOS image
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    completed = QtCore.pyqtSignal()
    update = QtCore.pyqtSignal(int)

    def __init__(self, ios_image, destination_file):

        QtCore.QThread.__init__(self)
        self._ios_image = ios_image
        self._destination_file = destination_file
        self._is_running = False

    def run(self):
        """
        Thread starting point.
        """

        self._is_running = True
        try:
            decompressIOS(self._ios_image, self._destination_file)
        except OSError as e:
            self.error.emit("Could not decompress {}: {}".format(self._ios_image, e), True)
            return

        # IOS image has successfully been decompressed
        self.completed.emit()

    def stop(self):
        """
        Stops this thread as soon as possible.
        """

        self._is_running = False
