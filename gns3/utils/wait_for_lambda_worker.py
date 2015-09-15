# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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
Thread showing a progress dialog and running the code from a lambda
"""

from ..qt import QtCore

import logging
log = logging.getLogger(__name__)


class WaitForLambdaWorker(QtCore.QObject):

    """
    Thread to wait for a lambda to be executed.

    :param lambda_runner: lambda to execute in background
    """

    error = QtCore.pyqtSignal(str, bool)
    finished = QtCore.pyqtSignal()
    updated = QtCore.pyqtSignal(int)

    def __init__(self, lambda_runner):

        super().__init__()
        self._lambda_runner = lambda_runner

    def run(self):
        """
        Worker starting point.
        """

        try:
            self._lambda_runner()
        except Exception as e:
            self.error.emit(str(e), True)
            return
        self.finished.emit()

    def cancel(self):
        pass
