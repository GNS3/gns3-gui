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
Configuration page for Docker images.
"""

from gns3.qt import QtWidgets

from ..ui.docker_vm_configuration_page_ui import Ui_dockerVMConfigPageWidget


class DockerVMConfigurationPage(
        QtWidgets.QWidget, Ui_dockerVMConfigPageWidget):
    """QWidget configuration page for Docker images."""

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        # TODO: finish docker name change
        self.uiImageListLabel.hide()
        self.uiImageListComboBox.hide()

    def loadSettings(self, settings, node=None, group=False):
        """
        Loads the VirtualBox VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of images
        """

        if not group:
            # set the device name
            if "name" in settings:
                self.uiNameLineEdit.setText(settings["name"])
            else:
                self.uiNameLabel.hide()
                self.uiNameLineEdit.hide()
            if "startcmd" in settings:
                self.uiCMDLineEdit.setText(settings["startcmd"])
            else:
                self.uiCMDLabel.hide()
                self.uiCMDLineEdit.hide()
        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiCMDLabel.hide()
            self.uiCMDLineEdit.hide()
            self.uiImageListLabel.hide()
            self.uiImageListComboBox.hide()

    def saveSettings(self, settings, node=None, group=False):
        """Saves the Docker container settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """
        if not group:
            if "startcmd" in settings:
                startcmd = self.uiCMDLineEdit.text()
                settings["startcmd"] = startcmd
            if "name" in settings:
                name = self.uiNameLineEdit.text()
                if not name:
                    QtWidgets.QMessageBox.critical(self, "Name", "VMware name cannot be empty!")
                else:
                    settings["name"] = name
        else:
            del settings["startcmd"]
            del settings["name"]
