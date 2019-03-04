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
Wizard for QEMU VMs.
"""

import sys

from gns3.qt import QtCore, QtGui, QtWidgets
from gns3.node import Node
from gns3.modules.module_error import ModuleError
from gns3.dialogs.vm_with_images_wizard import VMWithImagesWizard
from gns3.compute_manager import ComputeManager

from .. import Qemu
from ..ui.qemu_vm_wizard_ui import Ui_QemuVMWizard
from ..pages.qemu_vm_configuration_page import QemuVMConfigurationPage
from .qemu_image_wizard import QemuImageWizard


class QemuVMWizard(VMWithImagesWizard, Ui_QemuVMWizard):
    """
    Wizard to create a Qemu VM.

    :param parent: parent widget
    """

    def __init__(self, qemu_vms, parent):

        super().__init__(qemu_vms, parent)
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/icons/qemu.svg"))

        # Mandatory fields
        self.uiNameWizardPage.registerField("vm_name*", self.uiNameLineEdit)
        self.uiDiskWizardPage.registerField("hda_disk_image*", self.uiHdaDiskImageLineEdit)

        # Fill image combo boxes
        self.addImageSelector(self.uiHdaDiskExistingImageRadioButton, self.uiHdaDiskImageListComboBox, self.uiHdaDiskImageLineEdit, self.uiHdaDiskImageToolButton, QemuVMConfigurationPage.getDiskImage, create_image_wizard=QemuImageWizard, create_button=self.uiHdaDiskImageCreateToolButton, image_suffix="-hda")

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        if super().validateCurrentPage() is False:
            return False

        if self.currentPage() == self.uiNameWizardPage:
            self.uiRamSpinBox.setValue(512)

        if self.currentPage() == self.uiBinaryMemoryWizardPage:
            if not self.uiQemuListComboBox.count():
                QtWidgets.QMessageBox.critical(self, "QEMU binaries", "Sorry, no QEMU binary has been found. Please make sure QEMU is installed before continuing")
                return False
            qemu_path = self.uiQemuListComboBox.itemData(self.uiQemuListComboBox.currentIndex())

            if sys.platform.startswith("darwin") and "GNS3.app" in qemu_path:
                QtWidgets.QMessageBox.warning(self, "Qemu binaries", "This version of qemu is obsolete and provided only for compatibility with old GNS3 versions.\nPlease use Qemu in the GNS3 VM for full Qemu support.")
        return True

    def initializePage(self, page_id):

        super().initializePage(page_id)

        if self.currentPage() == self.uiNameWizardPage:
            if self.uiLocalRadioButton.isChecked() and not ComputeManager.instance().localPlatform().startswith("linux"):
                QtWidgets.QMessageBox.warning(self, "QEMU on Windows or Mac", "The recommended way to run QEMU on Windows and OSX is to use the GNS3 VM")

        if self.page(page_id) == self.uiDiskWizardPage:
            self.loadImagesList("/qemu/images")
        elif self.page(page_id) == self.uiBinaryMemoryWizardPage:
            try:
                Qemu.instance().getQemuBinariesFromServer(self._compute_id, self._getQemuBinariesFromServerCallback)
            except ModuleError as e:
                QtWidgets.QMessageBox.critical(self, "Qemu binaries", "Error while getting the QEMU binaries: {}".format(e))

    def _getQemuBinariesFromServerCallback(self, result, error=False, **kwargs):
        """
        Callback for getQemuBinariesFromServer.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtWidgets.QMessageBox.critical(self, "Qemu binaries", "{}".format(result["message"]))
        else:
            self.uiQemuListComboBox.clear()
            for qemu in result:
                if qemu["version"]:
                    self.uiQemuListComboBox.addItem("{path} (v{version})".format(path=qemu["path"], version=qemu["version"]), qemu["path"])
                else:
                    self.uiQemuListComboBox.addItem("{path}".format(path=qemu["path"]), qemu["path"])

            is_64bit = sys.maxsize > 2 ** 32
            if ComputeManager.instance().localPlatform().startswith("win") and self.uiLocalRadioButton.isChecked():
                if is_64bit:
                    # default is qemu-system-x86_64w.exe on Windows 64-bit with a remote server
                    search_string = "x86_64w.exe"
                else:
                    # default is qemu-system-i386w.exe on Windows 32-bit with a remote server
                    search_string = "i386w.exe"
            elif ComputeManager.instance().localPlatform().startswith("darwin") and hasattr(sys, "frozen") and self.uiLocalRadioButton.isChecked():
                search_string = "GNS3.app/Contents/MacOS/qemu/bin/qemu-system-x86_64"
            elif is_64bit:
                # default is qemu-system-x86_64 on other 64-bit platforms
                search_string = "x86_64"
            else:
                # default is qemu-system-i386 on other platforms
                search_string = "i386"

            index = self.uiQemuListComboBox.findData(search_string, flags=QtCore.Qt.MatchEndsWith)
            if index != -1:
                self.uiQemuListComboBox.setCurrentIndex(index)

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        console_type = self.uiQemuConsoleTypeComboBox.itemText(self.uiQemuConsoleTypeComboBox.currentIndex())
        qemu_path = self.uiQemuListComboBox.itemData(self.uiQemuListComboBox.currentIndex())
        settings = {
            "name": self.uiNameLineEdit.text(),
            "ram": self.uiRamSpinBox.value(),
            "qemu_path": qemu_path,
            "compute_id": self._compute_id,
            "category": Node.end_devices,
            "hda_disk_image": self.uiHdaDiskImageLineEdit.text(),
            "console_type": console_type,
            "options": ""
        }

        return settings
