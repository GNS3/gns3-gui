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
Configuration page for IOU device preferences.
"""

import copy
import os
import sys
import pkg_resources
import shutil

from gns3.qt import QtCore, QtGui
from gns3.main_window import MainWindow
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.dialogs.configuration_dialog import ConfigurationDialog

from .. import IOU
from ..ui.iou_device_preferences_page_ui import Ui_IOUDevicePreferencesPageWidget
from ..pages.iou_device_configuration_page import iouDeviceConfigurationPage
from ..dialogs.iou_device_wizard import IOUDeviceWizard


class IOUDevicePreferencesPage(QtGui.QWidget, Ui_IOUDevicePreferencesPageWidget):
    """
    QWidget preference page for IOU image & device preferences.
    """

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._iou_devices = {}
        self._items = []

        self.uiNewIOUDevicePushButton.clicked.connect(self._iouDeviceNewSlot)
        self.uiEditIOUDevicePushButton.clicked.connect(self._iouDeviceEditSlot)
        self.uiDeleteIOUDevicePushButton.clicked.connect(self._iouDeviceDeleteSlot)
        self.uiIOUDevicesTreeWidget.currentItemChanged.connect(self._iouDeviceChangedSlot)
        self.uiIOUDevicesTreeWidget.itemPressed.connect(self._iouDevicePressedSlot)

        # self.uiIOUPathToolButton.clicked.connect(self._iouImageBrowserSlot)
        # self.uiInitialConfigToolButton.clicked.connect(self._initialConfigBrowserSlot)

    def _iouDeviceChangedSlot(self, current, previous):
        """
        Loads a selected an IOU device from the tree widget.

        :param current: current QTreeWidgetItem instance
        :param previous: ignored
        """

        if not current:
            self.uiIOUDeviceInfoTreeWidget.clear()
            return

        self.uiEditIOUDevicePushButton.setEnabled(True)
        self.uiDeleteIOUDevicePushButton.setEnabled(True)
        key = current.data(0, QtCore.Qt.UserRole)
        iou_device = self._iou_devices[key]
        self._refreshInfo(iou_device)

    def _iouDeviceNewSlot(self):
        """
        Creates a new IOU device.
        """

        wizard = IOUDeviceWizard(self._iou_devices, parent=self)
        wizard.show()
        if wizard.exec_():

            new_device_settings = wizard.getSettings()

            key = "{server}:{name}".format(server=new_device_settings["server"], name=new_device_settings["name"])
            self._iou_devices[key] = {"name": new_device_settings["name"],
                                      "path": new_device_settings["path"],
                                      "default_symbol": new_device_settings["default_symbol"],
                                      "hover_symbol": new_device_settings["hover_symbol"],
                                      "category": new_device_settings["category"],
                                      "image": os.path.basename(new_device_settings["path"]),
                                      "initial_config": new_device_settings["initial_config"],
                                      "use_default_iou_values": True,
                                      "ram": 256,
                                      "nvram": 128,
                                      "ethernet_adapters": 2,
                                      "serial_adapters": 2,
                                      "server": new_device_settings["server"]}

            self._iou_devices[key].update(new_device_settings)
            item = QtGui.QTreeWidgetItem(self.uiIOUDevicesTreeWidget)
            item.setText(0, self._iou_devices[key]["name"])
            item.setIcon(0, QtGui.QIcon(self._iou_devices[key]["default_symbol"]))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiIOUDevicesTreeWidget.setCurrentItem(item)

    def _iouDeviceEditSlot(self):
        """
        Edits an IOU device.
        """

        item = self.uiIOUDevicesTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            iou_device = self._iou_devices[key]
            dialog = ConfigurationDialog(iou_device["name"], iou_device, iouDeviceConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                if iou_device["name"] != item.text(0):
                    if "{}:{}".format(iou_device["server"], iou_device["name"]) in self._iou_devices:
                        # FIXME: bug when changing name
                        QtGui.QMessageBox.critical(self, "New IOU device", "IOU device name {} already exists".format(iou_device["name"]))
                        iou_device["name"] = item.text(0)
                    item.setText(0, iou_device["name"])
                self._refreshInfo(iou_device)

    def _iouDeviceDeleteSlot(self):
        """
        Deletes an IOU device.
        """

        item = self.uiIOUDevicesTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            del self._iou_devices[key]
            self.uiIOUDevicesTreeWidget.takeTopLevelItem(self.uiIOUDevicesTreeWidget.indexOfTopLevelItem(item))

    def _createSectionItem(self, name):

        section_item = QtGui.QTreeWidgetItem(self.uiIOUDeviceInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, iou_device):

        self.uiIOUDeviceInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtGui.QTreeWidgetItem(section_item, ["Name:", iou_device["name"]])
        QtGui.QTreeWidgetItem(section_item, ["Server:", iou_device["server"]])
        QtGui.QTreeWidgetItem(section_item, ["Image:", iou_device["image"]])
        QtGui.QTreeWidgetItem(section_item, ["Initial config:", iou_device["initial_config"]])

        if iou_device["use_default_iou_values"]:
            QtGui.QTreeWidgetItem(section_item, ["RAM:", "default"])
            QtGui.QTreeWidgetItem(section_item, ["NVRAM:", "default"])
        else:
            QtGui.QTreeWidgetItem(section_item, ["RAM:", "{} MiB".format(iou_device["ram"])])
            QtGui.QTreeWidgetItem(section_item, ["NVRAM:", "{} KiB".format(iou_device["nvram"])])

        # fill out the Network section
        section_item = self._createSectionItem("Network")
        QtGui.QTreeWidgetItem(section_item, ["Ethernet adapters:", "{} ({} interfaces)".format(iou_device["ethernet_adapters"],
                                                                                               iou_device["ethernet_adapters"] * 4)])
        QtGui.QTreeWidgetItem(section_item, ["Serial adapters:", "{} ({} interfaces)".format(iou_device["serial_adapters"],
                                                                                             iou_device["serial_adapters"] * 4)])

        self.uiIOUDeviceInfoTreeWidget.expandAll()
        self.uiIOUDeviceInfoTreeWidget.resizeColumnToContents(0)
        self.uiIOUDeviceInfoTreeWidget.resizeColumnToContents(1)

    @staticmethod
    def getIOUImage(parent):
        """

        :param parent: parent widget

        :return: path to the IOU image or None
        """

        destination_directory = os.path.join(MainWindow.instance().settings()["images_path"], "IOU")
        path, _ = QtGui.QFileDialog.getOpenFileNameAndFilter(parent,
                                                             "Select an IOU image",
                                                             destination_directory,
                                                             "All files (*)",
                                                             "IOU image (*.bin *.image)")

        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(parent, "IOU image", "Cannot read {}".format(path))
            return

        try:
            with open(path, "rb") as f:
                # read the first 7 bytes of the file.
                elf_header_start = f.read(7)
        except OSError as e:
            QtGui.QMessageBox.critical(parent, "IOU image", "Cannot read ELF magic number: {}".format(e))
            return

        # file must start with the ELF magic number, be 32-bit, little endian and have an ELF version of 1
        # normal IOS image are big endian!
        if elf_header_start != b'\x7fELF\x01\x01\x01':
            QtGui.QMessageBox.critical(parent, "IOU image", "Sorry, this is not a valid IOU image!")
            return

        if not os.access(path, os.X_OK):
            QtGui.QMessageBox.critical(parent, "IOU image", "{} is not executable".format(path))
            return

        try:
            os.makedirs(destination_directory)
        except FileExistsError:
            pass
        except OSError as e:
            QtGui.QMessageBox.critical(parent, "IOU images directory", "Could not create the IOU images directory {}: {}".format(destination_directory, str(e)))
            return

        if os.path.dirname(path) != destination_directory:
            # the IOU image is not in the default images directory
            new_destination_path = os.path.join(destination_directory, os.path.basename(path))
            try:
                # try to create a symbolic link to it
                symlink_path = new_destination_path
                os.symlink(path, symlink_path)
                path = symlink_path
            except (OSError, NotImplementedError):
                # if unsuccessful, then copy the IOU image itself
                try:
                    shutil.copyfile(path, new_destination_path)
                    path = new_destination_path
                except OSError:
                    pass
        return path

    def _iouImageBrowserSlot(self):
        """
        Slot to open a file browser and select an IOU image.
        """

        path = self.getIOUImage(self)
        if not path:
            return
        self.uiIOUPathLineEdit.clear()
        self.uiIOUPathLineEdit.setText(path)

        if "l2" in path:
            # set the default L2 base initial-config
            resource_name = "configs/iou_l2_base_initial-config.txt"
            if hasattr(sys, "frozen") and os.path.isfile(resource_name):
                self.uiInitialConfigLineEdit.setText(os.path.normpath(resource_name))
            elif pkg_resources.resource_exists("gns3", resource_name):
                iou_base_config_path = pkg_resources.resource_filename("gns3", resource_name)
                self.uiInitialConfigLineEdit.setText(os.path.normpath(iou_base_config_path))
        else:
            # set the default L3 base initial-config
            resource_name = "configs/iou_l3_base_initial-config.txt"
            if hasattr(sys, "frozen") and os.path.isfile(resource_name):
                self.uiInitialConfigLineEdit.setText(os.path.normpath(resource_name))
            elif pkg_resources.resource_exists("gns3", resource_name):
                iou_base_config_path = pkg_resources.resource_filename("gns3", resource_name)
                self.uiInitialConfigLineEdit.setText(os.path.normpath(iou_base_config_path))

    def _initialConfigBrowserSlot(self):
        """
        Slot to open a file browser and select a initial-config file.
        """

        if hasattr(sys, "frozen"):
            config_dir = "configs"
        else:
            config_dir = pkg_resources.resource_filename("gns3", "configs")
        path = QtGui.QFileDialog.getOpenFileName(self, "Select an initial configuration", config_dir)
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "Initial configuration", "Cannot read {}".format(path))
            return

        self.uiInitialConfigLineEdit.clear()
        self.uiInitialConfigLineEdit.setText(path)

    def _iouDevicePressedSlot(self, item, column):
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
        Change a symbol for an IOU device.
        """

        dialog = SymbolSelectionDialog(self)
        dialog.show()
        if dialog.exec_():
            normal_symbol, selected_symbol = dialog.getSymbols()
            category = dialog.getCategory()
            item = self.uiIOUDevicesTreeWidget.currentItem()
            if item:
                item.setIcon(0, QtGui.QIcon(normal_symbol))
                key = item.data(0, QtCore.Qt.UserRole)
                iou_device = self._iou_devices[key]
                iou_device["default_symbol"] = normal_symbol
                iou_device["hover_symbol"] = selected_symbol
                iou_device["category"] = category

    def loadPreferences(self):
        """
        Loads the IOU devices preferences.
        """

        iou_module = IOU.instance()
        self._iou_devices = copy.deepcopy(iou_module.iouDevices())
        self._items.clear()

        for key, iou_device in self._iou_devices.items():
            item = QtGui.QTreeWidgetItem(self.uiIOUDevicesTreeWidget)
            item.setText(0, iou_device["name"])
            item.setIcon(0, QtGui.QIcon(iou_device["default_symbol"]))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiIOUDevicesTreeWidget.setCurrentItem(self._items[0])
            self.uiIOUDevicesTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def savePreferences(self):
        """
        Saves the IOU devices preferences.
        """

        #self._iouImageSaveSlot()
        IOU.instance().setIOUDevices(self._iou_devices)
