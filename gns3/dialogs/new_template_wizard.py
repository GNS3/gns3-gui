# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 GNS3 Technologies Inc.
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

import sys
import tempfile
import json
import sip
import os

from gns3.qt import QtCore, QtWidgets, qpartial
from gns3.controller import Controller
from gns3.appliance_manager import ApplianceManager

from ..ui.new_template_wizard_ui import Ui_NewTemplateWizard

import logging
log = logging.getLogger(__name__)


class NewTemplateWizard(QtWidgets.QWizard, Ui_NewTemplateWizard):
    """
    New template wizard.
    """

    def __init__(self, parent):

        super().__init__(parent)
        self.setupUi(self)

        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        if sys.platform.startswith("darwin"):
            # we want to see the cancel button on OSX
            self.setOptions(QtWidgets.QWizard.NoDefaultButton)

        # add a custom button to show appliance information
        self.setButtonText(QtWidgets.QWizard.CustomButton1, "&Update from online registry")
        self.setOption(QtWidgets.QWizard.HaveCustomButton1, True)
        self.customButtonClicked.connect(self._downloadAppliancesSlot)
        self.button(QtWidgets.QWizard.CustomButton1).hide()
        self.uiFilterLineEdit.textChanged.connect(self._filterTextChangedSlot)
        ApplianceManager.instance().appliances_changed_signal.connect(self._appliancesChangedSlot)

    def _downloadAppliancesSlot(self):
        """
        Request server to update appliances from online registry.
        """

        ApplianceManager.instance().refresh(update=True)
        Controller.instance().clearStaticCache()

    def _appliancesChangedSlot(self):
        """
        Called when the appliances have been updated.
        """

        self._get_appliances_from_server()
        QtWidgets.QMessageBox.information(self, "Appliances", "Appliances are up-to-date!")

    def _filterTextChangedSlot(self, text):
        self._get_appliances_from_server(appliance_filter=text)

    def _setItemIcon(self, item, icon):

        if item is None or sip.isdeleted(item):
            return
        item.setIcon(0, icon)

    def _get_tooltip_text(self, appliance):
        """
        Gets the appliance information to be displayed in the tooltip.
        """

        info = (("Product", "product_name"),
                ("Vendor", "vendor_name"),
                ("Availability", "availability"),
                ("Status", "status"),
                ("Maintainer", "maintainer"))

        if "qemu" in appliance:
            qemu_info = (("vCPUs", "qemu/cpus"),
                         ("RAM", "qemu/ram"),
                         ("Adapters", "qemu/adapters"),
                         ("Adapter type", "qemu/adapter_type"),
                         ("Console type", "qemu/console_type"),
                         ("Architecture", "qemu/arch"),
                         ("Console type", "qemu/console_type"),
                         ("KVM", "qemu/kvm"))
            info = info + qemu_info

        elif "docker" in appliance:
            docker_info = (("Image", "docker/image"),
                           ("Adapters", "docker/adapters"),
                           ("Console type", "docker/console_type"))
            info = info + docker_info

        elif "iou" in appliance:
            iou_info = (("RAM", "iou/ram"),
                        ("NVRAM", "iou/nvram"),
                        ("Ethernet adapters", "iou/ethernet_adapters"),
                        ("Serial adapters", "iou/serial_adapters"))
            info = info + iou_info

        elif "dynamips" in appliance:
            dynamips_info = (("Platform", "dynamips/platform"),
                             ("Chassis", "dynamips/chassis"),
                             ("Midplane", "dynamips/midplane"),
                             ("NPE", "dynamips/npe"),
                             ("RAM", "dynamips/ram"),
                             ("NVRAM", "dynamips/nvram"),
                             ("slot0", "dynamips/slot0"),
                             ("slot1", "dynamips/slot1"),
                             ("slot2", "dynamips/slot2"),
                             ("slot3", "dynamips/slot3"),
                             ("slot4", "dynamips/slot4"),
                             ("slot5", "dynamips/slot5"),
                             ("slot6", "dynamips/slot6"),
                             ("wic0", "dynamips/wic0"),
                             ("wic1", "dynamips/wic1"),
                             ("wic2", "dynamips/wic2"))
            info = info + dynamips_info

        text_info = ""
        for (name, key) in info:
            if "/" in key:
                key, subkey = key.split("/")
                value = appliance.get(key, {}).get(subkey, None)
            else:
                value = appliance.get(key, None)
            if value is None:
                continue
            text_info += "<span style='font-weight:bold;'>{}</span>: {}<br>".format(name, value)

        return text_info

    def _get_appliances_from_server(self, appliance_filter=None):
        """
        Gets the appliances from the server and display them.
        """

        self.uiAppliancesTreeWidget.clear()
        parent_routers = QtWidgets.QTreeWidgetItem(self.uiAppliancesTreeWidget)
        parent_routers.setText(0, "Routers")
        parent_routers.setFlags(parent_routers.flags() & ~QtCore.Qt.ItemIsSelectable)
        parent_switches = QtWidgets.QTreeWidgetItem(self.uiAppliancesTreeWidget)
        parent_switches.setText(0, "Switches")
        parent_switches.setFlags(parent_switches.flags() & ~QtCore.Qt.ItemIsSelectable)
        parent_guests = QtWidgets.QTreeWidgetItem(self.uiAppliancesTreeWidget)
        parent_guests.setText(0, "Guests")
        parent_guests.setFlags(parent_guests.flags() & ~QtCore.Qt.ItemIsSelectable)
        parent_firewalls = QtWidgets.QTreeWidgetItem(self.uiAppliancesTreeWidget)
        parent_firewalls.setText(0, "Firewalls")
        parent_firewalls.setFlags(parent_firewalls.flags() & ~QtCore.Qt.ItemIsSelectable)
        self.uiAppliancesTreeWidget.expandAll()

        for appliance in ApplianceManager.instance().appliances():
            if appliance_filter is None:
                appliance_filter = self.uiFilterLineEdit.text().strip()
            if appliance_filter and appliance_filter.lower() not in appliance["name"].lower():
                continue

            if appliance["category"] == "router":
                item = QtWidgets.QTreeWidgetItem(parent_routers)
            elif appliance["category"].endswith("switch"):
                item = QtWidgets.QTreeWidgetItem(parent_switches)
            elif appliance["category"] == "firewall":
                item = QtWidgets.QTreeWidgetItem(parent_firewalls)
            elif appliance["category"] == "guest":
                item = QtWidgets.QTreeWidgetItem(parent_guests)
            if appliance["builtin"]:
                appliance_name = appliance["name"]
            else:
                appliance_name = "{} (custom)".format(appliance["name"])

            item.setText(0, appliance_name)
            #item.setText(1, appliance["category"].capitalize().replace("_", " "))

            if "qemu" in appliance:
                item.setText(1, "Qemu")
            elif "iou" in appliance:
                item.setText(1, "IOU")
            elif "dynamips" in appliance:
                item.setText(1, "Dynamips")
            elif "docker" in appliance:
                item.setText(1, "Docker")
            else:
                item.setText(1, "N/A")

            item.setText(2, appliance["vendor_name"])
            item.setData(0, QtCore.Qt.UserRole, appliance)

            #item.setSizeHint(0, QtCore.QSize(32, 32))
            item.setToolTip(0, self._get_tooltip_text(appliance))
            Controller.instance().getSymbolIcon(appliance.get("symbol"), qpartial(self._setItemIcon, item),
                                                fallback=":/symbols/" + appliance["category"] + ".svg")

        self.uiAppliancesTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.uiAppliancesTreeWidget.resizeColumnToContents(0)
        if not appliance_filter:
            self.uiAppliancesTreeWidget.collapseAll()

    def initializePage(self, page_id):
        """
        Initialize Wizard pages.

        :param page_id: page identifier
        """

        super().initializePage(page_id)
        if self.page(page_id) == self.uiApplianceFromServerWizardPage:
            self.button(QtWidgets.QWizard.CustomButton1).show()
            self.setButtonText(QtWidgets.QWizard.FinishButton, "&Install")
            self._get_appliances_from_server()
        else:
            self.button(QtWidgets.QWizard.CustomButton1).hide()

    def cleanupPage(self, page_id):
        """
        Restore button default settings on the first page.
        """

        self.button(QtWidgets.QWizard.CustomButton1).hide()
        self.setButtonText(QtWidgets.QWizard.FinishButton, "&Finish")
        super().cleanupPage(page_id)

    def validateCurrentPage(self):
        """
        Validates if an appliance can be installed.
        """

        if self.currentPage() == self.uiSelectTemplateSourceWizardPage and not Controller.instance().connected():
            QtWidgets.QMessageBox.critical(self, "New template", "There is no connection to the server")
            return False
        elif self.currentPage() == self.uiApplianceFromServerWizardPage:
            if not self.uiAppliancesTreeWidget.selectedItems():
                QtWidgets.QMessageBox.critical(self, "New template", "Please select an appliance to install!")
                return False
        return True

    def nextId(self):
        """
        Wizard rules!
        """

        current_id = self.currentId()
        if self.page(current_id) == self.uiSelectTemplateSourceWizardPage and \
                (self.uiImportApplianceFromFileRadioButton.isChecked() or self.uiCreateTemplateManuallyRadioButton.isChecked()):
            self.done(True)
        return super().nextId()

    def done(self, result):
        """
        This dialog is closed.
        """

        super().done(result)
        if result:
            #ApplianceManager.instance().appliances_changed_signal.disconnect(self._appliancesChangedSlot)
            from gns3.main_window import MainWindow
            if self.currentPage() == self.uiApplianceFromServerWizardPage:
                items = self.uiAppliancesTreeWidget.selectedItems()
                for item in items:
                    f = tempfile.NamedTemporaryFile(mode="w+", suffix=".builtin.gns3a", delete=False)
                    json.dump(item.data(0, QtCore.Qt.UserRole), f)
                    f.close()
                    MainWindow.instance().loadPath(f.name)
                    try:
                        os.remove(f.name)
                    except OSError:
                        pass
            elif self.uiCreateTemplateManuallyRadioButton.isChecked():
                MainWindow.instance().preferencesActionSlot()
            elif self.uiImportApplianceFromFileRadioButton.isChecked():
                from gns3.main_window import MainWindow
                MainWindow.instance().openApplianceActionSlot()
