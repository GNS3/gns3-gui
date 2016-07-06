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

import os
import shutil
from ..qt import QtCore

import logging
log = logging.getLogger(__name__)


class ProcessFilesWorker(QtCore.QObject):

    """
    Thread to process files (copy or move).

    :param source_dir: path to the source directory
    :param destination_dir: path to the destination directory (created if doesn't exist)
    :param move: indicates if the files must be moved instead of copied
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    def __init__(self, source_dir, destination_dir, move=False, skip_dirs=None, skip_files=None):

        super().__init__()
        self._is_running = False
        self._source = source_dir
        self._destination = destination_dir
        self._move = move
        self._skip_dirs = []
        self._skip_files = []
        if skip_dirs:
            self._skip_dirs = skip_dirs
        if skip_files:
            self._skip_files = skip_files

    def run(self):
        """
        Worker starting point.
        """

        self._is_running = True
        try:
            os.makedirs(self._destination)
        except FileExistsError:
            pass
        except OSError as e:
            self.error.emit("Could not create directory {}: {}".format(self._destination, e), True)
            return

        # Source can be None if directory have never been created (temporary project only on remote servers)
        if self._source is None:
            self.finished.emit()
            return

        copied = 0
        # start copying/moving from the source directory
        try:
            # count the number of files in the source directory
            file_count = self._countFiles(self._source)

            for path, dirs, filenames in os.walk(self._source):
                dirs[:] = [d for d in dirs if d not in self._skip_dirs]
                filenames[:] = [f for f in filenames if f not in self._skip_files]
                base_dir = path.replace(self._source, self._destination)

                # start create the destination sub-directories
                for directory in dirs:
                    try:
                        destination_dir = os.path.join(base_dir, directory)
                        os.makedirs(destination_dir)
                    except FileExistsError:
                        pass
                    except OSError as e:
                        self.error.emit("Could not create directory {}: {}".format(destination_dir, e), True)
                        return
                    if not self._is_running:
                        return

                # finally the files themselves
                for sfile in filenames:
                    source_file = os.path.join(path, sfile)
                    destination_file = os.path.join(base_dir, sfile)
                    try:
                        if self._move:
                            shutil.move(source_file, destination_file)
                        else:
                            shutil.copy2(source_file, destination_file)
                    except OSError as e:
                        if self._move:
                            log.warning("Cannot move: {}".format(e))
                            self.error.emit("Could not move file to {}: {}".format(destination_file, e), False)
                        else:
                            log.warning("Cannot copy: {}".format(e))
                            self.error.emit("Could not copy file to {}: {}".format(destination_file, e), False)
                    if not self._is_running:
                        return
                    copied += 1
                    # update the progress made
                    progress = float(copied) / file_count * 100
                    self.updated.emit(progress)
        except RuntimeError:
            self.error.emit("Maximum path depth exceedeed when copying {}".format(self._source), True)

        # everything has been copied or moved, let's inform the GUI
        self.finished.emit()

    def _countFiles(self, directory):
        """
        Counts all the files in a directory.

        :param directory: path to the directory.
        """

        count = 0
        for _, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in self._skip_dirs]
            files[:] = [f for f in files if f not in self._skip_files]
            count += len(files)
        return count

    def cancel(self):
        """
        Cancel this worker.
        """

        if not self:
            return
        self._is_running = False
