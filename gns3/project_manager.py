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
from .utils.import_project_worker import ImportProjectWorker
from .dialogs.file_editor_dialog import FileEditorDialog
from .dialogs.project_dialog import ProjectDialog


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
            self._main_window.setWindowTitle("GNS3")
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
        self._project.project_updated_signal.connect(self._projectUpdatedSlot)
        self._setCurrent()

    def _projectUpdatedSlot(self):
        self._main_window.setWindowTitle("{name} - GNS3".format(name=self._project.name()))

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
        self.setProject(Project())
        self._project.project_creation_error_signal.connect(self._projectCreationErrorSlot)
        Topology.instance().project = self._project
        self._main_window.uiGraphicsView.reset()

        if "project_name" in project_settings:
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
        self._project.project_creation_error_signal.connect(self._projectCreationErrorSlot)
        self._main_window.uiGraphicsView.reset()
        self._project.load(path)
        self._main_window.uiStatusBar.showMessage("Project loaded {}".format(path), 2000)
        self._setCurrent(path)
        self.project_changed_signal.emit()
        return True

    def editReadme(self):
        dialog = FileEditorDialog(self.project(), "/README.txt", parent=self._main_window, default="Project title\n\nAuthor: Grace Hopper <grace@example.org>\n\nThis project is about...")
        dialog.show()
        dialog.exec_()

    def _projectCreationErrorSlot(self):
        self._project = None
        self._setCurrent()
        self._main_window.uiGraphicsView.reset()
        self.project_changed_signal.emit()

    def exportProject(self):
        include_image_question = """Would you like to include any base image?
The project will not require additional images to run on another host, however the resulting file will be much bigger.
It is your responsability to check if you have the right to distribute the image(s) as part of the project.
        """

        reply = QtWidgets.QMessageBox.question(self._main_window, "Export project", include_image_question,
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        include_images = int(reply == QtWidgets.QMessageBox.Yes)

        directory = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        if len(directory) == 0:
            directory = self.projectsDirPath()

        path, _ = QtWidgets.QFileDialog.getSaveFileName(self._main_window, "Export portable project", directory,
                                                        "GNS3 Portable Project (*.gns3project *.gns3p)",
                                                        "GNS3 Portable Project (*.gns3project *.gns3p)")
        if path is None or len(path) == 0:
            return

        if not path.endswith(".gns3project") and not path.endswith(".gns3p"):
            path += ".gns3project"

        try:
            open(path, 'wb+').close()
        except OSError as e:
            QtWidgets.QMessageBox.critical(self._main_window, "Export project", "Could not write {}: {}".format(path, e))
            return

        self.editReadme()

        export_worker = ExportProjectWorker(self._project, path, include_images)
        progress_dialog = ProgressDialog(export_worker, "Exporting project", "Exporting portable project files...", "Cancel", parent=self._main_window)
        progress_dialog.show()
        progress_dialog.exec_()

    def importProject(self, project_file):
        dialog = ProjectDialog(self._main_window, default_project_name=os.path.basename(project_file).split(".")[0])
        dialog.show()
        if not dialog.exec_():
            return

        import_worker = ImportProjectWorker(project_file,
                name=dialog.getProjectSettings()["project_name"],
                path=dialog.getProjectSettings()["project_path"])
        import_worker.imported.connect(self._projectImportedSlot)
        progress_dialog = ProgressDialog(import_worker, "Importing project", "Importing portable project files...", "Cancel", parent=self._main_window)
        progress_dialog.show()
        progress_dialog.exec_()

    def saveProjectAs(self):
        dialog = ProjectDialog(self._main_window, default_project_name=self._project.name())
        dialog.show()
        if dialog.exec_():
            self._project.duplicate(
                name=dialog.getProjectSettings()["project_name"],
                path=dialog.getProjectSettings()["project_path"]
            )

    def _projectImportedSlot(self, project_id):
        if self:
            self.createLoadProject({"project_id": project_id})

    def deleteProject(self):
        if self._project:
           self._project.destroy()
           self._project = None
           self._setCurrent()
        self.project_changed_signal.emit()
