# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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
Configuration page for VMware preferences.
"""

import os
import sys
import shutil
from gns3.qt import QtWidgets
from gns3.utils.sudo import sudo

from .. import VMware
from ..ui.vmware_preferences_page_ui import Ui_VMwarePreferencesPageWidget
from ..settings import VMWARE_SETTINGS


class VMwarePreferencesPage(QtWidgets.QWidget, Ui_VMwarePreferencesPageWidget):
    """
    QWidget preference page for VMware.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)

        # connect signals
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiVmrunPathToolButton.clicked.connect(self._vmrunPathBrowserSlot)
        self.uiConfigureVmnetPushButton.clicked.connect(self._configureVmnetSlot)
        self.uiResetVmnetPushButton.clicked.connect(self._resetVmnetSlot)

        if sys.platform.startswith("win"):
            # VMnet limit on Windows is 19
            self.uiVMnetEndRangeSpinBox.setMaximum(19)
        else:
            # VMnet limit on Linux/OSX is 255
            self.uiVMnetEndRangeSpinBox.setMaximum(255)

    def _vmrunPathBrowserSlot(self):
        """
        Slot to open a file browser and select vmrun.
        """

        vmrun_path = shutil.which("vmrun")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select vmrun", vmrun_path)
        if not path:
            return

        if self._checkVmrunPath(path):
            self.uiVmrunPathLineEdit.setText(os.path.normpath(path))

    def _checkVmrunPath(self, path):
        """
        Checks that the vmrun path is valid.

        :param path: vmrun path
        :returns: boolean
        """

        if not os.path.exists(path):
            QtWidgets.QMessageBox.critical(self, "vmrun", '"{}" does not exist'.format(path))
            return False

        if not os.access(path, os.X_OK):
            QtWidgets.QMessageBox.critical(self, "vmrun", "{} is not an executable".format(os.path.basename(path)))
            return False

        return True

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(VMWARE_SETTINGS)

    def _useLocalServerSlot(self, state):
        """
        Slot to enable or not local server settings.
        """

        if state:
            self.uiVmrunPathLineEdit.setEnabled(True)
            self.uiVmrunPathToolButton.setEnabled(True)
            self.uiNetworkTab.setEnabled(True)
        else:
            self.uiVmrunPathLineEdit.setEnabled(False)
            self.uiVmrunPathToolButton.setEnabled(False)
            self.uiNetworkTab.setEnabled(False)

    def _getGNS3Vmnet(self):
        """
        Get the gns3vmnet utility path.
        """

        gns3vmnet = shutil.which("gns3vmnet")
        if gns3vmnet is None:
            QtWidgets.QMessageBox.critical(self, "gns3vmnet", "The gns3vmnet utility is not installed")
            return None
        return gns3vmnet

    def _configureVmnetSlot(self):
        """
        Configure the vmnet interfaces.
        """

        vmnet_start = str(self.uiVMnetStartRangeSpinBox.value())
        vmnet_end = str(self.uiVMnetEndRangeSpinBox.value())
        gns3vmnet = self._getGNS3Vmnet()
        if gns3vmnet is None:
            return
        command = [gns3vmnet, "-r", vmnet_start, vmnet_end]
        sudo(command, parent=self)

    def _resetVmnetSlot(self):
        """
        Deletes all vmnet interface but vmnet1 and vmnet8
        """

        gns3vmnet = self._getGNS3Vmnet()
        if gns3vmnet is None:
            return
        command = [gns3vmnet, "-C"]
        sudo(command, parent=self)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: VMware settings
        """

        self.uiVmrunPathLineEdit.setText(settings["vmrun_path"])
        self.uiVMnetStartRangeSpinBox.setValue(settings["vmnet_start_range"])
        self.uiVMnetEndRangeSpinBox.setValue(settings["vmnet_end_range"])
        self.uiBlockHostTrafficCheckBox.setChecked(settings["block_host_traffic"])

    def loadPreferences(self):
        """
        Loads VMware preferences.
        """

        vmware_settings = VMware.instance().settings()
        self._populateWidgets(vmware_settings)

    def savePreferences(self):
        """
        Saves VMware preferences.
        """

        vmrun_path = self.uiVmrunPathLineEdit.text().strip()
        if vmrun_path and not self._checkVmrunPath(vmrun_path):
            return

        new_settings = {"vmrun_path": vmrun_path,
                        "vmnet_start_range": self.uiVMnetStartRangeSpinBox.value(),
                        "vmnet_end_range": self.uiVMnetEndRangeSpinBox.value(),
                        "block_host_traffic": self.uiBlockHostTrafficCheckBox.isChecked()}
        VMware.instance().setSettings(new_settings)
