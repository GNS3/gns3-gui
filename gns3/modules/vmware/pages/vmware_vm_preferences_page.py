# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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
Configuration page for VMware VM preferences.
"""

import copy

from gns3.qt import QtCore, QtGui, QtWidgets
from gns3.main_window import MainWindow
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.dialogs.configuration_dialog import ConfigurationDialog

from .. import VMware
from ..settings import VMWARE_VM_SETTINGS
from ..ui.vmware_vm_preferences_page_ui import Ui_VMwareVMPreferencesPageWidget
from ..pages.vmware_vm_configuration_page import VMwareVMConfigurationPage
from ..dialogs.vmware_vm_wizard import VMwareVMWizard


class VMwareVMPreferencesPage(QtWidgets.QWidget, Ui_VMwareVMPreferencesPageWidget):

    """
    QWidget preference page for VMware VM preferences.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._vmware_vms = {}
        self._items = []

        self.uiNewVMwareVMPushButton.clicked.connect(self._vmwareVMNewSlot)
        self.uiEditVMwareVMPushButton.clicked.connect(self._vmwareVMEditSlot)
        self.uiDeleteVMwareVMPushButton.clicked.connect(self._vmwareVMDeleteSlot)
        self.uiVMwareVMsTreeWidget.itemSelectionChanged.connect(self._vmwareVMChangedSlot)
        self.uiVMwareVMsTreeWidget.itemPressed.connect(self._vmwareVMPressedSlot)

    def _createSectionItem(self, name):

        section_item = QtWidgets.QTreeWidgetItem(self.uiVMwareVMInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, vmware_vm):

        self.uiVMwareVMInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtWidgets.QTreeWidgetItem(section_item, ["VM name:", vmware_vm["name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Server:", vmware_vm["server"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Remote console enabled:", "{}".format(vmware_vm["enable_remote_console"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Headless mode enabled:", "{}".format(vmware_vm["headless"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Linked base VM:", "{}".format(vmware_vm["linked_base"])])

        self.uiVMwareVMInfoTreeWidget.expandAll()
        self.uiVMwareVMInfoTreeWidget.resizeColumnToContents(0)
        self.uiVMwareVMInfoTreeWidget.resizeColumnToContents(1)

    def _vmwareVMChangedSlot(self):
        """
        Loads a selected VMware VM from the tree widget.
        """

        selection = self.uiVMwareVMsTreeWidget.selectedItems()
        self.uiDeleteVMwareVMPushButton.setEnabled(len(selection) != 0)
        single_selected = len(selection) == 1
        self.uiEditVMwareVMPushButton.setEnabled(single_selected)

        if single_selected:
            key = selection[0].data(0, QtCore.Qt.UserRole)
            vmware_vm = self._vmware_vms[key]
            self._refreshInfo(vmware_vm)
        else:
            self.uiVMwareVMInfoTreeWidget.clear()

    def _vmwareVMNewSlot(self):
        """
        Creates a new VMware VM.
        """

        wizard = VMwareVMWizard(self._vmware_vms, parent=self)
        wizard.show()
        if wizard.exec_():

            new_vm_settings = wizard.getSettings()
            key = "{server}:{name}".format(server=new_vm_settings["server"], name=new_vm_settings["name"])
            self._vmware_vms[key] = VMWARE_VM_SETTINGS.copy()
            self._vmware_vms[key].update(new_vm_settings)

            item = QtWidgets.QTreeWidgetItem(self.uiVMwareVMsTreeWidget)
            item.setText(0, self._vmware_vms[key]["name"])
            item.setIcon(0, QtGui.QIcon(self._vmware_vms[key]["default_symbol"]))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiVMwareVMsTreeWidget.setCurrentItem(item)

    def _vmwareVMEditSlot(self):
        """
        Edits a VMware VM.
        """

        item = self.uiVMwareVMsTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            vmware_vm = self._vmware_vms[key]
            dialog = ConfigurationDialog(vmware_vm["name"], vmware_vm, VMwareVMConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                if vmware_vm["name"] != item.text(0):
                    new_key = "{server}:{name}".format(server=vmware_vm["server"], name=vmware_vm["name"])
                    if new_key in self._vmware_vms:
                        QtWidgets.QMessageBox.critical(self, "VMware VM", "VMware VM name {} already exists for server {}".format(vmware_vm["name"],
                                                                                                                                  vmware_vm["server"]))
                        vmware_vm["name"] = item.text(0)
                        return
                    self._vmware_vms[new_key] = self._vmware_vms[key]
                    del self._vmware_vms[key]
                    item.setText(0, vmware_vm["name"])
                    item.setData(0, QtCore.Qt.UserRole, new_key)
                self._refreshInfo(vmware_vm)

    def _vmwareVMDeleteSlot(self):
        """
        Deletes a VMware VM.
        """

        for item in self.uiVMwareVMsTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)
                del self._vmware_vms[key]
                self.uiVMwareVMsTreeWidget.takeTopLevelItem(self.uiVMwareVMsTreeWidget.indexOfTopLevelItem(item))

    def _vmwareVMPressedSlot(self, item, column):
        """
        Slot for item pressed.

        :param item: ignored
        :param column: ignored
        """

        if QtWidgets.QApplication.mouseButtons() & QtCore.Qt.RightButton:
            self._showContextualMenu()

    def _showContextualMenu(self):
        """
        Contextual menu.
        """

        menu = QtWidgets.QMenu()

        change_symbol_action = QtWidgets.QAction("Change symbol", menu)
        change_symbol_action.setIcon(QtGui.QIcon(":/icons/node_conception.svg"))
        change_symbol_action.setEnabled(len(self.uiVMwareVMsTreeWidget.selectedItems()) == 1)
        change_symbol_action.triggered.connect(self._changeSymbolSlot)
        menu.addAction(change_symbol_action)

        delete_action = QtWidgets.QAction("Delete", menu)
        delete_action.triggered.connect(self._vmwareVMDeleteSlot)
        menu.addAction(delete_action)

        menu.exec_(QtGui.QCursor.pos())

    def _changeSymbolSlot(self):
        """
        Change a symbol for a VMware VM.
        """

        item = self.uiVMwareVMsTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            vmware_vm = self._vmware_vms[key]
            dialog = SymbolSelectionDialog(self, symbol=vmware_vm["default_symbol"], category=vmware_vm["category"])
            dialog.show()
            if dialog.exec_():
                normal_symbol, selected_symbol = dialog.getSymbols()
                category = dialog.getCategory()
                item.setIcon(0, QtGui.QIcon(normal_symbol))
                vmware_vm["default_symbol"] = normal_symbol
                vmware_vm["hover_symbol"] = selected_symbol
                vmware_vm["category"] = category

    def loadPreferences(self):
        """
        Loads the VMware VM preferences.
        """

        vmware_module = VMware.instance()
        self._vmware_vms = copy.deepcopy(vmware_module.vmwareVMs())
        self._items.clear()

        for key, vmware_vm in self._vmware_vms.items():
            item = QtWidgets.QTreeWidgetItem(self.uiVMwareVMsTreeWidget)
            item.setText(0, vmware_vm["name"])
            item.setIcon(0, QtGui.QIcon(vmware_vm["default_symbol"]))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiVMwareVMsTreeWidget.setCurrentItem(self._items[0])
            self.uiVMwareVMsTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def savePreferences(self):
        """
        Saves the VMware VM preferences.
        """

        VMware.instance().setVMwareVMs(self._vmware_vms)
