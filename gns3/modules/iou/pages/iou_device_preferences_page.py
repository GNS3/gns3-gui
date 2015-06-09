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

from gns3.qt import QtCore, QtGui, QtWidgets
from gns3.main_window import MainWindow
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.dialogs.configuration_dialog import ConfigurationDialog
from gns3.cloud.utils import UploadFilesThread
from gns3.image_manager import ImageManager

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
        self.uiIOUDevicesTreeWidget.itemPressed.connect(self._iouDevicePressedSlot)

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
        QtWidgets.QTreeWidgetItem(section_item, ["Name:", iou_device["name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Server:", iou_device["server"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Image:", iou_device["image"]])
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
            item.setIcon(0, QtGui.QIcon(self._iou_devices[key]["default_symbol"]))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiIOUDevicesTreeWidget.setCurrentItem(item)

            if new_device_settings["server"] == 'cloud':
                import logging
                log = logging.getLogger(__name__)

                # Start uploading the image to cloud files
                self._upload_image_progress_dialog = QtWidgets.QProgressDialog(
                    "Uploading image file {}".format(new_device_settings['image']), "Cancel", 0, 0, parent=self)
                self._upload_image_progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
                self._upload_image_progress_dialog.setWindowTitle("IOU image upload")
                self._upload_image_progress_dialog.show()
                try:
                    src = self._iou_devices[key]['path']
                    # Eg: images/IOU/i86.bin
                    dst = 'images/IOU/{}'.format(self._iou_devices[key]['image'])
                    upload_thread = UploadFilesThread(self, MainWindow.instance().cloudSettings(), [(src, dst)])
                    upload_thread.completed.connect(self._imageUploadComplete)
                    upload_thread.start()
                except Exception as e:
                    self._upload_image_progress_dialog.reject()
                    log.error(e)
                    QtWidgets.QMessageBox.critical(self, "IOU image upload", "Error uploading IOU image: {}".format(e))

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
                self._refreshInfo(iou_device)

    def _iouDeviceDeleteSlot(self):
        """
        Deletes an IOU device.
        """

        for item in self.uiIOUDevicesTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)
                del self._iou_devices[key]
                self.uiIOUDevicesTreeWidget.takeTopLevelItem(self.uiIOUDevicesTreeWidget.indexOfTopLevelItem(item))

    def _iouDevicePressedSlot(self, item, column):
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
        change_symbol_action.setEnabled(len(self.uiIOUDevicesTreeWidget.selectedItems()) == 1)
        change_symbol_action.triggered.connect(self._changeSymbolSlot)
        menu.addAction(change_symbol_action)

        delete_action = QtWidgets.QAction("Delete", menu)
        delete_action.triggered.connect(self._iouDeviceDeleteSlot)
        menu.addAction(delete_action)

        menu.exec_(QtGui.QCursor.pos())

    def _changeSymbolSlot(self):
        """
        Change a symbol for an IOU device.
        """

        item = self.uiIOUDevicesTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            iou_device = self._iou_devices[key]
            dialog = SymbolSelectionDialog(self, symbol=iou_device["default_symbol"], category=iou_device["category"])
            dialog.show()
            if dialog.exec_():
                normal_symbol, selected_symbol = dialog.getSymbols()
                category = dialog.getCategory()
                item.setIcon(0, QtGui.QIcon(normal_symbol))
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
            item = QtWidgets.QTreeWidgetItem(self.uiIOUDevicesTreeWidget)
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

        # self._iouImageSaveSlot()
        IOU.instance().setIOUDevices(self._iou_devices)

    def _imageUploadComplete(self):
        if self._upload_image_progress_dialog.wasCanceled():
            return
        self._upload_image_progress_dialog.accept()

    @staticmethod
    def getImageDirectory():
        return os.path.join(MainWindow.instance().imagesDirPath(), "IOU")

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
                                                        "All files (*)",
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

        path = ImageManager.askCopyUploadImage(parent, path, server, cls.getImageDirectory(), "/iou/vms")

        if os.path.exists(path) and not os.access(path, os.X_OK):
            QtWidgets.QMessageBox.warning(parent, "IOU image", "{} is not executable".format(path))

        return path
