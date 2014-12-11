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
Handles the saving and loading of a topology.
"""

import os

from .qt import QtCore, QtGui, QtSvg
from .items.node_item import NodeItem
from .items.link_item import LinkItem
from .items.note_item import NoteItem
from .items.rectangle_item import RectangleItem
from .items.ellipse_item import EllipseItem
from .items.image_item import ImageItem
from .servers import Servers
from .modules import MODULES
from .modules.module_error import ModuleError
from .utils.message_box import MessageBox
from .version import __version__

import logging
log = logging.getLogger(__name__)


class TopologyInstance:
    def __init__(self, name, id, size_id, image_id, private_key, public_key,
                 host=None, port=None, ssl_ca=None, ssl_ca_file=None):
        # host, port, ssl_ca and ssl_ca_file are not known when the instance is created.
        # They will typically be set at a later point in time.
        self.name = name
        self.id = id
        self.size_id = size_id
        self.image_id = image_id
        self.public_key = public_key
        self.private_key = private_key
        self.host = host
        self.port = port
        self.ssl_ca = ssl_ca
        self.ssl_ca_file = ssl_ca_file

    @classmethod
    def fields(cls):
        return ["name", "id", "size_id", "image_id", "private_key", "public_key",
                "host", "port", "ssl_ca", "ssl_ca_file"]

    def set_later_attributes(self, host, port, ssl_ca, ssl_ca_file):
        """
        Set attributes that are not known at the time of cloud instance creation.
        """
        self.host = host
        self.port = port
        self.ssl_ca = ssl_ca
        self.ssl_ca_file = ssl_ca_file

class Topology(object):
    """
    Topology.
    """

    def __init__(self):

        self._nodes = []
        self._links = []
        self._notes = []
        self._rectangles = []
        self._ellipses = []
        self._images = []
        self._topology = None
        self._initialized_nodes = []
        self._resources_type = "local"
        self._instances = []

    def addNode(self, node):
        """
        Adds a new node to this topology.

        :param node: Node instance
        """

        #self._topology.add_node(node)
        self._nodes.append(node)

    def removeNode(self, node):
        """
        Removes a node from this topology.

        :param node: Node instance
        """

        if node in self._nodes:
            self._nodes.remove(node)

    def getNode(self, node_id):
        """
        Lookups for a node using its identifier.

        :returns: Node instance or None
        """

        for node in self._nodes:
            if node.id() == node_id:
                return node
        return None

    def addLink(self, link):
        """
        Adds a new link to this topology.

        :param link: Link instance
        """

        #self._topology.add_node(node)
        self._links.append(link)

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

    def addInstance(self, name, id, size_id, image_id, private_key, public_key,
                    host=None, port=None, ssl_ca=None, ssl_ca_file=None):
        """
        Add an instance to this cloud topology
        """

        i = TopologyInstance(name=name, id=id, size_id=size_id, image_id=image_id,
                             private_key=private_key, public_key=public_key, host=host,
                             port=port, ssl_ca=ssl_ca, ssl_ca_file=ssl_ca_file)

        self._instances.append(i)

    def addInstance2(self, topology_instance):
        self._instances.append(topology_instance)

    def removeInstance(self, id):
        """
        Removes an instance from this cloud topology

        :param name: the name of the instance
        """

        for instance in self._instances:
            if instance.id == id:
                # remove all the nodes running on the instance
                for node in self._nodes:
                    if node._server.instance_id == id:
                        self.removeNode(node)
                        node.delete()
                # remove the instance itself
                self._instances.remove(instance)
                break

    def getInstance(self, id):
        """
        Return the instance if present

        :param id: the instance id
        :return: a TopologyInstance object
        """
        for instance in self._instances:
            if instance.id == id:
                return instance

    def anyInstance(self):
        # For now, just return the first instance
        return self._instances[0]

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

    def instances(self):
        """
        Returns the list of instances for this cloud topology
        """

        return self._instances

    def reset(self):
        """
        Resets this topology.
        """

        #self._topology.clear()
        self._links.clear()
        self._nodes.clear()
        self._notes.clear()
        self._rectangles.clear()
        self._ellipses.clear()
        self._images.clear()
        self._initialized_nodes.clear()
        self._resources_type = "local"
        self._instances = []
        log.info("topology has been reset")

    def _dump_gui_settings(self, topology):
        """
        Adds GUI settings to the topology when saving a topology.

        :param topology: topology representation
        """

        from .main_window import MainWindow
        main_window = MainWindow.instance()
        view = main_window.uiGraphicsView

        if "nodes" in topology["topology"]:
            for item in view.scene().items():
                if isinstance(item, NodeItem):
                    for node in topology["topology"]["nodes"]:
                        if node["id"] == item.node().id():
                            node["x"] = item.x()
                            node["y"] = item.y()
                            if item.zValue() != 1.0:
                                node["z"] = item.zValue()
                            if item.label():
                                node["label"] = item.label().dump()
                            default_symbol_path = item.defaultRenderer().objectName()
                            if default_symbol_path:
                                node["default_symbol"] = default_symbol_path
                            hover_symbol_path = item.hoverRenderer().objectName()
                            if hover_symbol_path:
                                node["hover_symbol"] = hover_symbol_path
                if isinstance(item, LinkItem):
                    for link in topology["topology"]["links"]:
                        if link["id"] == item.link().id():
                            source_port_label = item.sourcePort().label()
                            destination_port_label = item.destinationPort().label()
                            if source_port_label:
                                link["source_port_label"] = source_port_label.dump()
                            if destination_port_label:
                                link["destination_port_label"] = destination_port_label.dump()

        # notes
        if self._notes:
            topology_notes = topology["topology"]["notes"] = []
            for note in self._notes:
                topology_notes.append(note.dump())

        # rectangles
        if self._rectangles:
            topology_rectangles = topology["topology"]["rectangles"] = []
            for rectangle in self._rectangles:
                topology_rectangles.append(rectangle.dump())

        # ellipses
        if self._ellipses:
            topology_ellipses = topology["topology"]["ellipses"] = []
            for ellipse in self._ellipses:
                topology_ellipses.append(ellipse.dump())

        # images
        if self._images:
            topology_images = topology["topology"]["images"] = []
            for image in self._images:
                image_info = image.dump()
                if "path" in image_info:
                    image_info["path"] = os.path.relpath(image_info["path"], main_window.projectSettings()["project_files_dir"])
                topology_images.append(image_info)

    def dump(self, include_gui_data=True):
        """
        Creates a complete representation of the topology.

        :param include_gui_data: either to include or not the GUI specific info.

        :returns: topology representation
        """

        log.info("starting to save the topology (version {})".format(__version__))

        from .main_window import MainWindow
        project_settings = MainWindow.instance().projectSettings()
        topology = {"name": project_settings["project_name"],
                    "version": __version__,
                    "type": "topology",
                    "topology": {},
                    "resources_type": project_settings["project_type"],
                    }

        self._resources_type = project_settings["project_type"]

        servers = {}

        # nodes
        if self._nodes:
            topology_nodes = topology["topology"]["nodes"] = []
            for node in self._nodes:
                if node.server().id() not in servers:
                    servers[node.server().id()] = node.server()
                log.info("saving node: {}".format(node.name()))
                topology_nodes.append(node.dump())

        # links
        if self._links:
            topology_links = topology["topology"]["links"] = []
            for link in self._links:
                log.info("saving {}".format(str(link)))
                topology_links.append(link.dump())

        # servers
        if servers:
            topology_servers = topology["topology"]["servers"] = []
            for server in servers.values():
                log.info("saving server {}:{}".format(server.host, server.port))
                topology_servers.append(server.dump())

        # instances
        if self._resources_type == "cloud":
            topology_instances = topology["topology"]["instances"] = []
            for i in self._instances:
                log.info("saving cloud instance {}".format(i.name))
                topology_instances.append({
                    "name": i.name,
                    "id": i.id,
                    "size_id": i.size_id,
                    "image_id": i.image_id,
                    "private_key": i.private_key,
                    "public_key": i.public_key
                })
        if include_gui_data:
            self._dump_gui_settings(topology)

        return topology

    def load(self, topology):
        """
        Loads a topology.

        :param topology: topology representation
        """

        from .main_window import MainWindow
        main_window = MainWindow.instance()
        view = main_window.uiGraphicsView

        topology_file_errors = []
        if "topology" not in topology or "version" not in topology:
            log.warn("not a topology file")
            return

        # deactivate the unsaved state support
        main_window.ignoreUnsavedState(True)
        # trick: no matter what, reactivate the unsaved state support after 3 seconds
        QtCore.QTimer.singleShot(3000, self._reactivateUnsavedState)

        self._node_to_links_mapping = {}
        # create a mapping node ID to links
        if "links" in topology["topology"]:
            links = topology["topology"]["links"]
            for topology_link in links:
                log.debug("mapping node to link with ID {}".format(topology_link["id"]))
                source_id = topology_link["source_node_id"]
                destination_id = topology_link["destination_node_id"]
                if source_id not in self._node_to_links_mapping:
                    self._node_to_links_mapping[source_id] = []
                if destination_id not in self._node_to_links_mapping:
                    self._node_to_links_mapping[destination_id] = []
                self._node_to_links_mapping[source_id].append(topology_link)
                self._node_to_links_mapping[destination_id].append(topology_link)

        # servers
        self._servers = {}
        server_manager = Servers.instance()
        if "servers" in topology["topology"]:
            servers = topology["topology"]["servers"]
            for topology_server in servers:
                if "local" in topology_server and topology_server["local"]:
                    self._servers[topology_server["id"]] = server_manager.localServer()
                elif "cloud" in topology_server and topology_server["cloud"]:
                    self._servers[topology_server["id"]] = server_manager.anyCloudServer()
                else:
                    host = topology_server["host"]
                    port = topology_server["port"]
                    self._servers[topology_server["id"]] = server_manager.getRemoteServer(host, port)

        # nodes
        if "nodes" in topology["topology"]:
            topology_nodes = {}
            nodes = topology["topology"]["nodes"]
            for topology_node in nodes:
                # check for duplicate node IDs
                if topology_node["id"] in topology_nodes:
                    topology_file_errors.append("Duplicated node ID {} for {}".format(topology_node["id"],
                                                                                      topology_node["description"]))
                    continue
                topology_nodes[topology_node["id"]] = topology_node

            for topology_node in topology_nodes.values():
                log.debug("loading node with ID {}".format(topology_node["id"]))

                try:
                    node_module = None
                    for module in MODULES:
                        instance = module.instance()
                        node_class = module.getNodeClass(topology_node["type"])
                        if node_class:
                            node_module = instance
                            break
                    if not node_module:
                        raise ModuleError("Could not find any module for {}".format(topology_node["type"]))

                    server = None
                    if topology_node["server_id"] in self._servers:
                        server = self._servers[topology_node["server_id"]]

                    if not server:
                        topology_file_errors.append("No server reference for node ID {}".format(topology_node["id"]))
                        continue

                    node = node_module.createNode(node_class, server)
                    node.error_signal.connect(main_window.uiConsoleTextEdit.writeError)
                    node.warning_signal.connect(main_window.uiConsoleTextEdit.writeWarning)
                    node.server_error_signal.connect(main_window.uiConsoleTextEdit.writeServerError)

                except ModuleError as e:
                    topology_file_errors.append(str(e))
                    continue

                node.setId(topology_node["id"])

                # we want to know when the node has been created
                node.created_signal.connect(self._nodeCreatedSlot)

                # load the settings
                node.load(topology_node)

                # create the node item and restore GUI settings
                node_item = NodeItem(node)
                node_item.setPos(topology_node["x"], topology_node["y"])

                # create the node label if present
                label_info = topology_node.get("label")
                if label_info:
                    node_label = NoteItem(node_item)
                    node_label.setEditable(False)
                    node_label.load(label_info)
                    node_item.setLabel(node_label)

                if "z" in topology_node:
                    node_item.setZValue(topology_node["z"])

                if "default_symbol" in topology_node:
                    path = topology_node["default_symbol"]
                    default_renderer = QtSvg.QSvgRenderer(path)
                    if default_renderer.isValid():
                        default_renderer.setObjectName(path)
                        node_item.setDefaultRenderer(default_renderer)

                if "hover_symbol" in topology_node:
                    path = topology_node["hover_symbol"]
                    hover_renderer = QtSvg.QSvgRenderer(path)
                    if hover_renderer.isValid() and default_renderer.isValid():
                        # default renderer must be valid too
                        hover_renderer.setObjectName(path)
                        node_item.setHoverRenderer(hover_renderer)

                view.scene().addItem(node_item)
                self.addNode(node)
                main_window.uiTopologySummaryTreeWidget.addNode(node)

        self._resources_type = topology.get("resources_type")

        # notes
        if "notes" in topology["topology"]:
            notes = topology["topology"]["notes"]
            for topology_note in notes:
                note_item = NoteItem()
                note_item.load(topology_note)
                view.scene().addItem(note_item)
                self.addNote(note_item)

        # rectangles
        if "rectangles" in topology["topology"]:
            rectangles = topology["topology"]["rectangles"]
            for topology_rectangle in rectangles:
                rectangle_item = RectangleItem()
                rectangle_item.load(topology_rectangle)
                view.scene().addItem(rectangle_item)
                self.addRectangle(rectangle_item)

        # ellipses
        if "ellipses" in topology["topology"]:
            ellipses = topology["topology"]["ellipses"]
            for topology_ellipse in ellipses:
                ellipse_item = EllipseItem()
                ellipse_item.load(topology_ellipse)
                view.scene().addItem(ellipse_item)
                self.addEllipse(ellipse_item)

        # images
        if "images" in topology["topology"]:
            images = topology["topology"]["images"]
            for topology_image in images:

                updated_image_path = os.path.join(main_window.projectSettings()["project_files_dir"], topology_image["path"])
                if os.path.isfile(updated_image_path):
                    image_path = updated_image_path
                else:
                    image_path = topology_image["path"]
                if not os.path.isfile(image_path):
                    topology_file_errors.append("Path to image {} doesn't exist".format(image_path))
                    continue

                pixmap = QtGui.QPixmap(image_path)
                if pixmap.isNull():
                    topology_file_errors.append("Image format not supported for {}".format(image_path))
                    continue

                image_item = ImageItem(pixmap, image_path)
                image_item.load(topology_image)
                view.scene().addItem(image_item)
                self.addImage(image_item)

        # instances
        if "instances" in topology["topology"]:
            instances = topology["topology"]["instances"]
            for instance in instances:
                self.addInstance(instance["name"], instance["id"], instance["size_id"],
                                 instance["image_id"],
                                 instance["private_key"], instance["public_key"])

        if topology_file_errors:
            errors = "\n".join(topology_file_errors)
            MessageBox(main_window, "Topology", "Errors detected while importing the topology", errors)

    def _nodeCreatedSlot(self, node_id):
        """
        Slot to know when a node has been created.
        When all nodes have initialized, links can be created.

        :param node_id: node identifier
        """

        node = self.getNode(node_id)
        if not node or not node.initialized():
            log.warn("cannot find node or node not initialized")
            return

        from .main_window import MainWindow
        view = MainWindow.instance().uiGraphicsView

        log.debug("node {} has initialized".format(node.name()))
        self._initialized_nodes.append(node_id)

        if node_id in self._node_to_links_mapping:
            topology_link = self._node_to_links_mapping[node_id]
            for link in topology_link:
                source_node_id = link["source_node_id"]
                destination_node_id = link["destination_node_id"]
                if source_node_id in self._initialized_nodes and destination_node_id in self._initialized_nodes:

                    source_node = self.getNode(source_node_id)
                    destination_node = self.getNode(destination_node_id)

                    log.debug("creating link from {} to {}".format(source_node.name(), destination_node.name()))

                    source_port = None
                    destination_port = None

                    # find the source port
                    for port in source_node.ports():
                        if port.id() == link["source_port_id"]:
                            source_port = port
                            if "source_port_label" in link:
                                source_port.setLabel(self._createPortLabel(source_node, link["source_port_label"]))
                            break

                    # find the destination port
                    for port in destination_node.ports():
                        if port.id() == link["destination_port_id"]:
                            destination_port = port
                            if "destination_port_label" in link:
                                destination_port.setLabel(self._createPortLabel(destination_node, link["destination_port_label"]))
                            break

                    if source_port and destination_port:
                        view.addLink(source_node, source_port, destination_node, destination_port)

    def _createPortLabel(self, node, label_info):
        """
        Creates a port label.

        :param node: Node instance
        :param label_info:  label info (dictionary)

        :return: NoteItem instance
        """

        from .main_window import MainWindow
        view = MainWindow.instance().uiGraphicsView

        for item in view.scene().items():
            if isinstance(item, NodeItem) and node.id() == item.node().id():
                port_label = NoteItem(item)
                port_label.load(label_info)
                port_label.hide()
                return port_label
        return None

    def _reactivateUnsavedState(self):
        """
        Slots to reactivate the unsaved state support
        when the QTimer timeouts
        """

        from .main_window import MainWindow
        MainWindow.instance().ignoreUnsavedState(False)

    def __str__(self):

        return "GNS3 network topology"

    @staticmethod
    def instance():
        """
        Singleton to return only one instance of Topology.

        :returns: instance of Topology
        """

        if not hasattr(Topology, "_instance"):
            Topology._instance = Topology()
        return Topology._instance

    @property
    def resourcesType(self):
        return self._resources_type
