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
Configuration page for cloud node preferences.
"""

import copy

from gns3.qt import QtCore, QtGui, QtWidgets, qpartial
from gns3.main_window import MainWindow
from gns3.dialogs.configuration_dialog import ConfigurationDialog
from gns3.compute_manager import ComputeManager
from gns3.controller import Controller

from .. import Builtin
from ..settings import CLOUD_SETTINGS
from ..ui.cloud_preferences_page_ui import Ui_CloudPreferencesPageWidget
from ..pages.cloud_configuration_page import CloudConfigurationPage
from ..dialogs.cloud_wizard import CloudWizard


class CloudPreferencesPage(QtWidgets.QWidget, Ui_CloudPreferencesPageWidget):
    """
    QWidget preference page for cloud node preferences.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._cloud_nodes = {}
        self._items = []

        self.uiNewCloudNodePushButton.clicked.connect(self._newCloudNodeSlot)
        self.uiEditCloudNodePushButton.clicked.connect(self._editCloudNodeSlot)
        self.uiDeleteCloudNodePushButton.clicked.connect(self._deleteCloudNodeSlot)
        self.uiCloudNodesTreeWidget.itemSelectionChanged.connect(self._cloudNodeChangedSlot)

    def _createSectionItem(self, name):

        section_item = QtWidgets.QTreeWidgetItem(self.uiCloudNodeInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, cloud_node):

        self.uiCloudNodeInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtWidgets.QTreeWidgetItem(section_item, ["Template name:", cloud_node["name"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Default name format:", cloud_node["default_name_format"]])
        try:
            QtWidgets.QTreeWidgetItem(section_item, ["Server:", ComputeManager.instance().getCompute(cloud_node["server"]).name()])
        except KeyError:
            pass

        self.uiCloudNodeInfoTreeWidget.expandAll()
        self.uiCloudNodeInfoTreeWidget.resizeColumnToContents(0)
        self.uiCloudNodeInfoTreeWidget.resizeColumnToContents(1)
        self.uiCloudNodesTreeWidget.setMaximumWidth(self.uiCloudNodesTreeWidget.sizeHintForColumn(0) + 20)

    def _cloudNodeChangedSlot(self):
        """
        Loads a selected cloud node template from the tree widget.
        """

        selection = self.uiCloudNodesTreeWidget.selectedItems()
        self.uiDeleteCloudNodePushButton.setEnabled(len(selection) != 0)
        single_selected = len(selection) == 1
        self.uiEditCloudNodePushButton.setEnabled(single_selected)

        if single_selected:
            key = selection[0].data(0, QtCore.Qt.UserRole)
            cloud_node = self._cloud_nodes[key]
            self._refreshInfo(cloud_node)
        else:
            self.uiCloudNodeInfoTreeWidget.clear()

    def _newCloudNodeSlot(self):
        """
        Creates a new cloud node template.
        """

        wizard = CloudWizard(self._cloud_nodes, parent=self)
        wizard.show()
        if wizard.exec_():
            new_cloud_settings = wizard.getSettings()
            key = "{server}:{name}".format(server=new_cloud_settings["server"], name=new_cloud_settings["name"])
            self._cloud_nodes[key] = CLOUD_SETTINGS.copy()
            self._cloud_nodes[key].update(new_cloud_settings)

            item = QtWidgets.QTreeWidgetItem(self.uiCloudNodesTreeWidget)
            item.setText(0, self._cloud_nodes[key]["name"])
            Controller.instance().getSymbolIcon(self._cloud_nodes[key]["symbol"], qpartial(self._setItemIcon, item))

            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiCloudNodesTreeWidget.setCurrentItem(item)

    def _editCloudNodeSlot(self):
        """
        Edits a cloud node template.
        """

        item = self.uiCloudNodesTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            cloud_node = self._cloud_nodes[key]
            dialog = ConfigurationDialog(cloud_node["name"], cloud_node, CloudConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                # update the icon
                Controller.instance().getSymbolIcon(cloud_node["symbol"], qpartial(self._setItemIcon, item))
                if cloud_node["name"] != item.text(0):
                    new_key = "{server}:{name}".format(server=cloud_node["server"], name=cloud_node["name"])
                    if new_key in self._cloud_nodes:
                        QtWidgets.QMessageBox.critical(self, "Cloud node", "Cloud node name {} already exists for server {}".format(cloud_node["name"],
                                                                                                                                    cloud_node["server"]))
                        cloud_node["name"] = item.text(0)
                        return
                    self._cloud_nodes[new_key] = self._cloud_nodes[key]
                    del self._cloud_nodes[key]
                    item.setText(0, cloud_node["name"])
                    item.setData(0, QtCore.Qt.UserRole, new_key)
                self._refreshInfo(cloud_node)

    def _deleteCloudNodeSlot(self):
        """
        Deletes a cloud node template.
        """

        for item in self.uiCloudNodesTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)
                del self._cloud_nodes[key]
                self.uiCloudNodesTreeWidget.takeTopLevelItem(self.uiCloudNodesTreeWidget.indexOfTopLevelItem(item))

    def loadPreferences(self):
        """
        Loads the cloud node preferences.
        """

        builtin_module = Builtin.instance()
        self._cloud_nodes = copy.deepcopy(builtin_module.cloudNodes())
        self._items.clear()

        for key, cloud_node in self._cloud_nodes.items():
            item = QtWidgets.QTreeWidgetItem(self.uiCloudNodesTreeWidget)
            item.setText(0, cloud_node["name"])
            Controller.instance().getSymbolIcon(cloud_node["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiCloudNodesTreeWidget.setCurrentItem(self._items[0])
            self.uiCloudNodesTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.uiCloudNodesTreeWidget.setMaximumWidth(self.uiCloudNodesTreeWidget.sizeHintForColumn(0) + 20)

    def _setItemIcon(self, item, icon):
        item.setIcon(0, icon)
        self.uiCloudNodesTreeWidget.setMaximumWidth(self.uiCloudNodesTreeWidget.sizeHintForColumn(0) + 20)

    def savePreferences(self):
        """
        Saves the cloud node preferences.
        """

        Builtin.instance().setCloudNodes(self._cloud_nodes)
