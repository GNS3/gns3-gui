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

#import networkx as nx
from .qt import QtCore
from .items.node_item import NodeItem
from .servers import Servers
from .modules import MODULES
from .modules.module_error import ModuleError
from .utils.message_box import MessageBox
from .version import __version__

import logging
log = logging.getLogger(__name__)


class Topology(object):
    """
    Topology.
    """

    def __init__(self):

        self._nodes = []
        self._links = []
        self._topology = None
        self._initialized_nodes = []
        #self._topology = nx.Graph()
        self._resources_type = None

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

    def reset(self):
        """
        Resets this topology.
        """

        #self._topology.clear()
        self._links.clear()
        self._nodes.clear()
        self._initialized_nodes.clear()
        log.info("topology has been reset")

    def _dump_gui_settings(self, topology):
        """
        Adds GUI settings to the topology when saving a topology.

        :param topology: topology representation
        """

        from .main_window import MainWindow
        view = MainWindow.instance().uiGraphicsView

        if "nodes" in topology["topology"]:
            for item in view.scene().items():
                if isinstance(item, NodeItem):
                    for node in topology["topology"]["nodes"]:
                        if node["id"] == item.node().id():
                            node["x"] = item.x()
                            node["y"] = item.y()
                            if item.zValue() != 1.0:
                                node["z"] = item.zValue()

    def dump(self, include_gui_data=True):
        """
        Creates a complete representation of the topology.

        :param include_gui_data: either to include or not the GUI specific info.

        :returns: topology representation
        """

        log.info("starting to save the topology (version {})".format(__version__))

        topology = {"version": __version__,
                    "type": "topology",
                    "topology": {},
                    "resources_type": self._resources_type,
                    }

        servers = {}

        # first the nodes
        if self._nodes:
            topology_nodes = topology["topology"]["nodes"] = []
            for node in self._nodes:
                if node.server().id() not in servers:
                    servers[node.server().id()] = node.server()
                log.info("saving node: {}".format(node.name()))
                topology_nodes.append(node.dump())

        # then the links
        if self._links:
            topology_links = topology["topology"]["links"] = []
            for link in self._links:
                log.info("saving {}".format(link.description()))
                topology_links.append(link.dump())

        # finally the servers
        if servers:
            topology_servers = topology["topology"]["servers"] = []
            for server in servers.values():
                log.info("saving server {}:{}".format(server.host, server.port))
                topology_servers.append(server.dump())

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

        # deactivate the unsaved state support
        main_window.ignoreUnsavedState(True)
        # trick: no matter what, reactivate the unsaved state support after 3 seconds
        QtCore.QTimer.singleShot(3000, self._reactivateUnsavedState)

        if "topology" not in topology:
            log.warn("not a topology file")
            return

        self._node_to_links_mapping = {}
        # first create a mapping node ID to links
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

        # then load the servers
        self._servers = {}
        server_manager = Servers.instance()
        if "servers" in topology["topology"]:
            servers = topology["topology"]["servers"]
            for topology_server in servers:
                if "local" in topology_server and topology_server["local"]:
                    self._servers[topology_server["id"]] = server_manager.localServer()
                else:
                    host = topology_server["host"]
                    port = topology_server["port"]
                    self._servers[topology_server["id"]] = server_manager.getRemoteServer(host, port)

        # finally load the nodes
        node_errors = []
        if "nodes" in topology["topology"]:
            topology_nodes = {}
            nodes = topology["topology"]["nodes"]
            for topology_node in nodes:
                # check for duplicate node IDs
                if topology_node["id"] in topology_nodes:
                    node_errors.append("Duplicated node ID {} for {}".format(topology_node["id"],
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
                        node_errors.append("No server reference for node ID {}".format(topology_node["id"]))
                        continue

                    node = node_module.createNode(node_class, server)
                    node.error_signal.connect(main_window.uiConsoleTextEdit.writeError)
                    node.warning_signal.connect(main_window.uiConsoleTextEdit.writeWarning)
                    node.server_error_signal.connect(main_window.uiConsoleTextEdit.writeServerError)

                except ModuleError as e:
                    node_errors.append(str(e))
                    continue

                node.setId(topology_node["id"])

                # we want to know when the node has been created
                node.created_signal.connect(self._nodeCreatedSlot)

                # load the settings
                node.load(topology_node)

                # create the node item and restore GUI settings
                node_item = NodeItem(node)
                node_item.setPos(topology_node["x"], topology_node["y"])
                view.scene().addItem(node_item)
                self.addNode(node)
                main_window.uiTopologySummaryTreeWidget.addNode(node)

        self._resources_type = topology['resources_type']

        if node_errors:
            errors = "\n".join(node_errors)
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
                            break

                    # find the destination port
                    for port in destination_node.ports():
                        if port.id() == link["destination_port_id"]:
                            destination_port = port
                            break

                    if source_port and destination_port:
                        view.addLink(source_node, source_port, destination_node, destination_port)

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

    @resourcesType.setter
    def resourcesType(self, val):
        if val in ('local', 'cloud'):
            self._resources_type = val
