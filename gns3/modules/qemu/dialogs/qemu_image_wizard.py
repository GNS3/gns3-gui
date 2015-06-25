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
Wizard for QEMU images.
"""

import os
import subprocess
import sys

from gns3.qt import QtCore, QtGui, QtWidgets, QFileDialog
from gns3.servers import Servers
from gns3.image_manager import ImageManager

from .. import Qemu
from ..ui.qemu_image_wizard_ui import Ui_QemuImageWizard


class QemuImageWizard(QtWidgets.QWizard, Ui_QemuImageWizard):

    """
    Wizard to create a Qemu VM.

    :param parent: parent widget
    :param filename: Default filename of image.
    :param folder: Default folder for the image. If absent, defaults to Qemu's images folder.
    :param size: Default size (in MiB) for the image.
    """

    _mappings = None
    _folder = None

    def __init__(self, parent, filename="disk", folder=None, size=30000):

        super().__init__(parent)
        self.setupUi(self)
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/icons/qemu.svg"))

        # Initialize "constants"
        self._mappings = {
            self.uiFormatQcow2Radio: ("qcow2", ".qcow2", self.uiQcow2OptionsWizardPage),
            self.uiFormatQcowRadio: ("qcow", ".qcow", None),
            self.uiFormatVhdRadio: ("vpc", ".vhd", self.uiVhdOptionsWizardPage),
            self.uiFormatVdiRadio: ("vdi", ".vdi", self.uiVdiOptionsWizardPage),
            self.uiFormatVmdkRadio: ("vmdk", ".vmdk", self.uiVmdkOptionsWizardPage),
            self.uiFormatRawRadio: ("raw", ".img", None)
        }

        # isComplete() overrides
        self.uiSizeAndLocationWizardPage.isComplete = self._uiSizeAndLocationWizardPage_isComplete
        self.uiBinaryWizardPage.isComplete = self._uiBinaryWizardPage_isComplete

        # Signal connections
        self.uiFormatRadios.buttonClicked.connect(self._formatChangedSlot)
        self.uiLocationLineEdit.textChanged.connect(self._locationChangedSlot)
        self.uiLocationBrowseToolButton.clicked.connect(self._browserSlot)

        # Finisher setup
        self.page(self.pageIds()[-1]).validatePage = self._createDisk

        # Default values
        self._folder = folder or os.path.join(ImageManager.instance().getDirectoryForType("QEMU"))
        Qemu.instance().getQemuImgBinariesFromServer(Servers.instance().localServer(),
                                                     self._getQemuImgBinariesFromServerCallback)
        self.uiLocationLineEdit.setText(os.path.join(self._folder, filename))
        self.uiSizeSpinBox.setValue(size)

    def _getQemuImgBinariesFromServerCallback(self, result, error=False, **kwargs):
        """
        Callback for getQemuImgBinariesFromServer.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtWidgets.QMessageBox.critical(self, "Qemu-img binaries", "{}".format(result["message"]))
        else:
            self.uiBinaryComboBox.clear()
            for qemu in result:
                if qemu["version"]:
                    self.uiBinaryComboBox.addItem(
                        "{path} (v{version})".format(path=qemu["path"], version=qemu["version"]), qemu["path"]
                    )
                else:
                    self.uiBinaryComboBox.addItem("{path}".format(path=qemu["path"]), qemu["path"])

    def _uiSizeAndLocationWizardPage_isComplete(self):
        return not "" == self.uiLocationLineEdit.text()

    def _uiBinaryWizardPage_isComplete(self):
        return self.uiFormatRadios.checkedButton() is not None and self.uiBinaryComboBox.currentData() is not None

    def _locationChangedSlot(self, new_value):
        self.uiSizeAndLocationWizardPage.completeChanged.emit()

    def _browserSlot(self):
        path, name_filter = QFileDialog.getSaveFileName(
            self,
            'Image location',
            self.uiLocationLineEdit.text(),
            '{0} files (*{1});;All files (*)'.format(
                self.uiFormatRadios.checkedButton().text(),
                self._mappings[self.uiFormatRadios.checkedButton()][1]
            ),
            options=QFileDialog.DontConfirmOverwrite
        )
        if path:
            self.uiLocationLineEdit.setText(path)

    def _formatChangedSlot(self, new_format):
        dir, filename = os.path.split(self.uiLocationLineEdit.text())
        try:
            filename = filename[:filename.rindex('.')] + self._mappings[new_format][1]
        except ValueError:
            # The file has no extension; Just give it one
            filename = filename + self._mappings[new_format][1]
        self.uiLocationLineEdit.setText(os.path.join(dir, filename))
        self.uiBinaryWizardPage.completeChanged.emit()

    def _createDisk(self):
        final_location = os.path.join(self._folder, self.uiLocationLineEdit.text())
        if os.path.exists(final_location):
            overwrite_answer = QtWidgets.QMessageBox.question(
                self,
                "File exists",
                "The specified file already exists.\n\nYou you like to have it removed before proceeding?"
            )
            if not QtWidgets.QDialogButtonBox.Yes == overwrite_answer:
                return False
            try:
                os.remove(final_location)
            except:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Remove failed",
                    "Failed to remove the existing file."
                    "\n\n"
                    "Make sure the file is not in use, and try again. Alternatively, specify a different name."
                )
                return False

        format_options = []
        selected_format = self.uiFormatRadios.checkedButton()
        if selected_format == self.uiFormatQcow2Radio:
            preallocation = self.uiQcow2PreallocationRadios.checkedButton()
            if preallocation is not None:
                preallocation_mappings = {
                    self.uiQcow2PreallocationOffRadio: 'off',
                    self.uiQcow2PreallocationMetadataRadio: 'metadata',
                    self.uiQcow2PreallocationFallocRadio: 'falloc',
                    self.uiQcow2PreallocationFullRadio: 'full'
                }
                format_options.extend(['-o', 'preallocation=' + preallocation_mappings[preallocation]])

            cluster_size = self.uiQcow2ClusterSizeComboBox.currentText()
            if not '<default>' == cluster_size:
                format_options.extend(['-o', 'cluster_size=' + cluster_size])

            refcount_bits = self.uiRefcountEntrySizeComboBox.currentText()
            if not '<default>' == refcount_bits:
                format_options.extend(['-o', 'refcount_bits=' + cluster_size])

            lazy_refcounts = 'on' if QtCore.Qt.Checked == self.uiLazyRefcountsCheckBox.checkState() else 'off'
            format_options.extend(['-o', 'lazy_refcounts=' + lazy_refcounts])

        elif selected_format == self.uiFormatVhdRadio:
            size_mode = self.uiVhdSizeModeRadios.checkedButton()
            if size_mode is not None:
                size_mode_mappings = {
                    self.uiVhdFileSizeModeDynamicRadio: 'dynamic',
                    self.uiVhdFileSizeModeFixedRadio: 'fixed'
                }
                format_options.extend(['-o', 'subformat=' + size_mode_mappings[size_mode]])

        elif selected_format == self.uiFormatVdiRadio:
            size_mode = self.uiVhdSizeModeRadios.checkedButton()
            if size_mode is not None:
                static_value = 'on' if size_mode == self.uiVhdFileSizeModeFixedRadio else 'off'
                format_options.extend(['-o', 'static=' + static_value])

        elif selected_format == self.uiFormatVmdkRadio:
            zeroed_grain = 'on' if QtCore.Qt.Checked == self.uiVmdkZeroedGrainCheckBox.checkState() else 'off'
            format_options.extend(['-o', 'zeroed_grain=' + zeroed_grain])

            adapter_type = self.uiVmdkAdapterRadios.checkedButton()
            if adapter_type is not None:
                adapter_type_mappings = {
                    self.uiVmdkAdapterTypeIdeRadio: 'ide',
                    self.uiVmdkAdapterTypeLsiRadio: 'lsilogic',
                    self.uiVmdkAdapterTypeBusRadio: 'buslogic',
                    self.uiVmdkAdapterTypeEsxRadio: 'legacyESX'
                }
                format_options.extend(['-o', 'adapter_type=' + adapter_type_mappings[adapter_type]])

            stream_optimized = self.uiVmdkStreamOptimizedCheckBox.checkState()
            if QtCore.Qt.Checked == stream_optimized:
                format_options.extend(['-o', 'subformat=streamOptimized'])
            else:
                two = 'twoGbMaxExtent' if QtCore.Qt.Checked == self.uiVmdkSplit2gCheckBox.checkState() else 'monolithic'
                size_mode = self.uiVmdkSizeModeRadios.checkedButton()
                if size_mode is not None or two == 'twoGbMaxExtent':
                    if size_mode is None:
                        size_mode = self.uiVmdkFileSizeModeSparseRadio

                    size_mode_mappings = {
                        self.uiVmdkFileSizeModeSparseRadio: 'Sparse',
                        self.uiVmdkFileSizeModeFlatRadio: 'Flat'
                    }
                    format_options.extend(['-o', 'subformat=' + two + size_mode_mappings[size_mode]])

        command = [self.uiBinaryComboBox.currentData(), 'create', '-f', self._mappings[selected_format][0]]
        command.extend(format_options)
        command.extend([self.uiLocationLineEdit.text(), str(self.uiSizeSpinBox.value()) + 'M'])
        if sys.platform.startswith('win'):
            for i, arg in enumerate(command):
                command[i] = '"' + arg.replace('"', '"""') + '"'
            command = ' '.join(command)

        qemu_img = subprocess.Popen(
            command,
            stderr=subprocess.PIPE,
            cwd=self._folder
        )
        qemu_img_result = qemu_img.wait()
        if not 0 == qemu_img_result:
            error_lines = []
            for line in qemu_img.stderr.readlines():
                error_lines.append(line.decode("utf-8", "ignore"))
            QtWidgets.QMessageBox.critical(
                self,
                "Error from qemu-img",
                "\n".join(error_lines)
            )
            return False
        QtWidgets.QMessageBox.information(self, "Success", "Image created successfully.")
        return True

    def nextId(self):
        if self.page(self.currentId()) == self.uiBinaryWizardPage:
            current_format = self.uiFormatRadios.checkedButton()
            if not current_format:
                return self.currentId()
            next_page = self._mappings[current_format][2]
            if next_page:
                return next_page.nextId() - 1
        default_nextId = super().nextId()
        if not default_nextId == -1:
            return self.pageIds()[-1]
        return default_nextId
