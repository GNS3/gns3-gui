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

from .qt import QtGui, QtCore, QtWidgets, qslot
from .node import Node
from .topology import Topology
from .items.node_item import NodeItem
from .items.link_item import LinkItem
from .packet_capture import PacketCapture
from .utils import natural_sort_key

import logging
log = logging.getLogger(__name__)


class TopologyNodeItem(QtWidgets.QTreeWidgetItem):

    """
    Custom item for the QTreeWidget instance
    (topology summary view).

    :param parent: parent widget
    :param node: Node instance
    """

    def __init__(self, parent, node):

        super().__init__(parent)
        self._node = node
        self._parent = parent

        # we want to know about the node events
        node.started_signal.connect(self._refreshStatusSlot)
        node.stopped_signal.connect(self._refreshStatusSlot)
        node.suspended_signal.connect(self._refreshStatusSlot)
        node.updated_signal.connect(self._refreshNodeSlot)
        node.created_signal.connect(self._refreshNodeSlot)
        node.deleted_signal.connect(self._deletedNodeSlot)

        self._refreshStatusSlot()
        self._refreshNodeSlot()

    @qslot
    def _refreshStatusSlot(self, *args):
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

    @qslot
    def _refreshNodeSlot(self, *args):
        """
        Slot to update the node.
        """
        self.refresh()

    def node(self):
        """
        Returns the node.

        :return: Node instance
        """

        return self._node

    def refresh(self):
        """
        Updates the widget item with the current node name.
        """

        if self._node.name() != self.text(0):
            # refresh all the other item if the node name has changed
            self._parent.refreshAllLinks(source_child=self)
        self.setText(0, self._node.name())
        self.refreshLinks()
        self._parent.invisibleRootItem().sortChildren(0, QtCore.Qt.AscendingOrder)

    def refreshLinks(self):
        """
        List all the connections as children.
        """

        self.takeChildren()

        capturing = False
        for link in self._node.links():
            item = QtWidgets.QTreeWidgetItem()
            port = link.getNodePort(self._node)
            item.setText(0, "{} {}".format(port.shortName(), port.description(short=True)))
            item.setData(0, QtCore.Qt.UserRole, link)
            if link.capturing():
                item.setIcon(0, QtGui.QIcon(':/icons/inspect.svg'))
                capturing = True
            self.addChild(item)

        if self._parent.show_only_devices_with_capture and capturing is False:
            self.setHidden(True)
        else:
            self.setHidden(False)

        self.sortChildren(0, QtCore.Qt.AscendingOrder)

    @qslot
    def _deletedNodeSlot(self, *args):
        """
        Removes the node from the view.
        """

        tree = self.treeWidget()
        tree.takeTopLevelItem(tree.indexOfTopLevelItem(self))
        tree.nodes_id.remove(self._node.id())

    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        return natural_sort_key(self.text(column)) < natural_sort_key(otherItem.text(column))


