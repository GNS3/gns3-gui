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
from .items.group_item import GroupItem
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
        self._parent.refreshGroupVisibility()
        (self.parent() or self._parent.invisibleRootItem()).sortChildren(0, QtCore.Qt.SortOrder.AscendingOrder)

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
            item.setData(0, QtCore.Qt.ItemDataRole.UserRole, link)
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

        self.sortChildren(0, QtCore.Qt.SortOrder.AscendingOrder)

    @qslot
    def _deletedNodeSlot(self, *args):
        """
        Removes the node from the view.
        """

        tree = self.treeWidget()
        if not sip_is_deleted(tree):
            parent = self.parent()
            if parent:
                parent.takeChild(parent.indexOfChild(self))
            else:
                tree.takeTopLevelItem(tree.indexOfTopLevelItem(self))
            tree.nodes_id.discard(self._node.id())
            tree._node_items.pop(self._node.id(), None)
            tree.refreshGroupVisibility()

    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        return natural_sort_key(str(self.text(column))) < natural_sort_key(str(otherItem.text(column)))


class TopologyGroupItem(QtWidgets.QTreeWidgetItem):
    """A summary row for the same persistent container used by the canvas."""

    def __init__(self, group):
        super().__init__()
        self.group = group
        self.setIcon(0, QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirIcon))
        self.setExpanded(True)

    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        return natural_sort_key(self.text(column)) < natural_sort_key(other.text(column))


