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

import os
from ..qt import QtCore, QtGui
from ..ui.new_project_dialog_ui import Ui_NewProjectDialog
from ..settings import ENABLE_CLOUD


class NewProjectDialog(QtGui.QDialog, Ui_NewProjectDialog):

    """
    New project dialog.

    :param parent: parent widget.
    :param showed_from_startup: boolean to indicate if this dialog
    has been opened automatically when GNS3 started.
    """

    def __init__(self, parent, showed_from_startup=False):

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self._main_window = parent
        self._project_settings = {}
        default_project_name = "untitled"
        self.uiNameLineEdit.setText(default_project_name)
        self.uiLocationLineEdit.setText(os.path.join(self._main_window.projectsDirPath(), default_project_name))

        self.uiNameLineEdit.textEdited.connect(self._projectNameSlot)
        self.uiLocationBrowserToolButton.clicked.connect(self._projectPathSlot)
        self.uiOpenProjectPushButton.clicked.connect(self._openProjectActionSlot)
        self.uiRecentProjectsPushButton.clicked.connect(self._showRecentProjectsSlot)
        if not ENABLE_CLOUD:
            self.uiCloudRadioButton.hide()

        if not showed_from_startup:
            self.uiOpenProjectPushButton.hide()
            self.uiRecentProjectsPushButton.hide()

    def keyPressEvent(self, e):
        """
        Event handler in order to properly handle escape.
        """

        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def _projectNameSlot(self, text):

        project_dir = self._main_window.projectsDirPath()
        if os.path.dirname(self.uiLocationLineEdit.text()) == project_dir:
            self.uiLocationLineEdit.setText(os.path.join(project_dir, text))

    def _projectPathSlot(self):
        """
        Slot to select the a new project location.
        """

        path = QtGui.QFileDialog.getSaveFileName(self, "Project location", os.path.join(self._main_window.projectsDirPath(),
                                                                                        self.uiNameLineEdit.text()))
        if path:
            self.uiLocationLineEdit.setText(path)

    def getNewProjectSettings(self):

        return self._project_settings

    def _menuTriggeredSlot(self, action):
        """
        Closes this dialog when a recent project
        has been opened.

        :param action: ignored.
        """

        self.reject()

    def _openProjectActionSlot(self):
        """
        Opens a project and closes this dialog.
        """

        self._main_window.openProjectActionSlot()
        self.reject()

    def _showRecentProjectsSlot(self):
        """
        lot to show all the recent projects in a menu.
        """

        menu = QtGui.QMenu()
        menu.triggered.connect(self._menuTriggeredSlot)
        for action in self._main_window._recent_file_actions:
            menu.addAction(action)
        menu.exec_(QtGui.QCursor.pos())

    def done(self, result):

        if result:
            project_name = self.uiNameLineEdit.text()
            project_location = self.uiLocationLineEdit.text()
            if self.uiCloudRadioButton.isChecked():
                project_type = "cloud"
            else:
                project_type = "local"

            if not project_name:
                QtGui.QMessageBox.critical(self, "New project", "Project name is empty")
                return

            if not project_location:
                QtGui.QMessageBox.critical(self, "New project", "Project location is empty")
                return

            if os.path.isdir(project_location):
                reply = QtGui.QMessageBox.question(self,
                                                   "New project",
                                                   "Location {} already exists, overwrite it?".format(project_location),
                                                   QtGui.QMessageBox.Yes,
                                                   QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.No:
                    return

            self._project_settings["project_name"] = project_name
            self._project_settings["project_path"] = os.path.join(project_location, project_name + ".gns3")
            self._project_settings["project_files_dir"] = project_location
            self._project_settings["project_type"] = project_type

        QtGui.QDialog.done(self, result)