class TopologySummaryView(QtWidgets.QTreeWidget):

    """
    Topology summary view implementation.

    :param parent: parent widget
    """

    def __init__(self, parent):

        super().__init__(parent)
        self.nodes_id = set()
        self._topology = Topology.instance()
        self._topology.node_added_signal.connect(self._nodeAddedSlot)
        self._topology.project_changed_signal.connect(self._projectChangedSlot)
        self.itemSelectionChanged.connect(self._itemSelectionChangedSlot)
        self.show_only_devices_with_capture = False
        self.setExpandsOnDoubleClick(False)
        self.itemDoubleClicked.connect(self._itemDoubleClickedSlot)

    @qslot
    def _projectChangedSlot(self, *args):
        """
        Clears all the topology summary.
        """

        self.clear()

    def refreshAllLinks(self, source_child=None):
        """
        Refreshes all links for all items.
        """

        root = self.invisibleRootItem()
        for index in range(0, root.childCount()):
            child = root.child(index)
            if source_child and source_child == child:
                continue
            child.refreshLinks()

    @qslot
    def _nodeAddedSlot(self, base_node_id, *args):
        """
        Received events for node creation.

        :param base_node_id: base node identifier
        """

        if not base_node_id:
            log.error("node ID is null")
            return

        node = self._topology.getNode(base_node_id)
        if not node:
            log.error("could not find node with ID {}".format(base_node_id))
            return

        # We check if we don't already have this node because it seem
        # sometimes we can get twice the signal
        if node.id() in self.nodes_id:
            return
        self.nodes_id.add(node.id())
        TopologyNodeItem(self, node)

    @qslot
    def _itemSelectionChangedSlot(self, *args):
        """
        Slot called when an item is selected in the TreeWidget.
        """

        current_item = self.currentItem()
        if current_item:
            from .main_window import MainWindow
            view = MainWindow.instance().uiGraphicsView
            for item in view.scene().items():
                if isinstance(item, NodeItem):
                    item.setSelected(False)
                    if isinstance(current_item, TopologyNodeItem) and item.node().id() == current_item.node().id():
                        item.setSelected(True)
                elif isinstance(item, LinkItem):
                    item.setHovered(False)
                    if not isinstance(current_item, TopologyNodeItem):
                        port = current_item.data(0, QtCore.Qt.UserRole)
                        if item.sourcePort() == port or item.destinationPort() == port:
                            item.setHovered(True)

    @qslot
    def _itemDoubleClickedSlot(self, current_item, *args):
        """
        When user double click on an element we center the topology on it
        """
        if current_item != 0:
            from .main_window import MainWindow
            view = MainWindow.instance().uiGraphicsView
            for item in view.scene().items():
                if isinstance(item, NodeItem):
                    if isinstance(current_item, TopologyNodeItem) and item.node().id() == current_item.node().id():
                        view.centerOn(item)
                elif isinstance(item, LinkItem):
                    if not isinstance(current_item, TopologyNodeItem):
                        port = current_item.data(0, QtCore.Qt.UserRole)
                        if item.sourcePort() == port or item.destinationPort() == port:
                            view.centerOn(item)

    def mousePressEvent(self, event):
        """
        Handles all mouse press events.

        :param event: QMouseEvent instance
        """

        if event.button() == QtCore.Qt.RightButton:
            self._showContextualMenu()
        else:
            super().mousePressEvent(event)

    def _showContextualMenu(self):
        """
        Contextual menu to expand and collapse the tree.
        """

        menu = QtWidgets.QMenu()
        expand_all = QtWidgets.QAction("Expand all", menu)
        expand_all.setIcon(QtGui.QIcon(":/icons/plus.svg"))
        expand_all.triggered.connect(self._expandAllSlot)
        menu.addAction(expand_all)

        collapse_all = QtWidgets.QAction("Collapse all", menu)
        collapse_all.setIcon(QtGui.QIcon(":/icons/minus.svg"))
        collapse_all.triggered.connect(self._collapseAllSlot)
        menu.addAction(collapse_all)

        if self.show_only_devices_with_capture is False:
            devices_with_capture = QtWidgets.QAction("Show devices with capture(s)", menu)
            devices_with_capture.setIcon(QtGui.QIcon(":/icons/inspect.svg"))
            devices_with_capture.triggered.connect(self._devicesWithCaptureSlot)
            menu.addAction(devices_with_capture)
        else:
            show_all_devices = QtWidgets.QAction("Show all devices", menu)
            # show_all_devices.setIcon(QtGui.QIcon(":/icons/inspect.svg"))
            show_all_devices.triggered.connect(self._showAllDevicesSlot)
            menu.addAction(show_all_devices)

        stop_all_captures = QtWidgets.QAction("Stop all captures", menu)
        stop_all_captures.setIcon(QtGui.QIcon(":/icons/capture-stop.svg"))
        stop_all_captures.triggered.connect(self._stopAllCapturesSlot)
        menu.addAction(stop_all_captures)

        current_item = self.currentItem()
        from .main_window import MainWindow
        view = MainWindow.instance().uiGraphicsView
        if current_item and not current_item.isHidden():
            menu.addSeparator()
            if isinstance(current_item, TopologyNodeItem):
                view.populateDeviceContextualMenu(menu)
            else:
                port = current_item.data(0, QtCore.Qt.UserRole)
                for item in view.scene().items():
                    if isinstance(item, LinkItem) and (item.sourcePort() == port or item.destinationPort() == port):
                        item.populateLinkContextualMenu(menu)
                        break

        menu.exec_(QtGui.QCursor.pos())

    @qslot
    def _expandAllSlot(self, *args):
        """
        Expands all items.
        """

        self.expandAll()

    @qslot
    def _collapseAllSlot(self, *args):
        """
        Collapses all items.
        """

        self.collapseAll()

    @qslot
    def _devicesWithCaptureSlot(self, *args):
        """
        Show only devices with captures.
        """

        self.show_only_devices_with_capture = True
        self.refreshAllLinks()

    @qslot
    def _showAllDevicesSlot(self, *args):
        """
        Show all devices items.
        """

        self.show_only_devices_with_capture = False
        self.refreshAllLinks()

    @qslot
    def _stopAllCapturesSlot(self, *args):
        """
        Stop all packet captures.
        """

        for link in self._topology.links():
            if link.capturing():
                PacketCapture.instance().stopCapture(link)
