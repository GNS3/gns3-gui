# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
"""Canvas hierarchy operations, separate from the legacy device command code."""

from .qt import QtCore, QtGui, QtWidgets, sip
from .dialogs.group_properties_dialog import GroupPropertiesDialog
import math
from .items.group_item import GroupItem, item_reference, reparent
from .items.node_item import NodeItem
from .items.drawing_item import DrawingItem


class CanvasGroups:
    def __init__(self, view):
        self.view = view
        self.editing = None
        self.selection_pending = False
        self.selection_started = False
        self.restoring = False
        self._restore_pending = False
        self._resize = None
        self._drag_item = None
        self._drag_nodes = {}
        self._drag_targets = {}
        self._exit_groups = set()
        self._drag_hover_groups = set()
        self._outside_nodes = set()
        self.guide_parent = None
        self.drop_target = None

    def groups(self):
        return [item for item in self.view.scene().items() if isinstance(item, GroupItem)]

    def reset(self):
        self.selection_pending = False
        self.selection_started = False
        self.clearDropTarget()
        self.clearDrag()
        self._resize = None
        self.editing = None
        self._restore_pending = False

    def scheduleRestore(self):
        """Coalesce server notifications; never reattach halfway through a load."""
        if self._restore_pending:
            return
        self._restore_pending = True
        project = self.view._topology.project()

        def restore():
            self._restore_pending = False
            if sip.isdeleted(self.view) or self.view._topology.project() is not project:
                return
            try:
                self.restore()
            except ValueError as error:
                QtWidgets.QMessageBox.warning(self.view, "Canvas containers", str(error))
        QtCore.QTimer.singleShot(0, restore)

    def selected(self):
        """Topology selection only; never select both an ancestor and child."""
        items = {item for item in self.view.scene().selectedItems() if item_reference(item)}
        return [item for item in items if not any(parent.isAncestorOf(item) for parent in items)]

    def target(self, item):
        """Resolve clicks to the outermost closed container (labels included)."""
        target = item
        current = item.parentItem() if item else None
        while current is not None:
            if isinstance(current, GroupItem) and not current.editing:
                # Ancestors of the active container pass interaction through
                # without becoming additional editing containers themselves.
                if self.editing is None or not current.isAncestorOf(self.editing):
                    target = current
            current = current.parentItem()
        return target

    @staticmethod
    def initialGeometry(items):
        """Thirty percent extra in total (15% per side), plus the title row."""
        bounds = items[0].sceneBoundingRect()
        for item in items[1:]:
            bounds = bounds.united(item.sceneBoundingRect())
        margin_x = max(2, bounds.width() * .15)
        margin_y = max(2, bounds.height() * .15)
        position = bounds.topLeft() - QtCore.QPointF(margin_x, margin_y + GroupItem.TITLE_HEIGHT)
        return position, max(20, math.ceil(bounds.width() + 2 * margin_x)), max(20, math.ceil(bounds.height() + 2 * margin_y + GroupItem.TITLE_HEIGHT))

    def add(self, name, items, parent=None, position=None, width=None, height=None, style=None):
        initial_position, initial_width, initial_height = self.initialGeometry(items)
        group = GroupItem(name=name.strip(), width=width if width is not None else initial_width,
                          height=height if height is not None else initial_height,
                          project=self.view._topology.project())
        group.setStyle(style)
        self.view.scene().addItem(group)
        self.view._topology.addDrawing(group)
        if parent:
            reparent(group, parent)
        from .items.group_item import set_scene_position
        set_scene_position(group, initial_position if position is None else position)
        for item in items:
            item.setSelected(False)
            reparent(item, group)
        if group.style['shape'] != 'rect':
            group.fitMembers()
        group.setSelected(True)
        group.create()
        self.save([group])
        return group

    def group(self):
        items = self.selected()
        if not items:
            return
        parents = {item.parentItem() for item in items}
        if len(parents) != 1:
            QtWidgets.QMessageBox.warning(self.view, "Container", "Select items inside the same container.")
            return
        _, width, height = self.initialGeometry(items)
        result = GroupPropertiesDialog.getProperties(self.view, "Container", width, height)
        if result:
            name, width, height = result[:3]
            self.add(name, items, parent=items[0].parentItem(), width=width, height=height,
                     style=result[3] if len(result) > 3 else None)

    def requestGroup(self):
        """Group an existing selection, or wait for the next completed selection."""
        self.selection_pending = not bool(self.selected())
        if not self.selection_pending:
            self.group()
            return
        self.view.setFocus()
        self.view._main_window.uiStatusBar.showMessage("Select elements for the container; release the mouse to create it. Esc to cancel")

    def finishSelection(self):
        if self.selection_pending and self.selected():
            # Consume the request before opening a modal (which changes focus).
            self.selection_pending = False
            self.view._main_window.uiStatusBar.clearMessage()
            self.group()

    def rename(self, group):
        original = (group.name, group.rect().width(), group.rect().height(), dict(group.style))
        positions = {item: item.pos() for item in group.members()}

        def preview(values):
            name, width, height = values[:3]
            if len(values) > 3:
                group.setStyle(values[3], fit=False)
            group.name = name
            group.setToolTip(name)
            group.setDimensions(width, height)
            for item, position in positions.items():
                if not sip.isdeleted(item) and item.parentItem() is group:
                    reparent(item, group, position)
            if group.style['shape'] != original[3]['shape']:
                group.fitMembers()
            self.notifyHierarchy()

        result = GroupPropertiesDialog.getProperties(self.view, *original[:3], style=group.style, preview=preview)
        if result:
            preview(result)
            self.save([group])
        else:
            preview(original)  # Apply is a local preview, Cancel restores it.

    def notifyHierarchy(self):
        self.view._topology.hierarchy_changed_signal.emit()

    def clearDrag(self):
        self.clearDragFeedback()
        self._drag_item = None
        self._drag_nodes = {}
        self.guide_parent = None
        self.view.viewport().update()

    def beginDrag(self, item):
        self.clearDrag()
        if isinstance(item, QtWidgets.QGraphicsTextItem) and item.textInteractionFlags() & QtCore.Qt.TextInteractionFlag.TextEditorInteraction:
            return
        if item is not None and item_reference(item):
            parent = item.parentItem()
            editable = (parent is None and isinstance(item, NodeItem) or
                        isinstance(parent, GroupItem) and parent.editing)
            if editable and item.flags() & QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable:
                self._drag_item = item
                self._drag_nodes = {node: node.scenePos() for node in self.view.scene().selectedItems()
                                    if isinstance(node, NodeItem) and node.parentItem() is item.parentItem()}

    def clearDragFeedback(self):
        for group in self._exit_groups | self._drag_hover_groups:
            if not sip.isdeleted(group):
                group.exit_hover = False
                group.drop_hover = False
                group.update()
        self._exit_groups.clear()
        self._drag_hover_groups.clear()
        self._outside_nodes.clear()
        self._drag_targets.clear()

    def updateDrag(self):
        """Preview ownership changes without modifying the persisted hierarchy."""
        self.clearDragFeedback()
        for node, start in self._drag_nodes.items():
            if sip.isdeleted(node) or node.scene() is not self.view.scene() or node.scenePos() == start:
                continue
            parent = node.parentItem()
            center = node.mapToScene(node.boundingRect().center())
            if isinstance(parent, GroupItem) and not parent.shape().contains(parent.mapFromScene(center)):
                parent.exit_hover = True
                self._exit_groups.add(parent)
                self._outside_nodes.add(node)
                parent.update()
            destination = self.groupAt(center)
            self._drag_targets[node] = destination
            if destination is not None and destination is not parent:
                destination.drop_hover = True
                self._drag_hover_groups.add(destination)
                destination.update()
            if node is self._drag_item:
                self.guide_parent = destination
        self.view.viewport().update()

    def endDrag(self):
        """Commit the previewed parent on release, preserving position and links."""
        self.updateDrag()
        changed = []
        for node, destination in self._drag_targets.items():
            parent = node.parentItem()
            if destination is parent:
                continue
            reparent(node, destination)
            changed.append(node)
            if parent is not None:
                changed.append(parent)
        self.clearDrag()
        # Include an old parent that is now empty in the release's single save.
        return changed

    def drawDragPreviews(self, painter):
        """Paint the exiting symbol/labels outside ancestor clips, view-only.

        The actual device stays parented until release. Only the clipped-away
        pixels are painted here, leaving other overflowing children clipped.
        """
        for node in self._outside_nodes:
            if sip.isdeleted(node) or node.scene() is not self.view.scene():
                continue
            viewport = QtGui.QPainterPath()
            viewport.addPolygon(self.view.mapToScene(self.view.viewport().rect()))
            visible = viewport
            parent = node.parentItem()
            while isinstance(parent, GroupItem):
                visible = (visible.intersected(parent.mapToScene(parent.shape()))
                           if parent.flags() & QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape else visible)
                parent = parent.parentItem()
            painter.save()
            painter.setClipPath(viewport.subtracted(visible), QtCore.Qt.ClipOperation.IntersectClip)
            painter.setWorldTransform(node.sceneTransform(), True)

            def paint(item):
                if not item.isVisible():
                    return
                painter.save()
                painter.setOpacity(painter.opacity() * item.opacity())
                option = QtWidgets.QStyleOptionGraphicsItem()
                option.exposedRect = item.boundingRect()
                item.paint(painter, option)
                for child in sorted(item.childItems(), key=lambda child: child.zValue()):
                    painter.save()
                    painter.setWorldTransform(child.itemTransform(item)[0], True)
                    paint(child)
                    painter.restore()
                painter.restore()

            paint(node)
            painter.restore()

    def showGuides(self):
        item = self._drag_item
        if item is not None and not sip.isdeleted(item) and isinstance(item.parentItem(), GroupItem):
            self.guide_parent = item.parentItem()
            self.view.viewport().update()

    def snapPosition(self, item, value):
        if self.guide_parent is None or item is not self._drag_item or self.guide_parent is not item.parentItem():
            return value
        center = item.mapRectToParent(item.boundingRect()).center() - item.pos()
        target = self.guide_parent.rect().center()
        tolerance = 6 / max(.01, self.view.transform().m11())
        value = QtCore.QPointF(value)
        if abs(value.x() + center.x() - target.x()) <= tolerance:
            value.setX(target.x() - center.x())
        if abs(value.y() + center.y() - target.y()) <= tolerance:
            value.setY(target.y() - center.y())
        return value

    def drawGuides(self, painter):
        group = self.guide_parent
        if group is None or sip.isdeleted(group) or group.scene() is None:
            return
        painter.save()
        current = group
        while isinstance(current, GroupItem):
            path = current.mapToScene(current.shape())
            painter.setClipPath(path, QtCore.Qt.ClipOperation.IntersectClip)
            current = current.parentItem()
        pen = QtGui.QPen(QtGui.QColor("#e53935"), 0, QtCore.Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        painter.setPen(pen)
        rect = group.rect()
        center = rect.center()
        painter.drawLine(group.mapToScene(QtCore.QPointF(center.x(), 0)),
                         group.mapToScene(QtCore.QPointF(center.x(), rect.height())))
        painter.drawLine(group.mapToScene(QtCore.QPointF(0, center.y())),
                         group.mapToScene(QtCore.QPointF(rect.width(), center.y())))
        painter.restore()

    def groupAt(self, position):
        """The topmost visible container, including closed/nested groups."""
        for group in self.view.scene().items(position):
            if not isinstance(group, GroupItem):
                continue
            current = group
            eligible = True
            while isinstance(current, GroupItem):
                if current.locked() or not current.isVisible() or not current.shape().contains(current.mapFromScene(position)):
                    eligible = False
                    break
                current = current.parentItem()
            if eligible:
                return group
        return None

    def setDropTarget(self, position):
        target = self.groupAt(position)
        self.clearDropTarget()
        if target is not None:
            self.drop_target = target
            target.drop_hover = True
            self.guide_parent = target
            target.update()
            self.view.viewport().update()
        return target

    def clearDropTarget(self):
        old = self.drop_target
        self.drop_target = None
        if old is not None and not sip.isdeleted(old):
            old.drop_hover = False
            old.update()
        if self.guide_parent is old:
            self.guide_parent = None
        self.view.viewport().update()

    def resizeHandleAt(self, position):
        for group in self.groups():
            if not group.isSelected() or group.locked():
                continue
            # A nested group's handles cannot be reached through an ancestor's clip.
            ancestor = group.parentItem()
            visible = True
            while isinstance(ancestor, GroupItem):
                if not ancestor.shape().contains(ancestor.mapFromScene(position)):
                    visible = False
                    break
                ancestor = ancestor.parentItem()
            if not visible:
                continue
            screen = self.view.mapFromScene(position)
            for corner, point in group.corners().items():
                delta = self.view.mapFromScene(group.mapToScene(point)) - screen
                if max(abs(delta.x()), abs(delta.y())) <= 7:
                    return group, corner
        return None

    def beginResize(self, position):
        hit = self.resizeHandleAt(position)
        if hit is None:
            return False
        group, corner = hit
        self.clearDrag()
        self._resize = (group, corner, QtCore.QPointF(position), group.scenePos(), group.rect(),
                        [(child, child.pos()) for child in group.members()])
        return True

    def resizeTo(self, position):
        from .items.group_item import set_scene_position
        group, corner, start, origin, rect, members = self._resize
        delta = position - start
        left = min(delta.x(), rect.width() - GroupItem.MIN_SIZE) if "l" in corner else 0
        top = min(delta.y(), rect.height() - GroupItem.MIN_SIZE) if "t" in corner else 0
        right = max(GroupItem.MIN_SIZE, rect.width() + delta.x()) if "r" in corner else rect.width()
        bottom = max(GroupItem.MIN_SIZE, rect.height() + delta.y()) if "b" in corner else rect.height()
        offset = QtCore.QPointF(left, top)
        set_scene_position(group, origin + offset)
        for child, local in members:
            reparent(child, group, local - offset)
        group.setDimensions(min(1000000, right - left), min(1000000, bottom - top))

    def endResize(self):
        if self._resize is not None:
            group = self._resize[0]
            self._resize = None
            self.save([group])

    def ungroup(self):
        groups = [item for item in self.selected() if isinstance(item, GroupItem)]
        if self.hasLocked(groups):
            return
        self.leave()
        for group in groups:
            parent = group.parentItem()
            members = group.members()
            for child in members:
                reparent(child, parent)
                child.setSelected(True)
            group.delete()
            self.save(members)

    def enter(self, group):
        # To reach a nested container, enter its ancestors first.
        current = group
        while isinstance(current, GroupItem):
            if current.locked():
                return
            current = current.parentItem()
        self.leave()
        ancestors = []
        current = group
        while isinstance(current, GroupItem):
            ancestors.append(current)
            current = current.parentItem()
        self.view.scene().clearSelection()
        for current in ancestors:
            current.setEditing(current is group, allow_child_events=True)
        self.editing = group
        self.view._main_window.uiStatusBar.showMessage(
            "Editing {} — coordinates relative to group origin; Esc to leave".format(group.name))

    def leave(self):
        self.clearDrag()
        for group in self.groups():
            group.setEditing(False)
        self.editing = None

    def collapseSelection(self):
        """Normalize rubber-band/Ctrl+A selection to the current container level."""
        for item in list(self.view.scene().selectedItems()):
            if not item_reference(item):
                continue
            target = item
            parent = target.parentItem()
            while isinstance(parent, GroupItem) and parent is not self.editing:
                target = parent
                parent = target.parentItem()
            if target is not item:
                item.setSelected(False)
                target.setSelected(True)

    def save(self, roots=None):
        """Sync scene coordinates and local memberships after one user operation."""
        if self.restoring:
            return
        roots = self.selected() if roots is None else roots
        items = set()
        for root in roots:
            if sip.isdeleted(root) or root.scene() is not self.view.scene():
                continue
            items.add(root)
            if isinstance(root, GroupItem):
                items.update(root.descendants())
            parent = root.parentItem()
            while isinstance(parent, GroupItem):
                items.add(parent)
                parent = parent.parentItem()
        for item in items:
            if isinstance(item, NodeItem):
                item.updateNode()
            elif isinstance(item, DrawingItem) and not isinstance(item, GroupItem):
                item.updateDrawing()
        for item in items:
            if isinstance(item, GroupItem):
                item.refreshBounds()
                item.updateDrawing()
        self.notifyHierarchy()

    def hasLocked(self, roots):
        for item in roots:
            members = [item] + (list(item.descendants()) if isinstance(item, GroupItem) else [])
            if any(getattr(child, "locked", lambda: False)() for child in members):
                QtWidgets.QMessageBox.warning(self.view, "Container", "Unlock the container and its children first.")
                return True
        return False

    def restore(self):
        """Validate the whole graph before attaching any saved children.

        Drawing lists can arrive in arbitrary order. Dangling references are
        ignored (e.g. a device removed by another GUI); cycles and multiple
        ownership are rejected, rather than partially corrupting the canvas.
        """
        groups = self.groups()
        lookup = {item_reference(item): item for item in self.view.scene().items() if item_reference(item)}
        owners = {}
        edges = {}
        remapped = []
        for group in groups:
            edges[group] = []
            imported = group._saved_id is not None and group._saved_id != group.drawing_id()
            for member in group._members:
                child = lookup.get((member["type"], member["id"]))
                if child is None and imported and member.get("key"):
                    candidates = [item for (kind, _), item in lookup.items()
                                  if kind == member["type"] and
                                  (item.node().name() if kind == "node" else item._canvas_id) == member["key"]]
                    if len(candidates) > 1:
                        raise ValueError("Ambiguous imported container child")
                    child = candidates[0] if candidates else None
                if child is None:
                    continue
                if child in owners:
                    raise ValueError("A topology element has more than one parent")
                owners[child] = group
                edges[group].append((child, QtCore.QPointF(member["x"], member["y"])))
            if imported:
                remapped.append(group)
        visited, active = set(), set()

        def visit(group):
            if group in active:
                raise ValueError("Cyclic canvas container hierarchy")
            if group in visited:
                return
            active.add(group)
            for child, _ in edges[group]:
                if isinstance(child, GroupItem):
                    visit(child)
            active.remove(group)
            visited.add(group)

        for group in groups:
            visit(group)
        migrated = []
        self.restoring = True
        try:
            for group in groups:
                for child in group.members():
                    if owners.get(child) is not group:
                        reparent(child, None)
            # Parent groups first; each child's saved local position is applied
            # after its parent has been placed in the correct coordinate system.
            def attach(group):
                for child, position in edges[group]:
                    reparent(child, group, position)
                    if isinstance(child, GroupItem):
                        attach(child)
                if group.migrateLegacyBounds():
                    migrated.append(group)
                group.refreshBounds()
            for group in groups:
                if group not in owners:
                    attach(group)
        finally:
            self.restoring = False
        # GNS3 regenerates node/drawing IDs on portable import and Save As.
        # Repair references once, then return to strict ID-based ownership.
        for group in set(remapped + migrated):
            group._saved_id = group.drawing_id()
            group.updateDrawing()
        self.notifyHierarchy()

    def duplicate(self, roots):
        """Copy the complete tree, remapping every node/drawing/group identity.

        Node duplication is asynchronous. Do not persist group membership until
        all device IDs are known, and recreate only links internal to the copy.
        """
        from .items.group_item import scene_z
        view = self.view
        project = view._topology.project()
        offset = QtCore.QPointF(20, 20)
        mapping, pending, failed = {}, [], []
        all_items = []
        for root in roots:
            all_items.append(root)
            if isinstance(root, GroupItem):
                all_items.extend(root.descendants())
        internal_links = [link for link in view._topology.links()
                          if any(isinstance(item, NodeItem) and item.node() is link.sourceNode() for item in all_items)
                          and any(isinstance(item, NodeItem) and item.node() is link.destinationNode() for item in all_items)]
        snapshots = {item: (item.parentItem(), item.pos(), item.scenePos()) for item in all_items}
        names = {group.name for group in self.groups()}
        for item in all_items:
            if isinstance(item, GroupItem):
                name = item.name
                if item in roots:
                    # Rename only selected roots; nested names describe the
                    # copied hierarchy and can remain unchanged.
                    name = "Copy of " + item.name
                    number = 2
                    while name in names:
                        name = "Copy {} of {}".format(number, item.name)
                        number += 1
                    names.add(name)
                copy = GroupItem(name=name, project=project, width=item.rect().width(), height=item.rect().height())
                view.scene().addItem(copy)
                view._topology.addDrawing(copy)
                copy.setStyle(item.style)
                copy.setPos(item.scenePos() + offset)
                copy.setZValue(scene_z(item))
                copy.setLocked(item.locked())
                mapping[item] = copy
            elif isinstance(item, DrawingItem):
                kind = view.drawingType(item)
                copy = view.createDrawingItem(kind, item.scenePos().x() + 20,
                                              item.scenePos().y() + 20, scene_z(item),
                                              rotation=item.rotation(), locked=item.locked(), svg=item.toSvg(), create=False)
                mapping[item] = copy
            elif isinstance(item, NodeItem):
                pending.append(item)
        remaining = len(pending)

        def finish():
            if view._topology.project() is not project:
                return
            if failed:
                # There is no server transaction for multi-node duplication.
                # Roll back successful copies rather than leaving a partial LAN.
                for copy in mapping.values():
                    if isinstance(copy, NodeItem):
                        copy.node().delete()
                        view._topology.removeNode(copy.node())
                    else:
                        view._topology.removeDrawing(copy)
                        if copy.scene():
                            copy.scene().removeItem(copy)
                QtWidgets.QMessageBox.warning(view, "Duplicate container", "Could not duplicate every device; copies were rolled back.")
                return
            for original, copy in mapping.items():
                parent, local, _ = snapshots[original]
                if parent in mapping:
                    reparent(copy, mapping[parent], local)
                elif isinstance(parent, GroupItem) and not sip.isdeleted(parent) and parent.scene() is view.scene():
                    # Duplicating a nested group/drawing creates a sibling in
                    # that same container, including from the summary panel.
                    reparent(copy, parent, local + offset)
            for original, copy in mapping.items():
                if isinstance(copy, DrawingItem):
                    copy.create()
            # Recreate internal network connections, not external connections.
            node_map = {item.node().node_id(): copy.node() for item, copy in mapping.items() if isinstance(item, NodeItem)}
            for link in internal_links:
                source = node_map[link.sourceNode().node_id()]
                destination = node_map[link.destinationNode().node_id()]
                source_port = next((port for port in source.ports() if port.adapterNumber() == link.sourcePort().adapterNumber()
                                    and port.portNumber() == link.sourcePort().portNumber()), None)
                destination_port = next((port for port in destination.ports() if port.adapterNumber() == link.destinationPort().adapterNumber()
                                         and port.portNumber() == link.destinationPort().portNumber()), None)
                if source_port and destination_port:
                    view.addLink(source, source_port, destination, destination_port)
            view.scene().clearSelection()
            copies = [mapping[root] for root in roots]
            for copy in copies:
                copy.setSelected(True)
            self.save(copies)

        def duplicated(original, result, error=False):
            nonlocal remaining
            if view._topology.project() is not project:
                return
            if error:
                failed.append(original)
            else:
                identity = result["node_id"]
                node = view._topology.getNodeFromUuid(identity)
                if node is None:
                    view._topology.createNode(result)
                copy = next((item for item in view.scene().items()
                             if isinstance(item, NodeItem) and item.node().node_id() == identity), None)
                if copy is None:
                    failed.append(original)
                else:
                    mapping[original] = copy
            remaining -= 1
            if not remaining:
                finish()

        for item in pending:
            item.node().duplicate(item.scenePos().x() + 20, item.scenePos().y() + 20, scene_z(item),
                                  callback=lambda result, error=False, original=item: duplicated(original, result, error))
        if not pending:
            finish()
