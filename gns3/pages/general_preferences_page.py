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
Configuration page for general preferences.
"""

import os
import shutil
import json

from gns3.qt import QtGui, QtCore, QtWidgets
from gns3.local_config import LocalConfig
from ..ui.general_preferences_page_ui import Ui_GeneralPreferencesPageWidget
from gns3.local_server import LocalServer
from ..settings import GRAPHICS_VIEW_SETTINGS, GENERAL_SETTINGS, STYLES, SYMBOL_THEMES
from ..dialogs.console_command_dialog import ConsoleCommandDialog


class GeneralPreferencesPage(QtWidgets.QWidget, Ui_GeneralPreferencesPageWidget):

    """
    QWidget configuration page for general preferences.
    """

    def __init__(self, parent=None):

        super().__init__()
        self.setupUi(self)
        self._remote_servers = {}
        self._preferences_dialog = parent

        # Display the path of the config file
        config_file_path = LocalConfig.instance().configFilePath()
        self.uiConfigurationFileLabel.setText(config_file_path)

        self.uiProjectsPathToolButton.clicked.connect(self._projectsPathSlot)
        self.uiSymbolsPathToolButton.clicked.connect(self._symbolsPathSlot)
        self.uiImagesPathToolButton.clicked.connect(self._imagesPathSlot)
        self.uiConfigsPathToolButton.clicked.connect(self._configsPathSlot)
        self.uiAppliancesPathToolButton.clicked.connect(self._appliancesPathSlot)
        self.uiImportConfigurationFilePushButton.clicked.connect(self._importConfigurationFileSlot)
        self.uiExportConfigurationFilePushButton.clicked.connect(self._exportConfigurationFileSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiTelnetConsolePreconfiguredCommandPushButton.clicked.connect(self._telnetConsolePreconfiguredCommandSlot)
        self.uiVNCConsolePreconfiguredCommandPushButton.clicked.connect(self._vncConsolePreconfiguredCommandSlot)
        self.uiSPICEConsolePreconfiguredCommandPushButton.clicked.connect(self._spiceConsolePreconfiguredCommandSlot)
        self.uiDefaultLabelFontPushButton.clicked.connect(self._setDefaultLabelFontSlot)
        self.uiDefaultLabelColorPushButton.clicked.connect(self._setDefaultLabelColorSlot)
        self.uiDefaultNoteFontPushButton.clicked.connect(self._setDefaultNoteFontSlot)
        self.uiDefaultNoteColorPushButton.clicked.connect(self._setDefaultNoteColorSlot)
        self.uiBrowseConfigurationPushButton.clicked.connect(self._browseConfigurationDirectorySlot)
        self._default_label_color = QtGui.QColor(QtCore.Qt.black)
        self.uiStyleComboBox.addItems(STYLES)
        self.uiSymbolThemeComboBox.addItems(SYMBOL_THEMES)
        self.uiImageDirectoriesAddPushButton.clicked.connect(self._imageDirectoriesAddPushButtonSlot)
        self.uiImageDirectoriesDeletePushButton.clicked.connect(self._imageDirectoriesDeletePushButtonSlot)

    def _imageDirectoriesAddPushButtonSlot(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "My images directory", options=QtWidgets.QFileDialog.ShowDirsOnly)
        if path:
            if self.uiImageDirectoriesListWidget.findItems(path, QtCore.Qt.MatchFixedString):
                QtWidgets.QMessageBox.critical(self, "Images directory", "This directory has already been added")
                return
            count = 0
            for _, _, files in os.walk(path):
                count += len(files)
                if count > 10000:
                    QtWidgets.QMessageBox.warning(self, "Images directory", "This directory contains a lot of files, the scan process could consume a lot of resources")
                    break
            self.uiImageDirectoriesListWidget.addItem(path)

    def _imageDirectoriesDeletePushButtonSlot(self):
        item = self.uiImageDirectoriesListWidget.currentItem()
        if item:
            self.uiImageDirectoriesListWidget.takeItem(self.uiImageDirectoriesListWidget.currentRow())

    def _projectsPathSlot(self):
        """
        Slot to select the projects directory path.
        """

        local_server = LocalServer.instance().localServerSettings()
        directory = local_server["projects_path"]
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "My projects directory", directory, QtWidgets.QFileDialog.ShowDirsOnly)
        if path:
            self.uiProjectsPathLineEdit.setText(path)
            self.uiProjectsPathLineEdit.setCursorPosition(0)

    def _symbolsPathSlot(self):
        """
        Slot to select the symbols directory path.
        """

        local_server = LocalServer.instance().localServerSettings()
        directory = local_server["symbols_path"]
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "My symbols directory", directory, QtWidgets.QFileDialog.ShowDirsOnly)
        if path:
            self.uiSymbolsPathLineEdit.setText(path)
            self.uiSymbolsPathLineEdit.setCursorPosition(0)

    def _imagesPathSlot(self):
        """
        Slot to select the images directory path.
        """

        local_server = LocalServer.instance().localServerSettings()
        directory = local_server["images_path"]
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "My images directory", directory, QtWidgets.QFileDialog.ShowDirsOnly)
        if path:
            self.uiImagesPathLineEdit.setText(path)
            self.uiImagesPathLineEdit.setCursorPosition(0)

    def _configsPathSlot(self):
        """
        Slot to select the configs directory path.
        """

        local_server = LocalServer.instance().localServerSettings()
        directory = local_server["configs_path"]
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "My configs directory", directory, QtWidgets.QFileDialog.ShowDirsOnly)
        if path:
            self.uiConfigsPathLineEdit.setText(path)
            self.uiConfigsPathLineEdit.setCursorPosition(0)

    def _appliancesPathSlot(self):
        """
        Slot to select the appliances directory path.
        """

        local_server = LocalServer.instance().localServerSettings()
        directory = local_server["appliances_path"]
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "My custom appliances directory", directory, QtWidgets.QFileDialog.ShowDirsOnly)
        if path:
            self.uiAppliancesPathLineEdit.setText(path)
            self.uiAppliancesPathLineEdit.setCursorPosition(0)

    def _restoreDefaultsSlot(self):
        """
        Slot to restore default settings
        """

        self._populateGeneralSettingWidgets(GENERAL_SETTINGS)
        self._populateGraphicsViewSettingWidgets(GRAPHICS_VIEW_SETTINGS)

    def _telnetConsolePreconfiguredCommandSlot(self):
        """
        Slot to set a chosen pre-configured Telnet console command.
        """

        cmd = self.uiTelnetConsoleCommandLineEdit.text()
        (ok, cmd) = ConsoleCommandDialog.getCommand(self, console_type="telnet", current=cmd)
        if ok:
            self.uiTelnetConsoleCommandLineEdit.setText(cmd)

    def _vncConsolePreconfiguredCommandSlot(self):
        """
        Slot to set a chosen pre-configured VNC console command.
        """

        cmd = self.uiVNCConsoleCommandLineEdit.text()
        (ok, cmd) = ConsoleCommandDialog.getCommand(self, console_type="vnc", current=cmd)
        if ok:
            self.uiVNCConsoleCommandLineEdit.setText(cmd)

    def _spiceConsolePreconfiguredCommandSlot(self):
        """
        Slot to set a chosen pre-configured SPICE console command.
        """

        cmd = self.uiSPICEConsoleCommandLineEdit.text()
        (ok, cmd) = ConsoleCommandDialog.getCommand(self, console_type="spice", current=cmd)
        if ok:
            self.uiSPICEConsoleCommandLineEdit.setText(cmd)

    def _importConfigurationFileSlot(self):
        """
        Slot to import a configuration file.
        """

        configuration_file_path = LocalConfig.instance().configFilePath()
        directory = os.path.dirname(configuration_file_path)

        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import configuration file", directory, "Configuration file (*.ini *.conf);;All files (*.*)")
        if not path:
            return

        try:
            with open(path, encoding="utf-8") as f:
                config_file = json.load(f)
            if "type" not in config_file or config_file["type"] != "settings":
                QtWidgets.QMessageBox.critical(self, "Import configuration file", "Not a GNS3 configuration file: {}".format(path))
                return
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "Import configuration file", "Could not load configuration file {}: {}".format(os.path.basename(path), e))
            return
        except (ValueError, TypeError) as e:
            QtWidgets.QMessageBox.critical(self, "Import configuration file", "Invalid file: {}".format(e))
            return

        try:
            shutil.copyfile(path, configuration_file_path)
        except (shutil.Error, IOError) as e:
            QtWidgets.QMessageBox.critical(self, "Import configuration file", "Cannot import configuration file: {}".format(e))
            return

        QtWidgets.QMessageBox.information(self, "Configuration file", "Configuration file imported, default settings will be applied after a restart")

        # TODO: implement restart
        # QtCore.QProcess.startDetached(QtWidgets.QApplication.arguments()[0], QtWidgets.QApplication.arguments())
        # QtWidgets.QApplication.quit()
        LocalConfig.instance().setConfigFilePath(configuration_file_path)
        self._preferences_dialog.reject()

    def _browseConfigurationDirectorySlot(self):
        """
        Slot to open a file browser into the configuration directory
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("file://" + LocalConfig.instance().configDirectory()))

    def _exportConfigurationFileSlot(self):
        """
        Slot to export a configuration file.
        """

        configuration_file_path = LocalConfig.instance().configFilePath()
        directory = os.path.dirname(configuration_file_path)

        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export configuration file", directory, "Configuration file (*.ini *.conf);;All files (*.*)")
        if not path:
            return

        try:
            shutil.copyfile(configuration_file_path, path)
        except (shutil.Error, IOError) as e:
            QtWidgets.QMessageBox.critical(self, "Export configuration file", "Cannot export configuration file: {}".format(e))
            return

    def _setDefaultLabelFontSlot(self):
        """
        Slot to select the default label font.
        """

        selected_font, ok = QtWidgets.QFontDialog.getFont(self.uiDefaultLabelStylePlainTextEdit.font(), self)
        if ok:
            self.uiDefaultLabelStylePlainTextEdit.setFont(selected_font)

    def _setDefaultLabelColorSlot(self):
        """
        Slot to select the default label color.
        """

        color = QtWidgets.QColorDialog.getColor(self._default_label_color, self)
        if color.isValid():
            self._default_label_color = color
            self.uiDefaultLabelStylePlainTextEdit.setStyleSheet("color : {}".format(color.name()))

    def _setDefaultNoteFontSlot(self):
        """
        Slot to select the default note font.
        """

        selected_font, ok = QtWidgets.QFontDialog.getFont(self.uiDefaultNoteStylePlainTextEdit.font(), self)
        if ok:
            self.uiDefaultNoteStylePlainTextEdit.setFont(selected_font)

    def _setDefaultNoteColorSlot(self):
        """
        Slot to select the default note color.
        """

        color = QtWidgets.QColorDialog.getColor(self._default_note_color, self)
        if color.isValid():
            self._default_note_color = color
            self.uiDefaultNoteStylePlainTextEdit.setStyleSheet("color : {}".format(color.name()))

    def _populateGeneralSettingWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: General settings
        """

        local_server = LocalServer.instance().localServerSettings()
        self.uiProjectsPathLineEdit.setText(local_server["projects_path"])
        self.uiSymbolsPathLineEdit.setText(local_server["symbols_path"])
        self.uiImagesPathLineEdit.setText(local_server["images_path"])
        self.uiConfigsPathLineEdit.setText(local_server["configs_path"])
        self.uiAppliancesPathLineEdit.setText(local_server["appliances_path"])
        self.uiStatsCheckBox.setChecked(settings["send_stats"])
        self.uiOverlayNotificationsCheckBox.setChecked(settings["overlay_notifications"])
        self.uiCrashReportCheckBox.setChecked(local_server["report_errors"])
        self.uiCheckForUpdateCheckBox.setChecked(settings["check_for_update"])
        self.uiExperimentalFeaturesCheckBox.setChecked(settings["experimental_features"])
        self.uiHdpiCheckBox.setChecked(settings["hdpi"])
        self.uiTelnetConsoleCommandLineEdit.setText(settings["telnet_console_command"])
        self.uiTelnetConsoleCommandLineEdit.setCursorPosition(0)

        index = self.uiStyleComboBox.findText(settings["style"])
        if index != -1:
            self.uiStyleComboBox.setCurrentIndex(index)

        index = self.uiSymbolThemeComboBox.findText(settings["symbol_theme"])
        if index != -1:
            self.uiSymbolThemeComboBox.setCurrentIndex(index)

        self.uiDelayConsoleAllSpinBox.setValue(settings["delay_console_all"])

        self.uiVNCConsoleCommandLineEdit.setText(settings["vnc_console_command"])
        self.uiVNCConsoleCommandLineEdit.setCursorPosition(0)

        self.uiSPICEConsoleCommandLineEdit.setText(settings["spice_console_command"])
        self.uiSPICEConsoleCommandLineEdit.setCursorPosition(0)

        self.uiMultiProfilesCheckBox.setChecked(settings["multi_profiles"])

        self.uiImageDirectoriesListWidget.clear()
        for path in local_server["additional_images_paths"].split(";"):
            if len(path) > 0:
                self.uiImageDirectoriesListWidget.addItem(path)

        self.uiDirectFileUpload.setChecked(settings["direct_file_upload"])

    def _populateGraphicsViewSettingWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: Graphics view settings
        """

        self.uiSceneWidthSpinBox.setValue(settings["scene_width"])
        self.uiSceneHeightSpinBox.setValue(settings["scene_height"])
        self.uiNodeGridSizeSpinBox.setValue(settings["grid_size"])
        self.uiDrawingGridSizeSpinBox.setValue(settings["drawing_grid_size"])
        self.uiRectangleSelectedItemCheckBox.setChecked(settings["draw_rectangle_selected_item"])
        self.uiDrawLinkStatusPointsCheckBox.setChecked(settings["draw_link_status_points"])
        self.uiShowInterfaceLabelsOnNewProject.setChecked(settings["show_interface_labels_on_new_project"])
        self.uiLimitSizeNodeSymbolCheckBox.setChecked(settings["limit_size_node_symbols"])
        self.uiShowGridOnNewProject.setChecked(settings["show_grid_on_new_project"])
        self.uiSnapToGridOnNewProject.setChecked(settings["snap_to_grid_on_new_project"])

        qt_font = QtGui.QFont()
        if qt_font.fromString(settings["default_label_font"]):
            self.uiDefaultLabelStylePlainTextEdit.setFont(qt_font)
        qt_color = QtGui.QColor(settings["default_label_color"])
        if qt_color.isValid():
            self._default_label_color = qt_color
            self.uiDefaultLabelStylePlainTextEdit.setStyleSheet("color : {}".format(qt_color.name()))

        qt_font = QtGui.QFont()
        if qt_font.fromString(settings["default_note_font"]):
            self.uiDefaultNoteStylePlainTextEdit.setFont(qt_font)
        qt_color = QtGui.QColor(settings["default_note_color"])
        if qt_color.isValid():
            self._default_note_color = qt_color
            self.uiDefaultNoteStylePlainTextEdit.setStyleSheet("color : {}".format(qt_color.name()))

    def loadPreferences(self):
        """
        Loads the general preferences.
        """

        from ..main_window import MainWindow
        general_settings = MainWindow.instance().settings()
        self._populateGeneralSettingWidgets(general_settings)

        graphics_view_settings = MainWindow.instance().uiGraphicsView.settings()
        self._populateGraphicsViewSettingWidgets(graphics_view_settings)

    def savePreferences(self):
        """
        Saves the general preferences.
        """

        additional_images_paths = set()
        for i in range(0, self.uiImageDirectoriesListWidget.count()):
            item = self.uiImageDirectoriesListWidget.item(i)
            additional_images_paths.add(item.text())

        new_local_server_settings = {"images_path": self.uiImagesPathLineEdit.text(),
                                     "projects_path": self.uiProjectsPathLineEdit.text(),
                                     "symbols_path": self.uiSymbolsPathLineEdit.text(),
                                     "configs_path": self.uiConfigsPathLineEdit.text(),
                                     "appliances_path": self.uiAppliancesPathLineEdit.text(),
                                     "report_errors": self.uiCrashReportCheckBox.isChecked(),
                                     "additional_images_paths": ":".join(additional_images_paths)}
        LocalServer.instance().updateLocalServerSettings(new_local_server_settings)

        new_general_settings = {
            "style": self.uiStyleComboBox.currentText(),
            "symbol_theme": self.uiSymbolThemeComboBox.currentText(),
            "experimental_features": self.uiExperimentalFeaturesCheckBox.isChecked(),
            "hdpi": self.uiHdpiCheckBox.isChecked(),
            "check_for_update": self.uiCheckForUpdateCheckBox.isChecked(),
            "overlay_notifications": self.uiOverlayNotificationsCheckBox.isChecked(),
            "telnet_console_command": self.uiTelnetConsoleCommandLineEdit.text(),
            "vnc_console_command": self.uiVNCConsoleCommandLineEdit.text(),
            "spice_console_command": self.uiSPICEConsoleCommandLineEdit.text(),
            "delay_console_all": self.uiDelayConsoleAllSpinBox.value(),
            "send_stats": self.uiStatsCheckBox.isChecked(),
            "multi_profiles": self.uiMultiProfilesCheckBox.isChecked(),
            "direct_file_upload": self.uiDirectFileUpload.isChecked()
        }

        from ..main_window import MainWindow
        MainWindow.instance().setSettings(new_general_settings)

        new_graphics_view_settings = {"scene_width": self.uiSceneWidthSpinBox.value(),
                                      "scene_height": self.uiSceneHeightSpinBox.value(),
                                      "draw_rectangle_selected_item": self.uiRectangleSelectedItemCheckBox.isChecked(),
                                      "draw_link_status_points": self.uiDrawLinkStatusPointsCheckBox.isChecked(),
                                      "show_interface_labels_on_new_project": self.uiShowInterfaceLabelsOnNewProject.isChecked(),
                                      "limit_size_node_symbols": self.uiLimitSizeNodeSymbolCheckBox.isChecked(),
                                      "show_grid_on_new_project": self.uiShowGridOnNewProject.isChecked(),
                                      "snap_to_grid_on_new_project": self.uiSnapToGridOnNewProject.isChecked(),
                                      "default_label_font": self.uiDefaultLabelStylePlainTextEdit.font().toString(),
                                      "default_label_color": self._default_label_color.name(),
                                      "default_note_font": self.uiDefaultNoteStylePlainTextEdit.font().toString(),
                                      "default_note_color": self._default_note_color.name()}

        node_grid_size = self.uiNodeGridSizeSpinBox.value()
        drawing_grid_size = self.uiDrawingGridSizeSpinBox.value()
        if node_grid_size % drawing_grid_size != 0:
            QtWidgets.QMessageBox.critical(self, "Grid sizes", "Invalid grid sizes which will create overlapping lines")
        else:
            new_graphics_view_settings["grid_size"] = node_grid_size
            new_graphics_view_settings["drawing_grid_size"] = drawing_grid_size
        MainWindow.instance().uiGraphicsView.setSettings(new_graphics_view_settings)
