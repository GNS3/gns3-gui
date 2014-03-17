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
Configuration page for Dynamips preferences.
"""

from gns3.qt import QtGui
from gns3.servers import Servers
from .. import Dynamips
from ..ui.dynamips_preferences_page_ui import Ui_DynamipsPreferencesPageWidget
from ..settings import DYNAMIPS_SETTINGS


class DynamipsPreferencesPage(QtGui.QWidget, Ui_DynamipsPreferencesPageWidget):
    """
    QWidget preference page for Dynamips.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        # connect signals
        self.uiAllocateHypervisorPerDeviceCheckBox.stateChanged.connect(self._allocateHypervisorPerDeviceSlot)
        self.uiGhostIOSSupportCheckBox.stateChanged.connect(self._ghostIOSSupportSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiUseLocalServercheckBox.stateChanged.connect(self._useLocalServerSlot)

    def _allocateHypervisorPerDeviceSlot(self, state):
        """
        Slot to enable or not the memory usage limit per hypervisor and
        the per IOS allocation, based if the user want one hypervisor per IOS router.

        :param state: state of the allocate hypervisor per device checkBox
        """

        if state:
            self.uiMemoryUsageLimitPerHypervisorSpinBox.setEnabled(False)
            self.uiAllocateHypervisorPerIOSCheckBox.setEnabled(False)
        else:
            self.uiMemoryUsageLimitPerHypervisorSpinBox.setEnabled(True)
            self.uiAllocateHypervisorPerIOSCheckBox.setEnabled(True)

    def _ghostIOSSupportSlot(self, state):
        """
        Slot to have the mmap checkBox checked if ghost IOS is checked.
        Ghost IOS is dependent on the mmap feature.

        :param state: state of the ghost IOS checkBox
        """

        if state:
            self.uiMmapSupportCheckBox.setChecked(True)

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(DYNAMIPS_SETTINGS)

    def _useLocalServerSlot(self, state):
        """
        Slot to enable or not the QTreeWidget for remote servers.
        """

        if state:
            self.uiRemoteServersTreeWidget.setEnabled(False)
        else:
            self.uiRemoteServersTreeWidget.setEnabled(True)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: Dynamips settings
        """

        self.uiDynamipsPathLineEdit.setText(settings["path"])
        self.uiBaseHypervisorPortSpinBox.setValue(settings["base_hypervisor_port"])
        self.uiBaseConsolePortSpinBox.setValue(settings["base_console_port"])
        self.uiBaseAuxPortSpinBox.setValue(settings["base_aux_port"])
        self.uiUseLocalServercheckBox.setChecked(settings["use_local_server"])
        self.uiAllocateHypervisorPerDeviceCheckBox.setChecked(settings["allocate_hypervisor_per_device"])
        self.uiMemoryUsageLimitPerHypervisorSpinBox.setValue(settings["memory_usage_limit_per_hypervisor"])
        self.uiAllocateHypervisorPerIOSCheckBox.setChecked(settings["allocate_hypervisor_per_ios_image"])
        self.uiBaseUDPPortSpinBox.setValue(settings["base_udp_port"])
        self.uiBaseUDPPortIncrementationSpinBox.setValue(settings["udp_incrementation_per_hypervisor"])
        self.uiGhostIOSSupportCheckBox.setChecked(settings["ghost_ios_support"])
        self.uiMmapSupportCheckBox.setChecked(settings["mmap_support"])
        self.uiJITSharingSupportCheckBox.setChecked(settings["jit_sharing_support"])
        self.uiSparseMemorySupportCheckBox.setChecked(settings["sparse_memory_support"])

    def _updateRemoteServersSlot(self):
        """
        Adds/Updates the available remote servers.
        """

        servers = Servers.instance()
        self.uiRemoteServersTreeWidget.clear()
        for server in servers.remoteServers().values():
            host = server.host
            port = server.port
            item = QtGui.QTreeWidgetItem(self.uiRemoteServersTreeWidget)
            item.setText(0, host)
            item.setText(1, str(port))

    def loadPreferences(self):
        """
        Loads the Dynamips preferences.
        """

        dynamips_settings = Dynamips.instance().settings()
        self._populateWidgets(dynamips_settings)

        servers = Servers.instance()
        servers.updated_signal.connect(self._updateRemoteServersSlot)
        self._updateRemoteServersSlot()

    def savePreferences(self):
        """
        Saves the Dynamips preferences.
        """

        new_settings = {}
        new_settings["path"] = self.uiDynamipsPathLineEdit.text()
        new_settings["base_hypervisor_port"] = self.uiBaseHypervisorPortSpinBox.value()
        new_settings["base_console_port"] = self.uiBaseConsolePortSpinBox.value()
        new_settings["base_aux_port"] = self.uiBaseAuxPortSpinBox.value()
        new_settings["use_local_server"] = self.uiUseLocalServercheckBox.isChecked()
        new_settings["allocate_hypervisor_per_device"] = self.uiAllocateHypervisorPerDeviceCheckBox.isChecked()
        new_settings["memory_usage_limit_per_hypervisor"] = self.uiMemoryUsageLimitPerHypervisorSpinBox.value()
        new_settings["allocate_hypervisor_per_ios_image"] = self.uiAllocateHypervisorPerIOSCheckBox.isChecked()
        new_settings["base_udp_port"] = self.uiBaseUDPPortSpinBox.value()
        new_settings["udp_incrementation_per_hypervisor"] = self.uiBaseUDPPortIncrementationSpinBox.value()
        new_settings["ghost_ios_support"] = self.uiGhostIOSSupportCheckBox.isChecked()
        new_settings["mmap_support"] = self.uiMmapSupportCheckBox.isChecked()
        new_settings["jit_sharing_support"] = self.uiJITSharingSupportCheckBox.isChecked()
        new_settings["sparse_memory_support"] = self.uiSparseMemorySupportCheckBox.isChecked()
        Dynamips.instance().setSettings(new_settings)
