# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 GNS3 Technologies Inc.
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
Configuration page for TraceNG preferences.
"""

import os
import sys
import shutil

from gns3.qt import QtWidgets

from .. import TraceNG
from ..ui.traceng_preferences_page_ui import Ui_TraceNGPreferencesPageWidget
from ..settings import TRACENG_SETTINGS


class TraceNGPreferencesPage(QtWidgets.QWidget, Ui_TraceNGPreferencesPageWidget):
    """
    QWidget preference page for TraceNG
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        # connect signals
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiTraceNGPathToolButton.clicked.connect(self._tracengPathBrowserSlot)

    def _tracengPathBrowserSlot(self):
        """
        Slot to open a file browser and select traceng
        """

        filter = ""
        if sys.platform.startswith("win"):
            filter = "Executable (*.exe);;All files (*)"
        traceng_path = shutil.which("traceng")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select TraceNG", traceng_path, filter)
        if not path:
            return

        if self._checkTraceNGPath(path):
            self.uiTraceNGPathLineEdit.setText(os.path.normpath(path))

    def _checkTraceNGPath(self, path):
        """
        Checks that the TraceNG path is valid.

        :param path: TraceNG path
        :returns: boolean
        """

        if not os.path.exists(path):
            QtWidgets.QMessageBox.critical(self, "TraceNG", '"{}" does not exist'.format(path))
            return False

        if not os.access(path, os.X_OK):
            QtWidgets.QMessageBox.critical(self, "TraceNG", "{} is not an executable".format(os.path.basename(path)))
            return False

        return True

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(TRACENG_SETTINGS)

    def _useLocalServerSlot(self, state):
        """
        Slot to enable or not local server settings.
        """

        if state:
            self.uiTraceNGPathLineEdit.setEnabled(True)
            self.uiTraceNGPathToolButton.setEnabled(True)
        else:
            self.uiTraceNGPathLineEdit.setEnabled(False)
            self.uiTraceNGPathToolButton.setEnabled(False)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: TraceNG settings
        """

        self.uiTraceNGPathLineEdit.setText(settings["traceng_path"])

    def loadPreferences(self):
        """
        Loads TraceNG preferences.
        """

        traceng_settings = TraceNG.instance().settings()
        self._populateWidgets(traceng_settings)

    def savePreferences(self):
        """
        Saves TraceNG preferences.
        """

        traceng_path = self.uiTraceNGPathLineEdit.text().strip()
        if traceng_path and not self._checkTraceNGPath(traceng_path):
            return
        new_settings = {"traceng_path": traceng_path}
        TraceNG.instance().setSettings(new_settings)
