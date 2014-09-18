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
Configuration page for QEMU VM preferences.
"""

import os
import shutil

from gns3.qt import QtGui
from gns3.servers import Servers
from gns3.main_window import MainWindow
from gns3.modules.module_error import ModuleError
from .. import Qemu
from ..ui.qemu_vm_preferences_page_ui import Ui_QemuVMPreferencesPageWidget


class QemuVMPreferencesPage(QtGui.QWidget, Ui_QemuVMPreferencesPageWidget):
    """
    QWidget preference page for QEMU VM preferences.
    """

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._qemu_vms = {}

        self.uiSaveQemuVMPushButton.clicked.connect(self._qemuVMSaveSlot)
        self.uiDeleteQemuVMPushButton.clicked.connect(self._qemuVMDeleteSlot)
        self.uiRefreshPushButton.clicked.connect(self._qemuRefreshSlot)
        self.uiQemuVMsTreeWidget.itemClicked.connect(self._qemuVMClickedSlot)
        self.uiQemuVMsTreeWidget.itemSelectionChanged.connect(self._qemuVMChangedSlot)
        self.uiDiskImageToolButton.clicked.connect(self._diskImageBrowserSlot)

        self.uiAdapterTypesComboBox.clear()
        self.uiAdapterTypesComboBox.addItems(["ne2k_pci",
                                              "i82551",
                                              "i82557b",
                                              "i82559er",
                                              "rtl8139",
                                              "e1000",
                                              "pcnet",
                                              "virtio"])

        self.uiAdapterTypesComboBox.setCurrentIndex(5)  # e1000 is the default

    def showEvent(self, event):
        """
        Loads the QEMU binaries list when the page is shown.

        :param event: QShowEvent instance
        """

        self._qemuRefreshSlot()
        QtGui.QWidget.showEvent(self, event)

    def _qemuVMClickedSlot(self, item, column):
        """
        Loads a selected QEMU VM from the tree widget.

        :param item: selected QTreeWidgetItem instance
        :param column: ignored
        """

        name = item.text(0)
        server = item.text(1)
        key = "{server}:{name}".format(server=server, name=name)
        qemu_vm = self._qemu_vms[key]

        index = self.uiQemuListComboBox.findData("{server}:{qemu_path}".format(server=qemu_vm["server"], qemu_path=qemu_vm["qemu_path"]))
        if index != -1:
            self.uiQemuListComboBox.setCurrentIndex(index)
        else:
            QtGui.QMessageBox.warning(self, "QEMU VM", "Could not find the QEMU path on for this VM on server {}".format(server))

        self.uiNameLineEdit.setText(qemu_vm["name"])
        self.uiDiskImageLineEdit.setText(qemu_vm["disk_image"])
        self.uiRamSpinBox.setValue(qemu_vm["ram"])
        self.uiAdaptersSpinBox.setValue(qemu_vm["adapters"])
        index = self.uiAdapterTypesComboBox.findText(qemu_vm["adapter_type"])
        if index != -1:
            self.uiAdapterTypesComboBox.setCurrentIndex(index)
        self.uiQemuOptionsLineEdit.setText(qemu_vm["options"])

    def _qemuVMChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiQemuVMsTreeWidget.currentItem()
        if item:
            self.uiDeleteQemuVMPushButton.setEnabled(True)
        else:
            self.uiDeleteQemuVMPushButton.setEnabled(False)

    def _qemuVMSaveSlot(self):
        """
        Adds/Saves a QEMU VM.
        """

        if not self.uiQemuListComboBox.currentText():
            QtGui.QMessageBox.critical(self, "QEMU VM", "Please select a QEMU version")
            return

        server, qemu_path = self.uiQemuListComboBox.itemData(self.uiQemuListComboBox.currentIndex()).split(":", 1)
        name = self.uiNameLineEdit.text()
        if not name:
            QtGui.QMessageBox.critical(self, "QEMU VM", "The QEMU VM must have a name!")
            return

        disk_image = self.uiDiskImageLineEdit.text()
        ram = self.uiRamSpinBox.value()
        adapters = self.uiAdaptersSpinBox.value()
        adapter_type = self.uiAdapterTypesComboBox.currentText()
        options = self.uiQemuOptionsLineEdit.text()

        # #TODO: mutiple remote server
        # if VirtualBox.instance().settings()["use_local_server"]:
        #     server = "local"
        # else:
        #     server = next(iter(Servers.instance()))
        #     if not server:
        #         QtGui.QMessageBox.critical(self, "VirtualBox VM", "No remote server available!")
        #         return
        #     server = server.host

        key = "{server}:{name}".format(server=server, name=name)
        item = self.uiQemuVMsTreeWidget.currentItem()

        if key in self._qemu_vms and item and item.text(0) == name:
            item.setText(0, name)
            item.setText(1, server)
        elif key in self._qemu_vms:
            return
        else:
            # add a new entry in the tree widget
            item = QtGui.QTreeWidgetItem(self.uiQemuVMsTreeWidget)
            item.setText(0, name)
            item.setText(1, server)
            self.uiQemuVMsTreeWidget.setCurrentItem(item)

        self._qemu_vms[key] = {"name": name,
                               "qemu_path": qemu_path,
                               "disk_image": disk_image,
                               "ram": ram,
                               "adapters": adapters,
                               "adapter_type": adapter_type,
                               "options": options,
                               "server": server}

        self.uiQemuVMsTreeWidget.resizeColumnToContents(0)
        self.uiQemuVMsTreeWidget.resizeColumnToContents(1)

    def _qemuVMDeleteSlot(self):
        """
        Deletes a QEMU VM.
        """

        item = self.uiQemuVMsTreeWidget.currentItem()
        if item:
            name = item.text(0)
            server = item.text(1)
            key = "{server}:{name}".format(server=server, name=name)
            del self._qemu_vms[key]
            self.uiQemuVMsTreeWidget.takeTopLevelItem(self.uiQemuVMsTreeWidget.indexOfTopLevelItem(item))

    def _qemuRefreshSlot(self):
        """
        Gets/refreshes the QEMU binaries list for all servers.

        :param ignore_errors: either errors should be ignored or not
        """

        self.uiQemuListComboBox.clear()
        qemu_module = Qemu.instance()
        servers = Servers.instance()

        if qemu_module.settings()["use_local_server"]:
            try:
                qemu_module.get_qemu_list(servers.localServer(), self._QemuListCallback)
            except ModuleError as e:
                QtGui.QMessageBox.critical(self, "QEMU list", "{}".format(e))
        else:
            for server in servers.remoteServers().values():
                try:
                    qemu_module.get_qemu_list(server, self._QemuListCallback)
                except ModuleError as e:
                    print("{}".format(e))
                    continue

    def _QemuListCallback(self, result, error=False):
        """
        Callback to get the QEMU binaries list.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtGui.QMessageBox.critical(self, "QEMU list", "Could not get the QEMU binaries list: {}".format(result["message"]))
        else:
            for qemu in result["qemus"]:
                if Qemu.instance().settings()["use_local_server"]:
                    server = "local"
                else:
                    server = result["server"]
                key = "{server}:{qemu}".format(server=server, qemu=qemu["path"])
                self.uiQemuListComboBox.addItem("{key} (v{version})".format(key=key, version=qemu["version"]), key)

    def _diskImageBrowserSlot(self):
        """
        Slot to open a file browser and select a QEMU disk image.
        """

        destination_directory = os.path.join(MainWindow.instance().settings()["images_path"], "QEMU")
        path, _ = QtGui.QFileDialog.getOpenFileNameAndFilter(self,
                                                             "Select a QEMU disk image",
                                                             destination_directory,
                                                             "All files (*.*)")
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

        self.uiDiskImageLineEdit.clear()
        self.uiDiskImageLineEdit.setText(path)

    def loadPreferences(self):
        """
        Loads the QEMU VM preferences.
        """

        self._qemu_vms.clear()
        qemu_module = Qemu.instance()
        qemu_vms = qemu_module.qemuVMs()

        for qemu_vm in qemu_vms.values():
            item = QtGui.QTreeWidgetItem(self.uiQemuVMsTreeWidget)
            item.setText(0, qemu_vm["name"])
            item.setText(1, qemu_vm["server"])

        self.uiQemuVMsTreeWidget.resizeColumnToContents(0)
        self.uiQemuVMsTreeWidget.resizeColumnToContents(1)
        self._qemu_vms.update(qemu_vms)

    def savePreferences(self):
        """
        Saves the QEMU VM preferences.
        """

        Qemu.instance().setQemuVMs(self._qemu_vms)
