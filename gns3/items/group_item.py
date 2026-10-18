# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
"""Named topology containers, persisted through the existing drawing transport.

The server still receives scene coordinates for ordinary nodes/drawings. The
versioned SVG metadata on a group records *local* coordinates and stable child
IDs, allowing the GUI to reconstruct actual Qt parent/child relationships after
loading/importing a project. No client-only sidecar files are involved.
"""

import json
import math
import xml.etree.ElementTree as ET

from ..qt import QtCore, QtGui, QtWidgets
from .drawing_item import DrawingItem

GROUP_METADATA = "gns3-canvas-group"
GROUP_VERSION = 1
ITEM_METADATA = "gns3-canvas-item"


def drawing_identity(svg):
    root = ET.fromstring(svg)
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] == "metadata" and element.get("id") == ITEM_METADATA:
            return element.text
    return None


def with_identity(svg, identity):
    """Keep a drawing identity when the server regenerates IDs on import."""
    end = svg.rfind("</svg>")
    if end < 0:
        return svg
    # Replace rather than accumulate metadata when updating an image renderer.
    start = svg.find('<metadata id="{}">'.format(ITEM_METADATA))
    if start >= 0:
        stop = svg.find("</metadata>", start)
        if stop >= 0:
            svg = svg[:start] + svg[stop + len("</metadata>"):]
            end = svg.rfind("</svg>")
    metadata = ET.Element("metadata", {"id": ITEM_METADATA})
    metadata.text = identity
    return svg[:end] + ET.tostring(metadata, encoding="unicode") + svg[end:]


def item_reference(item):
    """Only topology objects have identities; labels belong to their owner."""
    from .node_item import NodeItem
    if isinstance(item, NodeItem):
        return "node", item.node().node_id()
    if isinstance(item, DrawingItem):
        return "group" if isinstance(item, GroupItem) else "drawing", item.drawing_id()
    return None


def scene_z(item):
    value = item.zValue()
    parent = item.parentItem()
    while isinstance(parent, GroupItem):
        value += parent.zValue()
        parent = parent.parentItem()
    return value


def set_scene_position(item, position):
    """Apply an API position without confusing scene and parent coordinates."""
    parent = item.parentItem()
    local = parent.mapFromScene(position) if parent else position
    # API acknowledgments and reparenting must never snap a second time.
    allowed = getattr(item, "_allow_snap_to_grid", True)
    item._allow_snap_to_grid = False
    try:
        item.setPos(local)
    finally:
        item._allow_snap_to_grid = allowed


def reparent(item, parent, local_position=None):
    """Preserve the scene transform, or restore an explicitly stored local pos.

    Containers only translate. Rotation/scale stay on the individual drawing;
    changing a parent must not change its appearance or snap it to a new grid.
    """
    if item is parent or (parent and item.isAncestorOf(parent)):
        raise ValueError("A group cannot contain itself or an ancestor")
    old_parent = item.parentItem()
    position = item.scenePos()
    z = scene_z(item)
    allowed = getattr(item, "_allow_snap_to_grid", True)
    item._allow_snap_to_grid = False
    try:
        item.setParentItem(parent)
        item.setPos(local_position if local_position is not None else
                    (parent.mapFromScene(position) if parent else position))
        item.setZValue(z - (scene_z(parent) if parent else 0))
    finally:
        item._allow_snap_to_grid = allowed
    if isinstance(old_parent, GroupItem):
        old_parent.refreshBounds()
    if isinstance(parent, GroupItem):
        parent.refreshBounds()


