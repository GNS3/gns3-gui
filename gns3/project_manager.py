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
from .servers import Servers
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

    def __init__(self, parent):

        super().__init__(parent)
        self._main_window = parent
        self._project = None
        self.createTemporaryProject()
        self.project_new_signal.connect(self.projectCreatedSlot)

    def _setCurrentFile(self, path=None):
        """
        Sets the current project file path.

        :param path: path to project file
        """

        if not path:
            self._main_window.setWindowFilePath("Unsaved project")
            self._main_window.setWindowTitle("Unsaved project[*] - GNS3")
        else:
            path = os.path.normpath(path)
            self._main_window.setWindowFilePath(path)
            self._main_window.setWindowTitle("{path}[*] - GNS3".format(path=os.path.basename(path)))
            self._main_window.updateRecentFileSettings(path)
            self._main_window.updateRecentFileActions()

        self._main_window.setWindowModified(False)

    def _runningNodes(self):
        """
        :returns: Return the list of running nodes
        """
        topology = Topology.instance()
        running_nodes = []
        for node in topology.nodes():
            if hasattr(node, "start") and node.status() == Node.started:
                running_nodes.append(node.name())
        return running_nodes

    def _isProjectOnRemoteServer(self):
        """
        :returns: Boolean True if project runs on a remote server
        """

        topology = Topology.instance()
        for node in topology.nodes():
            if not node.server().isLocal():
                return True
        return False

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
        self._setCurrentFile(project.topologyFile())

    @staticmethod
    def projectsDirPath():
        """
        Returns the projects directory path.

        :returns: path to the default projects directory
        """

        return Servers.instance().localServerSettings()["projects_path"]

    def createTemporaryProject(self):
        """
        Creates a temporary project.
        """

        if self._project:
            self._project.close()
        self._project = Project()
        self._project.setTemporary(True)
        self._project.setName("unsaved")
        self._main_window.uiGraphicsView.reset()
        self._setCurrentFile()

    def createNewProject(self, project_settings):

        self._project.close()
        self._project = Project()
        self._main_window.uiGraphicsView.reset()
        # create the destination directory for project files
        try:
            os.makedirs(project_settings["project_files_dir"], exist_ok=True)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self._main_window, "New project",
                                           "Could not create project files directory {}: {}".format(project_settings["project_files_dir"], e))
            self.createTemporaryProject()

        # let all modules know about the new project files directory
        # self.uiGraphicsView.updateProjectFilesDir(new_project_settings["project_files_dir"])

        topology = Topology.instance()
        topology.project = self._project

        self._project.setName(project_settings["project_name"])
        self._project.setTopologyFile(project_settings["project_path"])
        self.saveProject(project_settings["project_path"])
        self.project_new_signal.emit(self._project.topologyFile())

    def projectCreatedSlot(self, project):
        """
        This slot is invoked when a project is created or opened

        :param project: path to gns3 project file currently opened
        """

        if self._project.temporary():
            # do nothing if project is temporary
            return

        try:
            with open(project, encoding="utf-8") as f:
                json_topology = json.load(f)
                if not isinstance(json_topology, dict):
                    raise ValueError("Not a GNS3 project")
        except (OSError, ValueError) as e:
            QtWidgets.QMessageBox.critical(self._main_window, "Project", "Could not read project: {}".format(e))

    def loadProject(self, path):
        """
        Loads a project into GNS3.

        :param path: path to project file
        """

        self._project = Project()
        self._main_window.uiGraphicsView.reset()
        topology = Topology.instance()
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            topology.loadFile(path, self._project)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "Load", "Could not load project {}: {}".format(os.path.basename(path), e))
            self.createTemporaryProject()
            return False
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self, "Load", "Invalid or corrupted file: {}".format(e))
            self.createTemporaryProject()
            return False
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        self._main_window.uiStatusBar.showMessage("Project loaded {}".format(path), 2000)
        self._setCurrentFile(path)
        return True

    def saveProjectAs(self):
        """
        Saves a project to another location/name.

        :returns: GNS3 project file (.gns3)
        """

        if self._runningNodes():
            QtWidgets.QMessageBox.warning(self._main_window, "Save As", "All devices must be stopped before saving to another location")
            return False

        if self._isProjectOnRemoteServer() and not self._project.temporary():
            MessageBox(self, "Save project", "You can not use the save as function on a remote project for the moment.")
            return

        if self._project.temporary():
            default_project_name = "untitled"
        else:
            default_project_name = self._project.name()

        projects_dir_path = os.path.normpath(os.path.expanduser(self.projectsDirPath()))
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setWindowTitle("Save project")
        file_dialog.setNameFilters(["Directories"])
        file_dialog.setDirectory(projects_dir_path)
        file_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        file_dialog.setLabelText(QtWidgets.QFileDialog.FileName, "Project name:")
        file_dialog.selectFile(default_project_name)
        file_dialog.setOptions(QtWidgets.QFileDialog.ShowDirsOnly)
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        if file_dialog.exec_() == QtWidgets.QFileDialog.Rejected:
            return

        project_dir = file_dialog.selectedFiles()[0]
        project_name = os.path.basename(project_dir)
        topology_file_path = os.path.join(project_dir, project_name + ".gns3")
        old_topology_file_path = os.path.join(project_dir, default_project_name + ".gns3")

        # create the destination directory for project files
        try:
            os.makedirs(project_dir, exist_ok=True)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self._main_window, "Save project", "Could not create project directory {}: {}".format(project_dir, e))
            return

        if self._project.temporary():
            # move files if saving from a temporary project
            log.info("Moving project files from {} to {}".format(self._project.filesDir(), project_dir))
            worker = ProcessFilesWorker(self._project.filesDir(), project_dir, move=True, skip_files=[".gns3_temporary"])
            progress_dialog = ProgressDialog(worker, "Project", "Moving project files...", "Cancel", parent=self._main_window)
        else:
            # else, just copy the files
            log.info("Copying project files from {} to {}".format(self._project.filesDir(), project_dir))
            worker = ProcessFilesWorker(self._project.filesDir(), project_dir)
            progress_dialog = ProgressDialog(worker, "Project", "Copying project files...", "Cancel", parent=self._main_window)
        progress_dialog.show()
        progress_dialog.exec_()

        errors = progress_dialog.errors()
        if errors:
            errors = "\n".join(errors)
            MessageBox(self._main_window, "Save project", "Errors detected while saving the project", errors, icon=QtWidgets.QMessageBox.Warning)

        self._project.setName(project_name)
        if self._project.temporary():
            self._project.moveFromTemporaryToPath(project_dir)
            return self.saveProject(topology_file_path)
        else:
            # We save the topology and use the standard restore process to reinitialize everything
            self._project.setTopologyFile(topology_file_path)
            self.saveProject(topology_file_path, random_id=True)

            if os.path.exists(old_topology_file_path):
                try:
                    os.remove(old_topology_file_path)
                except OSError as e:
                    MessageBox(self._main_window, "Save project", "Errors detected while saving the project", str(e), icon=QtWidgets.QMessageBox.Warning)
            return self._main_window.loadPath(topology_file_path)

    def saveProject(self, path, random_id=False):
        """
        Saves a project.

        :param path: path to project file
        :param random_id: Randomize project and vm id (use for save as)
        """

        topology = Topology.instance()
        topology.project = self._project
        try:
            self._project.commit()
            topology = topology.dump(random_id=random_id)
            log.info("Saving project: {}".format(path))
            content = json.dumps(topology, sort_keys=True, indent=4)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self._main_window, "Save", "Could not save project to {}: {}".format(path, e))
            return False

        if self._main_window.settings()["auto_screenshot"]:
            self._main_window.createScreenshot(os.path.join(os.path.dirname(path), "screenshot.png"))
        self._main_window.uiStatusBar.showMessage("Project saved to {}".format(path), 2000)
        self._project.setTopologyFile(path)
        self._setCurrentFile(path)

        self._main_window.analyticsClient().sendScreenView("Main Window")
        return True

    def exportProject(self):
        """
        Exports a portable project.
        """

        running_nodes = self._runningNodes()
        if running_nodes:
            nodes = "\n".join(running_nodes)
            MessageBox(self, "Export project", "Please stop the following nodes before exporting the project", nodes)
            return

        if self._main_window.testAttribute(QtCore.Qt.WA_WindowModified):
            QtWidgets.QMessageBox.critical(self._main_window, "Export project", "Please save the project before exporting it")
            return

        if self.project().temporary():
            QtWidgets.QMessageBox.critical(self._main_window, "Export project", "A temporary project cannot be exported")
            return

        topology = Topology.instance()
        for node in topology.nodes():
            if node.__class__.__name__ in ["VirtualBoxVM", "VMwareVM"]:
                QtWidgets.QMessageBox.critical(self._main_window, "Export portable project" "A project containing VMware or VirtualBox VMs cannot be exported because the VMs are managed by these software.")
                return

        include_image_question = """Would you like to include any base image?

The project will not require additional images to run on another host, however the resulting file will be much bigger.

You are responsible to check if you have the right to distribute the image(s) as part of the project.
        """

        reply = QtWidgets.QMessageBox.question(self._main_window, "Export project", include_image_question,
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        include_images = int(reply == QtWidgets.QMessageBox.Yes)

        if not os.path.exists(self._project.readmePathFile()):
            text, ok = QtWidgets.QInputDialog.getMultiLineText(self._main_window, "Export project",
                                                               "Please provide a description for the project, especially if you want to share it. \nThe description will be saved in README.txt inside the project file",
                                                               "Project title\n\nAuthor: Grace Hopper <grace@hopper.com>\n\nThis project is about...")
            if not ok:
                return
            try:
                with open(self._project.readmePathFile(), 'w+') as f:
                    f.write(text)
            except OSError as e:
                QtWidgets.QMessageBox.critical(self._main_window, "Export project", "Could not create {}: {}".format(self._project.readmePathFile(), e))
                return

        for server in self._project.servers():
            if not server.isLocal() and not server.isGNS3VM():
                QtWidgets.QMessageBox.critical(self._main_window, "Export project", "Projects running on a remote server cannot be exported. Only projects running locally or in the GNS3 VM are supported.")
                return

        directory = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        if len(directory) == 0:
            directory = self.projectsDirPath()

        path, _ = QtWidgets.QFileDialog.getSaveFileName(self._main_window, "Export portable project", directory,
                                                        "GNS3 Portable Project (*.gns3project *.gns3p)",
                                                        "GNS3 Portable Project (*.gns3project *.gns3p)")
        if path is None or len(path) == 0:
            return

        if not path.endswith(".gns3project") or not path.endswith(".gns3p"):
            path += ".gns3project"

        try:
            open(path, 'wb+').close()
        except OSError as e:
            QtWidgets.QMessageBox.critical(self._main_window, "Export project", "Could not write {}: {}".format(path, e))
            return

        export_worker = ExportProjectWorker(self._project, path, include_images)
        progress_dialog = ProgressDialog(export_worker, "Exporting project", "Exporting portable project files...", "Cancel", parent=self._main_window)
        progress_dialog.show()
        progress_dialog.exec_()

    def importProject(self):
        """
        Imports a portable project.
        """

        directory = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DownloadLocation)
        if len(directory) == 0:
            directory = self.projectsDirPath()
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self._main_window, "Import project", directory,
                                                        "All files (*.*);;GNS3 Portable Project (*.gns3project *.gns3p)",
                                                        "GNS3 Portable Project (*.gns3project *.gns3p)")
        if not path:
            return
        self._main_window.loadPath(path)
