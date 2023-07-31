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

from .qt import QtGui, QtCore, QtWidgets, qslot, sip_is_deleted
from .node import Node
from .topology import Topology
from .items.node_item import NodeItem
from .items.link_item import LinkItem
from .packet_capture import PacketCapture
from .utils import natural_sort_key
from .utils.get_icon import get_icon

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
        if self._node.consoleType() in ("http", "https") and self._node.consoleType() and self._node.console():
            http_path = "{console_type}://{host}:{port}{path}".format(console_type=self._node.consoleType(),
                                                                      host=self._node.consoleHost(),
                                                                      port=self._node.console(),
                                                                      path=self._node.consoleHttpPath())
            self.setText(1, "{}".format(http_path))
        elif self._node.consoleType() != "none" and self._node.consoleType() and self._node.console():
            self.setText(1, "{} {}:{}".format(self._node.consoleType(), self._node.consoleHost(), self._node.console()))
        else:
            self.setText(1, "none")
        self.refreshLinks()
        self._parent.invisibleRootItem().sortChildren(0, QtCore.Qt.AscendingOrder)

    def refreshLinks(self):
        """
        List all the connections as children.
        """

        self.takeChildren()

        capturing = False
        filtering = False
        for link in self._node.links():
            item = QtWidgets.QTreeWidgetItem()
            port = link.getNodePort(self._node)
            item.setText(0, "{} {}".format(port.shortName(), port.description(short=True)))
            item.setData(0, QtCore.Qt.UserRole, link)
            if link.capturing():
                item.setIcon(0, QtGui.QIcon(':/icons/inspect.svg'))
                capturing = True
            if len(link.filters()) > 0:
                item.setIcon(0, QtGui.QIcon(':/icons/filter.svg'))
                filtering = True
            if link.capturing() and len(link.filters()) > 0:
                item.setIcon(0, QtGui.QIcon(':/icons/filter-capture.svg'))
            if link.suspended():
                item.setIcon(0, QtGui.QIcon(':/icons/pause.svg'))
            self.addChild(item)

        if self._parent.show_only_devices_with_capture and capturing is False:
            self.setHidden(True)
        elif self._parent.show_only_devices_with_filters and filtering is False:
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
        if not sip_is_deleted(tree):
            tree.takeTopLevelItem(tree.indexOfTopLevelItem(self))
            tree.nodes_id.remove(self._node.id())

    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        return natural_sort_key(str(self.text(column))) < natural_sort_key(str(otherItem.text(column)))


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
        self.show_only_devices_with_filters = False
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
        self.resizeColumnToContents(0)

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
                        link = current_item.data(0, QtCore.Qt.UserRole)
                        if item.link() == link:
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
                        link = current_item.data(0, QtCore.Qt.UserRole)
                        if item.link() == link:
                            view.centerOn(item)

    def contextMenuEvent(self, event):
        """
        Handles all context menu events.

        :param event: QContextMenuEvent instance
        """

        self._showContextualMenu(event.globalPos())

    def _showContextualMenu(self, pos):
        """
        Contextual menu to expand and collapse the tree.
        """

        menu = QtWidgets.QMenu()
        expand_all = QtWidgets.QAction("Expand all", menu)
        expand_all.setIcon(get_icon("plus.svg"))
        expand_all.triggered.connect(self._expandAllSlot)
        menu.addAction(expand_all)

        collapse_all = QtWidgets.QAction("Collapse all", menu)
        collapse_all.setIcon(get_icon("minus.svg"))
        collapse_all.triggered.connect(self._collapseAllSlot)
        menu.addAction(collapse_all)

        if self.show_only_devices_with_capture is False and self.show_only_devices_with_filters is False:
            devices_with_capture = QtWidgets.QAction("Show devices with capture(s)", menu)
            devices_with_capture.setIcon(get_icon("inspect.svg"))
            devices_with_capture.triggered.connect(self._devicesWithCaptureSlot)
            menu.addAction(devices_with_capture)

            devices_with_filters = QtWidgets.QAction("Show devices with packet filter(s)", menu)
            devices_with_filters.setIcon(get_icon("filter.svg"))
            devices_with_filters.triggered.connect(self._devicesWithFiltersSlot)
            menu.addAction(devices_with_filters)

        else:
            show_all_devices = QtWidgets.QAction("Show all devices", menu)
            # show_all_devices.setIcon(QtGui.QIcon(":/icons/inspect.svg"))
            show_all_devices.triggered.connect(self._showAllDevicesSlot)
            menu.addAction(show_all_devices)

        stop_all_captures = QtWidgets.QAction("Stop all captures", menu)
        stop_all_captures.setIcon(get_icon("capture-stop.svg"))
        stop_all_captures.triggered.connect(self._stopAllCapturesSlot)
        menu.addAction(stop_all_captures)

        reset_all_filters = QtWidgets.QAction("Reset all packet filters", menu)
        reset_all_filters.setIcon(get_icon("filter-reset.svg"))
        reset_all_filters.triggered.connect(self._resetAllFiltersSlot)
        menu.addAction(reset_all_filters)

        resume_suspended_links = QtWidgets.QAction("Resume all suspended links", menu)
        resume_suspended_links.setIcon(get_icon("start.svg"))
        resume_suspended_links.triggered.connect(self._resumeAllLinksSlot)
        menu.addAction(resume_suspended_links)

        current_item = self.currentItem()
        from .main_window import MainWindow
        view = MainWindow.instance().uiGraphicsView
        if current_item and not current_item.isHidden():
            menu.addSeparator()
            if isinstance(current_item, TopologyNodeItem):
                view.populateDeviceContextualMenu(menu)
            else:
                link = current_item.data(0, QtCore.Qt.UserRole)
                for item in view.scene().items():
                    if isinstance(item, LinkItem) and item.link() == link:
                        item.populateLinkContextualMenu(menu)
                        break

        menu.exec_(pos)

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
    def _devicesWithFiltersSlot(self, *args):
        """
        Show only devices with filters.
        """

        self.show_only_devices_with_filters = True
        self.refreshAllLinks()

    @qslot
    def _showAllDevicesSlot(self, *args):
        """
        Show all devices items.
        """

        self.show_only_devices_with_capture = False
        self.show_only_devices_with_filters = False
        self.refreshAllLinks()

    @qslot
    def _stopAllCapturesSlot(self, *args):
        """
        Stop all packet captures.
        """

        for link in self._topology.links():
            if link.capturing():
                PacketCapture.instance().stopCapture(link)

    @qslot
    def _resetAllFiltersSlot(self, *args):
        """
        Reset all packet filters
        """

        for link in self._topology.links():
            if len(link.filters()) > 0:
                filters = {}
                link.setFilters(filters)
                link.update()

    @qslot
    def _resumeAllLinksSlot(self, *args):
        """
        Resume all suspended links.
        """

        for link in self._topology.links():
            if link.suspended():
                link.toggleSuspend()

    def keyPressEvent(self, event):
        """
        Handles key press events
        """

        from .main_window import MainWindow
        view = MainWindow.instance().uiGraphicsView
        # only deleting a link or node is supported for now
        if event.key() == QtCore.Qt.Key_Delete:
            current_item = self.currentItem()
            if isinstance(current_item, TopologyNodeItem):
                current_item.node().delete()
            else:
                link = current_item.data(0, QtCore.Qt.UserRole)
                for item in view.scene().items():
                    if isinstance(item, LinkItem) and item.link() == link:
                        item.delete()
        super().keyPressEvent(event)
