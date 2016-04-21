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
Configuration page for packet capture preferences.
"""

import sys
import struct

from gns3.qt import QtCore, QtWidgets
from ..ui.packet_capture_preferences_page_ui import Ui_PacketCapturePreferencesPageWidget
from ..settings import PACKET_CAPTURE_SETTINGS, PRECONFIGURED_PACKET_CAPTURE_READER_COMMANDS
from ..local_config import LocalConfig


class PacketCapturePreferencesPage(QtWidgets.QWidget, Ui_PacketCapturePreferencesPageWidget):

    """
    QWidget configuration page for packet capture preferences.
    """

    def __init__(self, parent=None):

        super().__init__()
        self.setupUi(self)

        # Load the pre-configured capture reader commands
        for name, cmd in sorted(PRECONFIGURED_PACKET_CAPTURE_READER_COMMANDS.items()):
            self.uiPreconfiguredCaptureReaderCommandComboBox.addItem(name, cmd)

        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiPreconfiguredCaptureReaderCommandPushButton.clicked.connect(self._preconfiguredCaptureReaderCommandSlot)

        if not sys.platform.startswith("win") and not struct.calcsize("P") * 8 == 64:
            # packet analyzer not support on other platform than Windows 64-bit
            self.uiCaptureAnalyzerCommandLabel.hide()
            self.uiCaptureAnalyzerCommandLineEdit.hide()

    def _restoreDefaultsSlot(self):
        """
        Slot to restore default settings
        """

        self._populatePacketCaptureSettingWiddgets(PACKET_CAPTURE_SETTINGS)

    def _preconfiguredCaptureReaderCommandSlot(self):
        """
        Slot to set a chosen pre-configured packet capture reader command.
        """

        self.uiCaptureReaderCommandLineEdit.clear()
        command = self.uiPreconfiguredCaptureReaderCommandComboBox.itemData(self.uiPreconfiguredCaptureReaderCommandComboBox.currentIndex(), QtCore.Qt.UserRole)
        self.uiCaptureReaderCommandLineEdit.setText(command)
        self.uiCaptureReaderCommandLineEdit.setCursorPosition(0)

    def _populatePacketCaptureSettingWiddgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: packet capture settings
        """

        self.uiCaptureReaderCommandLineEdit.setText(settings["packet_capture_reader_command"])
        self.uiCaptureReaderCommandLineEdit.setCursorPosition(0)
        index = self.uiPreconfiguredCaptureReaderCommandComboBox.findData(settings["packet_capture_reader_command"])
        if index != -1:
            self.uiPreconfiguredCaptureReaderCommandComboBox.setCurrentIndex(index)
        self.uiAutoStartCheckBox.setChecked(settings["command_auto_start"])
        self.uiCaptureAnalyzerCommandLineEdit.setText(settings["packet_capture_analyzer_command"])
        self.uiCaptureAnalyzerCommandLineEdit.setCursorPosition(0)

    def loadPreferences(self):
        """
        Loads the packet capture preferences.
        """

        self._populatePacketCaptureSettingWiddgets(LocalConfig.instance().loadSectionSettings("PacketCapture", PACKET_CAPTURE_SETTINGS))

    def savePreferences(self):
        """
        Saves the packet capture preferences.
        """

        new_settings = {"packet_capture_reader_command": self.uiCaptureReaderCommandLineEdit.text(),
                        "command_auto_start": self.uiAutoStartCheckBox.isChecked(),
                        "packet_capture_analyzer_command": self.uiCaptureAnalyzerCommandLineEdit.text()}
        LocalConfig.instance().saveSectionSettings("PacketCapture", new_settings)