def read_group(svg):
    """Decode and validate our extension, leaving ordinary SVGs untouched.

    IDs are references, never file paths or executable code. Unknown versions,
    duplicate members and malformed numbers are rejected before reparenting.
    """
    root = ET.fromstring(svg)
    metadata = next((element for element in root.iter()
                     if element.tag.rsplit("}", 1)[-1] == "metadata"
                     and element.get("id") == GROUP_METADATA), None)
    if metadata is None:
        return None
    data = json.loads(metadata.text or "")
    if not isinstance(data, dict) or data.get("version") != GROUP_VERSION:
        raise ValueError("Unsupported canvas group version")
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        raise ValueError("A canvas group must have a name")
    if not isinstance(data.get("children"), list):
        raise ValueError("A canvas group must have a children list")
    if any(not isinstance(data.get(key), str) or not data[key] for key in ("drawing_id", "identity")):
        raise ValueError("Invalid canvas group identity")
    revision = data.get("revision", 0)
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise ValueError("Invalid canvas group revision")
    origin = data.get("origin")
    if not isinstance(origin, dict) or any(
        isinstance(origin.get(axis), bool) or not isinstance(origin.get(axis), (int, float))
        or not math.isfinite(origin[axis]) for axis in ("x", "y")
    ):
        raise ValueError("Invalid canvas group origin")
    seen = set()
    for child in data["children"]:
        if not isinstance(child, dict) or child.get("type") not in ("node", "drawing", "group"):
            raise ValueError("Invalid canvas group child")
        if not isinstance(child.get("id"), str) or not child["id"] or child["id"] in seen:
            raise ValueError("Invalid or duplicate child ID")
        seen.add(child["id"])
        if "key" in child and not isinstance(child["key"], str):
            raise ValueError("Invalid portable child identity")
        for coordinate in ("x", "y"):
            value = child.get(coordinate)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("Invalid canvas group coordinate")
    return data


