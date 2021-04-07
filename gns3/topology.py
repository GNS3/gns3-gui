# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GNS3 Technologies Inc.
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
Contains this entire topology: nodes and links.
"""

import os
import xml.etree.ElementTree as ET


from .local_server import LocalServer
from .qt import QtCore, QtWidgets

from .utils.progress_dialog import ProgressDialog
from .utils.import_project_worker import ImportProjectWorker
from .dialogs.project_export_wizard import ExportProjectWizard
from .dialogs.file_editor_dialog import FileEditorDialog
from .dialogs.project_welcome_dialog import ProjectWelcomeDialog

from .modules import MODULES
from .modules.module_error import ModuleError
from .compute_manager import ComputeManager
from .controller import Controller

import logging
log = logging.getLogger(__name__)


class Topology(QtCore.QObject):

    """
    Topology.
    """
    node_added_signal = QtCore.Signal(int)
    project_changed_signal = QtCore.Signal()

    def __init__(self):

        super().__init__()

        self._nodes = []
        self._links = []
        self._notes = []
        self._drawings = []
        self._images = []
        self._project = None
        self._main_window = None

        # If set the project is loaded when we got connection to the controller
        # useful when we open a project from cli or when server restart
        self._project_to_load_path = None
        self._project_id_to_load = None

        Controller.instance().connected_signal.connect(self._controllerConnectedSlot)
        Controller.instance().disconnected_signal.connect(self._controllerDisconnectedSlot)

    def _controllerConnectedSlot(self):
        """
        We reset current project because the remote controller could have
        change location
        """

        if self._project_to_load_path:
            path = self._project_to_load_path
            self.__project_to_load_path = None
            self.loadProject(path)
        elif self._project_id_to_load:
            self.createLoadProject({"project_id": self._project_id_to_load})
        else:
            self.setProject(None)

    def _controllerDisconnectedSlot(self):
        if self._project:
            self._project_id_to_load = self._project.id()
        self.setProject(None)

    def setMainWindow(self, main_window):
        self._main_window = main_window

    def projectsDirPath(self):
        """
        Returns the projects directory path.

        :returns: path to the default projects directory
        """

        return LocalServer.instance().localServerSettings()["projects_path"]

    def project(self):
        """
        Get topology project

        :returns: Project instance
        """

        return self._project

    def setProject(self, project, snapshot=False):
        """
        Set current project

        :param project: Project instance
        """

        if self._project and snapshot is False:
            # Assert to detect when we create a new project object for the same project
            assert project is None or (project != self._project and project.id != self._project.id)
            self._project.stopListenNotifications()

        self._main_window.uiGraphicsView.reset()
        self._project = project
        if project:
            self._project.project_updated_signal.connect(self._projectUpdatedSlot)
            self._project.project_creation_error_signal.connect(self._projectCreationErrorSlot)
            self._project.project_loaded_signal.connect(self._projectLoadedSlot)
            self._main_window.setWindowTitle("{name} - GNS3".format(name=self._project.name()))
            self._main_window.uiGraphicsView.setSceneSize(project.sceneWidth(), project.sceneHeight())
        else:
            self._main_window.setWindowTitle("GNS3")

        self.project_changed_signal.emit()

    def _projectUpdatedSlot(self):
        if not self._project or not self._project.filesDir() or not self._project.filename():
            return
        self._main_window.setWindowTitle("{name} - GNS3".format(name=self._project.name()))
        project_file = os.path.join(self._project.filesDir(), self._project.filename())
        self._main_window.uiGraphicsView.setSceneSize(self._project.sceneWidth(), self._project.sceneHeight())
        self._main_window.uiGraphicsView.setNodeGridSize(self._project.nodeGridSize())
        self._main_window.uiGraphicsView.setDrawingGridSize(self._project.drawingGridSize())
        self._main_window.uiShowGridAction.setChecked(self._project.showGrid())
        self._main_window.showGrid(self._project.showGrid())
        if not Controller.instance().isRemote() and os.path.exists(project_file):
            self._main_window.updateRecentFileSettings(project_file)
            self._main_window.updateRecentFileActions()

        self._main_window.updateRecentProjectsSettings(self._project.id(), self._project.name(), self._project.path())
        self._main_window.updateRecentProjectActions()

    def _projectLoadedSlot(self):
        # when project is loaded we can make updates in GUI
        if self._project is not None:
            self._main_window.uiShowLayersAction.setChecked(self._project.showLayers())
            self._main_window.showLayers(self._project.showLayers())

            self._main_window.uiGraphicsView.setNodeGridSize(self._project.nodeGridSize())
            self._main_window.uiGraphicsView.setDrawingGridSize(self._project.drawingGridSize())
            self._main_window.uiShowGridAction.setChecked(self._project.showGrid())
            self._main_window.showGrid(self._project.showGrid())

            self._main_window.uiSnapToGridAction.setChecked(self._project.snapToGrid())
            self._main_window.snapToGrid(self._project.snapToGrid())

            self._main_window.uiShowPortNamesAction.setChecked(self._project.showInterfaceLabels())
            self._main_window.showInterfaceLabels(self._project.showInterfaceLabels())

            self._main_window.uiGraphicsView.setZoom(self._project.zoom())

            supplier = self._project.supplier()
            if supplier:
                self._main_window.uiGraphicsView.addLogo(
                    supplier.get('logo', None),
                    supplier.get('url', None)
                )

            self._displayProjectWelcomeDialog()

    def _displayProjectWelcomeDialog(self):
        variables = self.project().variables()
        if variables:
            missing = [v for v in variables if v.get("value", "").strip() == ""]
            if len(missing) > 0:
                dialog = ProjectWelcomeDialog(self._main_window, self.project())
                dialog.show()
                dialog.exec_()

    def createLoadProject(self, project_settings):
        """
        Create load a project based on settings, not on the .gns3
        """

        self.setProject(None)
        from .project import Project
        project = Project()

        if "project_name" in project_settings:
            project.setName(project_settings["project_name"])

        if "project_path" in project_settings:
            project.setFilesDir(os.path.dirname(project_settings["project_path"]))
            project.setFilename(os.path.basename(project_settings["project_path"]))

        if "project_id" in project_settings:
            project.setId(project_settings["project_id"])
            self.setProject(project)
            project.load()
            self._main_window.uiStatusBar.showMessage("Project loaded", 2000)
        else:
            self.setProject(project)
            project.create()
            self._main_window.uiStatusBar.showMessage("Project created", 2000)
        return project

    def restoreSnapshot(self, project_id):
        """
        Restore a snapshot for a given project.
        """

        assert self._project.id() == project_id
        project = self._project
        self.setProject(project, snapshot=True)
        project.load()
        self._main_window.uiStatusBar.showMessage("Snapshot restored", 2000)

    def loadProject(self, path):
        """
        Loads a project into GNS3.

        :param path: path to project file
        """

        if not Controller.instance().connected():
            self._project_to_load_path = path
            return

        from .project import Project
        self.setProject(Project())
        self._project.load(path)
        self._main_window.uiStatusBar.showMessage("Project loaded {}".format(path), 2000)
        return True

    def editReadme(self):
        if self.project() is None:
            return
        dialog = FileEditorDialog(self.project(), "README.txt", parent=self._main_window, default="Project title\n\nAuthor: Grace Hopper <grace@example.org>\n\nThis project is about...")
        dialog.show()
        dialog.exec_()

    def _projectCreationErrorSlot(self, message):
        if self._project:
            self._project.project_creation_error_signal.disconnect(self._projectCreationErrorSlot)
            self.setProject(None)
            QtWidgets.QMessageBox.critical(self._main_window, "New project", message)

    def exportProject(self):
        if self._project is None:
            QtWidgets.QMessageBox.critical(self._main_window, "Export project", "No project has been opened")
            return
        export_wizard = ExportProjectWizard(self.project(), parent=self._main_window)
        export_wizard.show()
        export_wizard.exec_()

    def importProject(self, project_file):
        from .dialogs.project_dialog import ProjectDialog
        dialog = ProjectDialog(self._main_window, default_project_name=os.path.basename(project_file).split(".")[0], show_open_options=False)
        dialog.show()
        if not dialog.exec_():
            return

        import_worker = ImportProjectWorker(project_file,
                                            name=dialog.getProjectSettings()["project_name"],
                                            path=dialog.getProjectSettings().get("project_files_dir"))
        import_worker.imported.connect(self._projectImportedSlot)
        progress_dialog = ProgressDialog(import_worker, "Importing project", "Importing portable project files...", "Cancel", parent=self._main_window, create_thread=False)
        progress_dialog.show()
        progress_dialog.exec_()

    def saveProjectAs(self):
        project = self._project
        if not project:
            return

        from .dialogs.project_dialog import ProjectDialog
        dialog = ProjectDialog(self._main_window, default_project_name=project.name(), show_open_options=False)
        dialog.show()
        if dialog.exec_():
            project.duplicate(
                name=dialog.getProjectSettings()["project_name"],
                path=dialog.getProjectSettings().get("project_files_dir"),  # None when using remote controller
                callback=self._projectImportedSlot
            )

    def _projectImportedSlot(self, project_id):
        if self:
            self.createLoadProject({"project_id": project_id})

    def deleteProject(self):
        if self._project:
            self._project.destroy()

    def addNode(self, node):
        """
        Adds a new node to this topology.

        :param node: Node instance
        """

        self._nodes.append(node)
        self.node_added_signal.emit(node.id())

    def removeNode(self, node):
        """
        Removes a node from this topology.

        :param node: Node instance
        """

        if node in self._nodes:
            self._nodes.remove(node)

    def getNodeFromUuid(self, node_id):
        """
        Lookups for a node using its identifier.

        :returns: Node instance or None
        """

        for node in self._nodes:
            if hasattr(node, "node_id") and node.node_id() == node_id:
                return node
        return None

    def getNode(self, base_node_id):
        """
        Lookups for a node using its base bode id.

        :returns: Node instance or None
        """

        for node in self._nodes:
            if node.id() == base_node_id:
                return node
        return None

    def addLink(self, link):
        """
        Adds a new link to this topology.

        :param link: Link instance
        :returns: Boolean false if link already exists
        """

        for l in self._links:
            if (l._source_node == link._destination_node and l._source_port == link._destination_port) or \
                    (l._source_node == link._source_node and l._source_port == link._source_port):
                return False

        self._links.append(link)
        return True

    def removeLink(self, link):
        """
        Removes a link from this topology.

        :param link: Link instance
        """

        if link in self._links:
            self._links.remove(link)

    def getLink(self, link_id):
        """
        Lookups for a link using its identifier.

        :returns: Link instance or None
        """

        for link in self._links:
            if link.id() == link_id:
                return link
        return None

    def getLinkFromUuid(self, link_id):
        """
        Lookups for a link using its uuid.

        :returns: Link instance or None
        """

        for link in self._links:
            if link.link_id() == link_id:
                return link
        return None

    def addNote(self, note):
        """
        Adds a new note to this topology.

        :param note: NoteItem instance
        """

        self._notes.append(note)

    def removeNote(self, note):
        """
        Removes a note from this topology.

        :param note: NoteItem instance
        """

        if note in self._notes:
            self._notes.remove(note)

    def addDrawing(self, drawing):
        """
        Adds a new drawing to this topology.

        :param drawing: DrawingItem instance
        """

        self._drawings.append(drawing)

    def removeDrawing(self, drawing):
        """
        Removes a rectangle from this topology.

        :param rectangle: RectangleItem instance
        """

        if drawing in self._drawings:
            self._drawings.remove(drawing)

    def getDrawingFromUuid(self, drawing_id):
        """
        Lookups for a drawing using its identifier.

        :returns: Node instance or None
        """

        for drawing in self._drawings:
            if drawing.drawing_id() == drawing_id:
                return drawing
        return None

    def nodes(self):
        """
        Returns all the nodes in this topology.
        """

        return self._nodes

    def links(self):
        """
        Returns all the links in this topology.
        """

        return self._links

    def notes(self):
        """
        Returns all the notes in this topology.
        """

        return self._notes

    def drawings(self):
        """
        Returns all the drawings in this topology.
        """

        return self._drawings

    def images(self):
        """
        Returns all the images in this topology.
        """

        return self._images

    def reset(self):
        """
        Resets this topology.
        """

        self._links.clear()
        self._nodes.clear()
        self._notes.clear()
        self._drawings.clear()
        self._images.clear()

    def __str__(self):

        return "GNS3 network topology"

    def createNode(self, node_data):
        """
        Creates a new node on the scene.

        :param node_data: node data to create a new node
        """

        if not self._project:
            return  # The project has been deleted during the creation request

        node_module = None
        for module in MODULES:
            instance = module.instance()
            if node_data["node_type"] == "dynamips":
                node_class = module.getNodeClass(node_data["node_type"], node_data["properties"]["platform"])
            else:
                node_class = module.getNodeClass(node_data["node_type"])
            if node_class:
                node_module = module.instance()
                break

        if not node_module:
            raise ModuleError("Could not find any module for {}".format(node_class))

        node = node_module.instantiateNode(node_class, ComputeManager.instance().getCompute(node_data["compute_id"]), self._project)
        node.createNodeCallback(node_data)
        self._main_window.uiGraphicsView.createNodeItem(node, node_data["symbol"], node_data["x"], node_data["y"])

    def createLink(self, link_data):
        source_port = None
        destination_port = None
        if len(link_data["nodes"]) == 2:
            source_node = self.getNodeFromUuid(link_data["nodes"][0]["node_id"])
            destination_node = self.getNodeFromUuid(link_data["nodes"][1]["node_id"])
            if source_node is None or destination_node is None:
                return

            link_side = link_data["nodes"][0]

            for port in source_node.ports():
                if port.adapterNumber() == link_side["adapter_number"] and port.portNumber() == link_side["port_number"]:
                    source_port = port
                    break
            link_side = link_data["nodes"][1]
            for port in destination_node.ports():
                if port.adapterNumber() == link_side["adapter_number"] and port.portNumber() == link_side["port_number"]:
                    destination_port = port
                    break
        if source_port is None or destination_port is None:
            return
        self._main_window.uiGraphicsView.addLink(source_node, source_port, destination_node, destination_port, **link_data)

    def createDrawing(self, drawing_data):
        """
        Take info from the API and create a drawing

        :param drawing_data: Dict send by the API
        """
        try:
            svg = ET.fromstring(drawing_data["svg"])
        except ET.ParseError as e:
            log.error(str(e))
            return
        try:
            # If SVG is more complex we consider it as an image
            if len(svg[0]) != 0:
                type = "image"
            else:
                tag = svg[0].tag
                if tag == "ellipse":
                    type = "ellipse"
                elif tag == "rect":
                    type = "rect"
                elif tag == "text":
                    type = "text"
                elif tag == "line":
                    type = "line"
                else:
                    type = "image"
        except IndexError:
            # If unknow we render it as a raw SVG image
            type = "image"
        self._main_window.uiGraphicsView.createDrawingItem(type, drawing_data["x"], drawing_data["y"], drawing_data["z"], locked=drawing_data["locked"], rotation=drawing_data["rotation"], drawing_id=drawing_data["drawing_id"], svg=drawing_data["svg"])

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of Topology.

        :returns: instance of Topology
        """

        if not hasattr(Topology, "_instance"):
            Topology._instance = Topology()
        return Topology._instance
