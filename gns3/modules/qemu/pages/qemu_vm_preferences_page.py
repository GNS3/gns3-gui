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
import copy

from gns3.qt import QtCore, QtGui
from gns3.node import Node
from gns3.main_window import MainWindow
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.dialogs.configuration_dialog import ConfigurationDialog

from .. import Qemu
from ..ui.qemu_vm_preferences_page_ui import Ui_QemuVMPreferencesPageWidget
from ..pages.qemu_vm_configuration_page import QemuVMConfigurationPage
from ..dialogs.qemu_vm_wizard import QemuVMWizard


class QemuVMPreferencesPage(QtGui.QWidget, Ui_QemuVMPreferencesPageWidget):
    """
    QWidget preference page for QEMU VM preferences.
    """

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._qemu_vms = {}
        self._items = []

        self.uiNewQemuVMPushButton.clicked.connect(self._qemuVMNewSlot)
        self.uiEditQemuVMPushButton.clicked.connect(self._qemuVMEditSlot)
        self.uiDeleteQemuVMPushButton.clicked.connect(self._qemuVMDeleteSlot)
        self.uiQemuVMsTreeWidget.currentItemChanged.connect(self._qemuVMChangedSlot)
        self.uiQemuVMsTreeWidget.itemPressed.connect(self._qemuVMPressedSlot)

    def _createSectionItem(self, name):

        section_item = QtGui.QTreeWidgetItem(self.uiQemuVMInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, qemu_vm):

        self.uiQemuVMInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtGui.QTreeWidgetItem(section_item, ["VM name:", qemu_vm["name"]])
        QtGui.QTreeWidgetItem(section_item, ["Server:", qemu_vm["server"]])
        QtGui.QTreeWidgetItem(section_item, ["Memory:", "{} MB".format(qemu_vm["ram"])])
        if qemu_vm["qemu_path"]:
            QtGui.QTreeWidgetItem(section_item, ["QEMU binary:", os.path.basename(qemu_vm["qemu_path"])])

        # fill out the Hard disks section
        if qemu_vm["hda_disk_image"] or qemu_vm["hdb_disk_image"]:
            section_item = self._createSectionItem("Hard disks")
            if qemu_vm["hda_disk_image"]:
                QtGui.QTreeWidgetItem(section_item, ["Disk image (hda):", qemu_vm["hda_disk_image"]])
            if qemu_vm["hdb_disk_image"]:
                QtGui.QTreeWidgetItem(section_item, ["Disk image (hdb):", qemu_vm["hdb_disk_image"]])

        # fill out the Network section
        section_item = self._createSectionItem("Network")
        QtGui.QTreeWidgetItem(section_item, ["Adapters:", str(qemu_vm["adapters"])])
        QtGui.QTreeWidgetItem(section_item, ["Type:", qemu_vm["adapter_type"]])

        # fill out the Linux boot section
        if qemu_vm["initrd"] or qemu_vm["kernel_image"] or qemu_vm["kernel_command_line"]:
            section_item = self._createSectionItem("Linux boot")
            if qemu_vm["initrd"]:
                QtGui.QTreeWidgetItem(section_item, ["Initial RAM disk:", qemu_vm["initrd"]])
            if qemu_vm["kernel_image"]:
                QtGui.QTreeWidgetItem(section_item, ["Kernel image:", qemu_vm["kernel_image"]])
            if qemu_vm["kernel_command_line"]:
                QtGui.QTreeWidgetItem(section_item, ["Kernel command line:", qemu_vm["kernel_command_line"]])

        # fill out the Additional options section
        if qemu_vm["options"]:
            section_item = self._createSectionItem("Additional options")
            QtGui.QTreeWidgetItem(section_item, ["Options:", qemu_vm["options"]])

        self.uiQemuVMInfoTreeWidget.expandAll()
        self.uiQemuVMInfoTreeWidget.resizeColumnToContents(0)
        self.uiQemuVMInfoTreeWidget.resizeColumnToContents(1)

    def _qemuVMChangedSlot(self, current, previous):
        """
        Loads a selected QEMU VM from the tree widget.

        :param current: current QTreeWidgetItem instance
        :param previous: ignored
        """

        if not current:
            self.uiQemuVMInfoTreeWidget.clear()
            return

        self.uiEditQemuVMPushButton.setEnabled(True)
        self.uiDeleteQemuVMPushButton.setEnabled(True)
        key = current.data(0, QtCore.Qt.UserRole)
        qemu_vm = self._qemu_vms[key]
        self._refreshInfo(qemu_vm)

    def _qemuVMNewSlot(self):
        """
        Creates a new VM.
        """

        wizard = QemuVMWizard(self._qemu_vms, parent=self)
        wizard.show()
        if wizard.exec_():
            new_vm_settings = wizard.getSettings()

            key = "{server}:{name}".format(server=new_vm_settings["server"], name=new_vm_settings["name"])

            if key in self._qemu_vms:
                QtGui.QMessageBox.critical(self, "New QEMU VM", "VM name {} already exists".format(new_vm_settings["name"]))
                return

            self._qemu_vms[key] = {"name": "",
                                   "default_symbol": ":/symbols/qemu_guest.normal.svg",
                                   "hover_symbol": ":/symbols/qemu_guest.selected.svg",
                                   "category": Node.end_devices,
                                   "qemu_path": "default",
                                   "hda_disk_image": "",
                                   "hdb_disk_image": "",
                                   "ram": 256,
                                   "adapters": 1,
                                   "adapter_type": "e1000",
                                   "options": "",
                                   "initrd": "",
                                   "kernel_image": "",
                                   "kernel_command_line": "",
                                   "server": "local"}

            self._qemu_vms[key].update(new_vm_settings)
            item = QtGui.QTreeWidgetItem(self.uiQemuVMsTreeWidget)
            item.setText(0, self._qemu_vms[key]["name"])
            item.setIcon(0, QtGui.QIcon(self._qemu_vms[key]["default_symbol"]))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiQemuVMsTreeWidget.setCurrentItem(item)

    def _qemuVMEditSlot(self):
        """
        Edits a QEMU VM.
        """

        item = self.uiQemuVMsTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            qemu_vm = self._qemu_vms[key]
            dialog = ConfigurationDialog(qemu_vm["name"], qemu_vm, QemuVMConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                if qemu_vm["name"] != item.text(0):
                    if "{}:{}".format(qemu_vm["server"], qemu_vm["name"]) in self._qemu_vms:
                        # FIXME: bug when changing name
                        QtGui.QMessageBox.critical(self, "New QEMU VM", "VM name {} already exists".format(qemu_vm["name"]))
                        qemu_vm["name"] = item.text(0)
                    item.setText(0, qemu_vm["name"])
                self._refreshInfo(qemu_vm)

    def _qemuVMDeleteSlot(self):
        """
        Deletes a QEMU VM.
        """

        item = self.uiQemuVMsTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            del self._qemu_vms[key]
            self.uiQemuVMsTreeWidget.takeTopLevelItem(self.uiQemuVMsTreeWidget.indexOfTopLevelItem(item))

    def _qemuVMPressedSlot(self, item, column):
        """
        Slot for item pressed.
        """

        if QtGui.QApplication.mouseButtons() & QtCore.Qt.RightButton:
            self._showContextualMenu()

    def _showContextualMenu(self):
        """
        Contextual menu.
        """

        menu = QtGui.QMenu()
        change_symbol_action = QtGui.QAction("Change symbol", menu)
        change_symbol_action.setIcon(QtGui.QIcon(":/icons/node_conception.svg"))
        self.connect(change_symbol_action, QtCore.SIGNAL('triggered()'), self._changeSymbolSlot)
        menu.addAction(change_symbol_action)
        menu.exec_(QtGui.QCursor.pos())

    def _changeSymbolSlot(self):
        """
        Change a symbol for a QEMU VM.
        """

        dialog = SymbolSelectionDialog(self)
        dialog.show()
        if dialog.exec_():
            normal_symbol, selected_symbol = dialog.getSymbols()
            category = dialog.getCategory()
            item = self.uiQemuVMsTreeWidget.currentItem()
            if item:
                item.setIcon(0, QtGui.QIcon(normal_symbol))
                key = item.data(0, QtCore.Qt.UserRole)
                qemu_vm = self._qemu_vms[key]
                qemu_vm["default_symbol"] = normal_symbol
                qemu_vm["hover_symbol"] = selected_symbol
                qemu_vm["category"] = category

    def loadPreferences(self):
        """
        Loads the QEMU VM preferences.
        """

        qemu_module = Qemu.instance()
        self._qemu_vms = copy.deepcopy(qemu_module.qemuVMs())
        self._items.clear()

        for key, qemu_vm in self._qemu_vms.items():
            item = QtGui.QTreeWidgetItem(self.uiQemuVMsTreeWidget)
            item.setText(0, qemu_vm["name"])
            item.setIcon(0, QtGui.QIcon(qemu_vm["default_symbol"]))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiQemuVMsTreeWidget.setCurrentItem(self._items[0])
            self.uiQemuVMsTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def savePreferences(self):
        """
        Saves the QEMU VM preferences.
        """

        Qemu.instance().setQemuVMs(self._qemu_vms)
