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

import os
import json

from .project import Project
from .local_server import LocalServer
from .node import Node
from .qt import QtCore, QtWidgets
from .topology import Topology

from .utils.process_files_worker import ProcessFilesWorker
from .utils.progress_dialog import ProgressDialog
from .utils.message_box import MessageBox
from .utils.export_project_worker import ExportProjectWorker

import logging
log = logging.getLogger(__name__)


class ProjectManager(QtCore.QObject):

    # signal to tell a new project was created
    project_new_signal = QtCore.pyqtSignal(str)
    project_changed_signal = QtCore.pyqtSignal()

    def __init__(self, parent):

        super().__init__(parent)
        self._main_window = parent
        self._project = None

    def _setCurrent(self, path=None):
        """
        Sets the current project file path.

        :param path: path to project file
        """

        if self._project:
            self._main_window.setWindowTitle("{name} - GNS3".format(name=self._project.name()))
        else:
            self._main_window.setWindowTitle("GNS3".format(name=self._project.name()))
        if path:
            self._main_window.updateRecentFileSettings(path)
            self._main_window.updateRecentFileActions()

    def project(self):
        """
        Return current project
        """

        return self._project

    def setProject(self, project):
        """
        Set current project

        :param project: Project instance
        """

        self._project = project
        self._setCurrent()

    @staticmethod
    def projectsDirPath():
        """
        Returns the projects directory path.

        :returns: path to the default projects directory
        """

        return LocalServer.instance().localServerSettings()["projects_path"]

    def createLoadProject(self, project_settings):
        """
        Create load a project based on settings, not on the .gns3
        """
        if self._project:
            self._project.close()
        self._project = Project()
        Topology.instance().project = self._project
        self._main_window.uiGraphicsView.reset()

        self._project.setName(project_settings["project_name"])
        self._setCurrent(project_settings.get("project_path", None))

        if "project_id" in project_settings:
            self._project.setId(project_settings["project_id"])
            self._project.load()
            self._main_window.uiStatusBar.showMessage("Project loaded", 2000)
        else:
            self._project.setFilesDir(os.path.dirname(project_settings["project_path"]))
            self._project.create()
            self._main_window.uiStatusBar.showMessage("Project created", 2000)
        self._setCurrent()
        self.project_changed_signal.emit()

    def loadProject(self, path):
        """
        Loads a project into GNS3.

        :param path: path to project file
        """

        if self._project:
            self._project.close()
        self._project = Project()
        self._main_window.uiGraphicsView.reset()
        self._project.load(path)
        self._main_window.uiStatusBar.showMessage("Project loaded {}".format(path), 2000)
        self._setCurrent(path)
        self.project_changed_signal.emit()
        return True

    def deleteProject(self):
        if self._project:
           self._project.destroy()
           self._project = None
           self._setCurrent()
        self.project_changed_signal.emit()
