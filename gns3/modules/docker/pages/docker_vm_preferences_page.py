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

from gns3.qt import QtCore, QtGui, QtWidgets, qpartial
from gns3.main_window import MainWindow
from gns3.dialogs.configuration_dialog import ConfigurationDialog
from gns3.compute_manager import ComputeManager
from gns3.controller import Controller

from .. import Docker
from ..settings import DOCKER_CONTAINER_SETTINGS
from ..ui.docker_vm_preferences_page_ui import Ui_DockerVMPreferencesPageWidget
from ..pages.docker_vm_configuration_page import DockerVMConfigurationPage
from ..dialogs.docker_vm_wizard import DockerVMWizard


class DockerVMPreferencesPage(QtWidgets.QWidget, Ui_DockerVMPreferencesPageWidget):
    """
    QWidget preference page for Docker image preferences.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._main_window = MainWindow.instance()
        self._docker_containers = {}
        self._items = []

        self.uiNewDockerVMPushButton.clicked.connect(self._dockerImageNewSlot)
        self.uiEditDockerVMPushButton.clicked.connect(self._dockerImageEditSlot)
        self.uiDeleteDockerVMPushButton.clicked.connect(self._dockerImageDeleteSlot)
        self.uiDockerVMsTreeWidget.itemSelectionChanged.connect(self._dockerImageChangedSlot)

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
        QtWidgets.QTreeWidgetItem(section_item, ["Image name:", docker_image["image"]])
        try:
            QtWidgets.QTreeWidgetItem(section_item, ["Server:", ComputeManager.instance().getCompute(docker_image["server"]).name()])
        except KeyError:
            pass
        QtWidgets.QTreeWidgetItem(section_item, ["Console type:", str(docker_image["console_type"])])
        QtWidgets.QTreeWidgetItem(section_item, ["Default name format:", docker_image["default_name_format"]])
        QtWidgets.QTreeWidgetItem(section_item, ["Adapters:", str(docker_image["adapters"])])
        if docker_image["start_command"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Start command:", str(docker_image["start_command"])])
        if docker_image["environment"]:
            QtWidgets.QTreeWidgetItem(section_item, ["Environment:", str(docker_image["environment"])])

        self.uiDockerVMInfoTreeWidget.expandAll()
        self.uiDockerVMInfoTreeWidget.resizeColumnToContents(0)
        self.uiDockerVMInfoTreeWidget.resizeColumnToContents(1)
        self.uiDockerVMsTreeWidget.setMaximumWidth(self.uiDockerVMsTreeWidget.sizeHintForColumn(0) + 10)

    def _dockerImageChangedSlot(self):
        """
        Loads a selected Docker image from the tree widget.
        """

        selection = self.uiDockerVMsTreeWidget.selectedItems()
        self.uiDeleteDockerVMPushButton.setEnabled(len(selection) != 0)
        single_selected = len(selection) == 1
        self.uiEditDockerVMPushButton.setEnabled(single_selected)

        if single_selected:
            key = selection[0].data(0, QtCore.Qt.UserRole)
            docker_image = self._docker_containers[key]
            self._refreshInfo(docker_image)
        else:
            self.uiDockerVMInfoTreeWidget.clear()

    def _dockerImageNewSlot(self):
        """
        Creates a new Docker image.
        """
        wizard = DockerVMWizard(self._docker_containers, parent=self)
        wizard.show()
        if wizard.exec_():
            new_image_settings = wizard.getSettings()
            key = "{server}:{name}".format(server=new_image_settings["server"], name=new_image_settings["name"])
            self._docker_containers[key] = DOCKER_CONTAINER_SETTINGS.copy()
            self._docker_containers[key].update(new_image_settings)

            item = QtWidgets.QTreeWidgetItem(self.uiDockerVMsTreeWidget)
            item.setText(0, self._docker_containers[key]["name"])
            Controller.instance().getSymbolIcon(self._docker_containers[key]["symbol"], qpartial(self._setItemIcon, item))
            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)
            self.uiDockerVMsTreeWidget.setCurrentItem(item)

    def _dockerImageEditSlot(self):
        """
        Edits a Docker image.
        """

        item = self.uiDockerVMsTreeWidget.currentItem()
        if item:
            key = item.data(0, QtCore.Qt.UserRole)
            docker_image = self._docker_containers[key]
            dialog = ConfigurationDialog(docker_image["name"], docker_image, DockerVMConfigurationPage(), parent=self)
            dialog.show()
            if dialog.exec_():
                # update the icon
                Controller.instance().getSymbolIcon(docker_image["symbol"], qpartial(self._setItemIcon, item))
                if docker_image["name"] != item.text(0):
                    new_key = "{server}:{name}".format(server=docker_image["server"], name=docker_image["name"])
                    if new_key in self._docker_containers:
                        QtWidgets.QMessageBox.critical(self, "Docker image", "Docker container name {} already exists for server {}".format(docker_image["name"],
                                                                                                                                            docker_image["server"]))
                        docker_image["name"] = item.text(0)
                        return
                    self._docker_containers[new_key] = self._docker_containers[key]
                    del self._docker_containers[key]
                    item.setText(0, docker_image["name"])
                    item.setData(0, QtCore.Qt.UserRole, new_key)
                self._refreshInfo(docker_image)

    def _dockerImageDeleteSlot(self):
        """
        Deletes a Docker image.
        """

        for item in self.uiDockerVMsTreeWidget.selectedItems():
            if item:
                key = item.data(0, QtCore.Qt.UserRole)
                del self._docker_containers[key]
                self.uiDockerVMsTreeWidget.takeTopLevelItem(self.uiDockerVMsTreeWidget.indexOfTopLevelItem(item))

    def loadPreferences(self):
        """
        Loads the Docker VM preferences.
        """

        docker_module = Docker.instance()
        self._docker_containers = copy.deepcopy(docker_module.VMs())
        self._items.clear()

        for key, docker_image in self._docker_containers.items():
            item = QtWidgets.QTreeWidgetItem(self.uiDockerVMsTreeWidget)
            item.setText(0, docker_image["name"])

            Controller.instance().getSymbolIcon(docker_image["symbol"], qpartial(self._setItemIcon, item))

            item.setData(0, QtCore.Qt.UserRole, key)
            self._items.append(item)

        if self._items:
            self.uiDockerVMsTreeWidget.setCurrentItem(self._items[0])
            self.uiDockerVMsTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
            self.uiDockerVMsTreeWidget.setMaximumWidth(self.uiDockerVMsTreeWidget.sizeHintForColumn(0) + 10)

    def savePreferences(self):
        """
        Saves the Docker image preferences.
        """

        Docker.instance().setVMs(self._docker_containers)

    def _setItemIcon(self, item, icon):
        item.setIcon(0, icon)
        self.uiDockerVMsTreeWidget.setMaximumWidth(self.uiDockerVMsTreeWidget.sizeHintForColumn(0) + 10)
