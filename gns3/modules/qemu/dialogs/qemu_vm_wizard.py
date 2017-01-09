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
        self.uiInitrdKernelImageWizardPage.registerField("initrd*", self.uiInitrdImageLineEdit)
        self.uiInitrdKernelImageWizardPage.registerField("kernel_image*", self.uiKernelImageLineEdit)

        # Fill image combo boxes
        self.addImageSelector(self.uiHdaDiskExistingImageRadioButton, self.uiHdaDiskImageListComboBox, self.uiHdaDiskImageLineEdit, self.uiHdaDiskImageToolButton, QemuVMConfigurationPage.getDiskImage, create_image_wizard=QemuImageWizard, create_button=self.uiHdaDiskImageCreateToolButton, image_suffix="-hda")
        self.addImageSelector(self.uiLinuxExistingImageRadioButton, self.uiInitrdImageListComboBox, self.uiInitrdImageLineEdit, self.uiInitrdImageToolButton, QemuVMConfigurationPage.getDiskImage)
        self.addImageSelector(self.uiLinuxExistingImageRadioButton, self.uiKernelImageListComboBox, self.uiKernelImageLineEdit, self.uiKernelImageToolButton, QemuVMConfigurationPage.getDiskImage)

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        if super().validateCurrentPage() is False:
            return False

        if self.currentPage() == self.uiNameWizardPage:
            if self.uiLegacyASACheckBox.isChecked():
                QtWidgets.QMessageBox.warning(self, "Legacy ASA VM", "Running ASA (with initrd/kernel) is not recommended and will not work on Windows 10, please use ASAv instead")
                self.uiRamSpinBox.setValue(1024)
            else:
                self.uiRamSpinBox.setValue(256)

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

        if self.page(page_id) in [self.uiDiskWizardPage, self.uiInitrdKernelImageWizardPage]:
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
                if self.uiLegacyASACheckBox.isChecked():
                    search_string = r"qemu-0.13.0\qemu-system-i386w.exe"
                elif is_64bit:
                    # default is qemu-system-x86_64w.exe on Windows 64-bit with a remote server
                    search_string = "x86_64w.exe"
                else:
                    # default is qemu-system-i386w.exe on Windows 32-bit with a remote server
                    search_string = "i386w.exe"
            elif ComputeManager.instance().localPlatform().startswith("darwin") and hasattr(sys, "frozen") and self.uiLocalRadioButton.isChecked():
                search_string = "GNS3.app/Contents/Resources/qemu/bin/qemu-system-x86_64"
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
            "server": self._compute_id,
            "category": Node.end_devices,
            "hda_disk_image": self.uiHdaDiskImageLineEdit.text(),
            "console_type": console_type
        }

        if self.uiLegacyASACheckBox.isChecked():
            # special settings for legacy ASA VM
            settings["adapters"] = 4
            settings["initrd"] = self.uiInitrdImageLineEdit.text()
            settings["kernel_image"] = self.uiKernelImageLineEdit.text()
            settings["kernel_command_line"] = "ide_generic.probe_mask=0x01 ide_core.chs=0.0:980,16,32 auto nousb console=ttyS0,9600 bigphysarea=65536 ide1=noprobe no-hlt -net nic"
            settings["options"] = "-no-kvm -icount auto -hdachs 980,16,32"
            if not sys.platform.startswith("darwin"):
                settings["cpu_throttling"] = 80  # limit to 80% CPU usage
            settings["process_priority"] = "low"
            settings["symbol"] = ":/symbols/asa.svg"
            settings["category"] = Node.security_devices

        if "options" not in settings:
            settings["options"] = ""
        if self._compute_id == "local" and (sys.platform.startswith("win") and qemu_path.endswith(r"qemu-0.11.0\qemu.exe")) or \
                (sys.platform.startswith("darwin") and "GNS3.app" in qemu_path):
            settings["options"] += " -vga none -vnc none"
            settings["legacy_networking"] = True
        else:
            settings["options"] += " -nographic"
        settings["options"] = settings["options"].strip()

        return settings

    def nextId(self):
        """
        Wizard rules!
        """

        current_id = self.currentId()
        if self.page(current_id) == self.uiDiskWizardPage:
            if self.uiLegacyASACheckBox.isChecked():
                return self.uiDiskWizardPage.nextId()
            return -1
        elif self.page(current_id) == self.uiInitrdKernelImageWizardPage:
            return -1
        return QtWidgets.QWizard.nextId(self)
