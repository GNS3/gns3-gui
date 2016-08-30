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
Configuration page for GNS3 VM
"""

import copy

import logging
log = logging.getLogger(__name__)

from gns3.qt import QtWidgets, QtCore
from gns3.controller import Controller
from ..ui.gns3_vm_preferences_page_ui import Ui_GNS3VMPreferencesPageWidget


class GNS3VMPreferencesPage(QtWidgets.QWidget, Ui_GNS3VMPreferencesPageWidget):

    """
    QWidget configuration page for server preferences.
    """

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self._engines = []
        self._old_settings = None
        self._initialized = False
        self.uiRefreshPushButton.clicked.connect(self._refreshVMSlot)
        self.uiGNS3VMEngineComboBox.currentIndexChanged.connect(self._engineChangedSlot)
        Controller.instance().connected_signal.connect(self.loadPreferences)

    def pageInitialized(self):
        """
        :returns: Boolean True when the preference page is initialized
        """
        return self._initialized

    def _engineChangedSlot(self, index):
        index = self.uiGNS3VMEngineComboBox.currentIndex()
        engine_id = self.uiGNS3VMEngineComboBox.itemData(index, QtCore.Qt.UserRole)
        for engine in self._engines:
            if engine["engine_id"] == engine_id:
                break
        self.uiEngineDescriptionLabel.setText(engine["description"])
        self.uiHeadlessCheckBox.setVisible(engine["support_headless"])
        self.uiShutdownCheckBox.setVisible(engine["support_auto_stop"])
        self._refreshVMSlot()

    def loadPreferences(self):
        """
        Loads the preference from controller.
        """
        Controller.instance().get("/gns3vm", self._getSettingsCallback)

    def _getSettingsCallback(self, result, error=False, **kwargs):
        if error:
            if "message" in result:
                log.error("Error while get gettings: {}".format(result["message"]))
            return
        self._old_settings = copy.copy(result)
        self._settings = result
        self.uiEnableVMCheckBox.setChecked(self._settings["enable"])
        self.uiShutdownCheckBox.setChecked(self._settings["auto_stop"])
        self.uiHeadlessCheckBox.setChecked(self._settings["headless"])
        index = self.uiGNS3VMEngineComboBox.findText(self._settings["vmname"])
        self.uiGNS3VMEngineComboBox.setCurrentIndex(index)
        index = self.uiGNS3VMEngineComboBox.findData(self._settings["engine"])
        self.uiGNS3VMEngineComboBox.setCurrentIndex(index)
        Controller.instance().get("/gns3vm/engines", self._listEnginesCallback)

    def _listEnginesCallback(self, result, error=False, **kwargs):
        self.uiGNS3VMEngineComboBox.clear()
        self._engines = result
        for engine in self._engines:
            self.uiGNS3VMEngineComboBox.addItem(engine["name"], engine["engine_id"])
        index = self.uiGNS3VMEngineComboBox.findData(self._settings["engine"])
        self.uiGNS3VMEngineComboBox.setCurrentIndex(index)

    def _refreshVMSlot(self):
        engine_id = self.uiGNS3VMEngineComboBox.currentData()
        if engine_id:
            Controller.instance().get("/gns3vm/engines/{}/vms".format(engine_id), self._listVMsCallback)

    def _listVMsCallback(self, result, error=False, **kwargs):
        if error:
            if "message" in result:
                log.error("Error while listing vms: {}".format(result["message"]))
            return
        self.uiVMListComboBox.clear()
        for vm in result:
            self.uiVMListComboBox.addItem(vm["vmname"], vm["vmname"])
        self._initialized = True

    def savePreferences(self):
        """
        Saves the preferences on controller.
        """
        if not self._old_settings:
            return

        settings = {
            "enable": self.uiEnableVMCheckBox.isChecked(),
            "vmname": self.uiVMListComboBox.currentData(),
            "auto_stop": self.uiShutdownCheckBox.isChecked(),
            "headless": self.uiHeadlessCheckBox.isChecked(),
            "engine": self.uiGNS3VMEngineComboBox.currentData()
        }
        if self._old_settings != settings:
            Controller.instance().put("/gns3vm", self._saveSettingsCallback, settings)
            self._old_settings = copy.copy(settings)

    def _saveSettingsCallback(self, result, error=False, **kwargs):
        if error:
            if "message" in result:
                log.error("Error while save settings: {}".format(result["message"]))
            return
