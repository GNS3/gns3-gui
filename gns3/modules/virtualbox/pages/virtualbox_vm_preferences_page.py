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

from gns3.qt import QtCore, QtWidgets, qpartial
from gns3.controller import Controller
from gns3.main_window import MainWindow
from gns3.dialogs.configuration_dialog import ConfigurationDialog
from gns3.compute_manager import ComputeManager

from .. import VirtualBox
from ..settings import VBOX_VM_SETTINGS
from ..ui.virtualbox_vm_preferences_page_ui import Ui_VirtualBoxVMPreferencesPageWidget
from ..pages.virtualbox_vm_configuration_page import VirtualBoxVMConfigurationPage
from ..dialogs.virtualbox_vm_wizard import VirtualBoxVMWizard


class VirtualBoxVMPreferencesPage(QtWidgets.QWidget, Ui_VirtualBoxVMPreferencesPageWidget):

    """
    QWidget preference page for VirtualBox VM preferences.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._virtualbox_vms = {}
        self._items = []

        self.uiNewVirtualBoxVMPushButton.clicked.connect(self._vboxVMNewSlot)
        self.uiEditVirtualBoxVMPushButton.clicked.connect(self._vboxVMEditSlot)
        self.uiDeleteVirtualBoxVMPushButton.clicked.connect(self._vboxVMDeleteSlot)
        self.uiVirtualBoxVMsTreeWidget.itemSelectionChanged.connect(self._vboxVMChangedSlot)

    def _createSectionItem(self, name):

        section_item = QtWidgets.QTreeWidgetItem(self.uiVirtualBoxVMInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, vbox_vm):

        self.uiVirtualBoxVMInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtWidgets.QTreeWidgetItem(section_item, ["Template name:", vbox_vm["name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["VirtualBox name:", vbox_vm["vmname"]])
        if vbox_vm["linked_base"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Default name format:", vbox_vm["default_name_format"]])
        QtWidgets.QTreeWidgetItem(section_item, ["RAM:", str(vbox_vm["ram"])])
        try:
            QtWidgets.QTreeWidgetItem(section_item, ["Server:", ComputeManager.instance().getCompute(vbox_vm["server"]).name()])
        except KeyError:
            pass
        QtWidgets.QTreeWidgetItem(section_item, ["Headless mode enabled:", "{}".format(vbox_vm["headless"])])
        QtWidgets.QTreeWidgetItem(section_item, ["ACPI shutdown enabled:", "{}".format(vbox_vm["acpi_shutdown"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Linked base VM:", "{}".format(vbox_vm["linked_base"])])

        # fill out the Network section
        section_item = self._createSectionItem("Network")
        QtWidgets.QTreeWidgetItem(section_item, ["Adapters:", str(vbox_vm["adapters"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Name format:", vbox_vm["port_name_format"]])
        if vbox_vm["port_segment_size"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Segment size:", str(vbox_vm["port_segment_size"])])
        if vbox_vm["first_port_name"]:
            QtWidgets.QTreeWidgetItem(section_item, ["First port name:", vbox_vm["first_port_name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Use any adapter:", "{}".format(vbox_vm["use_any_adapter"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Type:", vbox_vm["adapter_type"]])

        self.uiVirtualBoxVMInfoTreeWidget.expandAll()
        self.uiVirtualBoxVMInfoTreeWidget.resizeColumnToContents(0)
        self.uiVirtualBoxVMInfoTreeWidget.resizeColumnToContents(1)
        self.uiVirtualBoxVMsTreeWidget.setMaximumWidth(self.uiVirtualBoxVMsTreeWidget.sizeHintForColumn(0) + 10)

    def _vboxVMChangedSlot(self):
        """
        Loads a selected VirtualBox VM from the tree widget.
        """

        selection = self.uiVirtualBoxVMsTreeWidget.selectedItems()
        self.uiDeleteVirtualBoxVMPushButton.setEnabled(len(selection) != 0)
        single_selected = len(selection) == 1
        self.uiEditVirtualBoxVMPushButton.setEnabled(single_selected)

        if single_selected:
            key = selection[0].data(0, QtCore.Qt.UserRole)
            vbox_vm = self._virtualbox_vms[key]
            self._refreshInfo(vbox_vm)
        else:
            self.uiVirtualBoxVMInfoTreeWidget.clear()

    def _vboxVMNewSlot(self):
        """
        Creates a new VirtualBox VM.
        """

        wizard = VirtualBoxVMWizard(self._virtualbox_vms, parent=self)
        wizard.show()
        if wizard.exec_():

            new_vm_settings = wizard.getSettings()
            key = "{server}:{vmname}".format(server=new_vm_settings["server"], vmname=new_vm_settings["vmname"])
            self._virtualbox_vms[key] = VBOX_VM_SETTINGS.copy()
            self._virtualbox_vms[key].update(new_vm_settings)

            item = QtWidgets.QTreeWidgetItem(self.uiVirtualBoxVMsTreeWidget)
            item.setText(0, self._virtualbox_vms[key]["name"])
            Controller.instance().getSymbolIcon(self._virtualbox_vms[key]["symbol"], qpartial(self._setItemIcon, item))
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
            dialog = ConfigurationDialog(vbox_vm["vmname"], vbox_vm, VirtualBoxVMConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                # update the icon
                Controller.instance().getSymbolIcon(vbox_vm["symbol"], qpartial(self._setItemIcon, item))

                if vbox_vm["name"] != item.text(0):
                    item.setText(0, vbox_vm["name"])
                self._refreshInfo(vbox_vm)

    def _vboxVMDeleteSlot(self):
        """
        Deletes a VirtualBox VM.
        """

        for item in self.uiVirtualBoxVMsTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)
                del self._virtualbox_vms[key]
                self.uiVirtualBoxVMsTreeWidget.takeTopLevelItem(self.uiVirtualBoxVMsTreeWidget.indexOfTopLevelItem(item))

    def loadPreferences(self):
        """
        Loads the VirtualBox VM preferences.
        """

        vbox_module = VirtualBox.instance()
        self._virtualbox_vms = copy.deepcopy(vbox_module.VMs())
        self._items.clear()

        for key, vbox_vm in self._virtualbox_vms.items():
            item = QtWidgets.QTreeWidgetItem(self.uiVirtualBoxVMsTreeWidget)
            item.setText(0, vbox_vm["name"])
            Controller.instance().getSymbolIcon(vbox_vm["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiVirtualBoxVMsTreeWidget.setCurrentItem(self._items[0])
            self.uiVirtualBoxVMsTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.uiVirtualBoxVMsTreeWidget.setMaximumWidth(self.uiVirtualBoxVMsTreeWidget.sizeHintForColumn(0) + 10)

    def savePreferences(self):
        """
        Saves the VirtualBox VM preferences.
        """

        # self._vboxVMSaveSlot()
        VirtualBox.instance().setVMs(self._virtualbox_vms)

    def _setItemIcon(self, item, icon):
        item.setIcon(0, icon)
        self.uiVirtualBoxVMsTreeWidget.setMaximumWidth(self.uiVirtualBoxVMsTreeWidget.sizeHintForColumn(0) + 10)
