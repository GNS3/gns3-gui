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
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog

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
        self.uiHdaDiskImageToolButton.clicked.connect(self._hdaDiskImageBrowserSlot)
        self.uiHdbDiskImageToolButton.clicked.connect(self._hdbDiskImageBrowserSlot)
        self.uiInitrdToolButton.clicked.connect(self._initrdBrowserSlot)
        self.uiKernelImageToolButton.clicked.connect(self._kernelImageBrowserSlot)
        self.uiApplyPreconfigurationPushButton.clicked.connect(self._applyPreconfigurationSlot)
        self.uiSymbolPushButton.clicked.connect(self._symbolSelectionSlot)

        self.uiAdapterTypesComboBox.clear()
        self.uiAdapterTypesComboBox.addItems(["ne2k_pci",
                                              "i82551",
                                              "i82557b",
                                              "i82559er",
                                              "rtl8139",
                                              "e1000",
                                              "pcnet",
                                              "virtio"])

        self.uiPreconfigurationComboBox.clear()
        self.uiPreconfigurationComboBox.addItems(["ASA 8.4(2)",
                                                  "ASA 8.0(2)",
                                                  "IDS"])

        self.uiAdapterTypesComboBox.setCurrentIndex(5)  # e1000 is the default

        # default symbol for QEMU VMs
        self.uiSymbolPushButton.setIcon(QtGui.QIcon(":/symbols/qemu_guest.normal.svg"))
        self.uiSymbolPushButton.setProperty("default_symbol", ":/symbols/qemu_guest.normal.svg")
        self.uiSymbolPushButton.setProperty("hover_symbol", ":/symbols/qemu_guest.selected.svg")

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
        self.uiHdaDiskImageLineEdit.setText(qemu_vm["hda_disk_image"])
        self.uiHdbDiskImageLineEdit.setText(qemu_vm["hdb_disk_image"])
        self.uiRamSpinBox.setValue(qemu_vm["ram"])
        self.uiAdaptersSpinBox.setValue(qemu_vm["adapters"])
        index = self.uiAdapterTypesComboBox.findText(qemu_vm["adapter_type"])
        if index != -1:
            self.uiAdapterTypesComboBox.setCurrentIndex(index)
        self.uiInitrdLineEdit.setText(qemu_vm["initrd"])
        self.uiKernelImageLineEdit.setText(qemu_vm["kernel_image"])
        self.uiKernelCommandLineEdit.setText(qemu_vm["kernel_command_line"])
        self.uiQemuOptionsLineEdit.setText(qemu_vm["options"])
        self.uiSymbolPushButton.setIcon(QtGui.QIcon(qemu_vm["default_symbol"]))
        self.uiSymbolPushButton.setProperty("default_symbol", qemu_vm["default_symbol"])
        self.uiSymbolPushButton.setProperty("hover_symbol", qemu_vm["hover_symbol"])

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

        hda_disk_image = self.uiHdaDiskImageLineEdit.text().strip()
        hdb_disk_image = self.uiHdbDiskImageLineEdit.text().strip()
        ram = self.uiRamSpinBox.value()
        adapters = self.uiAdaptersSpinBox.value()
        adapter_type = self.uiAdapterTypesComboBox.currentText()
        initrd = self.uiInitrdLineEdit.text().strip()
        kernel_image = self.uiKernelImageLineEdit.text().strip()
        kernel_command_line = self.uiKernelCommandLineEdit.text().strip()
        options = self.uiQemuOptionsLineEdit.text().strip()
        default_symbol = self.uiSymbolPushButton.property("default_symbol")
        hover_symbol = self.uiSymbolPushButton.property("hover_symbol")

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
                               "default_symbol": default_symbol,
                               "hover_symbol": hover_symbol,
                               "qemu_path": qemu_path,
                               "hda_disk_image": hda_disk_image,
                               "hdb_disk_image": hdb_disk_image,
                               "ram": ram,
                               "adapters": adapters,
                               "adapter_type": adapter_type,
                               "options": options,
                               "initrd": initrd,
                               "kernel_image": kernel_image,
                               "kernel_command_line": kernel_command_line,
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
                if qemu["version"]:
                    self.uiQemuListComboBox.addItem("{key} (v{version})".format(key=key, version=qemu["version"]), key)
                else:
                    self.uiQemuListComboBox.addItem("{key}".format(key=key), key)

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

    def _applyPreconfigurationSlot(self):
        """
        Slot to apply a selected preconfiguration.
        """

        preconfig = self.uiPreconfigurationComboBox.currentText()
        self.uiHdaDiskImageLineEdit.clear()
        self.uiHdbDiskImageLineEdit.clear()
        self.uiInitrdLineEdit.clear()
        self.uiKernelImageLineEdit.clear()
        self.uiKernelCommandLineEdit.clear()
        self.uiQemuOptionsLineEdit.clear()

        if preconfig == "ASA 8.0(2)":
            self.uiRamSpinBox.setValue(512)
            self.uiAdaptersSpinBox.setValue(6)
            self.uiAdapterTypesComboBox.setCurrentIndex(self.uiAdapterTypesComboBox.findText("e1000"))
            self.uiQemuOptionsLineEdit.setText("-vga none -hdachs 980,16,32")
            self.uiKernelCommandLineEdit.setText("auto nousb ide1=noprobe bigphysarea=16384 console=ttyS0,9600n8 hda=980,16,32")
            QtGui.QMessageBox.information(self, "ASA", "QEMU VM preconfigured for ASA 8.0(2), you must now provide an initrd file and a kernel image")
            self.uiSymbolPushButton.setIcon(QtGui.QIcon(":/symbols/asa.normal.svg"))
            self.uiSymbolPushButton.setProperty("default_symbol", ":/symbols/asa.normal.svg")
            self.uiSymbolPushButton.setProperty("hover_symbol", ":/symbols/asa.selected.svg")

        if preconfig == "ASA 8.4(2)":
            self.uiRamSpinBox.setValue(1024)
            self.uiAdaptersSpinBox.setValue(6)
            self.uiAdapterTypesComboBox.setCurrentIndex(self.uiAdapterTypesComboBox.findText("e1000"))
            self.uiQemuOptionsLineEdit.setText("-nographic -cpu coreduo -icount auto -hdachs 980,16,32")
            self.uiKernelCommandLineEdit.setText("ide_generic.probe_mask=0x01 ide_core.chs=0.0:980,16,32 auto nousb console=ttyS0,9600 bigphysarea=65536 ide1=noprobe no-hlt")
            QtGui.QMessageBox.information(self, "ASA", "QEMU VM preconfigured for ASA 8.4(2), you must now provide an initrd file and a kernel image")
            self.uiSymbolPushButton.setIcon(QtGui.QIcon(":/symbols/asa.normal.svg"))
            self.uiSymbolPushButton.setProperty("default_symbol", ":/symbols/asa.normal.svg")
            self.uiSymbolPushButton.setProperty("hover_symbol", ":/symbols/asa.selected.svg")

        if preconfig == "IDS":
            self.uiRamSpinBox.setValue(1024)
            self.uiAdaptersSpinBox.setValue(3)
            self.uiAdapterTypesComboBox.setCurrentIndex(self.uiAdapterTypesComboBox.findText("e1000"))
            self.uiQemuOptionsLineEdit.setText("-smbios type=1,product=IDS-4215")
            QtGui.QMessageBox.information(self, "IDS", "QEMU VM preconfigured for IDS, you must now provide 2 disk images (hda and hdb)")
            self.uiSymbolPushButton.setIcon(QtGui.QIcon(":/symbols/ids.normal.svg"))
            self.uiSymbolPushButton.setProperty("default_symbol", ":/symbols/ids.normal.svg")
            self.uiSymbolPushButton.setProperty("hover_symbol", ":/symbols/ids.selected.svg")

    def _symbolSelectionSlot(self):
        """
        Slot to select a symbol for the QEMU VM.
        """

        dialog = SymbolSelectionDialog(self)
        dialog.show()
        if dialog.exec_():
            normal_symbol, selected_symbol = dialog.getSymbols()
            self.uiSymbolPushButton.setIcon(QtGui.QIcon(normal_symbol))
            self.uiSymbolPushButton.setProperty("default_symbol", normal_symbol)
            self.uiSymbolPushButton.setProperty("hover_symbol", selected_symbol)

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
