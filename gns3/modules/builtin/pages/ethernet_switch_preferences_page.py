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
Configuration page for Ethernet switch preferences.
"""

import copy

from gns3.qt import QtCore, QtWidgets, qpartial
from gns3.controller import Controller

from gns3.main_window import MainWindow
from gns3.dialogs.configuration_dialog import ConfigurationDialog
from gns3.compute_manager import ComputeManager
from gns3.template_manager import TemplateManager
from gns3.template import Template

from ..settings import ETHERNET_SWITCH_SETTINGS
from ..ui.ethernet_switch_preferences_page_ui import Ui_EthernetSwitchPreferencesPageWidget
from ..pages.ethernet_switch_configuration_page import EthernetSwitchConfigurationPage
from ..dialogs.ethernet_switch_wizard import EthernetSwitchWizard


class EthernetSwitchPreferencesPage(QtWidgets.QWidget, Ui_EthernetSwitchPreferencesPageWidget):
    """
    QWidget preference page for Ethernet switch preferences.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._ethernet_switches = {}
        self._items = []

        self.uiNewEthernetSwitchPushButton.clicked.connect(self._newEthernetSwitchSlot)
        self.uiEditEthernetSwitchPushButton.clicked.connect(self._editEthernetSwitchSlot)
        self.uiDeleteEthernetSwitchPushButton.clicked.connect(self._deleteEthernetSwitchSlot)
        self.uiEthernetSwitchesTreeWidget.itemSelectionChanged.connect(self._ethernetSwitchChangedSlot)
        self.uiEthernetSwitchesTreeWidget.itemDoubleClicked.connect(self._editEthernetSwitchSlot)

    def _createSectionItem(self, name):
        """
        Adds a new section to the tree widget.

        :param name: section name
        """

        section_item = QtWidgets.QTreeWidgetItem(self.uiEthernetSwitchInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, ethernet_switch):
        """
        Refreshes the content of the tree widget.
        """

        self.uiEthernetSwitchInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtWidgets.QTreeWidgetItem(section_item, ["Template name:", ethernet_switch["name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Template ID:", ethernet_switch.get("template_id", "none")])
        QtWidgets.QTreeWidgetItem(section_item, ["Default name format:", ethernet_switch["default_name_format"]])
        try:
            compute_id = ethernet_switch.get("compute_id")
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

        QtWidgets.QTreeWidgetItem(section_item, ["Console type:", ethernet_switch["console_type"]])
        for port in ethernet_switch["ports_mapping"]:
            section_item = self._createSectionItem("Port{}".format(port["port_number"]))
            QtWidgets.QTreeWidgetItem(section_item, ["Name:", port["name"]])
            QtWidgets.QTreeWidgetItem(section_item, ["Type:", port["type"]])
            QtWidgets.QTreeWidgetItem(section_item, ["VLAN:", str(port["vlan"])])

        self.uiEthernetSwitchInfoTreeWidget.expandAll()
        self.uiEthernetSwitchInfoTreeWidget.resizeColumnToContents(0)
        self.uiEthernetSwitchInfoTreeWidget.resizeColumnToContents(1)
        self.uiEthernetSwitchesTreeWidget.setMaximumWidth(self.uiEthernetSwitchesTreeWidget.sizeHintForColumn(0) + 20)

    def _ethernetSwitchChangedSlot(self):
        """
        Loads a selected Ethernet switch from the tree widget.
        """

        selection = self.uiEthernetSwitchesTreeWidget.selectedItems()
        self.uiDeleteEthernetSwitchPushButton.setEnabled(len(selection) != 0)
        single_selected = len(selection) == 1
        self.uiEditEthernetSwitchPushButton.setEnabled(single_selected)

        if single_selected:
            key = selection[0].data(0, QtCore.Qt.UserRole)
            ethernet_switch = self._ethernet_switches[key]
            self._refreshInfo(ethernet_switch)
        else:
            self.uiEthernetSwitchInfoTreeWidget.clear()

    def _newEthernetSwitchSlot(self):
        """
        Creates a new Ethernet switch.
        """

        wizard = EthernetSwitchWizard(self._ethernet_switches, parent=self)
        wizard.show()
        if wizard.exec_():
            new_ethernet_switch_settings = wizard.getSettings()
            key = "{server}:{name}".format(server=new_ethernet_switch_settings["compute_id"], name=new_ethernet_switch_settings["name"])
            self._ethernet_switches[key] = ETHERNET_SWITCH_SETTINGS.copy()
            self._ethernet_switches[key].update(new_ethernet_switch_settings)

            item = QtWidgets.QTreeWidgetItem(self.uiEthernetSwitchesTreeWidget)
            item.setText(0, self._ethernet_switches[key]["name"])
            Controller.instance().getSymbolIcon(self._ethernet_switches[key]["symbol"], qpartial(self._setItemIcon, item))

            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiEthernetSwitchesTreeWidget.setCurrentItem(item)

    def _editEthernetSwitchSlot(self):
        """
        Edits an Ethernet switch.
        """

        item = self.uiEthernetSwitchesTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            ethernet_switch = self._ethernet_switches[key]
            dialog = ConfigurationDialog(ethernet_switch["name"], ethernet_switch, EthernetSwitchConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                # update the icon
                Controller.instance().getSymbolIcon(ethernet_switch["symbol"], qpartial(self._setItemIcon, item))
                if ethernet_switch["name"] != item.text(0):
                    new_key = "{server}:{name}".format(server=ethernet_switch["compute_id"], name=ethernet_switch["name"])
                    if new_key in self._ethernet_switches:
                        QtWidgets.QMessageBox.critical(self, "Ethernet switch", "Ethernet switch name {} already exists for server {}".format(ethernet_switch["name"],
                                                                                                                                              ethernet_switch["compute_id"]))
                        ethernet_switch["name"] = item.text(0)
                        return
                    self._ethernet_switches[new_key] = self._ethernet_switches[key]
                    del self._ethernet_switches[key]
                    item.setText(0, ethernet_switch["name"])
                    item.setData(0, QtCore.Qt.UserRole, new_key)
                self._refreshInfo(ethernet_switch)

    def _deleteEthernetSwitchSlot(self):
        """
        Deletes an Ethernet switch.
        """
        for item in self.uiEthernetSwitchesTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)
                del self._ethernet_switches[key]
                self.uiEthernetSwitchesTreeWidget.takeTopLevelItem(self.uiEthernetSwitchesTreeWidget.indexOfTopLevelItem(item))

    def loadPreferences(self):
        """
        Loads the ethernet switch preferences.
        """

        self._ethernet_switches = {}
        templates = TemplateManager.instance().templates()
        for template_id, template in templates.items():
            if template.template_type() == "ethernet_switch" and not template.builtin():
                name = template.name()
                server = template.compute_id()
                #TODO: use template id for the key
                key = "{server}:{name}".format(server=server, name=name)
                self._ethernet_switches[key] = copy.deepcopy(template.settings())

        self._items.clear()
        for key, ethernet_switch in self._ethernet_switches.items():
            item = QtWidgets.QTreeWidgetItem(self.uiEthernetSwitchesTreeWidget)
            item.setText(0, ethernet_switch["name"])
            Controller.instance().getSymbolIcon(ethernet_switch["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiEthernetSwitchesTreeWidget.setCurrentItem(self._items[0])
            self.uiEthernetSwitchesTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.uiEthernetSwitchesTreeWidget.setMaximumWidth(self.uiEthernetSwitchesTreeWidget.sizeHintForColumn(0) + 20)

    def _setItemIcon(self, item, icon):
        """
        Sets an item icon.
        """

        item.setIcon(0, icon)
        self.uiEthernetSwitchesTreeWidget.setMaximumWidth(self.uiEthernetSwitchesTreeWidget.sizeHintForColumn(0) + 20)

    def savePreferences(self):
        """
        Saves the Ethernet switch preferences.
        """

        templates = []
        for template in TemplateManager.instance().templates().values():
            if template.template_type() != "ethernet_switch":
                templates.append(template)
        for template_settings in self._ethernet_switches.values():
            templates.append(Template(template_settings))
        TemplateManager.instance().updateList(templates)

