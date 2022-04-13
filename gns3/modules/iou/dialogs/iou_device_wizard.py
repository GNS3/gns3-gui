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
Wizard for IOU devices.
"""

from gns3.qt import QtGui, QtWidgets
from gns3.node import Node
from gns3.dialogs.vm_with_images_wizard import VMWithImagesWizard
from gns3.compute_manager import ComputeManager

from ..ui.iou_device_wizard_ui import Ui_IOUDeviceWizard


class IOUDeviceWizard(VMWithImagesWizard, Ui_IOUDeviceWizard):

    """
    Wizard to create an IOU device.

    :param parent: parent widget
    """

    def __init__(self, iou_devices, parent):

        super().__init__(iou_devices, parent)
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/multilayer_switch.svg"))

        self.uiTypeComboBox.currentIndexChanged[str].connect(self._typeChangedSlot)

        if ComputeManager.instance().localPlatform().startswith("win") or ComputeManager.instance().localPlatform().startswith("darwin"):
            # Cannot use IOU locally on Windows and Mac
            self._disableLocalServer()

        # Available types
        self.uiTypeComboBox.addItems(["L2 image", "L3 image"])

        # Mandatory fields
        self.uiNameWizardPage.registerField("name*", self.uiNameLineEdit)
        self.uiNameWizardPage.registerField("image*", self.uiIOUImageLineEdit)

        self.uiIOUImageLineEdit.textChanged.connect(self._imageLineEditTextChangedSlot)

        # location of the base config templates
        self._base_iou_l2_config_template = "iou_l2_base_startup-config.txt"
        self._base_iou_l3_config_template = "iou_l3_base_startup-config.txt"

        from ..pages.iou_device_preferences_page import IOUDevicePreferencesPage
        self.addImageSelector(self.uiExistingImageRadioButton, self.uiIOUImageListComboBox, self.uiIOUImageLineEdit, self.uiIOUImageToolButton, IOUDevicePreferencesPage.getIOUImage)

    def _imageLineEditTextChangedSlot(self, text):
        """
        Set image type depending of user choice
        """

        if "l2" in text:
            self.uiTypeComboBox.setCurrentIndex(0)  # L2 image
        elif "l3" in text:
            self.uiTypeComboBox.setCurrentIndex(1)  # L3 image

    def _typeChangedSlot(self, image_type):
        """
        When the type of IOU device is changed.

        :param image_type: type of image (L2 or L3)
        """

        if image_type == "L2 image":
            #  L2 image
            self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/multilayer_switch.svg"))
        else:
            #  L3 image
            self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/router.svg"))

    def initializePage(self, page_id):

        super().initializePage(page_id)
        if self.page(page_id) == self.uiNameWizardPage:
            if not self.uiIOUImageToolButton.isEnabled():
                QtWidgets.QMessageBox.warning(self, "IOU image", "You have chosen to use a remote server, please provide the path to an IOU image located on this server!")
            self.loadImagesList("iou")

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        path = self.uiIOUImageLineEdit.text()

        startup_config = ""
        if self.uiTypeComboBox.currentText() == "L2 image":
            # set the default L2 base startup-config
            default_base_config = self._base_iou_l2_config_template
            if default_base_config:
                startup_config = default_base_config
            symbol = ":/symbols/multilayer_switch.svg"
            category = Node.switches
            ethernet_adapters = 4
            serial_adapters = 0
        else:
            # set the default L3 base startup-config
            default_base_config = self._base_iou_l3_config_template
            if default_base_config:
                startup_config = default_base_config
            symbol = ":/symbols/router.svg"
            category = Node.routers
            ethernet_adapters = 2
            serial_adapters = 2

        settings = {
            "name": self.uiNameLineEdit.text(),
            "path": path,
            "startup_config": startup_config,
            "ethernet_adapters": ethernet_adapters,
            "serial_adapters": serial_adapters,
            "symbol": symbol,
            "category": category,
            "compute_id": self._compute_id,
        }

        return settings
