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

from ..qt import QtCore, QtWidgets
from ..ui.exec_command_dialog_ui import Ui_ExecCommandDialog


class ExecCommandDialog(QtWidgets.QDialog, Ui_ExecCommandDialog):

    """
    Execute a command and display its output.
    """

    def __init__(self, parent, command, params):

        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Executing {}".format(command))
        self._process = QtCore.QProcess(self)
        self._process.readyRead.connect(self._dataReadySlot)
        self._process.start(command, params, QtCore.QProcess.Unbuffered | QtCore.QProcess.ReadWrite)

    def _dataReadySlot(self):
        """
        Display the command output when data is ready.
        """

        cursor = self.uiOutputTextEdit.textCursor()
        cursor.movePosition(cursor.End)
        for line in self._process.readAll():
            cursor.insertText(line)
        for line in self._process.readAllStandardError():
            cursor.insertText(line)
        self.uiOutputTextEdit.ensureCursorVisible()

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        self._process.kill()
        self._process.waitForFinished()
        super().done(result)
