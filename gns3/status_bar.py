#!/usr/bin/env python
#
# Copyright (C) 2017 GNS3 Technologies Inc.
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

import logging

from .qt import QtWidgets, QtGui, qslot


class StatusBarHandler(logging.StreamHandler):

    def __init__(self, widget):
        super().__init__()
        self._widget = widget
        self.setLevel(logging.WARNING)

    def emit(self, record):
        if record.levelno > logging.WARNING:
            self._widget.addError()
        else:
            self._widget.addWarning()


class StatusBar(QtWidgets.QStatusBar):
    """
    The status bar
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._parent = parent
        self._errors = 0
        self._warnings = 0

        self._errors_button = QtWidgets.QPushButton()
        self._errors_button.setFlat(True)
        self._errors_button.setIcon(QtGui.QIcon(":/icons/warning.svg"))
        self._errors_button.clicked.connect(self._errorButtonPushedSlot)
        self.addPermanentWidget(self._errors_button)

        self._refresh()

    def addError(self):
        """
        Increment error count
        """
        self._errors += 1
        self._refresh()

    def addWarning(self):
        """
        Increment warning count
        """
        self._warnings += 1
        self._refresh()

    def _refresh(self):
        if self._errors == 0 and self._warnings == 0:
            self._errors_button.setText("")
            self._errors_button.hide()
            return
        self._errors_button.show()
        text = ""
        if self._errors == 1:
            text += "1 error"
        elif self._errors > 1:
            text += "{} errors".format(self._errors)
        if self._warnings == 1:
            text += " 1 warning"
        elif self._warnings > 1:
            text += " {} warnings".format(self._warnings)
        self._errors_button.setText(text)

    @qslot
    def _errorButtonPushedSlot(self, *args, **kwargs):
        self._parent.uiConsoleDockWidget.toggleViewAction().trigger()
        self._warnings = 0
        self._errors = 0
        self._refresh()
