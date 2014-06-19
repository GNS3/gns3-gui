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
Topology summary view that list all the nodes, their status and connections.
"""

from .qt import QtGui, QtCore
from .node import Node
from .topology import Topology

import logging
log = logging.getLogger(__name__)


class TopologyNodeItem(QtGui.QTreeWidgetItem):
    """
    Custom item for the QTreeWidget instance
    (topology summary view).

    :param parent: parent widget
    :param node: Node instance
    """

    def __init__(self, parent, node):

        QtGui.QTreeWidgetItem.__init__(self, parent)
        self._node = node
        self._parent = parent

        # we want to know about the node events
        node.started_signal.connect(self._refreshStatusSlot)
        node.stopped_signal.connect(self._refreshStatusSlot)
        node.suspended_signal.connect(self._refreshStatusSlot)
        node.updated_signal.connect(self._refreshNodeSlot)
        node.deleted_signal.connect(self._deletedNodeSlot)

        self._refreshStatusSlot()
        self._refreshNodeSlot()

    def _refreshStatusSlot(self):
        """
        Changes the icon to show the node status (started, stopped etc.)
        """

        self.setText(0, self._node.name())
        if self._node.status() == Node.started:
            self.setIcon(0, QtGui.QIcon(':/icons/led_green.svg'))
        elif self._node.status() == Node.suspended:
            self.setIcon(0, QtGui.QIcon(':/icons/led_yellow.svg'))
        else:
            self.setIcon(0, QtGui.QIcon(':/icons/led_red.svg'))

    def _refreshNodeSlot(self):
        """
        Slot to update the node.
        """

        self.refresh()

    def refresh(self):
        """
        Updates the widget item with the current node name and list all the connections
        as children.
        """

        if self._node.name() != self.text(0):
            # refresh all the other item if the node name has changed
            self._parent.refreshAll(self)

        self.setText(0, self._node.name())
        ports = self._node.ports()
        self.takeChildren()

        for port in ports:
            if not port.isFree():
                item = QtGui.QTreeWidgetItem()
                item.setText(0, "{} {}".format(port.name(), port.description()))
                self.addChild(item)

        self.sortChildren(0, QtCore.Qt.AscendingOrder)

    def _deletedNodeSlot(self):
        """
        Removes the node from the view.
        """

        tree = self.treeWidget()
        tree.takeTopLevelItem(tree.indexOfTopLevelItem(self))


class TopologySummaryView(QtGui.QTreeWidget):
    """
    Topology summary view implementation.

    :param parent: parent widget
    """

    def __init__(self, parent):

        QtGui.QTreeWidget.__init__(self, parent)
        self._topology = Topology.instance()

    def addNode(self, node):
        """
        Adds a node to the summary view.

        :param node: Node instance
        """

        # we want to have this node listed only when completely created.
        node.created_signal.connect(self._createdNodeSlot)

    def clear(self):
        """
        Clears all the topology summary.
        """

        QtGui.QTreeWidget.clear(self)

    def refreshAll(self, source_child=None):
        """
        Refreshes all the items.
        """

        root = self.invisibleRootItem()
        for index in range(0, root.childCount()):
            child = root.child(index)
            if source_child and source_child == child:
                continue
            child.refresh()

    def _createdNodeSlot(self, node_id):
        """
        Received events for node creation.

        :param node_id: node identifier
        """

        if not node_id:
            log.error("node ID is null")
            return

        node = self._topology.getNode(node_id)
        if not node:
            log.error("could not find node with ID {}".format(node_id))
            return

        TopologyNodeItem(self, node)

    def mousePressEvent(self, event):
        """
        Handles all mouse press events.

        :param event: QMouseEvent instance
        """

        if event.button() == QtCore.Qt.RightButton:
            self._showContextualMenu()
        else:
            QtGui.QTreeWidget.mousePressEvent(self, event)

    def _showContextualMenu(self):
        """
        Contextual menu to expand and collapse the tree.
        """

        menu = QtGui.QMenu()
        expand_all = QtGui.QAction("Expand all", menu)
        expand_all.setIcon(QtGui.QIcon(":/icons/plus.svg"))
        self.connect(expand_all, QtCore.SIGNAL('triggered()'), self._expandAllSlot)
        collapse_all = QtGui.QAction("Collapse all", menu)
        collapse_all.setIcon(QtGui.QIcon(":/icons/minus.svg"))
        self.connect(collapse_all, QtCore.SIGNAL('triggered()'), self._collapseAllSlot)
        menu.addAction(expand_all)
        menu.addAction(collapse_all)
        menu.exec_(QtGui.QCursor.pos())

    def _expandAllSlot(self):
        """
        Expands all items.
        """

        self.expandAll()

    def _collapseAllSlot(self):
        """
        Collapses all items.
        """

        self.collapseAll()
