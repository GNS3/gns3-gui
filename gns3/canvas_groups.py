# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
"""Canvas hierarchy operations, separate from the legacy device command code."""

from .qt import QtCore, QtWidgets, sip
from .items.group_item import GroupItem, item_reference, reparent
from .items.node_item import NodeItem
from .items.drawing_item import DrawingItem


class CanvasGroups:
    def __init__(self, view):
        self.view = view
        self.editing = None
        self.restoring = False
        self._restore_pending = False

    def groups(self):
        return [item for item in self.view.scene().items() if isinstance(item, GroupItem)]

    def reset(self):
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
                QtWidgets.QMessageBox.warning(self.view, "Canvas groups", str(error))
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
                target = current
            current = current.parentItem()
        return target

    def add(self, name, items, parent=None, position=None):
        group = GroupItem(name=name.strip(), project=self.view._topology.project())
        self.view.scene().addItem(group)
        self.view._topology.addDrawing(group)
        if parent:
            reparent(group, parent)
        if position is None:
            bounds = items[0].sceneBoundingRect()
            for item in items[1:]:
                bounds = bounds.united(item.sceneBoundingRect())
            position = bounds.topLeft()
        from .items.group_item import set_scene_position
        set_scene_position(group, position)
        for item in items:
            item.setSelected(False)
            reparent(item, group)
        group.refreshBounds()
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
            QtWidgets.QMessageBox.warning(self.view, "Group", "Select items inside the same container.")
            return
        name, ok = QtWidgets.QInputDialog.getText(self.view, "Group", "Group name:")
        if not ok or not name.strip():
            return
        self.add(name, items, parent=items[0].parentItem())

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
            current.setEditing(True)
        self.editing = group
        self.view._main_window.uiStatusBar.showMessage(
            "Editing {} — coordinates relative to group origin; Esc to leave".format(group.name))

    def leave(self):
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

    def hasLocked(self, roots):
        for item in roots:
            members = [item] + (list(item.descendants()) if isinstance(item, GroupItem) else [])
            if any(getattr(child, "locked", lambda: False)() for child in members):
                QtWidgets.QMessageBox.warning(self.view, "Group", "Unlock the container and its children first.")
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
                        raise ValueError("Ambiguous imported group child")
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
                raise ValueError("Cyclic canvas group hierarchy")
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
                group.refreshBounds()
            for group in groups:
                if group not in owners:
                    attach(group)
        finally:
            self.restoring = False
        # GNS3 regenerates node/drawing IDs on portable import and Save As.
        # Repair references once, then return to strict ID-based ownership.
        for group in remapped:
            group._saved_id = group.drawing_id()
            group.updateDrawing()

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
        for item in all_items:
            if isinstance(item, GroupItem):
                copy = GroupItem(name=item.name, project=project)
                view.scene().addItem(copy)
                view._topology.addDrawing(copy)
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
                QtWidgets.QMessageBox.warning(view, "Duplicate group", "Could not duplicate every device; copies were rolled back.")
                return
            for original, copy in mapping.items():
                parent, local, _ = snapshots[original]
                if parent in mapping:
                    reparent(copy, mapping[parent], local)
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
