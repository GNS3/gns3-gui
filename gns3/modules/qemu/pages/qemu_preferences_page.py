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
Configuration page for QEMU preferences.
"""

from gns3.qt import QtGui
from .. import Qemu
from ..ui.qemu_preferences_page_ui import Ui_QemuPreferencesPageWidget
from ..settings import QEMU_SETTINGS


class QemuPreferencesPage(QtGui.QWidget, Ui_QemuPreferencesPageWidget):

    """
    QWidget preference page for QEMU.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        # connect signals
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(QEMU_SETTINGS)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: QEMU settings
        """

        self.uiUseLocalServercheckBox.setChecked(settings["use_local_server"])

    def loadPreferences(self):
        """
        Loads QEMU preferences.
        """

        qemu_settings = Qemu.instance().settings()
        self._populateWidgets(qemu_settings)

    def savePreferences(self):
        """
        Saves QEMU preferences.
        """

        new_settings = {}
        new_settings["use_local_server"] = self.uiUseLocalServercheckBox.isChecked()
        Qemu.instance().setSettings(new_settings)
