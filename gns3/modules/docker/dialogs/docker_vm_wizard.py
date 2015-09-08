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

from gns3.qt import QtGui, QtWidgets
from gns3.dialogs.vm_wizard import VMWizard

from ..ui.docker_vm_wizard_ui import Ui_DockerVMWizard
from .. import Docker


class DockerVMWizard(VMWizard, Ui_DockerVMWizard):
    """Wizard to create a Docker image.

    :param docker_images: existing Docker images
    :param parent: parent widget
    """

    def __init__(self, docker_images, parent):

        super().__init__(parent=parent, devices=[], use_local_server=True)
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(
            ":/icons/docker.png"))
        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)

        self._docker_images = docker_images

        if Docker.instance().settings()["use_local_server"]:
            # skip the server page if we use the local server
            self.setStartId(1)

    def initializePage(self, page_id):

        super().initializePage(page_id)

        if self.page(page_id) == self.uiImageWizardPage:
            self._server.get(
                "/docker/images", self._getDockerImagesFromServerCallback)

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
            existing_images = []
            for existing_image in self._docker_images.values():
                existing_images.append(existing_image["imagename"])

            for image in result:
                if image["imagename"] not in existing_images:
                    self.uiImageListComboBox.addItem(image["imagename"], image)

    def validateCurrentPage(self):
        """Validates the server."""

        if super().validateCurrentPage() is False:
            return False

        if self.currentPage() == self.uiImageWizardPage:
            if not self.uiImageListComboBox.count():
                QtWidgets.QMessageBox.critical(
                    self, "Docker images",
                    "There are no Docker images available!")
                return False
        return True

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

        index = self.uiImageListComboBox.currentIndex()
        imagename = self.uiImageListComboBox.itemText(index)
        # FIXME: add some more configuration options for images
        imageinfo = self.uiImageListComboBox.itemData(index)

        settings = {
            "imagename": imagename,
            "server": server,
        }
        return settings