class TopologySummaryView(QtWidgets.QTreeWidget):

    """
    Topology summary view implementation.

    :param parent: parent widget
    """

    def __init__(self, parent):

        super().__init__(parent)
        self.nodes_id = set()
        self._node_items = {}
        self._group_items = {}
        self._topology = Topology.instance()
        self._topology.node_added_signal.connect(self._nodeAddedSlot)
        self._topology.hierarchy_changed_signal.connect(self.refreshHierarchy)
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

    def clear(self):
        """Canvas reset also clears the tree directly, outside project signals."""
        super().clear()
        self.nodes_id.clear()
        self._node_items.clear()
        self._group_items.clear()

    def refreshAllLinks(self, source_child=None):
        """
        Refreshes all links for all items.
        """

        for child in list(self._node_items.values()):
            if source_child is not child:
                child.refreshLinks()
        self.refreshGroupVisibility()

    def refreshGroupVisibility(self):
        """Preserve existing capture/filter behavior within nested groups."""
        filtered = self.show_only_devices_with_capture or self.show_only_devices_with_filters

        def visible(row):
            if isinstance(row, TopologyGroupItem):
                children = [visible(row.child(index)) for index in range(row.childCount())]
                row.setHidden(bool(filtered and not any(children)))
            return not row.isHidden()
        for row in self._group_items.values():
            if row.parent() is None:
                visible(row)

    @qslot
    def refreshHierarchy(self, *args):
        """Reparent existing rows, retaining ports, expansion and selection."""
        from .main_window import MainWindow
        view = MainWindow.instance().uiGraphicsView
        if not isinstance(view, QtWidgets.QGraphicsView):
            return
        groups = {item.drawing_id(): item for item in view.scene().items() if isinstance(item, GroupItem)}
        nodes = {item.node().id(): item for item in view.scene().items() if isinstance(item, NodeItem)}
        blocker = QtCore.QSignalBlocker(self)
        current = self.currentItem()
        old_rows = list(self._group_items.values()) + list(self._node_items.values())
        expanded = {id(row): row.isExpanded() for row in old_rows}
        for row in old_rows:
            parent = row.parent()
            if parent:
                parent.takeChild(parent.indexOfChild(row))
            else:
                self.takeTopLevelItem(self.indexOfTopLevelItem(row))
        self._group_items = {identity: self._group_items.get(identity) or TopologyGroupItem(group)
                             for identity, group in groups.items()}
        for identity, row in self._group_items.items():
            group = groups[identity]
            row.group = group
            row.setText(0, group.name)
            row.setText(1, "Group")
            parent = group.parentItem()
            parent_row = self._group_items.get(parent.drawing_id()) if isinstance(parent, GroupItem) else None
            if parent_row:
                parent_row.addChild(row)
            else:
                self.addTopLevelItem(row)
        for identity, row in self._node_items.items():
            node = nodes.get(identity)
            parent = node.parentItem() if node else None
            parent_row = self._group_items.get(parent.drawing_id()) if isinstance(parent, GroupItem) else None
            if parent_row:
                parent_row.addChild(row)
            else:
                self.addTopLevelItem(row)
        for row in list(self._group_items.values()) + list(self._node_items.values()):
            row.setExpanded(expanded.get(id(row), isinstance(row, TopologyGroupItem)))
            row.sortChildren(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.invisibleRootItem().sortChildren(0, QtCore.Qt.SortOrder.AscendingOrder)
        if current and any(current is row for row in old_rows) and current.treeWidget() is self:
            self.setCurrentItem(current)
        self.refreshGroupVisibility()
        self.resizeColumnToContents(0)
        del blocker

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
        self._node_items[node.id()] = TopologyNodeItem(self, node)
        self.refreshHierarchy()
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
            if isinstance(current_item, TopologyGroupItem):
                self._selectGroup(current_item.group)
                return
            view._groups.leave()
            view.scene().clearSelection()
            for item in view.scene().items():
                if isinstance(item, NodeItem) and isinstance(current_item, TopologyNodeItem) and item.node().id() == current_item.node().id():
                    parent = item.parentItem()
                    if isinstance(parent, GroupItem):
                        view.enterGroup(parent)
                    item.setSelected(True)
                elif isinstance(item, LinkItem):
                    item.setHovered(False)
                    if not isinstance(current_item, TopologyNodeItem):
                        link = current_item.data(0, QtCore.Qt.ItemDataRole.UserRole)
                        if item.link() == link:
                            item.setHovered(True)

    def _selectGroup(self, group):
        from .main_window import MainWindow
        view = MainWindow.instance().uiGraphicsView
        view._groups.leave()
        view.scene().clearSelection()
        group.setSelected(True)

    def groupMenu(self, group):
        """Use the same validated operations as the canvas, including recursion."""
        from .main_window import MainWindow
        view = MainWindow.instance().uiGraphicsView
        menu = QtWidgets.QMenu(self)

        def run(callback):
            self._selectGroup(group)
            callback()
        for text, callback in (("Rename group", lambda: view.renameGroup(group)),
                               ("Duplicate", view.duplicateActionSlot),
                               ("Delete", view.deleteActionSlot)):
            menu.addAction(text).triggered.connect(lambda checked=False, callback=callback: run(callback))
        return menu

    @qslot
    def _itemDoubleClickedSlot(self, current_item, *args):
        """
        When user double click on an element we center the topology on it
        """
        if isinstance(current_item, TopologyGroupItem):
            from .main_window import MainWindow
            view = MainWindow.instance().uiGraphicsView
            if not args or args[0] == 0:
                view.renameGroup(current_item.group)
            else:
                view.centerOn(current_item.group)
            return
        if current_item != 0:
            from .main_window import MainWindow
            view = MainWindow.instance().uiGraphicsView
            for item in view.scene().items():
                if isinstance(item, NodeItem):
                    if isinstance(current_item, TopologyNodeItem) and item.node().id() == current_item.node().id():
                        view.centerOn(item)
                elif isinstance(item, LinkItem):
                    if not isinstance(current_item, TopologyNodeItem):
                        link = current_item.data(0, QtCore.Qt.ItemDataRole.UserRole)
                        if item.link() == link:
                            view.centerOn(item)

    def contextMenuEvent(self, event):
        """
        Handles all context menu events.

        :param event: QContextMenuEvent instance
        """

        row = self.itemAt(event.pos())
        if row:
            self.setCurrentItem(row)
        if isinstance(row, TopologyGroupItem):
            self.groupMenu(row.group).exec(event.globalPos())
        else:
            self._showContextualMenu(event.globalPos())

    def _showContextualMenu(self, pos):
        """
        Contextual menu to expand and collapse the tree.
        """

        menu = QtWidgets.QMenu(parent=self)
        expand_all = QtGui.QAction("Expand all", menu)
        expand_all.setIcon(get_icon("plus.svg"))
        expand_all.triggered.connect(self._expandAllSlot)
        menu.addAction(expand_all)

        collapse_all = QtGui.QAction("Collapse all", menu)
        collapse_all.setIcon(get_icon("minus.svg"))
        collapse_all.triggered.connect(self._collapseAllSlot)
        menu.addAction(collapse_all)

        if self.show_only_devices_with_capture is False and self.show_only_devices_with_filters is False:
            devices_with_capture = QtGui.QAction("Show devices with capture(s)", menu)
            devices_with_capture.setIcon(get_icon("inspect.svg"))
            devices_with_capture.triggered.connect(self._devicesWithCaptureSlot)
            menu.addAction(devices_with_capture)

            devices_with_filters = QtGui.QAction("Show devices with packet filter(s)", menu)
            devices_with_filters.setIcon(get_icon("filter.svg"))
            devices_with_filters.triggered.connect(self._devicesWithFiltersSlot)
            menu.addAction(devices_with_filters)

        else:
            show_all_devices = QtGui.QAction("Show all devices", menu)
            # show_all_devices.setIcon(QtGui.QIcon(":/icons/inspect.svg"))
            show_all_devices.triggered.connect(self._showAllDevicesSlot)
            menu.addAction(show_all_devices)

        stop_all_captures = QtGui.QAction("Stop all captures", menu)
        stop_all_captures.setIcon(get_icon("capture-stop.svg"))
        stop_all_captures.triggered.connect(self._stopAllCapturesSlot)
        menu.addAction(stop_all_captures)

        reset_all_filters = QtGui.QAction("Reset all packet filters", menu)
        reset_all_filters.setIcon(get_icon("filter-reset.svg"))
        reset_all_filters.triggered.connect(self._resetAllFiltersSlot)
        menu.addAction(reset_all_filters)

        resume_suspended_links = QtGui.QAction("Resume all suspended links", menu)
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
                link = current_item.data(0, QtCore.Qt.ItemDataRole.UserRole)
                for item in view.scene().items():
                    if isinstance(item, LinkItem) and item.link() == link:
                        item.populateLinkContextualMenu(menu)
                        break

        menu.exec(pos)

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
        if event.key() == QtCore.Qt.Key.Key_Delete:
            current_item = self.currentItem()
            if current_item is None:
                return
            if isinstance(current_item, TopologyGroupItem):
                self._selectGroup(current_item.group)
                view.deleteActionSlot()
                event.accept()
                return
            if isinstance(current_item, TopologyNodeItem):
                current_item.node().delete()
            else:
                link = current_item.data(0, QtCore.Qt.ItemDataRole.UserRole)
                for item in view.scene().items():
                    if isinstance(item, LinkItem) and item.link() == link:
                        item.delete()
        super().keyPressEvent(event)
