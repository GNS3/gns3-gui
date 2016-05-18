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
import json
import uuid
import glob
import shutil
import sys

from .qt import QtGui, QtWidgets, QtSvg, qpartial
from .qt.qimage_svg_renderer import QImageSvgRenderer

from .items.node_item import NodeItem
from .items.svg_node_item import SvgNodeItem
from .items.link_item import LinkItem
from .items.note_item import NoteItem
from .items.rectangle_item import RectangleItem
from .items.ellipse_item import EllipseItem
from .items.svg_image_item import SvgImageItem
from .items.pixmap_image_item import PixmapImageItem
from .servers import Servers
from .modules import MODULES
from .modules.module_error import ModuleError
from .utils.message_box import MessageBox
from .utils.server_select import server_select
from .version import __version__
from .topology_check import getTopologyValidationErrors

import logging
log = logging.getLogger(__name__)

# The topology version supported by client
TOPOLOGY_REVISION = 4

VALIDATION_ERROR_MESSAGE = "Validation error when dumping the topology.\nIt's probably a false positive but please send the error and the .gns3 file to developers@gns3.net.\nThanks !"


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


class Topology:

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
        self._initialized_links = []
        self._instances = []
        self._auto_start = False
        self._project = None

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

    def addNode(self, node):
        """
        Adds a new node to this topology.

        :param node: Node instance
        """

        # self._topology.add_node(node)
        self._nodes.append(node)

    def removeNode(self, node):
        """
        Removes a node from this topology.

        :param node: Node instance
        """

        if node in self._nodes:
            self._nodes.remove(node)

    def getVM(self, vm_id):
        """
        Lookups for a vm using its identifier.

        :returns: Node instance or None
        """

        for node in self._nodes:
            if hasattr(node, "vm_id") and node.vm_id() == vm_id:
                return node
        return None

    def getNode(self, node_id):
        """
        Lookups for a node using its vm_id.

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


    def addInstance(self, name, id, size_id, image_id, private_key, public_key,
                    host=None, port=None, ssl_ca=None, ssl_ca_file=None):
        """
        Add an instance to this cloud topology
        """

        i = TopologyInstance(name=name, id=id, size_id=size_id, image_id=image_id,
                             private_key=private_key, public_key=public_key, host=host,
                             port=port, ssl_ca=ssl_ca, ssl_ca_file=ssl_ca_file)

        self._instances.append(i)

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

        # self._topology.clear()
        self._links.clear()
        self._nodes.clear()
        self._notes.clear()
        self._rectangles.clear()
        self._ellipses.clear()
        self._images.clear()
        self._initialized_nodes.clear()
        self._initialized_links.clear()
        self._instances = []
        log.info("Topology reset")

    def _dump_gui_settings(self, topology):
        """
        Adds GUI settings to the topology when saving a topology.

        :param topology: topology representation
        """

        from .main_window import MainWindow
        main_window = MainWindow.instance()
        if main_window.uiShowPortNamesAction.isChecked():
            topology["show_port_names"] = True
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
                            symbol_path = None
                            if isinstance(item, SvgNodeItem):
                                symbol_path = item.renderer().objectName()

                            if os.path.exists(symbol_path):
                                symbol_dir_path = os.path.join(self._project.filesDir(), "project-files", "symbols")
                                os.makedirs(symbol_dir_path, exist_ok=True)
                                new_symbol_path = os.path.join(symbol_dir_path, os.path.basename(symbol_path))
                                try:
                                    shutil.copyfile(symbol_path, new_symbol_path)
                                except shutil.SameFileError:
                                    pass
                                symbol_path = os.path.basename(symbol_path)
                            if symbol_path:
                                node["symbol"] = symbol_path
                if isinstance(item, LinkItem):
                    if item.link() is not None:
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
                image_in_default_dir = os.path.join(self._project.filesDir(), "project-files", "images", os.path.basename(image_info["path"]))
                if os.path.exists(image_in_default_dir):
                    image_info["path"] = os.path.join("images", os.path.basename(image_info["path"]))
                topology_images.append(image_info)

    def dump(self, include_gui_data=True, random_id=False):
        """
        Creates a complete representation of the topology.

        :param include_gui_data: either to include or not the GUI specific info.
        :param dump_id: change vm id and project id too a new randow value (save as feature)
        :param random_id: Randomize vm and project id (for save as)

        :returns: topology representation
        """

        log.info("Starting to save the topology (version {})".format(__version__))
        topology = {"project_id": self._project.id(),
                    "name": self._project.name(),
                    "version": __version__,
                    "type": "topology",
                    "topology": {},
                    "auto_start": False,
                    "revision": TOPOLOGY_REVISION
                    }

        servers = {}

        # nodes
        if self._nodes:
            topology_nodes = topology["topology"]["nodes"] = []
            for node in self._nodes:
                if not node.initialized():
                    continue
                if node.server().id() not in servers:
                    servers[node.server().id()] = node.server()
                log.info("Saving node: {}".format(node.name()))
                topology_nodes.append(node.dump())

        # links
        if self._links:
            topology_links = topology["topology"]["links"] = []
            for link in self._links:
                log.info("Saving link: {}".format(str(link)))
                topology_links.append(link.dump())

        # servers
        if servers:
            topology_servers = topology["topology"]["servers"] = []
            for server in servers.values():
                log.info("Saving server: {}".format(server.url()))
                topology_servers.append(server.dump())

        if include_gui_data:
            self._dump_gui_settings(topology)

        if random_id:
            topology = self._randomize_id(topology)

        errors = getTopologyValidationErrors(topology)
        if errors:
            log.error(errors)
            print(errors)
            print(VALIDATION_ERROR_MESSAGE)
            if hasattr(sys, '_called_from_test'):
                raise Exception

        return topology

    def _randomize_id(self, topology):
        """
        Iterate on all keys and replace the uuid by a new one.Use by save as
        for create new topology. It's also rename the VM folder on disk.

        """
        topology["project_id"] = str(uuid.uuid4())
        if "nodes" in topology["topology"]:
            for key, node in enumerate(topology["topology"]["nodes"]):
                old_uuid = topology["topology"]["nodes"][key].get("vm_id", None)
                new_uuid = str(uuid.uuid4())
                topology["topology"]["nodes"][key]["vm_id"] = new_uuid
                if old_uuid:
                    for path in glob.glob(os.path.join(glob.escape(self.project.filesDir()), "project-files", "*", old_uuid)):
                        new_path = path.replace(old_uuid, new_uuid)
                        shutil.move(path, new_path)
        return topology

    def loadFile(self, path, project):
        """
        Load a topology file

        :param path: Path to topology directory
        :param project: Project instance
        """

        log.debug("Start loading topology")
        self._project = project

        with open(path, encoding="utf-8") as f:
            log.info("loading project: {}".format(path))
            json_topology = json.load(f)

        if not isinstance(json_topology, dict):
            raise ValueError("Not a GNS3 project")

        if "revision" in json_topology and json_topology["revision"] > TOPOLOGY_REVISION:
            raise ValueError("This topology is not supported by your version of GNS3 please use GNS3 {} or later".format(json_topology["version"]))

        errors = getTopologyValidationErrors(json_topology)
        if errors:
            log.error(errors)
            print(errors)
            print(VALIDATION_ERROR_MESSAGE)
            if hasattr(sys, '_called_from_test'):
                raise Exception

        if "project_id" in json_topology:
            self._project.setId(json_topology["project_id"])
        self._project.setName(json_topology.get("name", "unnamed"))
        self._project.setTopologyFile(path)
        self._load(json_topology)

    def _load(self, topology):
        """
        Loads a topology.

        :param topology: topology representation
        """

        from .main_window import MainWindow
        main_window = MainWindow.instance()
        main_window.setProject(self._project)
        view = main_window.uiGraphicsView

        topology_file_errors = []
        if "topology" not in topology or "version" not in topology:
            log.warn("not a topology file")
            return

        # auto start option
        self._auto_start = topology.get("auto_start", False)

        # show port name option
        if topology.get("show_port_names", False):
            main_window.uiShowPortNamesAction.setChecked(True)
            LinkItem.showPortLabels(True)

        # deactivate the unsaved state support
        main_window.ignoreUnsavedState(True)
        # trick: no matter what, reactivate the unsaved state support after 5 seconds
        main_window.run_later(5000, self._reactivateUnsavedState)

        self._node_to_links_mapping = {}
        # create a mapping node ID to links
        if "links" in topology["topology"]:
            links = topology["topology"]["links"]
            for topology_link in links:
                # It seem an 1.0 topology could be corrupt and missed the id
                if "id" in topology_link:
                    log.debug("Mapping node to link with ID {}".format(topology_link["id"]))
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
                elif "vm" in topology_server and topology_server["vm"]:
                    gns3_vm_server = server_manager.vmServer()
                    if gns3_vm_server is None:
                        QtWidgets.QMessageBox.critical(main_window, "GNS3 VM", "The GNS3 VM is not running")
                        return
                    self._servers[topology_server["id"]] = gns3_vm_server
                else:
                    protocol = topology_server.get("protocol", "http")
                    host = topology_server["host"]
                    port = topology_server["port"]
                    user = topology_server.get("user", None)

                    topology_server.pop("cloud", False)
                    topology_server.pop("vm", False)
                    topology_server.pop("local", False)

                    server_id = topology_server.pop("id")
                    self._servers[server_id] = server_manager.findRemoteServer(protocol, host, port, user, topology_server)

                    if self._servers[server_id] is None:
                        reply = QtWidgets.QMessageBox.warning(main_window,
                                                              "Remote server not found",
                                                              "Remote server {}://{}:{} doesn't exist in your preferences, do you want to select another server?\n\nIt is recommended to backup your project first.".format(protocol, host, port),
                                                              QtWidgets.QMessageBox.Yes,
                                                              QtWidgets.QMessageBox.No)
                        if reply == QtWidgets.QMessageBox.Yes:
                            self._servers[server_id] = server_select(main_window)

                    if self._servers[server_id] is None:
                        # The user has not changed the server, let's create the server from the topology
                        self._servers[server_id] = server_manager.getRemoteServer(protocol, host, port, user, topology_server)

        # nodes
        self._load_old_topology = False
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

                    node = node_module.createNode(node_class, server, self._project)
                    node.error_signal.connect(main_window.uiConsoleTextEdit.writeError)
                    node.warning_signal.connect(main_window.uiConsoleTextEdit.writeWarning)
                    node.server_error_signal.connect(main_window.uiConsoleTextEdit.writeServerError)

                except ModuleError as e:
                    topology_file_errors.append(str(e))
                    continue

                node.setId(topology_node["id"])

                # we want to know when the node has been created
                callback = qpartial(self._nodeCreatedSlot, topology)
                node.created_signal.connect(callback)

                self.addNode(node)

                # load the settings
                node.load(topology_node)

                # for backward compatibility before version 1.4
                if "default_symbol" in topology_node:
                    topology_node["symbol"] = topology_node["default_symbol"]
                    topology_node["symbol"] = topology_node["symbol"][:-11] + ".svg" if topology_node["symbol"].endswith("normal.svg") else topology_node["symbol"]

                renderer = None
                if "symbol" in topology_node:
                    symbol_path = topology_node["symbol"]
                    renderer = QImageSvgRenderer(symbol_path)

                    if not renderer.isValid():
                        symbol_path = os.path.join(self._project.filesDir(), "project-files", "symbols", topology_node["symbol"])
                        renderer = QImageSvgRenderer(symbol_path)

                    if not renderer.isValid():
                        symbol_path = os.path.normpath(symbol_path)
                        renderer = QImageSvgRenderer(symbol_path)

                if renderer and renderer.isValid():
                    node_item = SvgNodeItem(node, symbol_path)
                else:
                    if "symbol" in topology_node:
                        topology_file_errors.append("Symbol {} is invalid or doesn't exist".format(topology_node["symbol"]))
                    node_item = SvgNodeItem(node)

                # create the node item and restore GUI settings
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

                view.scene().addItem(node_item)
                main_window.uiTopologySummaryTreeWidget.addNode(node)

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
        log.debug("Finish loading topology")
        self._autoStart(topology)

    def _load_images(self, topology):

        from .main_window import MainWindow
        main_window = MainWindow.instance()
        view = main_window.uiGraphicsView
        topology_file_errors = []

        # images
        if "images" in topology["topology"]:
            images = topology["topology"]["images"]
            for topology_image in images:
                updated_image_path = os.path.join(self._project.filesDir(), "project-files", topology_image["path"])
                if os.path.exists(updated_image_path):
                    image_path = updated_image_path
                else:
                    image_path = topology_image["path"]

                image_path = os.path.normpath(image_path)
                if not os.path.isfile(image_path):
                    topology_file_errors.append("Path to image {} doesn't exist".format(image_path))
                    continue

                pixmap = QtGui.QPixmap(image_path)
                if pixmap.isNull():
                    topology_file_errors.append("Image format not supported for {}".format(image_path))
                    continue

                renderer = QtSvg.QSvgRenderer(image_path)
                if renderer.isValid():
                    # use a SVG image item if this is a valid SVG file
                    image_item = SvgImageItem(renderer, image_path)
                else:
                    image_item = PixmapImageItem(pixmap, image_path)
                image_item.load(topology_image)
                view.scene().addItem(image_item)
                self.addImage(image_item)

        if topology_file_errors:
            errors = "\n".join(topology_file_errors)
            MessageBox(main_window, "Topology", "Errors detected while importing the topology", errors)

    def _nodeCreatedSlot(self, topology, node_id):
        """
        Slot to know when a node has been created.
        When all nodes have initialized, links can be created.

        :param node_id: node identifier
        """

        node = self.getNode(node_id)
        if not node or not node.initialized():
            log.warn("Cannot find node {node_id} or node not initialized".format(node_id=node_id))
            return

        from .main_window import MainWindow
        main_window = MainWindow.instance()
        view = main_window.uiGraphicsView
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
                    found = False
                    for port in source_node.ports():
                        if port.id() == link["source_port_id"]:
                            found = True
                            source_port = port
                            if "source_port_label" in link:
                                source_port.setLabel(self._createPortLabel(source_node, link["source_port_label"]))
                            break
                    if not found:
                        msg = "Corrupted topology {} source port doesn't exist".format(link["description"])
                        print(msg)
                        log.error(msg)

                    # find the destination port
                    found = False
                    for port in destination_node.ports():
                        if port.id() == link["destination_port_id"]:
                            found = True
                            destination_port = port
                            if "destination_port_label" in link:
                                destination_port.setLabel(self._createPortLabel(destination_node, link["destination_port_label"]))
                            break
                    if not found:
                        msg = "Corrupted topology {} destination port {} doesn't exist".format(link["description"], link["destination_port_id"])
                        print(msg)
                        log.error(msg)

                    if source_port and destination_port:
                        link = view.addLink(source_node, source_port, destination_node, destination_port)
                        callback = qpartial(self._linkCreatedSlot, topology)
                        link.add_link_signal.connect(callback)

        # We save at the end of initialization process in order to upgrade old topologies
        if len(topology["topology"]["nodes"]) == len(self._initialized_nodes):
            self._autoStart(topology)

            self._load_images(topology)
            if "project_id" not in topology:
                log.info("Saving converted topology...")
                main_window.saveProject(self._project.topologyFile())

    def _linkCreatedSlot(self, topology, link_id):
        """
        Called when a link is successfully created
        """

        self._initialized_links.append(link_id)
        self._autoStart(topology)

    def _autoStart(self, topology):
        """
        If everything is created auto start the topology
        """

        if "nodes" not in topology["topology"] or ((len(topology["topology"].get("links", [])) == len(self._initialized_links)) and (len(topology["topology"]["nodes"]) == len(self._initialized_nodes))):
            log.info("Topology initialized")
            # Auto start
            if self._auto_start:
                log.info("Auto start nodes")
                for initialized_node in self._initialized_nodes:
                    initialized_node = self.getNode(initialized_node)
                    if hasattr(initialized_node, "start"):
                        log.info("Auto start node %s", initialized_node.name())
                        initialized_node.start()

    def _createPortLabel(self, node, label_info):
        """
        Creates a port label.

        :param node: Node instance
        :param label_info:  label info (dictionary)

        :return: NoteItem instance
        """

        from .main_window import MainWindow
        main_window = MainWindow.instance()
        view = main_window.uiGraphicsView
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
        main_window = MainWindow.instance()
        main_window.ignoreUnsavedState(False)

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
