# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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
Configuration page for Ethernet hub preferences.
"""

import copy

from gns3.qt import QtCore, QtGui, QtWidgets, qpartial

from gns3.main_window import MainWindow
from gns3.dialogs.configuration_dialog import ConfigurationDialog
from gns3.compute_manager import ComputeManager
from gns3.controller import Controller

from .. import Builtin
from ..settings import ETHERNET_HUB_SETTINGS
from ..ui.ethernet_hub_preferences_page_ui import Ui_EthernetHubPreferencesPageWidget
from ..pages.ethernet_hub_configuration_page import EthernetHubConfigurationPage
from ..dialogs.ethernet_hub_wizard import EthernetHubWizard


class EthernetHubPreferencesPage(QtWidgets.QWidget, Ui_EthernetHubPreferencesPageWidget):
    """
    QWidget preference page for Ethernet hub preferences.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._ethernet_hubs = {}
        self._items = []

        self.uiNewEthernetHubPushButton.clicked.connect(self._newEthernetHubSlot)
        self.uiEditEthernetHubPushButton.clicked.connect(self._editEthernetHubSlot)
        self.uiDeleteEthernetHubPushButton.clicked.connect(self._deleteEthernetHubSlot)
        self.uiEthernetHubsTreeWidget.itemSelectionChanged.connect(self._ethernetHubChangedSlot)

    def _createSectionItem(self, name):

        section_item = QtWidgets.QTreeWidgetItem(self.uiEthernetHubInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, ethernet_hub):

        self.uiEthernetHubInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtWidgets.QTreeWidgetItem(section_item, ["Template name:", ethernet_hub["name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Default name format:", ethernet_hub["default_name_format"]])
        try:
            QtWidgets.QTreeWidgetItem(section_item, ["Server:", ComputeManager.instance().getCompute(ethernet_hub["server"]).name()])
        except KeyError:
            pass
        QtWidgets.QTreeWidgetItem(section_item, ["Number of ports:", str(len(ethernet_hub["ports_mapping"]))])

        self.uiEthernetHubInfoTreeWidget.expandAll()
        self.uiEthernetHubInfoTreeWidget.resizeColumnToContents(0)
        self.uiEthernetHubInfoTreeWidget.resizeColumnToContents(1)
        self.uiEthernetHubsTreeWidget.setMaximumWidth(self.uiEthernetHubsTreeWidget.sizeHintForColumn(0) + 20)

    def _ethernetHubChangedSlot(self):
        """
        Loads a selected Ethernet hub template from the tree widget.
        """

        selection = self.uiEthernetHubsTreeWidget.selectedItems()
        self.uiDeleteEthernetHubPushButton.setEnabled(len(selection) != 0)
        single_selected = len(selection) == 1
        self.uiEditEthernetHubPushButton.setEnabled(single_selected)

        if single_selected:
            key = selection[0].data(0, QtCore.Qt.UserRole)
            ethernet_hub = self._ethernet_hubs[key]
            self._refreshInfo(ethernet_hub)
        else:
            self.uiEthernetHubInfoTreeWidget.clear()

    def _newEthernetHubSlot(self):
        """
        Creates a new Ethernet hub template.
        """

        wizard = EthernetHubWizard(self._ethernet_hubs, parent=self)
        wizard.show()
        if wizard.exec_():
            new_ethernet_hub_settings = wizard.getSettings()
            key = "{server}:{name}".format(server=new_ethernet_hub_settings["server"], name=new_ethernet_hub_settings["name"])
            self._ethernet_hubs[key] = ETHERNET_HUB_SETTINGS.copy()
            self._ethernet_hubs[key].update(new_ethernet_hub_settings)

            item = QtWidgets.QTreeWidgetItem(self.uiEthernetHubsTreeWidget)
            item.setText(0, self._ethernet_hubs[key]["name"])
            Controller.instance().getSymbolIcon(self._ethernet_hubs[key]["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiEthernetHubsTreeWidget.setCurrentItem(item)

    def _editEthernetHubSlot(self):
        """
        Edits an Ethernet hub template.
        """

        item = self.uiEthernetHubsTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            ethernet_hub = self._ethernet_hubs[key]
            dialog = ConfigurationDialog(ethernet_hub["name"], ethernet_hub, EthernetHubConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                # update the icon
                Controller.instance().getSymbolIcon(ethernet_hub["symbol"], qpartial(self._setItemIcon, item))
                if ethernet_hub["name"] != item.text(0):
                    new_key = "{server}:{name}".format(server=ethernet_hub["server"], name=ethernet_hub["name"])
                    if new_key in self._ethernet_hubs:
                        QtWidgets.QMessageBox.critical(self, "Ethernet hub", "Ethernet hub name {} already exists for server {}".format(ethernet_hub["name"],
                                                                                                                                        ethernet_hub["server"]))
                        ethernet_hub["name"] = item.text(0)
                        return
                    self._ethernet_hubs[new_key] = self._ethernet_hubs[key]
                    del self._ethernet_hubs[key]
                    item.setText(0, ethernet_hub["name"])
                    item.setData(0, QtCore.Qt.UserRole, new_key)
                self._refreshInfo(ethernet_hub)

    def _deleteEthernetHubSlot(self):
        """
        Deletes an Ethernet hub template.
        """

        for item in self.uiEthernetHubsTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)
                del self._ethernet_hubs[key]
                self.uiEthernetHubsTreeWidget.takeTopLevelItem(self.uiEthernetHubsTreeWidget.indexOfTopLevelItem(item))

    def loadPreferences(self):
        """
        Loads the ethernet hub preferences.
        """

        builtin_module = Builtin.instance()
        self._ethernet_hubs = copy.deepcopy(builtin_module.ethernetHubs())
        self._items.clear()

        for key, ethernet_hub in self._ethernet_hubs.items():
            item = QtWidgets.QTreeWidgetItem(self.uiEthernetHubsTreeWidget)
            item.setText(0, ethernet_hub["name"])
            Controller.instance().getSymbolIcon(ethernet_hub["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiEthernetHubsTreeWidget.setCurrentItem(self._items[0])
            self.uiEthernetHubsTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.uiEthernetHubsTreeWidget.setMaximumWidth(self.uiEthernetHubsTreeWidget.sizeHintForColumn(0) + 20)

    def _setItemIcon(self, item, icon):
        item.setIcon(0, icon)
        self.uiEthernetHubsTreeWidget.setMaximumWidth(self.uiEthernetHubsTreeWidget.sizeHintForColumn(0) + 20)

    def savePreferences(self):
        """
        Saves the Ethernet hub preferences.
        """

        Builtin.instance().setEthernetHubs(self._ethernet_hubs)
