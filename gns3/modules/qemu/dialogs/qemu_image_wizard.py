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

from gns3.qt import QtCore, QtGui, QtWidgets, QFileDialog
from .. import Qemu
from ..ui.qemu_image_wizard_ui import Ui_QemuImageWizard


class QemuImageWizard(QtWidgets.QWizard, Ui_QemuImageWizard):

    """
    Wizard to create a Qemu VM.

    :param parent: parent widget
    :param server: Server where the image should be created
    :param filename: Default filename of image.
    :param folder: Default folder for the image. If absent, defaults to Qemu's images folder.
    :param size: Default size (in MiB) for the image.
    """

    def __init__(self, parent, server, filename="disk", folder=None, size=30000):

        super().__init__(parent)

        self._server = server
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
        Qemu.instance().getQemuImgBinariesFromServer(self._server,
                                                     self._getQemuImgBinariesFromServerCallback)
        self.uiLocationLineEdit.setText(filename)
        self.uiSizeSpinBox.setValue(size)
        self._formatChangedSlot(self.uiFormatQcow2Radio)

        # Hide the file browse button for remote servers
        if not self._server.isLocal():
            self.uiLocationBrowseToolButton.hide()

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
        self.uiBinaryWizardPage.completeChanged.emit()

    def _getCreateDiskServerCallback(self, result, error=False, **kwargs):
        """
        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtWidgets.QMessageBox.critical(self, "Create disk", "{}".format(result["message"]))

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
        selected_format = self.uiFormatRadios.checkedButton()

        options = {}
        options["path"] = self.uiLocationLineEdit.text()
        options["qemu_img"] = self.uiBinaryComboBox.currentData()
        options["format"] = self._mappings[selected_format][0]
        options["size"] = self.uiSizeSpinBox.value()

        if selected_format == self.uiFormatQcow2Radio:
            preallocation = self.uiQcow2PreallocationRadios.checkedButton()
            if preallocation is not None:
                preallocation_mappings = {
                    self.uiQcow2PreallocationOffRadio: 'off',
                    self.uiQcow2PreallocationMetadataRadio: 'metadata',
                    self.uiQcow2PreallocationFallocRadio: 'falloc',
                    self.uiQcow2PreallocationFullRadio: 'full'
                }
                options["preallocation"] = preallocation_mappings[preallocation]

            cluster_size = self.uiQcow2ClusterSizeComboBox.currentText()
            if not '<default>' == cluster_size:
                if cluster_size.endswith('k'):
                    options["cluster_size"] = int(cluster_size[:-1]) * 1024
                else:
                    options["cluster_size"] = int(cluster_size)

            refcount_bits = self.uiRefcountEntrySizeComboBox.currentText()
            if not '<default>' == refcount_bits:
                options["refcount_bits"] = int(refcount_bits)

            options["lazy_refcounts"] = 'on' if QtCore.Qt.Checked == self.uiLazyRefcountsCheckBox.checkState() else 'off'

        elif selected_format == self.uiFormatVhdRadio:
            size_mode = self.uiVhdSizeModeRadios.checkedButton()
            if size_mode is not None:
                size_mode_mappings = {
                    self.uiVhdFileSizeModeDynamicRadio: 'dynamic',
                    self.uiVhdFileSizeModeFixedRadio: 'fixed'
                }
                options['subformat'] = size_mode_mappings[size_mode]

        elif selected_format == self.uiFormatVdiRadio:
            size_mode = self.uiVhdSizeModeRadios.checkedButton()
            if size_mode is not None:
                options["static"] = 'on' if size_mode == self.uiVhdFileSizeModeFixedRadio else 'off'

        elif selected_format == self.uiFormatVmdkRadio:
            options["zeroed_grain"] = 'on' if QtCore.Qt.Checked == self.uiVmdkZeroedGrainCheckBox.checkState() else 'off'

            adapter_type = self.uiVmdkAdapterRadios.checkedButton()
            if adapter_type is not None:
                adapter_type_mappings = {
                    self.uiVmdkAdapterTypeIdeRadio: 'ide',
                    self.uiVmdkAdapterTypeLsiRadio: 'lsilogic',
                    self.uiVmdkAdapterTypeBusRadio: 'buslogic',
                    self.uiVmdkAdapterTypeEsxRadio: 'legacyESX'
                }
                options['adapter_type'] = adapter_type_mappings[adapter_type]

            stream_optimized = self.uiVmdkStreamOptimizedCheckBox.checkState()
            if QtCore.Qt.Checked == stream_optimized:
                options['subformat'] = 'streamOptimized'
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
                    options['subformat'] = two + size_mode_mappings[size_mode]

        Qemu.instance().createDiskImage(self._server, self._getCreateDiskServerCallback, options)
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
