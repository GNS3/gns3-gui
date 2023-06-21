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
Configuration page for IOS router preferences.
"""

import os
import copy
import sys
import math
import zipfile
import logging

from gns3.qt import QtCore, QtWidgets, qpartial, qslot
from gns3.controller import Controller

from gns3.main_window import MainWindow
from gns3.dialogs.configuration_dialog import ConfigurationDialog
from gns3.utils.progress_dialog import ProgressDialog
from gns3.image_manager import ImageManager
from gns3.compute_manager import ComputeManager
from gns3.template_manager import TemplateManager
from gns3.template import Template

from ..settings import IOS_ROUTER_SETTINGS
from ..utils.decompress_ios import isIOSCompressed
from ..utils.decompress_ios_worker import DecompressIOSWorker
from ..ui.ios_router_preferences_page_ui import Ui_IOSRouterPreferencesPageWidget
from ..pages.ios_router_configuration_page import IOSRouterConfigurationPage
from ..dialogs.ios_router_wizard import IOSRouterWizard


log = logging.getLogger(__name__)


class IOSRouterPreferencesPage(QtWidgets.QWidget, Ui_IOSRouterPreferencesPageWidget):

    """
    QWidget preference page for IOS routers.
    """

    _default_images_dir = ""

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._ios_routers = {}
        self._items = []

        self.uiNewIOSRouterPushButton.clicked.connect(self._iosRouterNewSlot)
        self.uiCopyIOSRouterPushButton.clicked.connect(self._iosRouterCopySlot)
        self.uiEditIOSRouterPushButton.clicked.connect(self._iosRouterEditSlot)
        self.uiDeleteIOSRouterPushButton.clicked.connect(self._iosRouterDeleteSlot)
        self.uiIOSRoutersTreeWidget.itemSelectionChanged.connect(self._iosRouterChangedSlot)
        self.uiDecompressIOSPushButton.clicked.connect(self._decompressIOSSlot)
        self.uiIOSRoutersTreeWidget.itemDoubleClicked.connect(self._iosRouterEditSlot)

    def _iosRouterChangedSlot(self):
        """
        Loads a selected an IOS router from the tree widget.
        """

        selection = self.uiIOSRoutersTreeWidget.selectedItems()
        self.uiDeleteIOSRouterPushButton.setEnabled(len(selection) != 0)
        single_selected = len(selection) == 1
        self.uiEditIOSRouterPushButton.setEnabled(single_selected)
        self.uiCopyIOSRouterPushButton.setEnabled(single_selected)
        self.uiDecompressIOSPushButton.setEnabled(single_selected)

        if single_selected:
            key = selection[0].data(0, QtCore.Qt.UserRole)
            ios_router = self._ios_routers[key]
            self._refreshInfo(ios_router)
        else:
            self.uiIOSRouterInfoTreeWidget.clear()

    @qslot
    def _iosRouterNewSlot(self, *args):
        """
        Creates a new IOS router.
        """

        wizard = IOSRouterWizard(self._ios_routers, parent=self)
        wizard.show()
        if wizard.exec_():

            ios_settings = wizard.getSettings()
            key = "{server}:{name}".format(server=ios_settings["compute_id"], name=ios_settings["name"])

            self._ios_routers[key] = IOS_ROUTER_SETTINGS.copy()
            self._ios_routers[key].update(ios_settings)

            if ios_settings["platform"] == "c7200":
                self._ios_routers[key]["midplane"] = "vxr"
                self._ios_routers[key]["npe"] = "npe-400"
            else:
                self._ios_routers[key]["iomem"] = 5

            for slot_id in range(0, 7):
                slot = "slot{}".format(slot_id)
                if slot in ios_settings:
                    self._ios_routers[key][slot] = ios_settings[slot]

            for wic_id in range(0, 3):
                wic = "wic{}".format(wic_id)
                if wic in ios_settings:
                    self._ios_routers[key][wic] = ios_settings[wic]

            self._ios_routers[key].update(ios_settings)
            item = QtWidgets.QTreeWidgetItem(self.uiIOSRoutersTreeWidget)
            item.setText(0, self._ios_routers[key]["name"])
            Controller.instance().getSymbolIcon(self._ios_routers[key]["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiIOSRoutersTreeWidget.setCurrentItem(item)

    def _iosRouterCopySlot(self):
        """
        Copies an IOS router.
        """

        item = self.uiIOSRoutersTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            copied_ios_router_settings = copy.deepcopy(self._ios_routers[key])
            new_name, ok = QtWidgets.QInputDialog.getText(self, "Copy IOS router template", "Template name:", QtWidgets.QLineEdit.Normal, "Copy of {}".format(copied_ios_router_settings["name"]))
            if ok:
                key = "{server}:{name}".format(server=copied_ios_router_settings["compute_id"], name=new_name)
                if key in self._ios_routers:
                    QtWidgets.QMessageBox.critical(self, "IOS router template", "IOS router template name {} already exists".format(new_name))
                    return
                self._ios_routers[key] = IOS_ROUTER_SETTINGS.copy()
                self._ios_routers[key].update(copied_ios_router_settings)
                self._ios_routers[key]["name"] = new_name
                self._ios_routers[key].pop("template_id", None)

                item = QtWidgets.QTreeWidgetItem(self.uiIOSRoutersTreeWidget)
                item.setText(0, self._ios_routers[key]["name"])
                Controller.instance().getSymbolIcon(self._ios_routers[key]["symbol"], qpartial(self._setItemIcon, item))
                item.setData(0, QtCore.Qt.UserRole, key)
                self._items.append(item)
                self.uiIOSRoutersTreeWidget.setCurrentItem(item)

    def _iosRouterEditSlot(self):
        """
        Edits an IOS router.
        """

        item = self.uiIOSRoutersTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            ios_router = self._ios_routers[key]
            dialog = ConfigurationDialog(ios_router["name"], ios_router, IOSRouterConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                # update the icon
                Controller.instance().getSymbolIcon(self._ios_routers[key]["symbol"], qpartial(self._setItemIcon, item))

                if ios_router["name"] != item.text(0):
                    # rename the IOS router
                    new_key = "{server}:{name}".format(server=ios_router["compute_id"], name=ios_router["name"])
                    if new_key in self._ios_routers:
                        QtWidgets.QMessageBox.critical(self, "IOS router", "IOS router name {} already exists for server {}".format(ios_router["name"],
                                                                                                                                    ios_router["compute_id"]))
                        ios_router["name"] = item.text(0)
                        return
                    self._ios_routers[new_key] = self._ios_routers[key]
                    del self._ios_routers[key]
                    item.setText(0, ios_router["name"])
                    item.setData(0, QtCore.Qt.UserRole, new_key)

                self._refreshInfo(ios_router)

    def _iosRouterDeleteSlot(self):
        """
        Deletes an IOS router.
        """

        for item in self.uiIOSRoutersTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)

                del self._ios_routers[key]
                self.uiIOSRoutersTreeWidget.takeTopLevelItem(self.uiIOSRoutersTreeWidget.indexOfTopLevelItem(item))
                if self._ios_routers == {}:
                    self.uiEditIOSRouterPushButton.setEnabled(False)
                    self.uiDeleteIOSRouterPushButton.setEnabled(False)
                    self.uiDecompressIOSPushButton.setEnabled(False)

    def _imageUploadComplete(self):
        if self._upload_image_progress_dialog.wasCanceled():
            return
        self._upload_image_progress_dialog.accept()

    @staticmethod
    def getImageDirectory():
        return ImageManager.instance().getDirectoryForType("DYNAMIPS")

    @classmethod
    def getIOSImage(cls, parent, server):
        """

        :param parent: parent widget
        :param server: The server where the image is located

        :return: path to the IOS image or None
        """

        if not cls._default_images_dir:
            cls._default_images_dir = cls.getImageDirectory()

        path, _ = QtWidgets.QFileDialog.getOpenFileName(parent,
                                                        "Select an IOS image",
                                                        cls._default_images_dir,
                                                        "All files (*.*);;IOS image (*.bin *.image)",
                                                        "IOS image (*.bin *.image)")

        if not path:
            return
        cls._default_images_dir = os.path.dirname(path)

        if not os.access(path, os.R_OK):
            QtWidgets.QMessageBox.critical(parent, "IOS image", "Cannot read {}".format(path))
            return

        if sys.platform.startswith('win'):
            # Dynamips (Cygwin actually) doesn't like non ascii paths on Windows
            try:
                path.encode('ascii')
            except UnicodeEncodeError:
                QtWidgets.QMessageBox.warning(parent, "IOS image", "The IOS image filename should contains only ascii (English) characters.")

        try:
            with open(path, "rb") as f:
                # read the first 7 bytes of the file.
                elf_header_start = f.read(7)
        except OSError as e:
            QtWidgets.QMessageBox.critical(parent, "IOS image", "Cannot read ELF magic number: {}".format(e))
            return

        # file must start with the ELF magic number, be 32-bit, big endian and have an ELF version of 1
        if elf_header_start != b'\x7fELF\x01\x02\x01':
            QtWidgets.QMessageBox.critical(parent, "IOS image", "Sorry, this is not a valid IOS image!")
            return

        try:
            os.makedirs(cls.getImageDirectory(), exist_ok=True)
        except OSError as e:
            QtWidgets.QMessageBox.critical(parent, "IOS images directory", "Could not create the IOS images directory {}: {}".format(cls.getImageDirectory(), e))
            return

        compressed = False
        try:
            compressed = isIOSCompressed(path)
        except (OSError, ValueError):
            pass  # ignore errors if we cannot find out the IOS image is compressed.
        if compressed:
            reply = QtWidgets.QMessageBox.question(parent, "IOS image", "Would you like to decompress this IOS image?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                decompressed_image_path = os.path.join(cls.getImageDirectory(), os.path.basename(os.path.splitext(path)[0] + ".image"))
                worker = DecompressIOSWorker(path, decompressed_image_path)
                progress_dialog = ProgressDialog(worker,
                                                 "IOS image",
                                                 "Decompressing IOS image {}...".format(os.path.basename(path)),
                                                 "Cancel", busy=True, parent=parent)
                progress_dialog.show()
                if progress_dialog.exec_() is not False:
                    path = decompressed_image_path

        path = ImageManager.instance().askCopyUploadImage(parent, path, server, "DYNAMIPS")

        return path

    @staticmethod
    def getMinimumRequiredRAM(path):
        """
        Returns the minimum RAM required to run an IOS image.

        :param path: path to the IOS image

        :returns: minimum RAM in MB or 0 if there is an error
        """

        try:
            if isIOSCompressed(path):
                zip_file = zipfile.ZipFile(path, "r")
                decompressed_size = 0
                for zip_info in zip_file.infolist():
                    decompressed_size += zip_info.file_size
            else:
                decompressed_size = os.path.getsize(path)
        except (zipfile.BadZipFile, OSError, ValueError):
            return 0

        # get the size in MB
        decompressed_size = (decompressed_size / (1000 * 1000)) + 1
        # round up to the closest multiple of 32 (step of the RAM SpinBox)
        return math.ceil(decompressed_size / 32) * 32

    def _decompressIOSSlot(self):
        """
        Slot to decompress an IOS image.
        """

        item = self.uiIOSRoutersTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            ios_router = self._ios_routers[key]
            path = ios_router["image"]
            if not os.path.isabs(path):
                path = os.path.join(self.getImageDirectory(), path)
            if not os.path.isfile(path):
                QtWidgets.QMessageBox.critical(self, "IOS image", "IOS image file {} does not exist".format(path))
                return
            try:
                if not isIOSCompressed(path):
                    QtWidgets.QMessageBox.critical(self, "IOS image", "IOS image {} is not compressed".format(os.path.basename(path)))
                    return
            except OSError as e:
                # errno 22, invalid argument means the file system where the IOS image is located doesn't support mmap
                if e.errno == 22:
                    QtWidgets.QMessageBox.critical(self, "IOS image", "IOS image {} cannot be memory mapped, most likely because the file system doesn't support it".format(os.path.basename(path)))
                else:
                    QtWidgets.QMessageBox.critical(self, "IOS image", "Could not determine if the IOS image is compressed: {}".format(e))
                return
            except ValueError as e:
                QtWidgets.QMessageBox.critical(self, "IOS image", "Could not determine if the IOS image is compressed: {}".format(e))
                return

            decompressed_image_path = os.path.splitext(path)[0] + ".image"
            if os.path.isfile(decompressed_image_path):
                QtWidgets.QMessageBox.critical(self, "IOS image", "Decompressed IOS image {} already exist".format(os.path.basename(decompressed_image_path)))
                return

            worker = DecompressIOSWorker(path, decompressed_image_path)
            progress_dialog = ProgressDialog(worker,
                                             "IOS image",
                                             "Decompressing IOS image {}...".format(path),
                                             "Cancel", busy=True, parent=self)
            progress_dialog.show()
            if progress_dialog.exec_() is not False:
                ios_router["image"] = decompressed_image_path
                self._refreshInfo(ios_router)

    def _createSectionItem(self, name):
        """
        Adds a new section to the tree widget.

        :param name: section name
        """

        section_item = QtWidgets.QTreeWidgetItem(self.uiIOSRouterInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, ios_router):
        """
        Refreshes the content of the tree widget.
        """

        self.uiIOSRouterInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtWidgets.QTreeWidgetItem(section_item, ["Template name:", ios_router["name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Template ID:", ios_router.get("template_id", "none")])
        QtWidgets.QTreeWidgetItem(section_item, ["Default name format:", ios_router["default_name_format"]])
        try:
            compute_id = ios_router.get("compute_id")
            if compute_id:
                QtWidgets.QTreeWidgetItem(section_item, ["Compute:", ComputeManager.instance().getCompute(compute_id).name()])
            else:
                if Controller.instance().settings()["dynamic_compute_allocation"]:
                    msg = "Dynamically allocated by the controller"
                else:
                    msg = "Manually chosen"
                QtWidgets.QTreeWidgetItem(section_item, ["Compute:", msg])
        except KeyError:
            pass
        QtWidgets.QTreeWidgetItem(section_item, ["Platform:", ios_router["platform"]])
        if ios_router.get("chassis"):
            QtWidgets.QTreeWidgetItem(section_item, ["Chassis:", ios_router.get("chassis")])
        QtWidgets.QTreeWidgetItem(section_item, ["Image:", ios_router["image"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Console type:", ios_router["console_type"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Auto start console:", "{}".format(ios_router["console_auto_start"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Auxiliary console type:", ios_router["aux_type"]])
        if ios_router["idlepc"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Idle-PC:", ios_router["idlepc"]])
        if ios_router["startup_config"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Startup-config:", ios_router["startup_config"]])
        if ios_router["private_config"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Private-config:", ios_router["private_config"]])
        if ios_router["platform"] == "c7200":
            QtWidgets.QTreeWidgetItem(section_item, ["Midplane:", ios_router.get("midplane", "vxr")])
            QtWidgets.QTreeWidgetItem(section_item, ["NPE:", ios_router.get("npe", "npe-400")])

        # fill out the Memories and disk section
        section_item = self._createSectionItem("Memories and disks")
        QtWidgets.QTreeWidgetItem(section_item, ["RAM:", "{} MiB".format(ios_router["ram"])])
        QtWidgets.QTreeWidgetItem(section_item, ["NVRAM:", "{} KiB".format(ios_router["nvram"])])
        if "iomem" in ios_router and ios_router["iomem"]:
            QtWidgets.QTreeWidgetItem(section_item, ["I/O memory:", "{}%".format(ios_router["iomem"])])
        QtWidgets.QTreeWidgetItem(section_item, ["PCMCIA disk0:", "{} MiB".format(ios_router["disk0"])])
        QtWidgets.QTreeWidgetItem(section_item, ["PCMCIA disk1:", "{} MiB".format(ios_router["disk1"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Auto delete:", "{}".format(ios_router["auto_delete_disks"])])

        # fill out the Adapters section
        section_item = self._createSectionItem("Adapters")
        for slot_id in range(0, 7):
            slot = "slot{}".format(slot_id)
            if slot in ios_router and ios_router[slot]:
                QtWidgets.QTreeWidgetItem(section_item, ["Slot {}:".format(slot_id), ios_router[slot]])
        if section_item.childCount() == 0:
            self.uiIOSRouterInfoTreeWidget.takeTopLevelItem(self.uiIOSRouterInfoTreeWidget.indexOfTopLevelItem(section_item))

        # fill out the WICs section
        section_item = self._createSectionItem("WICs")
        for wic_id in range(0, 3):
            wic = "wic{}".format(wic_id)
            if wic in ios_router and ios_router[wic]:
                QtWidgets.QTreeWidgetItem(section_item, ["WIC {}:".format(wic_id), ios_router[wic]])
        if section_item.childCount() == 0:
            self.uiIOSRouterInfoTreeWidget.takeTopLevelItem(self.uiIOSRouterInfoTreeWidget.indexOfTopLevelItem(section_item))

        self.uiIOSRouterInfoTreeWidget.expandAll()
        self.uiIOSRouterInfoTreeWidget.resizeColumnToContents(0)
        self.uiIOSRouterInfoTreeWidget.resizeColumnToContents(1)
        self.uiIOSRoutersTreeWidget.setMaximumWidth(self.uiIOSRoutersTreeWidget.sizeHintForColumn(0) + 10)

    def loadPreferences(self):
        """
        Loads the IOS router preferences.
        """

        self._ios_routers = {}
        templates = TemplateManager.instance().templates()
        for template_id, template in templates.items():
            if template.template_type() == "dynamips" and not template.builtin():
                name = template.name()
                server = template.compute_id()
                #TODO: use template id for the key
                key = "{server}:{name}".format(server=server, name=name)
                self._ios_routers[key] = copy.deepcopy(template.settings())

        self._items.clear()
        for key, ios_router in self._ios_routers.items():
            item = QtWidgets.QTreeWidgetItem(self.uiIOSRoutersTreeWidget)
            item.setText(0, ios_router["name"])
            Controller.instance().getSymbolIcon(ios_router["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiIOSRoutersTreeWidget.setCurrentItem(self._items[0])
            self.uiIOSRoutersTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.uiIOSRoutersTreeWidget.setMaximumWidth(self.uiIOSRoutersTreeWidget.sizeHintForColumn(0) + 10)

    def savePreferences(self):
        """
        Saves the IOS router preferences.
        """

        templates = []
        for template in TemplateManager.instance().templates().values():
            if template.template_type() != "dynamips":
                templates.append(template)
        for template_settings in self._ios_routers.values():
            templates.append(Template(template_settings))
        TemplateManager.instance().updateList(templates)

    def _setItemIcon(self, item, icon):
        item.setIcon(0, icon)
        self.uiIOSRoutersTreeWidget.setMaximumWidth(self.uiIOSRoutersTreeWidget.sizeHintForColumn(0) + 10)
