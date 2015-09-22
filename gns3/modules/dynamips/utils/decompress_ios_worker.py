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

import zipfile
import zlib

from gns3.qt import QtCore
from .decompress_ios import decompressIOS


class DecompressIOSWorker(QtCore.QObject):

    """
    Thread to decompress an IOS image.

    :param ios_image: IOS image path
    :param destination_file: destination path for the decompressed IOS image
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    def __init__(self, ios_image, destination_file):

        super().__init__()
        self._is_running = False
        self._ios_image = ios_image
        self._destination_file = destination_file

    def run(self):
        """
        Thread starting point.
        """

        self._is_running = True
        try:
            decompressIOS(self._ios_image, self._destination_file)
        except (zipfile.BadZipFile, zlib.error) as e:
            self.error.emit("File {} is corrupted {}".format(self._ios_image, e), True)
            return
        except (OSError, MemoryError) as e:
            self.error.emit("Could not decompress {}: {}".format(self._ios_image, e), True)
            return

        # IOS image has successfully been decompressed
        self.finished.emit()

    def cancel(self):
        """
        Cancel this worker.
        """

        if not self:
            return
        self._is_running = False
