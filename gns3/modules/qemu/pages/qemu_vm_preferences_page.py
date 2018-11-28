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

from gns3.qt import QtCore, QtWidgets, qpartial
from gns3.main_window import MainWindow
from gns3.dialogs.configuration_dialog import ConfigurationDialog
from gns3.compute_manager import ComputeManager
from gns3.template_manager import TemplateManager
from gns3.controller import Controller
from gns3.template import Template

from ..settings import QEMU_VM_SETTINGS
from ..ui.qemu_vm_preferences_page_ui import Ui_QemuVMPreferencesPageWidget
from ..pages.qemu_vm_configuration_page import QemuVMConfigurationPage
from ..dialogs.qemu_vm_wizard import QemuVMWizard


class QemuVMPreferencesPage(QtWidgets.QWidget, Ui_QemuVMPreferencesPageWidget):
    """
    QWidget preference page for QEMU VM preferences.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._qemu_vms = {}
        self._items = []

        self.uiNewQemuVMPushButton.clicked.connect(self._qemuVMNewSlot)
        self.uiCopyQemuVMPushButton.clicked.connect(self._qemuVMCopySlot)
        self.uiEditQemuVMPushButton.clicked.connect(self._qemuVMEditSlot)
        self.uiDeleteQemuVMPushButton.clicked.connect(self._qemuVMDeleteSlot)
        self.uiQemuVMsTreeWidget.itemSelectionChanged.connect(self._qemuVMChangedSlot)

    def _createSectionItem(self, name):
        """
        Adds a new section to the tree widget.

        :param name: section name
        """

        section_item = QtWidgets.QTreeWidgetItem(self.uiQemuVMInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, qemu_vm):
        """
        Refreshes the content of the tree widget.
        """

        self.uiQemuVMInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtWidgets.QTreeWidgetItem(section_item, ["Template name:", qemu_vm["name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Template ID:", qemu_vm.get("template_id", "none")])
        if qemu_vm["linked_clone"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Default name format:", qemu_vm["default_name_format"]])
        try:
            QtWidgets.QTreeWidgetItem(section_item, ["Server:", ComputeManager.instance().getCompute(qemu_vm["compute_id"]).name()])
        except KeyError:
            pass
        QtWidgets.QTreeWidgetItem(section_item, ["Console type:", qemu_vm["console_type"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Auto start console:", "{}".format(qemu_vm["console_auto_start"])])
        QtWidgets.QTreeWidgetItem(section_item, ["CPUs:", str(qemu_vm["cpus"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Memory:", "{} MB".format(qemu_vm["ram"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Linked base VM:", "{}".format(qemu_vm["linked_clone"])])

        if qemu_vm["qemu_path"]:
            QtWidgets.QTreeWidgetItem(section_item, ["QEMU binary:", os.path.basename(qemu_vm["qemu_path"])])

        # fill out the Hard disks section
        if qemu_vm["hda_disk_image"] or qemu_vm["hdb_disk_image"] or qemu_vm["hdc_disk_image"] or qemu_vm["hdd_disk_image"]:
            section_item = self._createSectionItem("Hard disks")
            if qemu_vm["hda_disk_image"]:
                QtWidgets.QTreeWidgetItem(section_item, ["Disk image (hda):", qemu_vm["hda_disk_image"]])
                QtWidgets.QTreeWidgetItem(section_item, ["Disk interface (hda):", qemu_vm["hda_disk_interface"]])
            if qemu_vm["hdb_disk_image"]:
                QtWidgets.QTreeWidgetItem(section_item, ["Disk image (hdb):", qemu_vm["hdb_disk_image"]])
                QtWidgets.QTreeWidgetItem(section_item, ["Disk interface (hdb):", qemu_vm["hdb_disk_interface"]])
            if qemu_vm["hdc_disk_image"]:
                QtWidgets.QTreeWidgetItem(section_item, ["Disk image (hdc):", qemu_vm["hdc_disk_image"]])
                QtWidgets.QTreeWidgetItem(section_item, ["Disk interface (hdc):", qemu_vm["hdc_disk_interface"]])
            if qemu_vm["hdd_disk_image"]:
                QtWidgets.QTreeWidgetItem(section_item, ["Disk image (hdd):", qemu_vm["hdd_disk_image"]])
                QtWidgets.QTreeWidgetItem(section_item, ["Disk interface (hdd):", qemu_vm["hdd_disk_interface"]])
            if qemu_vm["cdrom_image"]:
                QtWidgets.QTreeWidgetItem(section_item, ["CD/DVD image:", qemu_vm["cdrom_image"]])
            if qemu_vm["bios_image"]:
                QtWidgets.QTreeWidgetItem(section_item, ["Bios image:", qemu_vm["bios_image"]])

        # fill out the Network section
        section_item = self._createSectionItem("Network")
        QtWidgets.QTreeWidgetItem(section_item, ["Adapters:", str(qemu_vm["adapters"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Name format:", qemu_vm["port_name_format"]])
        if qemu_vm["port_segment_size"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Segment size:", str(qemu_vm["port_segment_size"])])
        if qemu_vm["first_port_name"]:
            QtWidgets.QTreeWidgetItem(section_item, ["First port name:", qemu_vm["first_port_name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Type:", qemu_vm["adapter_type"]])
        if qemu_vm["mac_address"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Base MAC address:", qemu_vm["mac_address"]])

        # fill out the Linux boot section
        if qemu_vm["initrd"] or qemu_vm["kernel_image"] or qemu_vm["kernel_command_line"]:
            section_item = self._createSectionItem("Linux boot")
            if qemu_vm["initrd"]:
                QtWidgets.QTreeWidgetItem(section_item, ["Initial RAM disk:", qemu_vm["initrd"]])
            if qemu_vm["kernel_image"]:
                QtWidgets.QTreeWidgetItem(section_item, ["Kernel image:", qemu_vm["kernel_image"]])
            if qemu_vm["kernel_command_line"]:
                QtWidgets.QTreeWidgetItem(section_item, ["Kernel command line:", qemu_vm["kernel_command_line"]])

        # performance section
        section_item = self._createSectionItem("Optimizations")
        if qemu_vm["cpu_throttling"]:
            QtWidgets.QTreeWidgetItem(section_item, ["CPU throttling:", "{}%".format(qemu_vm["cpu_throttling"])])
        else:
            QtWidgets.QTreeWidgetItem(section_item, ["CPU throttling:", "disabled"])
        QtWidgets.QTreeWidgetItem(section_item, ["Process priority:", qemu_vm["process_priority"]])

        # fill out the Additional options section
        section_item = self._createSectionItem("Additional options")
        if qemu_vm["options"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Options:", qemu_vm["options"]])
        QtWidgets.QTreeWidgetItem(section_item, ["On close:", "{}".format(qemu_vm["on_close"])])

        self.uiQemuVMInfoTreeWidget.expandAll()
        self.uiQemuVMInfoTreeWidget.resizeColumnToContents(0)
        self.uiQemuVMInfoTreeWidget.resizeColumnToContents(1)
        self.uiQemuVMsTreeWidget.setMaximumWidth(self.uiQemuVMsTreeWidget.sizeHintForColumn(0) + 10)

    def _qemuVMChangedSlot(self):
        """
        Loads a selected QEMU VM from the tree widget.
        """

        selection = self.uiQemuVMsTreeWidget.selectedItems()
        self.uiDeleteQemuVMPushButton.setEnabled(len(selection) != 0)
        single_selected = len(selection) == 1
        self.uiEditQemuVMPushButton.setEnabled(single_selected)
        self.uiCopyQemuVMPushButton.setEnabled(single_selected)

        if single_selected:
            key = selection[0].data(0, QtCore.Qt.UserRole)
            qemu_vm = self._qemu_vms[key]
            self._refreshInfo(qemu_vm)
        else:
            self.uiQemuVMInfoTreeWidget.clear()

    def _qemuVMNewSlot(self):
        """
        Creates a new VM.
        """

        wizard = QemuVMWizard(self._qemu_vms, parent=self)
        wizard.show()
        if wizard.exec_():

            new_vm_settings = wizard.getSettings()
            key = "{server}:{name}".format(server=new_vm_settings["compute_id"], name=new_vm_settings["name"])
            if key in self._qemu_vms:
                QtWidgets.QMessageBox.critical(self, "New QEMU VM", "VM name {} already exists".format(new_vm_settings["name"]))
                return
            self._qemu_vms[key] = QEMU_VM_SETTINGS.copy()
            self._qemu_vms[key].update(new_vm_settings)

            item = QtWidgets.QTreeWidgetItem(self.uiQemuVMsTreeWidget)
            item.setText(0, self._qemu_vms[key]["name"])
            Controller.instance().getSymbolIcon(self._qemu_vms[key]["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiQemuVMsTreeWidget.setCurrentItem(item)

    def _qemuVMCopySlot(self):
        """
        Copies a QEMU VM.
        """

        item = self.uiQemuVMsTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            copied_vm_settings = copy.deepcopy(self._qemu_vms[key])
            new_name, ok = QtWidgets.QInputDialog.getText(self, "Copy Qemu template", "Template name:", QtWidgets.QLineEdit.Normal, "Copy of {}".format(copied_vm_settings["name"]))
            if ok:
                key = "{server}:{name}".format(server=copied_vm_settings["compute_id"], name=new_name)
                if key in self._qemu_vms:
                    QtWidgets.QMessageBox.critical(self, "Qemu template", "Qemu template name {} already exists".format(new_name))
                    return
                self._qemu_vms[key] = QEMU_VM_SETTINGS.copy()
                self._qemu_vms[key].update(copied_vm_settings)
                self._qemu_vms[key]["name"] = new_name
                self._qemu_vms[key].pop("template_id", None)

                item = QtWidgets.QTreeWidgetItem(self.uiQemuVMsTreeWidget)
                item.setText(0, self._qemu_vms[key]["name"])
                Controller.instance().getSymbolIcon(self._qemu_vms[key]["symbol"], qpartial(self._setItemIcon, item))
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
                # update the icon
                Controller.instance().getSymbolIcon(qemu_vm["symbol"], qpartial(self._setItemIcon, item))

                if qemu_vm["name"] != item.text(0):
                    new_key = "{server}:{name}".format(server=qemu_vm["compute_id"], name=qemu_vm["name"])
                    if new_key in self._qemu_vms:
                        QtWidgets.QMessageBox.critical(self, "QEMU VM", "QEMU VM name {} already exists for server {}".format(qemu_vm["name"],
                                                                                                                              qemu_vm["compute_id"]))
                        qemu_vm["name"] = item.text(0)
                        return
                    self._qemu_vms[new_key] = self._qemu_vms[key]
                    del self._qemu_vms[key]
                    item.setText(0, qemu_vm["name"])
                    item.setData(0, QtCore.Qt.UserRole, new_key)

                self._refreshInfo(qemu_vm)

    def _qemuVMDeleteSlot(self):
        """
        Deletes a QEMU VM.
        """

        for item in self.uiQemuVMsTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)
                del self._qemu_vms[key]
                self.uiQemuVMsTreeWidget.takeTopLevelItem(self.uiQemuVMsTreeWidget.indexOfTopLevelItem(item))

    def loadPreferences(self):
        """
        Loads the QEMU VM preferences.
        """

        self._qemu_vms  = {}
        templates = TemplateManager.instance().templates()
        for template_id, template in templates.items():
            if template.template_type() == "qemu" and not template.builtin():
                name = template.name()
                server = template.compute_id()
                #TODO: use template id for the key
                key = "{server}:{name}".format(server=server, name=name)
                self._qemu_vms[key] = copy.deepcopy(template.settings())

        self._items.clear()
        for key, qemu_vm in self._qemu_vms.items():
            item = QtWidgets.QTreeWidgetItem(self.uiQemuVMsTreeWidget)
            item.setText(0, qemu_vm["name"])
            Controller.instance().getSymbolIcon(qemu_vm["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiQemuVMsTreeWidget.setCurrentItem(self._items[0])
            self.uiQemuVMsTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.uiQemuVMsTreeWidget.setMaximumWidth(self.uiQemuVMsTreeWidget.sizeHintForColumn(0) + 10)

    def _setItemIcon(self, item, icon):
        item.setIcon(0, icon)
        self.uiQemuVMsTreeWidget.setMaximumWidth(self.uiQemuVMsTreeWidget.sizeHintForColumn(0) + 10)

    def savePreferences(self):
        """
        Saves the QEMU VM preferences.
        """

        templates = []
        for template in TemplateManager.instance().templates().values():
            if template.template_type() != "qemu":
                templates.append(template)
        for template_settings in self._qemu_vms.values():
            templates.append(Template(template_settings))
        TemplateManager.instance().updateList(templates)

