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
Configuration page for IOS image & router preferences.
"""

import os
import sys
import re
from gns3.qt import QtGui
from ..settings import PLATFORMS_DEFAULT_RAM
from .. import Dynamips
from ..ui.ios_router_preferences_page_ui import Ui_IOSRouterPreferencesPageWidget

# platforms with supported chassis
CHASSIS = {"c1700": ("1720", "1721", "1750", "1751", "1760"),
           "c2600": ("2610", "2611", "2620", "2621", "2610XM", "2611XM", "2620XM", "2621XM", "2650XM", "2651XM"),
           "c3600": ("3620", "3640", "3660")}


class IOSRouterPreferencesPage(QtGui.QWidget, Ui_IOSRouterPreferencesPageWidget):
    """
    QWidget preference page for IOS images and routers.
    """

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self._ios_images = {}
        self.uiPlatformComboBox.currentIndexChanged[str].connect(self._platformChangedSlot)
        self.uiPlatformComboBox.addItems(list(PLATFORMS_DEFAULT_RAM.keys()))
        self.uiSaveIOSImagePushButton.clicked.connect(self._iosImageSaveSlot)
        self.uiDeleteIOSImagePushButton.clicked.connect(self._iosImageDeleteSlot)
        self.uiIOSImagesTreeWidget.itemClicked.connect(self._iosImageClickedSlot)
        self.uiIOSImagesTreeWidget.itemSelectionChanged.connect(self._iosImageChangedSlot)
        self.uiIOSPathToolButton.clicked.connect(self._iosImageBrowserSlot)
        self.uiStartupConfigToolButton.clicked.connect(self._startupConfigBrowserSlot)
        self.uiIdlePCFinderPushButton.clicked.connect(self._idlePCFinderSlot)
        self.uiIOSImageTestSettingsPushButton.clicked.connect(self._testSettingsSlot)

    def _platformChangedSlot(self, platform):
        """
        Updates the chassis comboBox based on the selected platform.

        :param platform: selected router platform
        """

        self.uiChassisComboBox.clear()
        if platform in CHASSIS:
            self.uiChassisComboBox.addItems(CHASSIS[platform])

    def _iosImageClickedSlot(self, item, column):
        """
        Loads a selected IOS image from the tree widget.

        :param item: selected QTreeWidgetItem instance
        :param column: ignored
        """

        image = item.text(0)
        key = "{server}:{image}".format(server="local", image=image)
        ios_image = self._ios_images[key]

        self.uiIOSPathLineEdit.setText(ios_image["path"])
        self.uiStartupConfigLineEdit.setText(ios_image["startup_config"])
        index = self.uiPlatformComboBox.findText(ios_image["platform"])
        if index != -1:
            self.uiPlatformComboBox.setCurrentIndex(index)
        index = self.uiChassisComboBox.findText(ios_image["chassis"])
        if index != -1:
            self.uiChassisComboBox.setCurrentIndex(index)
        self.uiIdlePCLineEdit.setText(ios_image["idlepc"])
        self.uiRAMSpinBox.setValue(ios_image["ram"])

    def _iosImageChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiIOSImagesTreeWidget.currentItem()
        if item:
            self.uiDeleteIOSImagePushButton.setEnabled(True)
        else:
            self.uiDeleteIOSImagePushButton.setEnabled(False)

    def _iosImageSaveSlot(self):
        """
        Adds/Saves an IOS image.
        """

        path = self.uiIOSPathLineEdit.text()
        startup_config = self.uiStartupConfigLineEdit.text()
        platform = self.uiPlatformComboBox.currentText()
        chassis = self.uiChassisComboBox.currentText()
        idlepc = self.uiIdlePCLineEdit.text()
        ram = self.uiRAMSpinBox.value()

        # basename doesn't work on Unix with Windows paths
        if not sys.platform.startswith('win') and len(path) > 2 and path[1] == ":":
            import ntpath
            image = ntpath.basename(path)
        else:
            image = os.path.basename(path)

        if image.startswith("c7200p"):
            QtGui.QMessageBox.warning(self, "IOS Image", "This IOS image is for the c7200 platform with NPE-G2 and using it is not recommended.\nPlease use an IOS image that do not start with c7200p.")

        #ios_images = Dynamips.instance().iosImages()
        key = "{server}:{image}".format(server="local", image=image)
        item = self.uiIOSImagesTreeWidget.currentItem()

        if key in self._ios_images and item and item.text(0) == image:
            item.setText(0, image)
            item.setText(1, platform)
            item.setText(2, "local")
        elif key in self._ios_images:
            print("Image already added")
            return
        else:
            # add a new entry in the tree widget
            item = QtGui.QTreeWidgetItem(self.uiIOSImagesTreeWidget)
            item.setText(0, image)
            item.setText(1, platform)
            item.setText(2, "local")
            self.uiIOSImagesTreeWidget.setCurrentItem(item)

        self._ios_images[key] = {"path": path,
                                 "image": image,
                                 "startup_config": startup_config,
                                 "platform": platform,
                                 "chassis": chassis,
                                 "idlepc": idlepc,
                                 "ram": ram,
                                 "server": "local"}

        self.uiIOSImagesTreeWidget.resizeColumnToContents(0)
        self.uiIOSImagesTreeWidget.resizeColumnToContents(1)

    def _iosImageDeleteSlot(self):
        """
        Deletes an IOS image.
        """

        item = self.uiIOSImagesTreeWidget.currentItem()
        if item:
            image = item.text(0)
            key = "{server}:{image}".format(server="local", image=image)
            del self._ios_images[key]
            self.uiIOSImagesTreeWidget.takeTopLevelItem(self.uiIOSImagesTreeWidget.indexOfTopLevelItem(item))

    def _iosImageBrowserSlot(self):
        """
        Slot to open a file browser and select an IOS image.
        """

        #TODO: current directory for IOS image + filter?
        path = QtGui.QFileDialog.getOpenFileName(self, "Select an IOS image", ".", "IOS image (*.bin *.image)")
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "IOS image", "Cannot read {}".format(path))
            return

        if sys.platform.startswith('win'):
            # Dynamips (Cygwin acutally) doesn't like non ascii paths on Windows
            try:
                path.encode('ascii')
            except UnicodeEncodeError:
                QtGui.QMessageBox.warning(self, "IOS image", "The IOS image filename should contains only ascii (English) characters.")

        self.uiIOSPathLineEdit.clear()
        self.uiIOSPathLineEdit.setText(path)

        # try to guess the platform
        image = os.path.basename(path)
        match = re.match("^(c[0-9]+)\\-\w+", image)
        if not match:
            QtGui.QMessageBox.warning(self, "IOS image", "Could not detect the platform, make sure this is a valid IOS image!")
            return

        detected_platform = match.group(1)
        if detected_platform not in PLATFORMS_DEFAULT_RAM:
            QtGui.QMessageBox.warning(self, "IOS image", "This IOS image is for the {} platform and is not supported by this application!".format(detected_platform))
            return

        index = self.uiPlatformComboBox.findText(detected_platform)
        if index != -1:
            self.uiPlatformComboBox.setCurrentIndex(index)

        self.uiRAMSpinBox.setValue(PLATFORMS_DEFAULT_RAM[detected_platform])

    def _startupConfigBrowserSlot(self):
        """
        Slot to open a file browser and select a startup-config file.
        """

        #TODO: current directory for startup-config + filter?
        path = QtGui.QFileDialog.getOpenFileName(self, "Select a startup configuration", ".")
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "Startup configuration", "Cannot read {}".format(path))
            return

        if sys.platform.startswith('win'):
            # Dynamips (Cygwin acutally) doesn't like non ascii paths on Windows
            try:
                path.encode('ascii')
            except UnicodeEncodeError:
                QtGui.QMessageBox.warning(self, "Startup configuration", "The startup configuration filename should contains only ascii (English) characters.")

        self.uiStartupConfigLineEdit.clear()
        self.uiStartupConfigLineEdit.setText(path)

    def _idlePCFinderSlot(self):

        QtGui.QMessageBox.critical(self, "Idle-PC finder", "Sorry, not yet implemented!")

    def _testSettingsSlot(self):

        QtGui.QMessageBox.critical(self, "Test settings", "Sorry, not yet implemented!")

    def loadPreferences(self):
        """
        Loads the IOS image & router preferences.
        """

        self._ios_images.clear()
        self.uiIOSImagesTreeWidget.clear()
        ios_images = Dynamips.instance().iosImages()
        for ios_image in ios_images.values():
            item = QtGui.QTreeWidgetItem(self.uiIOSImagesTreeWidget)
            item.setText(0, ios_image["image"])
            item.setText(1, ios_image["platform"])
            item.setText(2, "local")

        self.uiIOSImagesTreeWidget.resizeColumnToContents(0)
        self.uiIOSImagesTreeWidget.resizeColumnToContents(1)
        self._ios_images.update(ios_images)

    def savePreferences(self):
        """
        Saves the IOS image & router preferences.
        """

        Dynamips.instance().setIOSImages(self._ios_images)
