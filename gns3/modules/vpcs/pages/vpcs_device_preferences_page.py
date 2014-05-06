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
Configuration page for VPCS image & device preferences.
"""

import os
import sys
from gns3.qt import QtGui
from gns3.servers import Servers
from .. import VPCS
from ..ui.vpcs_device_preferences_page_ui import Ui_VPCSDevicePreferencesPageWidget


class VPCSDevicePreferencesPage(QtGui.QWidget, Ui_VPCSDevicePreferencesPageWidget):
    """
    QWidget preference page for VPCS image & device preferences.
    """

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self._vpcs_images = {}

        self.uiSaveVPCSImagePushButton.clicked.connect(self._vpcsImageSaveSlot)
        self.uiDeleteVPCSImagePushButton.clicked.connect(self._vpcsImageDeleteSlot)
        self.uiVPCSImagesTreeWidget.itemClicked.connect(self._vpcsImageClickedSlot)
        self.uiVPCSImagesTreeWidget.itemSelectionChanged.connect(self._vpcsImageChangedSlot)
        self.uiVPCSPathToolButton.clicked.connect(self._vpcsImageBrowserSlot)
        self.uiStartupConfigToolButton.clicked.connect(self._startupConfigBrowserSlot)
        self.uiVPCSImageTestSettingsPushButton.clicked.connect(self._testSettingsSlot)

    def _vpcsImageClickedSlot(self, item, column):
        """
        Loads a selected VPCS image from the tree widget.

        :param item: selected QTreeWidgetItem instance
        :param column: ignored
        """

        image = item.text(0)
        server = item.text(1)
        key = "{server}:{image}".format(server=server, image=image)
        vpcs_image = self._vpcs_images[key]

        self.uiVPCSPathLineEdit.setText(vpcs_image["path"])
        self.uiStartupConfigLineEdit.setText(vpcs_image["script_file"])

    def _vpcsImageChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiVPCSImagesTreeWidget.currentItem()
        if item:
            self.uiDeleteVPCSImagePushButton.setEnabled(True)
        else:
            self.uiDeleteVPCSImagePushButton.setEnabled(False)

    def _vpcsImageSaveSlot(self):
        """
        Adds/Saves an VPCS image.
        """

        path = self.uiVPCSPathLineEdit.text()
        script_file = self.uiStartupConfigLineEdit.text()
        nvram = self.uiNVRAMSpinBox.value()
        ram = self.uiRAMSpinBox.value()

        # basename doesn't work on Unix with Windows paths
        if not sys.platform.startswith('win') and len(path) > 2 and path[1] == ":":
            import ntpath
            image = ntpath.basename(path)
        else:
            image = os.path.basename(path)

        #TODO: mutiple remote server
        if VPCS.instance().settings()["use_local_server"]:
            server = "local"
        else:
            server = next(iter(Servers.instance()))
            if not server:
                QtGui.QMessageBox.critical(self, "VPCS image", "No remote server available!")
                return
            server = server.host

        key = "{server}:{image}".format(server=server, image=image)
        item = self.uiVPCSImagesTreeWidget.currentItem()

        if key in self._vpcs_images and item and item.text(0) == image:
            item.setText(0, image)
            item.setText(1, server)
        elif key in self._vpcs_images:
            return
        else:
            # add a new entry in the tree widget
            item = QtGui.QTreeWidgetItem(self.uiVPCSImagesTreeWidget)
            item.setText(0, image)
            item.setText(1, server)
            self.uiVPCSImagesTreeWidget.setCurrentItem(item)

        self._vpcs_images[key] = {"path": path,
                                 "image": image,
                                 "script_file": script_file}

        self.uiVPCSImagesTreeWidget.resizeColumnToContents(0)
        self.uiVPCSImagesTreeWidget.resizeColumnToContents(1)

    def _vpcsImageDeleteSlot(self):
        """
        Deletes an VPCS image.
        """

        item = self.uiVPCSImagesTreeWidget.currentItem()
        if item:
            image = item.text(0)
            server = item.text(1)
            key = "{server}:{image}".format(server=server, image=image)
            del self._vpcs_images[key]
            self.uiVPCSImagesTreeWidget.takeTopLevelItem(self.uiVPCSImagesTreeWidget.indexOfTopLevelItem(item))

    def _vpcsImageBrowserSlot(self):
        """
        Slot to open a file browser and select an VPCS image.
        """

        #TODO: current directory for VPCS image + filter?
        path = QtGui.QFileDialog.getOpenFileName(self, "Select an VPCS image", ".", "VPCS image (*.bin *.image)")
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "VPCS image", "Cannot read {}".format(path))
            return

        try:
            with open(path, "rb") as f:
                # read the first 7 bytes of the file.
                elf_header_start = f.read(7)
        except OSError as e:
            QtGui.QMessageBox.critical(self, "VPCS image", "Cannot read ELF magic number: {}".format(e))
            return

        # file must start with the ELF magic number, be 32-bit, little endian and have an ELF version of 1
        # normal IOS image are big endian!
        if elf_header_start != b'\x7fELF\x01\x01\x01':
            QtGui.QMessageBox.critical(self, "VPCS image", "Sorry, this is not a valid VPCS image!")
            return

        self.uiVPCSPathLineEdit.clear()
        self.uiVPCSPathLineEdit.setText(path)
        self.uiRAMSpinBox.setValue(256)
        self.uiNVRAMSpinBox.setValue(128)

    def _startupConfigBrowserSlot(self):
        """
        Slot to open a file browser and select a script-file file.
        """

        #TODO: current directory for script-file + filter?
        path = QtGui.QFileDialog.getOpenFileName(self, "Select a startup configuration", ".")
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "Startup configuration", "Cannot read {}".format(path))
            return

        self.uiStartupConfigLineEdit.clear()
        self.uiStartupConfigLineEdit.setText(path)

    def _testSettingsSlot(self):

        QtGui.QMessageBox.critical(self, "Test settings", "Sorry, not yet implemented!")

    def loadPreferences(self):
        """
        Loads the VPCS image & device preferences.
        """

        self._vpcs_images.clear()
        self.uiVPCSImagesTreeWidget.clear()

        vpcs_images = VPCS.instance().vpcsImages()
        for vpcs_image in vpcs_images.values():
            item = QtGui.QTreeWidgetItem(self.uiVPCSImagesTreeWidget)
            item.setText(0, vpcs_image["image"])
            item.setText(1, vpcs_image["server"])

        self.uiVPCSImagesTreeWidget.resizeColumnToContents(0)
        self.uiVPCSImagesTreeWidget.resizeColumnToContents(1)
        self._vpcs_images.update(vpcs_images)

    def savePreferences(self):
        """
        Saves the VPCS image & device preferences.
        """

        VPCS.instance().setVPCSImages(self._vpcs_images)
