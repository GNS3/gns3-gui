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

"""Wizard for Docker images."""

import sys

from gns3.qt import QtGui, QtWidgets
from gns3.dialogs.vm_wizard import VMWizard

from ..ui.docker_vm_wizard_ui import Ui_DockerVMWizard
from .. import Docker


class DockerVMWizard(VMWizard, Ui_DockerVMWizard):
    """Wizard to create a Docker image.

    :param docker_containers: existing Docker images
    :param parent: parent widget
    """

    def __init__(self, docker_containers, parent):

        super().__init__(parent=parent, devices=[], use_local_server=Docker.instance().settings()["use_local_server"])
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(
            ":/icons/docker.png"))

        self.uiNewImageRadioButton.setChecked(True)
        self._existingImageRadioButtonToggledSlot(False)
        self.uiExistingImageRadioButton.toggled.connect(self._existingImageRadioButtonToggledSlot)

        if sys.platform.startswith("win") or sys.platform.startswith("darwin"):
            # Cannot use Docker locally on Windows and Mac
            self.uiLocalRadioButton.setEnabled(False)

        self._docker_containers = docker_containers

    def _existingImageRadioButtonToggledSlot(self, status):
        if self.uiExistingImageRadioButton.isChecked():
            self.uiImageLineEdit.hide()
            self.uiImageNameLabel.hide()
            self.uiImageListLabel.show()
            self.uiImageListComboBox.show()
        else:
            self.uiImageNameLabel.show()
            self.uiImageLineEdit.show()
            self.uiImageListLabel.hide()
            self.uiImageListComboBox.hide()

    def initializePage(self, page_id):

        super().initializePage(page_id)

        if self.page(page_id) == self.uiImageWizardPage:
            Docker.instance().getDockerImagesFromServer(self._server, self._getDockerImagesFromServerCallback)

    def _getDockerImagesFromServerCallback(
            self, result, error=False, **kwargs):
        """Callback for getDockerImagesFromServer.

        :param progress_dialog: QProgressDialog instance
        :param result: server response
        :param error: indicates an error (boolean)
        """
        if error:
            QtWidgets.QMessageBox.critical(
                self, "Docker Images", "{}".format(result["message"]))
        else:
            self.uiImageListComboBox.clear()
            if len(result) == 0:
                self.uiNewImageRadioButton.setChecked(True)
            else:
                self.uiExistingImageRadioButton.setChecked(True)
                for image in result:
                    self.uiImageListComboBox.addItem(image["image"], image)

    def validateCurrentPage(self):
        """Validates the server."""

        if super().validateCurrentPage() is False:
            return False

        if self.currentPage() == self.uiImageWizardPage:
            if self.uiImageListComboBox.currentIndex() < 0 and self.uiExistingImageRadioButton.isChecked():
                QtWidgets.QMessageBox.critical(
                    self, "Docker images",
                    "There are no Docker images selected!")
                return False
            self.uiNameLineEdit.setText(self._getImageName().split(":")[0])

        if self.currentPage() == self.uiNameWizardPage:
            if self.uiNameLineEdit.text() in [ d["name"] for d in self._docker_containers.values() ]:
                QtWidgets.QMessageBox.critical(
                    self, "Container name",
                    "This name already exist!")
                return False
        return True

    def _getImageName(self):
        if self.uiExistingImageRadioButton.isChecked():
            index = self.uiImageListComboBox.currentIndex()
            return self.uiImageListComboBox.itemText(index)
        else:
            name = self.uiImageLineEdit.text()
            return name

    def getSettings(self):
        """Returns the settings set in this Wizard.

        :return: settings
        :rtype: dict
        """

        if self.uiLocalRadioButton.isChecked():
            server = "local"
        elif self.uiRemoteRadioButton.isChecked():
            server = self.uiRemoteServersComboBox.currentText()
        elif self.uiVMRadioButton.isChecked():
            server = "vm"

        image = self._getImageName()
        start_command = self.uiStartCommandLineEdit.text()
        name = self.uiNameLineEdit.text()

        settings = {
            "image": image,
            "server": server,
            "adapters": self.uiAdaptersSpinBox.value(),
            "name": name,
            "environment": self.uiEnvironmentTextEdit.toPlainText(),
            "start_command": start_command,
            "console_type": self.uiConsoleTypeComboBox.currentText()
        }
        return settings
