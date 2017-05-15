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

from gns3.qt import QtCore, QtWidgets, qpartial

from gns3.main_window import MainWindow
from gns3.dialogs.configuration_dialog import ConfigurationDialog
from gns3.image_manager import ImageManager
from gns3.compute_manager import ComputeManager
from gns3.controller import Controller

from .. import IOU
from ..settings import IOU_DEVICE_SETTINGS
from ..ui.iou_device_preferences_page_ui import Ui_IOUDevicePreferencesPageWidget
from ..pages.iou_device_configuration_page import iouDeviceConfigurationPage
from ..dialogs.iou_device_wizard import IOUDeviceWizard


class IOUDevicePreferencesPage(QtWidgets.QWidget, Ui_IOUDevicePreferencesPageWidget):

    """
    QWidget preference page for IOU image & device preferences.
    """

    _default_images_dir = ""

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._iou_devices = {}
        self._items = []

        self.uiNewIOUDevicePushButton.clicked.connect(self._iouDeviceNewSlot)
        self.uiEditIOUDevicePushButton.clicked.connect(self._iouDeviceEditSlot)
        self.uiDeleteIOUDevicePushButton.clicked.connect(self._iouDeviceDeleteSlot)
        self.uiIOUDevicesTreeWidget.itemSelectionChanged.connect(self._iouDeviceChangedSlot)

    def _createSectionItem(self, name):

        section_item = QtWidgets.QTreeWidgetItem(self.uiIOUDeviceInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, iou_device):

        self.uiIOUDeviceInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtWidgets.QTreeWidgetItem(section_item, ["Template name:", iou_device["name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Default name format:", iou_device["default_name_format"]])
        try:
            QtWidgets.QTreeWidgetItem(section_item, ["Server:", ComputeManager.instance().getCompute(iou_device["server"]).name()])
        except KeyError:
            # Compute doesn't exists
            pass
        QtWidgets.QTreeWidgetItem(section_item, ["Image:", iou_device["path"]])
        if iou_device["startup_config"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Startup-config:", iou_device["startup_config"]])

        if iou_device["private_config"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Private-config:", iou_device["private_config"]])

        if iou_device["use_default_iou_values"]:
            QtWidgets.QTreeWidgetItem(section_item, ["RAM:", "default"])
            QtWidgets.QTreeWidgetItem(section_item, ["NVRAM:", "default"])
        else:
            QtWidgets.QTreeWidgetItem(section_item, ["RAM:", "{} MiB".format(iou_device["ram"])])
            QtWidgets.QTreeWidgetItem(section_item, ["NVRAM:", "{} KiB".format(iou_device["nvram"])])

        # fill out the Network section
        section_item = self._createSectionItem("Network")
        QtWidgets.QTreeWidgetItem(section_item, ["Ethernet adapters:", "{} ({} interfaces)".format(iou_device["ethernet_adapters"],
                                                                                                   iou_device["ethernet_adapters"] * 4)])
        QtWidgets.QTreeWidgetItem(section_item, ["Serial adapters:", "{} ({} interfaces)".format(iou_device["serial_adapters"],
                                                                                                 iou_device["serial_adapters"] * 4)])

        self.uiIOUDeviceInfoTreeWidget.expandAll()
        self.uiIOUDeviceInfoTreeWidget.resizeColumnToContents(0)
        self.uiIOUDeviceInfoTreeWidget.resizeColumnToContents(1)
        self.uiIOUDevicesTreeWidget.setMaximumWidth(self.uiIOUDevicesTreeWidget.sizeHintForColumn(0) + 10)

    def _iouDeviceChangedSlot(self):
        """
        Loads a selected an IOU device from the tree widget.
        """

        selection = self.uiIOUDevicesTreeWidget.selectedItems()
        self.uiDeleteIOUDevicePushButton.setEnabled(len(selection) != 0)
        single_selected = len(selection) == 1
        self.uiEditIOUDevicePushButton.setEnabled(single_selected)

        if single_selected:
            key = selection[0].data(0, QtCore.Qt.UserRole)
            iou_device = self._iou_devices[key]
            self._refreshInfo(iou_device)
        else:
            self.uiIOUDeviceInfoTreeWidget.clear()

    def _iouDeviceNewSlot(self):
        """
        Creates a new IOU device.
        """

        wizard = IOUDeviceWizard(self._iou_devices, parent=self)
        wizard.show()
        if wizard.exec_():

            new_device_settings = wizard.getSettings()
            key = "{server}:{name}".format(server=new_device_settings["server"], name=new_device_settings["name"])
            self._iou_devices[key] = IOU_DEVICE_SETTINGS.copy()
            self._iou_devices[key].update(new_device_settings)

            item = QtWidgets.QTreeWidgetItem(self.uiIOUDevicesTreeWidget)
            item.setText(0, self._iou_devices[key]["name"])
            Controller.instance().getSymbolIcon(self._iou_devices[key]["symbol"], qpartial(self._setItemIcon, item))
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
                # update the icon
                Controller.instance().getSymbolIcon(iou_device["symbol"], qpartial(self._setItemIcon, item))
                if iou_device["name"] != item.text(0):
                    new_key = "{server}:{name}".format(server=iou_device["server"], name=iou_device["name"])
                    if new_key in self._iou_devices:
                        QtWidgets.QMessageBox.critical(self, "IOU device", "IOU device name {} already exists for server {}".format(iou_device["name"],
                                                                                                                                    iou_device["server"]))
                        iou_device["name"] = item.text(0)
                        return
                    self._iou_devices[new_key] = self._iou_devices[key]
                    del self._iou_devices[key]
                    item.setText(0, iou_device["name"])
                    item.setData(0, QtCore.Qt.UserRole, new_key)
                self._refreshInfo(dialog.settings)

    def _iouDeviceDeleteSlot(self):
        """
        Deletes an IOU device.
        """

        for item in self.uiIOUDevicesTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)
                del self._iou_devices[key]
                self.uiIOUDevicesTreeWidget.takeTopLevelItem(self.uiIOUDevicesTreeWidget.indexOfTopLevelItem(item))

    def loadPreferences(self):
        """
        Loads the IOU devices preferences.
        """

        iou_module = IOU.instance()
        self._iou_devices = copy.deepcopy(iou_module.VMs())
        self._items.clear()

        for key, iou_device in self._iou_devices.items():
            item = QtWidgets.QTreeWidgetItem(self.uiIOUDevicesTreeWidget)
            item.setText(0, iou_device["name"])
            Controller.instance().getSymbolIcon(iou_device["symbol"], qpartial(self._setItemIcon, item))

            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiIOUDevicesTreeWidget.setCurrentItem(self._items[0])
            self.uiIOUDevicesTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.uiIOUDevicesTreeWidget.setMaximumWidth(self.uiIOUDevicesTreeWidget.sizeHintForColumn(0) + 10)

    def savePreferences(self):
        """
        Saves the IOU devices preferences.
        """

        # self._iouImageSaveSlot()
        IOU.instance().setVMs(self._iou_devices)

    def _imageUploadComplete(self):
        if self._upload_image_progress_dialog.wasCanceled():
            return
        self._upload_image_progress_dialog.accept()

    @staticmethod
    def getImageDirectory():
        return ImageManager.instance().getDirectoryForType("IOU")

    @classmethod
    def getIOUImage(cls, parent, server):
        """

        :param parent: parent widget
        :param server: The server where the image is located

        :return: path to the IOU image or None
        """

        if not cls._default_images_dir:
            cls._default_images_dir = cls.getImageDirectory()

        path, _ = QtWidgets.QFileDialog.getOpenFileName(parent,
                                                        "Select an IOU image",
                                                        cls._default_images_dir,
                                                        "All file (*);;IOU image (*.bin *.image)",
                                                        "IOU image (*.bin *.image)")

        if not path:
            return
        cls._default_images_dir = os.path.dirname(path)

        if not os.access(path, os.R_OK):
            QtWidgets.QMessageBox.critical(parent, "IOU image", "Cannot read {}".format(path))
            return

        try:
            with open(path, "rb") as f:
                # read the first 7 bytes of the file.
                elf_header_start = f.read(7)
        except OSError as e:
            QtWidgets.QMessageBox.critical(parent, "IOU image", "Cannot read ELF magic number: {}".format(e))
            return

        # file must start with the ELF magic number, be 32-bit, little endian and have an ELF version of 1
        # normal IOS image are big endian!
        if elf_header_start != b'\x7fELF\x01\x01\x01':
            QtWidgets.QMessageBox.critical(parent, "IOU image", "Sorry, this is not a valid IOU image!")
            return

        try:
            os.makedirs(cls.getImageDirectory(), exist_ok=True)
        except OSError as e:
            QtWidgets.QMessageBox.critical(parent, "IOU images directory", "Could not create the IOU images directory {}: {}".format(cls.getImageDirectory(), e))
            return

        path = ImageManager.instance().askCopyUploadImage(parent, path, server, "IOU")

        if os.path.exists(path) and not os.access(path, os.X_OK):
            QtWidgets.QMessageBox.warning(parent, "IOU image", "{} is not executable".format(path))

        return path

    def _setItemIcon(self, item, icon):
        item.setIcon(0, icon)
        self.uiIOUDevicesTreeWidget.setMaximumWidth(self.uiIOUDevicesTreeWidget.sizeHintForColumn(0) + 10)