class GroupItem(QtWidgets.QGraphicsRectItem, DrawingItem):
    """A drawable container whose direct children use its origin as (0, 0)."""

    def __init__(self, name="Group", svg=None, **kwargs):
        self.name = name
        self._members = []
        self._origin = QtCore.QPointF()
        self._saved_id = None
        self._revision = 0
        self._ready = False
        self.editing = False
        super().__init__(**kwargs)
        self._ready = True
        self.setFiltersChildEvents(True)
        self.setToolTip(name)
        if svg:
            self.fromSvg(svg)
        self.refreshBounds()

    def create(self):
        self._revision += 1
        self._members = read_group(self.toSvg())["children"]
        self._saved_id = self.drawing_id()
        super().create()

    def updateDrawing(self):
        self._revision += 1
        # Notifications may arrive before this HTTP request is acknowledged.
        # Keep the current local graph authoritative during that interval.
        self._members = read_group(self.toSvg())["children"]
        self._saved_id = self.drawing_id()
        super().updateDrawing()

    def updateDrawingCallback(self, result, error=False, **kwargs):
        if not error and "svg" in result:
            try:
                data = read_group(result["svg"])
                if data is None or data.get("revision", 0) < self._revision:
                    return
            except (ValueError, TypeError, ET.ParseError) as invalid:
                QtWidgets.QMessageBox.warning(self._graphics_view, "Canvas group", str(invalid))
                return
        DrawingItem.updateDrawingCallback(self, result, error, **kwargs)
        if error:
            QtWidgets.QMessageBox.warning(self._graphics_view, "Canvas group", result.get("message", "Could not save group"))

    def members(self):
        return [child for child in self.childItems() if item_reference(child)]

    def descendants(self):
        for child in self.members():
            yield child
            if isinstance(child, GroupItem):
                yield from child.descendants()

    def refreshBounds(self):
        if not self._ready:
            return
        bounds = self.childrenBoundingRect()
        if bounds.isEmpty():
            bounds = QtCore.QRectF(0, 0, 120, 60)
        # Leave room for the name without changing the local coordinate origin.
        width = QtGui.QFontMetricsF(QtGui.QFont()).horizontalAdvance(self.name) + 16
        rect = bounds.adjusted(-12, -30, 12, 12)
        rect.setWidth(max(rect.width(), width))
        self.setRect(rect)
        parent = self.parentItem()
        if isinstance(parent, GroupItem):
            parent.refreshBounds()

    def paint(self, painter, option, widget=None):
        painter.save()
        color = QtGui.QColor("#3484c6")
        painter.setPen(QtGui.QPen(color, 2 if self.isSelected() else 1,
                                  QtCore.Qt.PenStyle.DashLine))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect())
        label = self.rect().adjusted(6, 2, -6, 0)
        painter.drawText(label, QtCore.Qt.AlignmentFlag.AlignLeft |
                         QtCore.Qt.AlignmentFlag.AlignTop,
                         self.name + (" [editing]" if self.editing else ""))
        painter.restore()

    def setEditing(self, editing):
        self.editing = editing
        self.setFiltersChildEvents(not editing)
        self.update()

    def sceneEventFilter(self, watched, event):
        # A closed container owns mouse interaction with its descendants. Keep
        # the original scene positions, but translate item-local event positions
        # before invoking Qt's normal selection and multiple-item drag handlers.
        handlers = {
            QtCore.QEvent.Type.GraphicsSceneMousePress: QtWidgets.QGraphicsItem.mousePressEvent,
            QtCore.QEvent.Type.GraphicsSceneMouseMove: QtWidgets.QGraphicsItem.mouseMoveEvent,
            QtCore.QEvent.Type.GraphicsSceneMouseRelease: QtWidgets.QGraphicsItem.mouseReleaseEvent,
        }
        if event.type() == QtCore.QEvent.Type.GraphicsSceneMouseDoubleClick:
            self._graphics_view.enterGroup(self)
            event.accept()
            return True
        handler = handlers.get(event.type())
        if handler:
            event.setPos(self.mapFromScene(event.scenePos()))
            handler(self, event)
            return True
        if event.type() == QtCore.QEvent.Type.GraphicsSceneContextMenu:
            self.setSelected(True)
            event.accept()
            return True
        return False

    def mouseDoubleClickEvent(self, event):
        self._graphics_view.enterGroup(self)
        event.accept()

    def itemChange(self, change, value):
        if not self._ready:
            return QtWidgets.QGraphicsItem.itemChange(self, change, value)
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange and self._allow_snap_to_grid:
            if self.locked() or any(getattr(child, "locked", lambda: False)() for child in self.descendants()):
                return self.pos()
        if change in (QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged,
                      QtWidgets.QGraphicsItem.GraphicsItemChange.ItemZValueHasChanged):
            for child in self.descendants():
                from .node_item import NodeItem
                if isinstance(child, NodeItem):
                    for link in child.links():
                        link.adjust()
            parent = self.parentItem()
            if isinstance(parent, GroupItem):
                parent.refreshBounds()
        # A container has one origin, independent of its children's centers.
        # Its own translation is not snapped again for each child.
        return QtWidgets.QGraphicsItem.itemChange(self, change, value)

    def toSvg(self):
        children = []
        for item in sorted(self.members(), key=lambda child: item_reference(child)):
            kind, identity = item_reference(item)
            key = item.node().name() if kind == "node" else item._canvas_id
            children.append({"type": kind, "id": identity, "key": key, "x": item.x(), "y": item.y()})
        root = ET.Element("svg", {"xmlns": "http://www.w3.org/2000/svg",
                                  "width": str(max(1, self.rect().right())),
                                  "height": str(max(1, self.rect().bottom()))})
        metadata = ET.SubElement(root, "metadata", {"id": GROUP_METADATA})
        metadata.text = json.dumps({"version": GROUP_VERSION, "revision": self._revision, "name": self.name,
                                    "drawing_id": self.drawing_id(), "identity": self._canvas_id,
                                    "origin": {"x": self.scenePos().x(), "y": self.scenePos().y()},
                                    "children": children}, ensure_ascii=False, allow_nan=False)
        # An older GUI can still render the name, even without understanding
        # containers. Topology node/drawing coordinates remain useful to it.
        text = ET.SubElement(root, "text", {"x": "0", "y": "16", "fill": "#3484c6"})
        text.text = self.name
        return ET.tostring(root, encoding="unicode")

    def fromSvg(self, svg):
        data = read_group(svg)
        if data is None:
            raise ValueError("Missing canvas group metadata")
        self.name = data["name"].strip()
        self._revision = data.get("revision", 0)
        self._saved_id = data.get("drawing_id")
        self._canvas_id = data.get("identity", self.drawing_id())
        self._members = data["children"]
        self._origin = QtCore.QPointF(data["origin"]["x"], data["origin"]["y"])
        set_scene_position(self, self._origin)
        self.setToolTip(self.name)
        self.refreshBounds()

    def setRotation(self, rotation):
        # Container axes stay parallel to the canvas; children retain rotations.
        if rotation:
            raise ValueError("Canvas groups support translation, not rotation")
        super().setRotation(rotation)
