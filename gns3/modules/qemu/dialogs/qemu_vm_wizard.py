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
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/qemu_guest.svg"))

        # Mandatory fields
        self.uiNameWizardPage.registerField("vm_name*", self.uiNameLineEdit)
        self.uiInitrdKernelImageWizardPage.registerField("initrd*", self.uiInitrdImageLineEdit)
        self.uiInitrdKernelImageWizardPage.registerField("kernel_image*", self.uiKernelImageLineEdit)

        # Fill image combo boxes
        self.addImageSelector(self.uiHdaDiskExistingImageRadioButton, self.uiHdaDiskImageListComboBox, self.uiHdaDiskImageLineEdit, self.uiHdaDiskImageToolButton, QemuVMConfigurationPage.getDiskImage, create_image_wizard=QemuImageWizard, create_button=self.uiHdaDiskImageCreateToolButton, image_suffix="-hda")
        self.addImageSelector(self.uiLinuxExistingImageRadioButton, self.uiInitrdImageListComboBox, self.uiInitrdImageLineEdit, self.uiInitrdImageToolButton, QemuVMConfigurationPage.getDiskImage)
        self.addImageSelector(self.uiLinuxExistingImageRadioButton, self.uiKernelImageListComboBox, self.uiKernelImageLineEdit, self.uiKernelImageToolButton, QemuVMConfigurationPage.getDiskImage)

    def initializePage(self, page_id):

        super().initializePage(page_id)

        if self.currentPage() == self.uiNameWizardPage:
            if self.uiLocalRadioButton.isChecked() and not ComputeManager.instance().localPlatform().startswith("linux"):
                QtWidgets.QMessageBox.warning(self, "QEMU on Windows or Mac", "The recommended way to run QEMU on Windows and OSX is to use the GNS3 VM")

        if self.page(page_id) in [self.uiDiskWizardPage, self.uiInitrdKernelImageWizardPage]:
            self.loadImagesList("qemu")
        elif self.page(page_id) == self.uiPlatformMemoryWizardPage:
            platforms = Qemu.getQemuPlatforms()
            self.uiQemuPlatformComboBox.addItems(platforms)
            index = self.uiQemuPlatformComboBox.findText("x86_64", flags=QtCore.Qt.MatchEndsWith)
            if index != -1:
                self.uiQemuPlatformComboBox.setCurrentIndex(index)

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        console_type = self.uiQemuConsoleTypeComboBox.itemText(self.uiQemuConsoleTypeComboBox.currentIndex())
        qemu_platform = self.uiQemuPlatformComboBox.itemText(self.uiQemuPlatformComboBox.currentIndex())
        settings = {
            "name": self.uiNameLineEdit.text(),
            "ram": self.uiRamSpinBox.value(),
            "platform": qemu_platform,
            "compute_id": self._compute_id,
            "category": Node.end_devices,
            "console_type": console_type
        }

        if self.uiHdaDiskImageLineEdit.text().strip():
            settings["hda_disk_image"] = self.uiHdaDiskImageLineEdit.text().strip()
            settings["hda_disk_interface"] = "ide"

        if "options" not in settings:
            settings["options"] = ""
        settings["options"] = settings["options"].strip()

        return settings

    def nextId(self):
        """
        Wizard rules!
        """

        current_id = self.currentId()
        if self.page(current_id) == self.uiDiskWizardPage:
            return -1
        elif self.page(current_id) == self.uiInitrdKernelImageWizardPage:
            return -1
        return QtWidgets.QWizard.nextId(self)
