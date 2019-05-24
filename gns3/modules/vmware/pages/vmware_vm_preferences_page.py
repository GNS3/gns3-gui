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

from gns3.qt import QtCore, QtWidgets, qpartial
from gns3.controller import Controller
from gns3.main_window import MainWindow
from gns3.dialogs.configuration_dialog import ConfigurationDialog
from gns3.compute_manager import ComputeManager
from gns3.template_manager import TemplateManager
from gns3.template import Template

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

    def _createSectionItem(self, name):
        """
        Adds a new section to the tree widget.

        :param name: section name
        """

        section_item = QtWidgets.QTreeWidgetItem(self.uiVMwareVMInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, vmware_vm):
        """
        Refreshes the content of the tree widget.
        """

        self.uiVMwareVMInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtWidgets.QTreeWidgetItem(section_item, ["Template name:", vmware_vm["name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Template ID:", vmware_vm.get("template_id", "none")])
        if vmware_vm["linked_clone"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Default name format:", vmware_vm["default_name_format"]])
        try:
            QtWidgets.QTreeWidgetItem(section_item, ["Server:", ComputeManager.instance().getCompute(vmware_vm["compute_id"]).name()])
        except KeyError:
            pass
        QtWidgets.QTreeWidgetItem(section_item, ["Headless mode enabled:", "{}".format(vmware_vm["headless"])])
        QtWidgets.QTreeWidgetItem(section_item, ["On close:", "{}".format(vmware_vm["on_close"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Linked base VM:", "{}".format(vmware_vm["linked_clone"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Console type:", vmware_vm["console_type"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Auto start console:", "{}".format(vmware_vm["console_auto_start"])])

        # fill out the Network section
        section_item = self._createSectionItem("Network")
        QtWidgets.QTreeWidgetItem(section_item, ["Adapters:", str(vmware_vm["adapters"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Name format:", vmware_vm["port_name_format"]])
        if vmware_vm["port_segment_size"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Segment size:", str(vmware_vm["port_segment_size"])])
        if vmware_vm["first_port_name"]:
            QtWidgets.QTreeWidgetItem(section_item, ["First port name:", vmware_vm["first_port_name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Use any adapter:", "{}".format(vmware_vm["use_any_adapter"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Type:", vmware_vm["adapter_type"]])

        self.uiVMwareVMInfoTreeWidget.expandAll()
        self.uiVMwareVMInfoTreeWidget.resizeColumnToContents(0)
        self.uiVMwareVMInfoTreeWidget.resizeColumnToContents(1)
        self.uiVMwareVMsTreeWidget.setMaximumWidth(self.uiVMwareVMsTreeWidget.sizeHintForColumn(0) + 10)

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
            key = "{server}:{name}".format(server=new_vm_settings["compute_id"], name=new_vm_settings["name"])
            self._vmware_vms[key] = VMWARE_VM_SETTINGS.copy()
            self._vmware_vms[key].update(new_vm_settings)

            item = QtWidgets.QTreeWidgetItem(self.uiVMwareVMsTreeWidget)
            item.setText(0, self._vmware_vms[key]["name"])
            Controller.instance().getSymbolIcon(self._vmware_vms[key]["symbol"], qpartial(self._setItemIcon, item))
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
                # update the icon
                Controller.instance().getSymbolIcon(vmware_vm["symbol"], qpartial(self._setItemIcon, item))

                if vmware_vm["name"] != item.text(0):
                    new_key = "{server}:{name}".format(server=vmware_vm["compute_id"], name=vmware_vm["name"])
                    if new_key in self._vmware_vms:
                        QtWidgets.QMessageBox.critical(self, "VMware VM", "VMware VM name {} already exists for server {}".format(vmware_vm["name"],
                                                                                                                                  vmware_vm["compute_id"]))
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

    def loadPreferences(self):
        """
        Loads the VMware VM preferences.
        """

        self._vmware_vms = {}
        templates = TemplateManager.instance().templates()
        for template_id, template in templates.items():
            if template.template_type() == "vmware" and not template.builtin():
                name = template.name()
                server = template.compute_id()
                #TODO: use template id for the key
                key = "{server}:{name}".format(server=server, name=name)
                self._vmware_vms[key] = copy.deepcopy(template.settings())

        self._items.clear()
        for key, vmware_vm in self._vmware_vms.items():
            item = QtWidgets.QTreeWidgetItem(self.uiVMwareVMsTreeWidget)
            item.setText(0, vmware_vm["name"])
            Controller.instance().getSymbolIcon(vmware_vm["symbol"], qpartial(self._setItemIcon, item))

            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiVMwareVMsTreeWidget.setCurrentItem(self._items[0])
            self.uiVMwareVMsTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.uiVMwareVMsTreeWidget.setMaximumWidth(self.uiVMwareVMsTreeWidget.sizeHintForColumn(0) + 10)

    def savePreferences(self):
        """
        Saves the VMware VM preferences.
        """

        templates = []
        for template in TemplateManager.instance().templates().values():
            if template.template_type() != "vmware":
                templates.append(template)
        for template_settings in self._vmware_vms.values():
            templates.append(Template(template_settings))
        TemplateManager.instance().updateList(templates)


    def _setItemIcon(self, item, icon):

        item.setIcon(0, icon)
        self.uiVMwareVMsTreeWidget.setMaximumWidth(self.uiVMwareVMsTreeWidget.sizeHintForColumn(0) + 10)
