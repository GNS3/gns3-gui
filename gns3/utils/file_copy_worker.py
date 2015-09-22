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
Thread to copy or move files without blocking the GUI.
"""

import shutil
from ..qt import QtCore

import logging
log = logging.getLogger(__name__)


class FileCopyWorker(QtCore.QObject):

    """
    Worker to copy a file.

    :param source: path to the source file
    :param destination: path to the destination file
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    def __init__(self, source, destination):

        super().__init__()
        self._is_running = False
        self._source = source
        self._destination = destination

    def run(self):
        """
        Worker starting point.
        """

        self._is_running = True
        try:
            shutil.copyfile(self._source, self._destination)
        except OSError as e:
            log.warning("cannot copy: {}".format(e))
            self.error.emit("Could not copy file to {}: {}".format(self._destination, e), False)
        self.finished.emit()

    def cancel(self):
        """
        Stops this worker.
        """

        if not self:
            return
        self._is_running = False
