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

"""
Configuration page for TraceNG node preferences.
"""

import copy

from gns3.qt import QtCore, QtWidgets, qpartial

from gns3.main_window import MainWindow
from gns3.dialogs.configuration_dialog import ConfigurationDialog
from gns3.compute_manager import ComputeManager
from gns3.template_manager import TemplateManager
from gns3.controller import Controller
from gns3.template import Template

from ..settings import TRACENG_NODES_SETTINGS
from ..ui.traceng_node_preferences_page_ui import Ui_TraceNGNodePageWidget
from ..pages.traceng_node_configuration_page import TraceNGNodeConfigurationPage
from ..dialogs.traceng_node_wizard import TraceNGNodeWizard


class TraceNGNodePreferencesPage(QtWidgets.QWidget, Ui_TraceNGNodePageWidget):
    """
    QWidget preference page for TraceNG node preferences.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._traceng_nodes = {}
        self._items = []

        self.uiNewTraceNGPushButton.clicked.connect(self._newTraceNGSlot)
        self.uiEditTraceNGPushButton.clicked.connect(self._editTraceNGSlot)
        self.uiDeleteTraceNGPushButton.clicked.connect(self._deleteTraceNGSlot)
        self.uiTraceNGTreeWidget.itemSelectionChanged.connect(self._tracengChangedSlot)

    def _createSectionItem(self, name):
        """
        Adds a new section to the tree widget.

        :param name: section name
        """

        section_item = QtWidgets.QTreeWidgetItem(self.uiTraceNGInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, traceng_node):
        """
        Refreshes the content of the tree widget.
        """

        self.uiTraceNGInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtWidgets.QTreeWidgetItem(section_item, ["Template name:", traceng_node["name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Template ID:", traceng_node.get("template_id", "none")])
        QtWidgets.QTreeWidgetItem(section_item, ["IP address:", traceng_node["ip_address"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Default name format:", traceng_node["default_name_format"]])
        try:
            QtWidgets.QTreeWidgetItem(section_item, ["Server:", ComputeManager.instance().getCompute(traceng_node["compute_id"]).name()])
        except KeyError:
            pass

        self.uiTraceNGInfoTreeWidget.expandAll()
        self.uiTraceNGInfoTreeWidget.resizeColumnToContents(0)
        self.uiTraceNGInfoTreeWidget.resizeColumnToContents(1)
        self.uiTraceNGTreeWidget.setMaximumWidth(self.uiTraceNGTreeWidget.sizeHintForColumn(0) + 20)

    def _tracengChangedSlot(self):
        """
        Loads a selected TraceNG node from the tree widget.
        """

        selection = self.uiTraceNGTreeWidget.selectedItems()
        self.uiDeleteTraceNGPushButton.setEnabled(len(selection) != 0)
        single_selected = len(selection) == 1
        self.uiEditTraceNGPushButton.setEnabled(single_selected)

        if single_selected:
            key = selection[0].data(0, QtCore.Qt.UserRole)
            traceng_node = self._traceng_nodes[key]
            self._refreshInfo(traceng_node)
        else:
            self.uiTraceNGInfoTreeWidget.clear()

    def _newTraceNGSlot(self):
        """
        Creates a new TraceNG node.
        """

        wizard = TraceNGNodeWizard(self._traceng_nodes, parent=self)
        wizard.show()
        if wizard.exec_():
            new_traceng_node_settings = wizard.getSettings()
            key = "{server}:{name}".format(server=new_traceng_node_settings["compute_id"], name=new_traceng_node_settings["name"])
            self._traceng_nodes[key] = TRACENG_NODES_SETTINGS.copy()
            self._traceng_nodes[key].update(new_traceng_node_settings)

            item = QtWidgets.QTreeWidgetItem(self.uiTraceNGTreeWidget)
            item.setText(0, self._traceng_nodes[key]["name"])
            Controller.instance().getSymbolIcon(self._traceng_nodes[key]["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiTraceNGTreeWidget.setCurrentItem(item)

    def _editTraceNGSlot(self):
        """
        Edits a TraceNG node.
        """

        item = self.uiTraceNGTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            traceng_node = self._traceng_nodes[key]
            dialog = ConfigurationDialog(traceng_node["name"], traceng_node, TraceNGNodeConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                # update the icon
                Controller.instance().getSymbolIcon(traceng_node["symbol"], qpartial(self._setItemIcon, item))
                if traceng_node["name"] != item.text(0):
                    new_key = "{server}:{name}".format(server=traceng_node["compute_id"], name=traceng_node["name"])
                    if new_key in self._traceng_nodes:
                        QtWidgets.QMessageBox.critical(self, "TraceNG node", "TraceNG node name {} already exists for server {}".format(traceng_node["name"],
                                                                                                                                  traceng_node["compute_id"]))
                        traceng_node["name"] = item.text(0)
                        return
                    self._traceng_nodes[new_key] = self._traceng_nodes[key]
                    del self._traceng_nodes[key]
                    item.setText(0, traceng_node["name"])
                    item.setData(0, QtCore.Qt.UserRole, new_key)
                self._refreshInfo(traceng_node)

    def _deleteTraceNGSlot(self):
        """
        Deletes a TraceNG node.
        """

        for item in self.uiTraceNGTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)
                del self._traceng_nodes[key]
                self.uiTraceNGTreeWidget.takeTopLevelItem(self.uiTraceNGTreeWidget.indexOfTopLevelItem(item))

    def loadPreferences(self):
        """
        Loads the TraceNG node preferences.
        """

        self._traceng_nodes  = {}
        templates = TemplateManager.instance().templates()
        for template_id, template in templates.items():
            if template.template_type() == "traceng" and not template.builtin():
                name = template.name()
                server = template.compute_id()
                #TODO: use template id for the key
                key = "{server}:{name}".format(server=server, name=name)
                self._traceng_nodes[key] = copy.deepcopy(template.settings())

        self._items.clear()
        for key, node in self._traceng_nodes.items():
            item = QtWidgets.QTreeWidgetItem(self.uiTraceNGTreeWidget)
            item.setText(0, node["name"])
            Controller.instance().getSymbolIcon(node["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiTraceNGTreeWidget.setCurrentItem(self._items[0])
            self.uiTraceNGTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.uiTraceNGTreeWidget.setMaximumWidth(self.uiTraceNGTreeWidget.sizeHintForColumn(0) + 20)

    def _setItemIcon(self, item, icon):
        item.setIcon(0, icon)
        self.uiTraceNGTreeWidget.setMaximumWidth(self.uiTraceNGTreeWidget.sizeHintForColumn(0) + 20)

    def savePreferences(self):
        """
        Saves the TraceNG node preferences.
        """

        templates = []
        for template in TemplateManager.instance().templates().values():
            if template.template_type() != "traceng":
                templates.append(template)
        for template_settings in self._traceng_nodes.values():
            templates.append(Template(template_settings))
        TemplateManager.instance().updateList(templates)

