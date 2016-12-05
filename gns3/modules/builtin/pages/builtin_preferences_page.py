# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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
Configuration page for Built-in preferences.
"""

from gns3.qt import QtWidgets
from .. import Builtin
from ..ui.builtin_preferences_page_ui import Ui_BuiltinPreferencesPageWidget
from ..settings import BUILTIN_SETTINGS


class BuiltinPreferencesPage(QtWidgets.QWidget, Ui_BuiltinPreferencesPageWidget):
    """QWidget preference page for Built-in."""

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        # connect signals
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)

    def _restoreDefaultsSlot(self):
        """Slot to populate the page widgets with the default settings."""

        self._populateWidgets(BUILTIN_SETTINGS)

    def _populateWidgets(self, settings):
        """Populates the widgets with the settings.

        :param settings: Built-in settings
        """

    def loadPreferences(self):
        """Loads Built-in preferences."""

        builtin_settings = Builtin.instance().settings()
        self._populateWidgets(builtin_settings)

    def savePreferences(self):
        """Saves Built-in preferences."""

        new_settings = {}
        Builtin.instance().setSettings(new_settings)
