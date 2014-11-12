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
from functools import partial

from gns3.qt import QtCore, QtGui
from gns3.servers import Servers
from gns3.modules.module_error import ModuleError
from gns3.main_window import MainWindow
from gns3.dialogs.node_configurator_dialog import ConfigurationError

from ..ui.qemu_vm_configuration_page_ui import Ui_QemuVMConfigPageWidget
from .. import Qemu
from ..settings import QEMU_BINARIES_FOR_CLOUD


class QemuVMConfigurationPage(QtGui.QWidget, Ui_QemuVMConfigPageWidget):
    """
    QWidget configuration page for QEMU VMs.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.uiHdaDiskImageToolButton.clicked.connect(self._hdaDiskImageBrowserSlot)
        self.uiHdbDiskImageToolButton.clicked.connect(self._hdbDiskImageBrowserSlot)
        self.uiInitrdToolButton.clicked.connect(self._initrdBrowserSlot)
        self.uiKernelImageToolButton.clicked.connect(self._kernelImageBrowserSlot)

        self.uiAdapterTypesComboBox.clear()
        self.uiAdapterTypesComboBox.addItems(["ne2k_pci",
                                              "i82551",
                                              "i82557b",
                                              "i82559er",
                                              "rtl8139",
                                              "e1000",
                                              "pcnet",
                                              "virtio"])

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

    def _getQemuBinariesFromServerCallback(self, result, error=False, qemu_path=None):
        """
        Callback for getQemuBinariesFromServer.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if self._qemu_binaries_progress_dialog.wasCanceled():
            return
        self._qemu_binaries_progress_dialog.accept()

        if error:
            QtGui.QMessageBox.critical(self, "Qemu binaries", "Error: ".format(result["message"]))
        else:
            self.uiQemuListComboBox.clear()
            for qemu in result["qemus"]:
                if qemu["version"]:
                    self.uiQemuListComboBox.addItem("{path} (v{version})".format(path=qemu["path"], version=qemu["version"]), qemu["path"])
                else:
                    self.uiQemuListComboBox.addItem("{path}".format(path=qemu["path"]), qemu["path"])

        index = self.uiQemuListComboBox.findData("{path}".format(path=qemu_path))
        if index != -1:
            self.uiQemuListComboBox.setCurrentIndex(index)
        else:
            QtGui.QMessageBox.critical(self, "Qemu", "Could not find {} in the Qemu binaries list".format(qemu_path))
            self.uiQemuListComboBox.clear()

    def loadSettings(self, settings, node=None, group=False):
        """
        Loads the QEMU VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        if node:
            server = node.server()
        else:
            server = settings["server"]
            if server == "local":
                server = Servers.instance().localServer()
            elif ":" in server:
                host, port = server.rsplit(":")
                server = Servers.instance().getRemoteServer(host, port)

        if server == "cloud":
            for binary in QEMU_BINARIES_FOR_CLOUD:
                self.uiQemuListComboBox.addItem("{path}".format(path=binary), binary)
        else:
            self._qemu_binaries_progress_dialog = QtGui.QProgressDialog("Loading QEMU binaries", "Cancel", 0, 0, parent=self)
            self._qemu_binaries_progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            self._qemu_binaries_progress_dialog.setWindowTitle("QEMU binaries")
            self._qemu_binaries_progress_dialog.show()

            callback = partial(self._getQemuBinariesFromServerCallback, qemu_path=settings["qemu_path"])
            try:
                Qemu.instance().getQemuBinariesFromServer(server, callback)
            except ModuleError as e:
                self._qemu_binaries_progress_dialog.reject()
                QtGui.QMessageBox.critical(self, "Qemu binaries", "Error while getting the QEMU binaries: {}".format(e))
                self.uiQemuListComboBox.clear()

        if not group:
            # set the device name
            self.uiNameLineEdit.setText(settings["name"])
            if "console" in settings:
                self.uiConsolePortSpinBox.setValue(settings["console"])
            else:
                self.uiConsolePortLabel.hide()
                self.uiConsolePortSpinBox.hide()
            self.uiHdaDiskImageLineEdit.setText(settings["hda_disk_image"])
            self.uiHdbDiskImageLineEdit.setText(settings["hdb_disk_image"])
            self.uiInitrdLineEdit.setText(settings["initrd"])
            self.uiKernelImageLineEdit.setText(settings["kernel_image"])
        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiConsolePortLabel.hide()
            self.uiConsolePortSpinBox.hide()
            self.uiHdaDiskImageLabel.hide()
            self.uiHdaDiskImageLineEdit.hide()
            self.uiHdaDiskImageToolButton.hide()
            self.uiHdbDiskImageLabel.hide()
            self.uiHdbDiskImageLineEdit.hide()
            self.uiHdbDiskImageToolButton.hide()
            self.uiInitrdLabel.hide()
            self.uiInitrdLineEdit.hide()
            self.uiInitrdToolButton.hide()
            self.uiKernelImageLabel.hide()
            self.uiKernelImageLineEdit.hide()
            self.uiKernelImageToolButton.hide()

        self.uiKernelCommandLineEdit.setText(settings["kernel_command_line"])
        self.uiAdaptersSpinBox.setValue(settings["adapters"])
        index = self.uiAdapterTypesComboBox.findText(settings["adapter_type"])
        if index != -1:
            self.uiAdapterTypesComboBox.setCurrentIndex(index)

        self.uiRamSpinBox.setValue(settings["ram"])
        self.uiQemuOptionsLineEdit.setText(settings["options"])

    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the QEMU VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        # these settings cannot be shared by nodes and updated
        # in the node configurator.
        if not group:

            name = self.uiNameLineEdit.text()
            if not name:
                QtGui.QMessageBox.critical(self, "Name", "The QEMU VM name cannot be empty!")
            else:
                settings["name"] = name

            if "console" in settings:
                settings["console"] = self.uiConsolePortSpinBox.value()
            settings["hda_disk_image"] = self.uiHdaDiskImageLineEdit.text()
            settings["hdb_disk_image"] = self.uiHdbDiskImageLineEdit.text()
            settings["initrd"] = self.uiInitrdLineEdit.text()
            settings["kernel_image"] = self.uiKernelImageLineEdit.text()

        else:
            del settings["name"]
            if "console" in settings:
                del settings["console"]
            del settings["hda_disk_image"]
            del settings["hdb_disk_image"]
            del settings["initrd"]
            del settings["kernel_image"]

        if self.uiQemuListComboBox.count():
            qemu_path = self.uiQemuListComboBox.itemData(self.uiQemuListComboBox.currentIndex())
            settings["qemu_path"] = qemu_path

        settings["adapter_type"] = self.uiAdapterTypesComboBox.currentText()
        settings["kernel_command_line"] = self.uiKernelCommandLineEdit.text()

        adapters = self.uiAdaptersSpinBox.value()
        if node and settings["adapters"] != adapters:
            # check if the adapters settings have changed
            node_ports = node.ports()
            for node_port in node_ports:
                if not node_port.isFree():
                    QtGui.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
                    raise ConfigurationError()

        settings["adapters"] = adapters
        settings["ram"] = self.uiRamSpinBox.value()
        settings["options"] = self.uiQemuOptionsLineEdit.text()
