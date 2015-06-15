# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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
Configuration page for Docker image preferences.
"""

import copy

from gns3.qt import QtCore, QtGui, QtWidgets
from gns3.main_window import MainWindow
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from gns3.dialogs.configuration_dialog import ConfigurationDialog

from .. import Docker
from ..settings import DOCKER_CONTAINER_SETTINGS
from ..ui.docker_vm_preferences_page_ui import Ui_DockerVMPreferencesPageWidget
from ..pages.docker_vm_configuration_page import DockerVMConfigurationPage
from ..dialogs.docker_vm_wizard import DockerVMWizard


class DockerVMPreferencesPage(
        QtWidgets.QWidget, Ui_DockerVMPreferencesPageWidget):
    """QWidget preference page for Docker image preferences."""

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._docker_images = {}
        self._items = []

        self.uiNewDockerVMPushButton.clicked.connect(self._dockerImageNewSlot)
        self.uiEditDockerVMPushButton.clicked.connect(
            self._dockerImageEditSlot)
        self.uiDeleteDockerVMPushButton.clicked.connect(
            self._dockerImageDeleteSlot)
        self.uiDockerVMsTreeWidget.itemSelectionChanged.connect(
            self._dockerImageChangedSlot)
        self.uiDockerVMsTreeWidget.itemPressed.connect(
            self._dockerImagePressedSlot)

    def _createSectionItem(self, name):
        section_item = QtWidgets.QTreeWidgetItem(self.uiDockerVMInfoTreeWidget)
        section_item.setText(0, name)
        font = section_item.font(0)
        font.setBold(True)
        section_item.setFont(0, font)
        return section_item

    def _refreshInfo(self, docker_image):

        self.uiDockerVMInfoTreeWidget.clear()

        # fill out the General section
        section_item = self._createSectionItem("General")
        QtWidgets.QTreeWidgetItem(
            section_item, ["Image name:", docker_image["imagename"]])
        # FIXME: add more configuration options
        QtWidgets.QTreeWidgetItem(
            section_item, ["CMD:", str(docker_image["startcmd"])])
        # QtWidgets.QTreeWidgetItem(
        #     section_item, ["Server:", docker_image["server"]])

        # # fill out the Network section
        # section_item = self._createSectionItem("Network")
        # QtWidgets.QTreeWidgetItem(
        #     section_item, ["Adapters:", str(docker_image["adapters"])])
        # QtWidgets.QTreeWidgetItem(
        #     section_item, ["Use any adapter:", "{}".format(
        #         docker_image["use_any_adapter"])])
        # QtWidgets.QTreeWidgetItem(
        #     section_item, ["Type:", docker_image["adapter_type"]])

        self.uiDockerVMInfoTreeWidget.expandAll()
        self.uiDockerVMInfoTreeWidget.resizeColumnToContents(0)
        self.uiDockerVMInfoTreeWidget.resizeColumnToContents(1)

    def _dockerImageChangedSlot(self):
        """Loads a selected Docker image from the tree widget."""

        selection = self.uiDockerVMsTreeWidget.selectedItems()
        self.uiDeleteDockerVMPushButton.setEnabled(len(selection) != 0)
        single_selected = len(selection) == 1
        self.uiEditDockerVMPushButton.setEnabled(single_selected)

        if single_selected:
            key = selection[0].data(0, QtCore.Qt.UserRole)
            docker_image = self._docker_images[key]
            self._refreshInfo(docker_image)
        else:
            self.uiDockerVMInfoTreeWidget.clear()

    def _dockerImageNewSlot(self):
        """Creates a new Docker image."""
        wizard = DockerVMWizard(self._docker_images, parent=self)
        wizard.show()
        if wizard.exec_():
            new_image_settings = wizard.getSettings()
            key = "{server}:{imagename}".format(
                server=new_image_settings["server"],
                imagename=new_image_settings["imagename"])
            self._docker_images[key] = DOCKER_CONTAINER_SETTINGS.copy()
            self._docker_images[key].update(new_image_settings)

            item = QtWidgets.QTreeWidgetItem(self.uiDockerVMsTreeWidget)
            item.setText(0, self._docker_images[key]["imagename"])
            item.setIcon(
                0, QtGui.QIcon(self._docker_images[key]["symbol"]))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiDockerVMsTreeWidget.setCurrentItem(item)

    def _dockerImageEditSlot(self):
        """Edits a Docker image"""
        item = self.uiDockerVMsTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            docker_image = self._docker_images[key]
            dialog = ConfigurationDialog(
                docker_image["imagename"], docker_image,
                DockerVMConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                if docker_image["imagename"] != item.text(0):
                    new_key = "{server}:{imagename}".format(
                        server=docker_image["server"],
                        name=docker_image["imagename"])
                    if new_key in self._docker_images:
                        QtWidgets.QMessageBox.critical(
                            self, "Docker image",
                            "Docker image name {} already exists for server {}".format(
                                docker_image["imagename"],
                                docker_image["server"]))
                        docker_image["imagename"] = item.text(0)
                        return
                    self._docker_images[new_key] = self._docker_images[key]
                    del self._docker_images[key]
                    item.setText(0, docker_image["imagename"])
                    item.setData(0, QtCore.Qt.UserRole, new_key)
                self._refreshInfo(docker_image)

    def _dockerImageDeleteSlot(self):
        """Deletes a Docker image."""
        for item in self.uiDockerVMsTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)
                del self._docker_images[key]
                self.uiDockerVMsTreeWidget.takeTopLevelItem(
                    self.uiDockerVMsTreeWidget.indexOfTopLevelItem(item))

    def _dockerImagePressedSlot(self, item, column):
        """Slot for item pressed.

        :param item: ignored
        :param column: ignored
        """
        if QtWidgets.QApplication.mouseButtons() & QtCore.Qt.RightButton:
            self._showContextualMenu()

    def _showContextualMenu(self):
        """Contextual menu."""
        menu = QtWidgets.QMenu()

        change_symbol_action = QtWidgets.QAction("Change symbol", menu)
        change_symbol_action.setIcon(QtGui.QIcon(":/icons/node_conception.svg"))
        change_symbol_action.setEnabled(len(self.uiDockerVMsTreeWidget.selectedItems()) == 1)
        change_symbol_action.triggered.connect(self._changeSymbolSlot)
        menu.addAction(change_symbol_action)

        delete_action = QtWidgets.QAction("Delete", menu)
        delete_action.triggered.connect(self._dockerImageDeleteSlot)
        menu.addAction(delete_action)

        menu.exec_(QtGui.QCursor.pos())

    def _changeSymbolSlot(self):
        """Change a symbol for a Docker image."""
        item = self.uiDockerVMsTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            docker_image = self._docker_images[key]
            dialog = SymbolSelectionDialog(
                self, symbol=docker_image["symbol"],
                category=docker_image["category"])
            dialog.show()
            if dialog.exec_():
                normal_symbol, selected_symbol = dialog.getSymbols()
                category = dialog.getCategory()
                item.setIcon(0, QtGui.QIcon(normal_symbol))
                docker_image["symbol"] = normal_symbol
                docker_image["category"] = category

    def loadPreferences(self):
        """Loads the Docker VM preferences."""

        docker_module = Docker.instance()
        self._docker_images = copy.deepcopy(docker_module.dockerImages())
        self._items.clear()

        for key, docker_image in self._docker_images.items():
            item = QtWidgets.QTreeWidgetItem(self.uiDockerVMsTreeWidget)
            item.setText(0, docker_image["imagename"])
            item.setIcon(0, QtGui.QIcon(docker_image["symbol"]))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiDockerVMsTreeWidget.setCurrentItem(self._items[0])
            self.uiDockerVMsTreeWidget.sortByColumn(
                0, QtCore.Qt.AscendingOrder)

    def savePreferences(self):
        """Saves the Docker image preferences."""
        Docker.instance().setDockerImages(self._docker_images)
