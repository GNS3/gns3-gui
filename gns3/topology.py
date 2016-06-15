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

from .qt import QtCore
from .modules import MODULES
from .modules.module_error import ModuleError
from .items.node_item import NodeItem
from .compute_manager import ComputeManager


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
        self._rectangles = []
        self._ellipses = []
        self._images = []
        self._project = None
        self._main_window = None

    def setMainWindow(self, main_window):
        self._main_window = main_window

    @property
    def project(self):
        """
        Get topology project

        :returns: Project instance
        """

        return self._project

    @project.setter
    def project(self, project):
        """
        Set topology project

        :params project: Project
        """

        self._project = project
        self.project_changed_signal.emit()

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

    def addRectangle(self, rectangle):
        """
        Adds a new rectangle to this topology.

        :param rectangle: RectangleItem instance
        """

        self._rectangles.append(rectangle)

    def removeRectangle(self, rectangle):
        """
        Removes a rectangle from this topology.

        :param rectangle: RectangleItem instance
        """

        if rectangle in self._rectangles:
            self._rectangles.remove(rectangle)

    def addEllipse(self, ellipse):
        """
        Adds a new ellipse to this topology.

        :param ellipse: EllipseItem instance
        """

        self._ellipses.append(ellipse)

    def removeEllipse(self, ellipse):
        """
        Removes an ellipse from this topology.

        :param ellipse: EllipseItem instance
        """

        if ellipse in self._ellipses:
            self._ellipses.remove(ellipse)

    def addImage(self, image):
        """
        Adds a new image to this topology.

        :param image: ImageItem instance
        """

        self._images.append(image)

    def removeImage(self, image):
        """
        Removes an image from this topology.

        :param image: ImageItem instance
        """

        if image in self._images:
            self._images.remove(image)

        if not self._project:
            return

        # We delete by security only images in the project files directory
        if not os.path.isabs(image.filePath()):
            if image.filePath() not in [ image.filePath() for image in self._images ]:
                os.remove(os.path.join(self._project.filesDir(), "project-files", image.filePath()))

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

    def rectangles(self):
        """
        Returns all the rectangles in this topology.
        """

        return self._rectangles

    def ellipses(self):
        """
        Returns all the ellipses in this topology.
        """

        return self._ellipses

    def images(self):
        """
        Returns all the images in this topology.
        """

        return self._images

    def reset(self):
        """
        Resets this topology.
        """

        # self._topology.clear()
        self._links.clear()
        self._nodes.clear()
        self._notes.clear()
        self._rectangles.clear()
        self._ellipses.clear()
        self._images.clear()

    def __str__(self):

        return "GNS3 network topology"

    def createNode(self, node_data):
        """
        Creates a new node on the scene.

        :param node_data: node data to create a new node
        """
        node_module = None
        for module in MODULES:
            instance = module.instance()
            if node_data["node_type"] == "dynamips":
                node_class = module.getNodeType(node_data["node_type"], node_data["properties"]["platform"])
            else:
                node_class = module.getNodeType(node_data["node_type"])
            if node_class:
                node_module = module.instance()
                break

        if not node_module:
            raise ModuleError("Could not find any module for {}".format(node_class))

        node = node_module.instantiateNode(node_class, ComputeManager.instance().getCompute(node_data["compute_id"]), self._project)
        node.error_signal.connect(self._main_window.uiConsoleTextEdit.writeError)
        node.warning_signal.connect(self._main_window.uiConsoleTextEdit.writeWarning)
        node.server_error_signal.connect(self._main_window.uiConsoleTextEdit.writeServerError)
        node.createNodeCallback(node_data)

        self._main_window.uiGraphicsView.createNodeItem(node, node_data["symbol"], node_data["x"], node_data["y"])

    def createLink(self, link_data):
        if len(link_data["nodes"]) == 2:
            link_side = link_data["nodes"][0]
            source_node = self.getNodeFromUuid(link_side["node_id"])
            for port in source_node.ports():
                if port.adapterNumber() == link_side["adapter_number"] and port.portNumber() == link_side["port_number"]:
                    source_port = port
                    break
            link_side = link_data["nodes"][1]
            destination_node = self.getNodeFromUuid(link_side["node_id"])
            for port in destination_node.ports():
                if port.adapterNumber() == link_side["adapter_number"] and port.portNumber() == link_side["port_number"]:
                    destination_port = port
                    break
        self._main_window.uiGraphicsView.addLink(source_node, source_port, destination_node, destination_port, link_id=link_data["link_id"])

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of Topology.

        :returns: instance of Topology
        """

        if not hasattr(Topology, "_instance"):
            Topology._instance = Topology()
        return Topology._instance
