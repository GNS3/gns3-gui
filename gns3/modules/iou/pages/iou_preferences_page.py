# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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
Configuration page for IOU preferences.
"""

import os
import copy

from gns3.qt import QtCore, QtWidgets, qslot, sip_is_deleted
from gns3.controller import Controller

from ..ui.iou_preferences_page_ui import Ui_IOUPreferencesPageWidget
from ..settings import IOU_SETTINGS

import logging
log = logging.getLogger(__name__)


class IOUPreferencesPage(QtWidgets.QWidget, Ui_IOUPreferencesPageWidget):

    """
    QWidget preference page for IOU.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self._old_settings = None

        # connect signals
        self.uiIOURCPathToolButton.clicked.connect(self._iourcPathBrowserSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        Controller.instance().connected_signal.connect(self.loadPreferences)

    def _iourcPathBrowserSlot(self):
        """
        Slot to open a file browser and select an iourc file
        """

        documents_path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the IOURC file", documents_path)
        if not path:
            return

        try:
            with open(path) as f:
                content = f.read().strip()
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "IOURC file", "{} cannot be read.\n{}".format(os.path.basename(path), str(e)))
            return
        except UnicodeDecodeError as e:
            QtWidgets.QMessageBox.critical(self, "IOURC file", "{} is not a licence file.".format(os.path.basename(path)))
            return
        if not content.startswith("[license]"):
            QtWidgets.QMessageBox.critical(self, "IOURC file", "This is not a valid IOURC file")
            return

        self.IOULicenceTextEdit.setPlainText(content)

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(IOU_SETTINGS)

    def _useLocalServerSlot(self, state):
        """
        Slot to enable or not local server settings.
        """

        if state:
            self.uiLicensecheckBox.setEnabled(True)
        else:
            self.uiLicensecheckBox.setEnabled(False)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: IOU settings
        """

        if settings["iourc_content"]:
            self.IOULicenceTextEdit.blockSignals(True)
            self.IOULicenceTextEdit.setPlainText(settings["iourc_content"])
            self.IOULicenceTextEdit.blockSignals(False)
        self.uiLicensecheckBox.setChecked(settings["license_check"])

    def loadPreferences(self):
        """
        Loads IOU preferences.
        """

        if Controller.instance().connected():
            Controller.instance().get("/iou_license", self._getSettingsCallback)
        else:
            log.error("Cannot load the IOU license in the preferences dialog: not connected to the controller")

    @qslot
    def _getSettingsCallback(self, result, error=False, **kwargs):

        if sip_is_deleted(self):
            return
        if error:
            if "message" in result:
                log.error("Error while getting the IOU license information: {}".format(result["message"]))
            return
        self._old_settings = copy.copy(result)
        self._populateWidgets(result)

    def savePreferences(self):
        """
        Saves IOU preferences.
        """

        if not self._old_settings:
            return

        iourc_content = self.IOULicenceTextEdit.toPlainText().strip().replace("\r\n", "\n")

        new_settings = {"iourc_content": iourc_content,
                        "license_check": self.uiLicensecheckBox.isChecked()}

        if self._old_settings != new_settings:
            Controller.instance().put("/iou_license", self._saveSettingsCallback, new_settings, timeout=60)
            self._old_settings = copy.copy(new_settings)

    def _saveSettingsCallback(self, result, error=False, **kwargs):
        if error and "message" in result:
            QtWidgets.QMessageBox.critical(self, "Save settings", "Error while saving settings: {}".format(result["message"]))
