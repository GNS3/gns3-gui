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

from gns3.qt import QtWidgets
from .. import Qemu
from ..ui.qemu_preferences_page_ui import Ui_QemuPreferencesPageWidget
from ..settings import QEMU_SETTINGS


class QemuPreferencesPage(QtWidgets.QWidget, Ui_QemuPreferencesPageWidget):
    """
    QWidget preference page for QEMU.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        # connect signals
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiEnableHardwareAccelerationCheckBox.stateChanged.connect(self._hardwareAccelerationSlot)

    def _hardwareAccelerationSlot(self, state):
        """
        Slot to enable or not the require KVM acceleration check box.
        """

        if state:
            self.uiRequireHardwareAccelerationCheckBox.setEnabled(True)
            self.uiRequireHardwareAccelerationCheckBox.setChecked(True)
        else:
            self.uiRequireHardwareAccelerationCheckBox.setEnabled(False)
            self.uiRequireHardwareAccelerationCheckBox.setChecked(False)

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

        self.uiEnableHardwareAccelerationCheckBox.setChecked(settings["enable_hardware_acceleration"])
        self.uiRequireHardwareAccelerationCheckBox.setChecked(settings["require_hardware_acceleration"])

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

        new_settings = {"enable_hardware_acceleration": self.uiEnableHardwareAccelerationCheckBox.isChecked(),
                        "require_hardware_acceleration": self.uiRequireHardwareAccelerationCheckBox.isChecked()}
        Qemu.instance().setSettings(new_settings)
