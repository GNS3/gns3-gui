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
Configuration page for VirtualBox VM preferences.
"""

import copy

from gns3.qt import QtCore, QtGui
from gns3.node import Node
from gns3.main_window import MainWindow
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.dialogs.configuration_dialog import ConfigurationDialog

from .. import VirtualBox
from ..ui.virtualbox_vm_preferences_page_ui import Ui_VirtualBoxVMPreferencesPageWidget
from ..pages.virtualbox_vm_configuration_page import virtualBoxVMConfigurationPage
from ..dialogs.virtualbox_vm_wizard import VirtualBoxVMWizard


class VirtualBoxVMPreferencesPage(QtGui.QWidget, Ui_VirtualBoxVMPreferencesPageWidget):
    """
    QWidget preference page for VirtualBox VM preferences.
    """

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._virtualbox_vms = {}
        self._items = []

        self.uiNewVirtualBoxVMPushButton.clicked.connect(self._vboxVMNewSlot)
        self.uiEditVirtualBoxVMPushButton.clicked.connect(self._vboxVMEditSlot)
        self.uiDeleteVirtualBoxVMPushButton.clicked.connect(self._vboxVMDeleteSlot)
        self.uiVirtualBoxVMsTreeWidget.currentItemChanged.connect(self._vboxVMChangedSlot)
        self.uiVirtualBoxVMsTreeWidget.itemPressed.connect(self._vboxVMPressedSlot)

    def _vboxVMChangedSlot(self, current, previous):
        """
        Loads a selected VirtualBox VM from the tree widget.

        :param current: current QTreeWidgetItem instance
        :param previous: ignored
        """

        if not current:
            self.uiVirtualBoxVMInfoTreeWidget.clear()
            return

        self.uiEditVirtualBoxVMPushButton.setEnabled(True)
        self.uiDeleteVirtualBoxVMPushButton.setEnabled(True)
        key = current.data(0, QtCore.Qt.UserRole)
        vbox_vm = self._virtualbox_vms[key]
        self._refreshInfo(vbox_vm)

    def _createSectionItem(self, name):

        section_item = QtGui.QTreeWidgetItem(self.uiVirtualBoxVMInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, vbox_vm):

        self.uiVirtualBoxVMInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtGui.QTreeWidgetItem(section_item, ["VM name:", vbox_vm["vmname"]])
        QtGui.QTreeWidgetItem(section_item, ["Server:", vbox_vm["server"]])
        QtGui.QTreeWidgetItem(section_item, ["Remote console enabled:", "{}".format(vbox_vm["enable_console"])])
        QtGui.QTreeWidgetItem(section_item, ["Headless mode enabled:", "{}".format(vbox_vm["headless"])])

        # fill out the Network section
        section_item = self._createSectionItem("Network")
        QtGui.QTreeWidgetItem(section_item, ["Adapters:", str(vbox_vm["adapters"])])
        QtGui.QTreeWidgetItem(section_item, ["Start at:", str(vbox_vm["adapter_start_index"])])
        QtGui.QTreeWidgetItem(section_item, ["Type:", vbox_vm["adapter_type"]])

        self.uiVirtualBoxVMInfoTreeWidget.expandAll()
        self.uiVirtualBoxVMInfoTreeWidget.resizeColumnToContents(0)
        self.uiVirtualBoxVMInfoTreeWidget.resizeColumnToContents(1)

    def _vboxVMNewSlot(self):
        """
        Creates a new VirtualBox VM.
        """

        wizard = VirtualBoxVMWizard(self._virtualbox_vms, parent=self)
        wizard.show()
        if wizard.exec_():

            new_vm_settings = wizard.getSettings()
            if not new_vm_settings:
                return

            key = "{server}:{vmname}".format(server=new_vm_settings["server"], vmname=new_vm_settings["vmname"])
            self._virtualbox_vms[key] = {"vmname": "",
                                         "default_symbol": ":/symbols/vbox_guest.normal.svg",
                                         "hover_symbol": ":/symbols/vbox_guest.selected.svg",
                                         "category": Node.end_devices,
                                         "adapters": 1,
                                         "adapter_start_index": 0,
                                         "adapter_type": "Automatic",
                                         "headless": False,
                                         "enable_console": False,
                                         "server": "local"}

            self._virtualbox_vms[key].update(new_vm_settings)
            item = QtGui.QTreeWidgetItem(self.uiVirtualBoxVMsTreeWidget)
            item.setText(0, self._virtualbox_vms[key]["vmname"])
            item.setIcon(0, QtGui.QIcon(self._virtualbox_vms[key]["default_symbol"]))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiVirtualBoxVMsTreeWidget.setCurrentItem(item)

    def _vboxVMEditSlot(self):
        """
        Edits a VirtualBox VM.
        """

        item = self.uiVirtualBoxVMsTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            vbox_vm = self._virtualbox_vms[key]
            dialog = ConfigurationDialog(vbox_vm["vmname"], vbox_vm, virtualBoxVMConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                if vbox_vm["vmname"] != item.text(0):
                    if "{}:{}".format(vbox_vm["server"], vbox_vm["vmname"]) in self._virtualbox_vms:
                        # FIXME: bug when changing name
                        QtGui.QMessageBox.critical(self, "New VirtualBox VM", "VM name {} already exists".format(vbox_vm["vmname"]))
                        vbox_vm["vmname"] = item.text(0)
                    item.setText(0, vbox_vm["vmname"])
                self._refreshInfo(vbox_vm)

    def _vboxVMDeleteSlot(self):
        """
        Deletes a VirtualBox VM.
        """

        item = self.uiVirtualBoxVMsTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            del self._virtualbox_vms[key]
            self.uiVirtualBoxVMsTreeWidget.takeTopLevelItem(self.uiVirtualBoxVMsTreeWidget.indexOfTopLevelItem(item))

    def _vboxVMPressedSlot(self, item, column):
        """
        Slot for item pressed.

        :param item: ignored
        :param column: ignored
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
        Change a symbol for a VirtualBox VM.
        """

        dialog = SymbolSelectionDialog(self)
        dialog.show()
        if dialog.exec_():
            normal_symbol, selected_symbol = dialog.getSymbols()
            category = dialog.getCategory()
            item = self.uiVirtualBoxVMsTreeWidget.currentItem()
            if item:
                item.setIcon(0, QtGui.QIcon(normal_symbol))
                key = item.data(0, QtCore.Qt.UserRole)
                vbox_vm = self._virtualbox_vms[key]
                vbox_vm["default_symbol"] = normal_symbol
                vbox_vm["hover_symbol"] = selected_symbol
                vbox_vm["category"] = category

    def loadPreferences(self):
        """
        Loads the VirtualBox VM preferences.
        """

        vbox_module = VirtualBox.instance()
        self._virtualbox_vms = copy.deepcopy(vbox_module.virtualBoxVMs())
        self._items.clear()

        for key, vbox_vm in self._virtualbox_vms.items():
            item = QtGui.QTreeWidgetItem(self.uiVirtualBoxVMsTreeWidget)
            item.setText(0, vbox_vm["vmname"])
            item.setIcon(0, QtGui.QIcon(vbox_vm["default_symbol"]))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiVirtualBoxVMsTreeWidget.setCurrentItem(self._items[0])
            self.uiVirtualBoxVMsTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def savePreferences(self):
        """
        Saves the VirtualBox VM preferences.
        """

        #self._vboxVMSaveSlot()
        VirtualBox.instance().setVirtualBoxVMs(self._virtualbox_vms)
