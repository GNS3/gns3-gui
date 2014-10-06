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
Configuration page for QEMU VMs.
"""

import os
import shutil

from gns3.qt import QtCore, QtGui
from gns3.main_window import MainWindow

from ..ui.qemu_vm_wizard_ui import Ui_QemuVMWizard
from .. import Qemu


class QemuVMWizard(QtGui.QWizard, Ui_QemuVMWizard):
    """
    Wizard to create a Qemu VM.

    :param parent: parent widget
    """

    def __init__(self, parent):

        QtGui.QWizard.__init__(self, parent)
        self.setupUi(self)
        self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(":/icons/qemu.svg"))
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.uiHdaDiskImageToolButton.clicked.connect(self._hdaDiskImageBrowserSlot)
        self.uiHdbDiskImageToolButton.clicked.connect(self._hdbDiskImageBrowserSlot)
        self.uiInitrdToolButton.clicked.connect(self._initrdBrowserSlot)
        self.uiKernelImageToolButton.clicked.connect(self._kernelImageBrowserSlot)

        # Available types
        self.uiTypeComboBox.addItems(["Default", "ASA 8.4(2)", "IDS"])

        # Mandatory fields
        self.uiNameTypeWizardPage.registerField("vm_name*", self.uiNameLineEdit)
        self.uiDiskWizardPage.registerField("hda_disk_image*", self.uiHdaDiskImageLineEdit)
        self.uiDiskImageHdbWizardPage.registerField("hdb_disk_image*", self.uiHdbDiskImageLineEdit)
        self.uiASAWizardPage.registerField("initrd*", self.uiInitrdLineEdit)
        self.uiASAWizardPage.registerField("kernel_image*", self.uiKernelImageLineEdit)

        # Wizard pages to IDs
        self._ids = {self.uiNameTypeWizardPage: 0,
                     self.uiBinaryMemoryWizardPage: 1,
                     self.uiDiskWizardPage: 2,
                     self.uiASAWizardPage: 3,
                     self.uiDiskImageHdbWizardPage: 4}

        self.setStartId(self._ids[self.uiNameTypeWizardPage])
        qemu_binaries = Qemu.instance().getQemuBinariesList()

        for server in qemu_binaries:
            qemus = qemu_binaries[server]["qemus"]
            for qemu in qemus:
                key = "{server}:{qemu}".format(server=server, qemu=qemu["path"])
                self.uiQemuListComboBox.addItem("{key} (v{version})".format(key=key, version=qemu["version"]), key)

        # default is qemu-system-x86_64
        index = self.uiQemuListComboBox.findText("x86_64 ", QtCore.Qt.MatchContains)  # the space after x86_64 must be present!
        if index != -1:
            self.uiQemuListComboBox.setCurrentIndex(index)

    def _getDiskImage(self):

        destination_directory = os.path.join(MainWindow.instance().settings()["images_path"], "QEMU")
        path, _ = QtGui.QFileDialog.getOpenFileNameAndFilter(self,
                                                             "Select a QEMU disk image",
                                                             destination_directory)
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "QEMU disk image", "Cannot read {}".format(path))
            return

        try:
            os.makedirs(destination_directory)
        except FileExistsError:
            pass
        except OSError as e:
            QtGui.QMessageBox.critical(self, "QEMU disk images directory", "Could not create the QEMU disk images directory {}: {}".format(destination_directory,
                                                                                                                                           str(e)))
            return

        if os.path.dirname(path) != destination_directory:
            # the QEMU disk image is not in the default images directory
            new_destination_path = os.path.join(destination_directory, os.path.basename(path))
            try:
                # try to create a symbolic link to it
                symlink_path = new_destination_path
                os.symlink(path, symlink_path)
                path = symlink_path
            except (OSError, NotImplementedError):
                # if unsuccessful, then copy the QEMU disk image itself
                try:
                    shutil.copyfile(path, new_destination_path)
                    path = new_destination_path
                except OSError:
                    pass

        return path

    def _hdaDiskImageBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU hda disk image.
        """

        path = self._getDiskImage()
        if path:
            self.uiHdaDiskImageLineEdit.clear()
            self.uiHdaDiskImageLineEdit.setText(path)

    def _hdbDiskImageBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU hdb disk image.
        """

        path = self._getDiskImage()
        if path:
            self.uiHdbDiskImageLineEdit.clear()
            self.uiHdbDiskImageLineEdit.setText(path)

    def _initrdBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU initrd.
        """

        path = self._getDiskImage()
        if path:
            self.uiInitrdLineEdit.clear()
            self.uiInitrdLineEdit.setText(path)

    def _kernelImageBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU kernel image.
        """

        path = self._getDiskImage()
        if path:
            self.uiKernelImageLineEdit.clear()
            self.uiKernelImageLineEdit.setText(path)

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        server, qemu_path = self.uiQemuListComboBox.itemData(self.uiQemuListComboBox.currentIndex()).split(":", 1)

        settings = {
            "name": self.uiNameLineEdit.text(),
            "ram": self.uiRamSpinBox.value(),
            "qemu_path": qemu_path,
            "server": "local",
        }

        if self.uiTypeComboBox.currentText() == "ASA 8.4(2)":
            settings["adapters"] = 6
            settings["initrd"] = self.uiInitrdLineEdit.text()
            settings["kernel_image"] = self.uiKernelImageLineEdit.text()
            settings["kernel_command_line"] = "ide_generic.probe_mask=0x01 ide_core.chs=0.0:980,16,32 auto nousb console=ttyS0,9600 bigphysarea=65536 ide1=noprobe no-hlt"
            settings["options"] = "-nographic -cpu coreduo -icount auto -hdachs 980,16,32"
            settings["default_symbol"] = ":/symbols/asa.normal.svg"
            settings["hover_symbol"] = ":/symbols/asa.selected.svg"
        elif self.uiTypeComboBox.currentText() == "IDS":
            settings["adapters"] = 3
            settings["hda_disk_image"] = self.uiHdaDiskImageLineEdit.text()
            settings["hdb_disk_image"] = self.uiHdbDiskImageLineEdit.text()
            settings["options"] = "-smbios type=1,product=IDS-4215"
            settings["default_symbol"] = ":/symbols/ids.normal.svg"
            settings["hover_symbol"] = ":/symbols/ids.selected.svg"
        else:
            settings["hda_disk_image"] = self.uiHdaDiskImageLineEdit.text()

        return settings

    def nextId(self):
        """
        Wizard rules!
        """

        current_id = self.currentId()
        if self.page(current_id) == self.uiNameTypeWizardPage:

            if self.uiTypeComboBox.currentText() != "Default":
                self.uiRamSpinBox.setValue(1024)
            return self._ids[self.uiBinaryMemoryWizardPage]

        elif self.page(current_id) == self.uiBinaryMemoryWizardPage:

            if self.uiTypeComboBox.currentText() == "ASA 8.4(2)":
                return self._ids[self.uiASAWizardPage]
            return self._ids[self.uiDiskWizardPage]

        elif self.page(current_id) == self.uiDiskWizardPage:

            if self.uiTypeComboBox.currentText() == "IDS":
                return self._ids[self.uiDiskImageHdbWizardPage]
            return -1
        else:
            return -1
