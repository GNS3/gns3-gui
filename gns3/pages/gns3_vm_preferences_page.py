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
from gns3.qt import QtWidgets, QtCore, qpartial, qslot, sip_is_deleted
from gns3.controller import Controller
from ..ui.gns3_vm_preferences_page_ui import Ui_GNS3VMPreferencesPageWidget

import logging
log = logging.getLogger(__name__)


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
        self.uiWhenExitKeepRadioButton.setVisible(engine["support_when_exit"])
        self.uiWhenExitSuspendRadioButton.setVisible(engine["support_when_exit"])
        self.uiWhenExitStopRadioButton.setVisible(engine["support_when_exit"])
        self.uiActionCloseLabel.setVisible(engine["support_when_exit"])
        self.uiCpuLabel.setVisible(engine["support_ram"])
        self.uiRamLabel.setVisible(engine["support_ram"])
        self.uiRamSpinBox.setVisible(engine["support_ram"])
        self.uiCpuSpinBox.setVisible(engine["support_ram"])
        self._refreshVMSlot(ignore_error=True)

    def loadPreferences(self):
        """
        Loads the preference from controller.
        """
        Controller.instance().get("/gns3vm", self._getSettingsCallback)

    @qslot
    def _getSettingsCallback(self, result, error=False, **kwargs):

        if sip_is_deleted(self.uiRamSpinBox) or sip_is_deleted(self):
            return
        if error:
            if "message" in result:
                log.error("Error while getting settings : {}".format(result["message"]))
            return
        self._old_settings = copy.copy(result)
        self._settings = result
        self.uiRamSpinBox.setValue(self._settings["ram"])
        self.uiCpuSpinBox.setValue(self._settings["vcpus"])
        self.uiEnableVMCheckBox.setChecked(self._settings["enable"])
        if self._settings["when_exit"] == "keep":
            self.uiWhenExitKeepRadioButton.setChecked(True)
        elif self._settings["when_exit"] == "suspend":
            self.uiWhenExitSuspendRadioButton.setChecked(True)
        else:
            self.uiWhenExitStopRadioButton.setChecked(True)
        self.uiHeadlessCheckBox.setChecked(self._settings["headless"])
        Controller.instance().get("/gns3vm/engines", self._listEnginesCallback)

    @qslot
    def _listEnginesCallback(self, result, error=False, ignore_error=False, **kwargs):

        if sip_is_deleted(self.uiGNS3VMEngineComboBox) or sip_is_deleted(self):
            return

        if error:
            if "message" in result:
                log.error("Error while getting the list of GNS3 VM engines : {}".format(result["message"]))
            return

        self.uiGNS3VMEngineComboBox.clear()
        self._engines = result
        # We insert first the current engine to avoid triggering unexpected signals
        for engine in self._engines:
            if self._settings["engine"] == engine["engine_id"]:
                self.uiGNS3VMEngineComboBox.addItem(engine["name"], engine["engine_id"])
        for engine in self._engines:
            if self._settings["engine"] != engine["engine_id"]:
                self.uiGNS3VMEngineComboBox.addItem(engine["name"], engine["engine_id"])

    @qslot
    def _refreshVMSlot(self, ignore_error=False):
        engine_id = self.uiGNS3VMEngineComboBox.currentData()
        if engine_id:
            Controller.instance().get("/gns3vm/engines/{}/vms".format(engine_id), qpartial(self._listVMsCallback, ignore_error=ignore_error))

    @qslot
    def _listVMsCallback(self, result, ignore_error=False, error=False, **kwargs):
        if error:
            if "message" in result:
                if not ignore_error:
                    QtWidgets.QMessageBox.critical(self, "List vms", "Error while listing vms: {}".format(result["message"]))
            return
        if not sip_is_deleted(self.uiVMListComboBox):
            self.uiVMListComboBox.clear()
            for vm in result:
                self.uiVMListComboBox.addItem(vm["vmname"], vm["vmname"])
            index = self.uiVMListComboBox.findText(self._settings["vmname"])
            if index == -1:
                index = self.uiVMListComboBox.findText("GNS3 VM")
                if index == -1:
                    index = 0
            self.uiVMListComboBox.setCurrentIndex(index)
            self._initialized = True

    def savePreferences(self):
        """
        Saves the preferences on controller.
        """
        if not self._old_settings:
            return

        if self.uiWhenExitKeepRadioButton.isChecked():
            when_exit = "keep"
        elif self.uiWhenExitSuspendRadioButton.isChecked():
            when_exit = "suspend"
        else:
            when_exit = "stop"

        settings = {
            "enable": self.uiEnableVMCheckBox.isChecked(),
            "vmname": self.uiVMListComboBox.currentData(),
            "headless": self.uiHeadlessCheckBox.isChecked(),
            "when_exit": when_exit,
            "engine": self.uiGNS3VMEngineComboBox.currentData(),
            "ram": self.uiRamSpinBox.value(),
            "vcpus": self.uiCpuSpinBox.value()
        }
        if self._old_settings != settings:
            Controller.instance().put("/gns3vm", self._saveSettingsCallback, settings, timeout=60 * 5)
            self._old_settings = copy.copy(settings)

    def _saveSettingsCallback(self, result, error=False, **kwargs):
        if error:
            if "message" in result:
                QtWidgets.QMessageBox.critical(self, "Save settings", "Error while saving settings: {}".format(result["message"]))
            return
