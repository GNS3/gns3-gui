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
Configuration page for VPCS node preferences.
"""

import copy

from gns3.qt import QtCore, QtWidgets, qpartial

from gns3.main_window import MainWindow
from gns3.dialogs.configuration_dialog import ConfigurationDialog
from gns3.compute_manager import ComputeManager
from gns3.template_manager import TemplateManager
from gns3.template import Template
from gns3.controller import Controller

from ..settings import VPCS_NODES_SETTINGS
from ..ui.vpcs_node_preferences_page_ui import Ui_VPCSNodePageWidget
from ..pages.vpcs_node_configuration_page import VPCSNodeConfigurationPage
from ..dialogs.vpcs_node_wizard import VPCSNodeWizard


class VPCSNodePreferencesPage(QtWidgets.QWidget, Ui_VPCSNodePageWidget):
    """
    QWidget preference page for VPCS node preferences.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._vpcs_nodes = {}
        self._items = []

        self.uiNewVPCSPushButton.clicked.connect(self._newVPCSSlot)
        self.uiEditVPCSPushButton.clicked.connect(self._editVPCSSlot)
        self.uiDeleteVPCSPushButton.clicked.connect(self._deleteVPCSSlot)
        self.uiVPCSTreeWidget.itemSelectionChanged.connect(self._vpcsChangedSlot)

    def _createSectionItem(self, name):
        """
        Adds a new section to the tree widget.

        :param name: section name
        """

        section_item = QtWidgets.QTreeWidgetItem(self.uiVPCSInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, vpcs_node):
        """
        Refreshes the content of the tree widget.
        """

        self.uiVPCSInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtWidgets.QTreeWidgetItem(section_item, ["Template name:", vpcs_node["name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Template ID:", vpcs_node.get("template_id", "none")])
        QtWidgets.QTreeWidgetItem(section_item, ["Default name format:", vpcs_node["default_name_format"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Console type:", vpcs_node["console_type"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Auto start console:", "{}".format(vpcs_node["console_auto_start"])])
        try:
            QtWidgets.QTreeWidgetItem(section_item, ["Server:", ComputeManager.instance().getCompute(vpcs_node["compute_id"]).name()])
        except KeyError:
            pass
        if vpcs_node["base_script_file"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Base script file:", vpcs_node["base_script_file"]])

        self.uiVPCSInfoTreeWidget.expandAll()
        self.uiVPCSInfoTreeWidget.resizeColumnToContents(0)
        self.uiVPCSInfoTreeWidget.resizeColumnToContents(1)
        self.uiVPCSTreeWidget.setMaximumWidth(self.uiVPCSTreeWidget.sizeHintForColumn(0) + 20)

    def _vpcsChangedSlot(self):
        """
        Loads a selected VPCS node from the tree widget.
        """

        selection = self.uiVPCSTreeWidget.selectedItems()
        self.uiDeleteVPCSPushButton.setEnabled(len(selection) != 0)
        single_selected = len(selection) == 1
        self.uiEditVPCSPushButton.setEnabled(single_selected)

        if single_selected:
            key = selection[0].data(0, QtCore.Qt.UserRole)
            vpcs_node = self._vpcs_nodes[key]
            self._refreshInfo(vpcs_node)
        else:
            self.uiVPCSInfoTreeWidget.clear()

    def _newVPCSSlot(self):
        """
        Creates a new VPCS node.
        """

        wizard = VPCSNodeWizard(self._vpcs_nodes, parent=self)
        wizard.show()
        if wizard.exec_():
            new_vpcs_node_settings = wizard.getSettings()
            key = "{server}:{name}".format(server=new_vpcs_node_settings["compute_id"], name=new_vpcs_node_settings["name"])
            self._vpcs_nodes[key] = VPCS_NODES_SETTINGS.copy()
            self._vpcs_nodes[key].update(new_vpcs_node_settings)

            item = QtWidgets.QTreeWidgetItem(self.uiVPCSTreeWidget)
            item.setText(0, self._vpcs_nodes[key]["name"])
            Controller.instance().getSymbolIcon(self._vpcs_nodes[key]["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiVPCSTreeWidget.setCurrentItem(item)

    def _editVPCSSlot(self):
        """
        Edits a VPCS node.
        """

        item = self.uiVPCSTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            vpcs_node = self._vpcs_nodes[key]
            dialog = ConfigurationDialog(vpcs_node["name"], vpcs_node, VPCSNodeConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                # update the icon
                Controller.instance().getSymbolIcon(vpcs_node["symbol"], qpartial(self._setItemIcon, item))
                if vpcs_node["name"] != item.text(0):
                    new_key = "{server}:{name}".format(server=vpcs_node["compute_id"], name=vpcs_node["name"])
                    if new_key in self._vpcs_nodes:
                        QtWidgets.QMessageBox.critical(self, "VPCS node", "VPCS node name {} already exists for server {}".format(vpcs_node["name"],
                                                                                                                                  vpcs_node["compute_id"]))
                        vpcs_node["name"] = item.text(0)
                        return
                    self._vpcs_nodes[new_key] = self._vpcs_nodes[key]
                    del self._vpcs_nodes[key]
                    item.setText(0, vpcs_node["name"])
                    item.setData(0, QtCore.Qt.UserRole, new_key)
                self._refreshInfo(vpcs_node)

    def _deleteVPCSSlot(self):
        """
        Deletes a VPCS node.
        """

        for item in self.uiVPCSTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)
                del self._vpcs_nodes[key]
                self.uiVPCSTreeWidget.takeTopLevelItem(self.uiVPCSTreeWidget.indexOfTopLevelItem(item))

    def loadPreferences(self):
        """
        Loads the VPCS node preferences.
        """

        self._vpcs_nodes = {}
        templates = TemplateManager.instance().templates()
        for template_id, template in templates.items():
            if template.template_type() == "vpcs" and not template.builtin():
                name = template.name()
                server = template.compute_id()
                #TODO: use template id for the key
                key = "{server}:{name}".format(server=server, name=name)
                self._vpcs_nodes[key] = copy.deepcopy(template.settings())

        self._items.clear()
        for key, node in self._vpcs_nodes.items():
            item = QtWidgets.QTreeWidgetItem(self.uiVPCSTreeWidget)
            item.setText(0, node["name"])
            Controller.instance().getSymbolIcon(node["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiVPCSTreeWidget.setCurrentItem(self._items[0])
            self.uiVPCSTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.uiVPCSTreeWidget.setMaximumWidth(self.uiVPCSTreeWidget.sizeHintForColumn(0) + 20)

    def _setItemIcon(self, item, icon):
        item.setIcon(0, icon)
        self.uiVPCSTreeWidget.setMaximumWidth(self.uiVPCSTreeWidget.sizeHintForColumn(0) + 20)

    def savePreferences(self):
        """
        Saves the VPCS node preferences.
        """

        templates = []
        for template in TemplateManager.instance().templates().values():
            if template.template_type() != "vpcs":
                templates.append(template)
        for template_settings in self._vpcs_nodes.values():
            templates.append(Template(template_settings))
        TemplateManager.instance().updateList(templates)
