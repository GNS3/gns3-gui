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

import os
import sys
import pkg_resources

from gns3.qt import QtGui
from gns3.node import Node
from gns3.servers import Servers

from ....settings import ENABLE_CLOUD
from ..ui.iou_device_wizard_ui import Ui_IOUDeviceWizard
from .. import IOU


class IOUDeviceWizard(QtGui.QWizard, Ui_IOUDeviceWizard):
    """
    Wizard to create an IOU device.

    :param parent: parent widget
    """

    def __init__(self, iou_devices, parent):

        QtGui.QWizard.__init__(self, parent)
        self.setupUi(self)
        self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/multilayer_switch.normal.svg"))
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        if sys.platform.startswith("darwin"):
            # we want to see the cancel button on OSX
            self.setOptions(QtGui.QWizard.NoDefaultButton)

        self.uiRemoteRadioButton.toggled.connect(self._remoteServerToggledSlot)
        self.uiLoadBalanceCheckBox.toggled.connect(self._loadBalanceToggledSlot)
        self.uiIOUImageToolButton.clicked.connect(self._iouImageBrowserSlot)
        self.uiTypeComboBox.currentIndexChanged[str].connect(self._typeChangedSlot)

        if sys.platform.startswith("win"):
            # Cannot use IOU locally on Windows
            self.uiLocalRadioButton.setEnabled(False)

        # Available types
        self.uiTypeComboBox.addItems(["L2 image", "L3 image"])

        # Mandatory fields
        self.uiNameImageWizardPage.registerField("name*", self.uiNameLineEdit)
        self.uiNameImageWizardPage.registerField("image*", self.uiIOUImageLineEdit)

        self._iou_devices = iou_devices

        if IOU.instance().settings()["use_local_server"]:
            # skip the server page if we use the local server
            self.setStartId(1)
        else:
            self.uiIOUImageToolButton.setEnabled(False)

        if not ENABLE_CLOUD:
            self.uiCloudRadioButton.hide()


    def _remoteServerToggledSlot(self, checked):
        """
        Slot for when the remote server radio button is toggled.

        :param checked: either the button is checked or not
        """

        if checked:
            self.uiRemoteServersGroupBox.setEnabled(True)
            self.uiIOUImageToolButton.setEnabled(False)
        else:
            self.uiRemoteServersGroupBox.setEnabled(False)
            self.uiIOUImageToolButton.setEnabled(True)

    def _loadBalanceToggledSlot(self, checked):
        """
        Slot for when the load balance checkbox is toggled.

        :param checked: either the box is checked or not
        """

        if checked:
            self.uiRemoteServersComboBox.setEnabled(False)
        else:
            self.uiRemoteServersComboBox.setEnabled(True)

    def _iouImageBrowserSlot(self):
        """
        Slot to open a file browser and select an IOU image.
        """

        from ..pages.iou_device_preferences_page import IOUDevicePreferencesPage
        path = IOUDevicePreferencesPage.getIOUImage(self)
        if not path:
            return
        self.uiIOUImageLineEdit.clear()
        self.uiIOUImageLineEdit.setText(path)
        if "l2" in path:
            self.uiTypeComboBox.setCurrentIndex(0)  # L2 image
        else:
            self.uiTypeComboBox.setCurrentIndex(1)  # L3 image

    def _typeChangedSlot(self, image_type):
        """
        When the type of IOU device is changed.

        :param image_type: type of image (L2 or L3)
        """

        if image_type == "L2 image":
            #  L2 image
            self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/multilayer_switch.normal.svg"))
        else:
            #  L3 image
            self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/router.normal.svg"))

    def initializePage(self, page_id):

        if self.page(page_id) == self.uiServerWizardPage:
            self.uiRemoteServersComboBox.clear()
            for server in Servers.instance().remoteServers().values():
                self.uiRemoteServersComboBox.addItem("{}:{}".format(server.host, server.port), server)
        if self.page(page_id) == self.uiNameImageWizardPage:
            if not self.uiIOUImageToolButton.isEnabled():
                QtGui.QMessageBox.warning(self, "IOU image", "You have chosen to use a remote server, please provide the path to an IOU image located on this server!")

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        if self.currentPage() == self.uiNameImageWizardPage:
            name = self.uiNameLineEdit.text()
            for iou_device in self._iou_devices.values():
                if iou_device["name"] == name:
                    QtGui.QMessageBox.critical(self, "Name", "{} is already used, please choose another name".format(name))
                    return False
        return True

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        path = self.uiIOUImageLineEdit.text()

        if self.uiTypeComboBox.currentText() == "L2 image":
            # set the default L2 base initial-config
            resource_name = "configs/iou_l2_base_initial-config.txt"
            if hasattr(sys, "frozen") and os.path.isfile(resource_name):
                initial_config = os.path.normpath(resource_name)
            elif pkg_resources.resource_exists("gns3", resource_name):
                iou_base_config_path = pkg_resources.resource_filename("gns3", resource_name)
                initial_config = os.path.normpath(iou_base_config_path)
            default_symbol = ":/symbols/multilayer_switch.normal.svg"
            hover_symbol = ":/symbols/multilayer_switch.selected.svg"
            category = Node.switches
        else:
            # set the default L3 base initial-config
            resource_name = "configs/iou_l3_base_initial-config.txt"
            if hasattr(sys, "frozen") and os.path.isfile(resource_name):
                initial_config = os.path.normpath(resource_name)
            elif pkg_resources.resource_exists("gns3", resource_name):
                iou_base_config_path = pkg_resources.resource_filename("gns3", resource_name)
                initial_config = os.path.normpath(iou_base_config_path)
            default_symbol = ":/symbols/router.normal.svg"
            hover_symbol = ":/symbols/router.selected.svg"
            category = Node.routers

        if IOU.instance().settings()["use_local_server"] or self.uiLocalRadioButton.isChecked():
            server = "local"
        elif self.uiRemoteRadioButton.isChecked():
            if self.uiLoadBalanceCheckBox.isChecked():
                server = next(iter(Servers.instance()))
                if not server:
                    QtGui.QMessageBox.critical(self, "IOU device", "No remote server available!")
                    return
                server = "{}:{}".format(server.host, server.port)
            else:
                server = self.uiRemoteServersComboBox.currentText()
        else: # Cloud is selected
            server = "cloud"

        settings = {
            "name": self.uiNameLineEdit.text(),
            "path": path,
            "image": os.path.basename(path),
            "initial_config": initial_config,
            "default_symbol": default_symbol,
            "category": category,
            "hover_symbol": hover_symbol,
            "server": server,
        }

        return settings
