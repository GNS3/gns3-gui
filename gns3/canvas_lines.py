# SPDX-License-Identifier: GPL-3.0-or-later
"""Two-click visual lines and viewport-sized endpoint hit areas.

This controller is independent of containers. When CanvasGroups is installed,
its selection/clip rules and persistence remain authoritative.
"""

from .qt import QtCore, QtGui, QtWidgets, sip_is_deleted
from .items.line_item import LineItem
from .dialogs.line_properties_dialog import LinePropertiesDialog


class CanvasLines:
    def __init__(self, view):
        self.view = view
        self.preview = None
        self.origin = None
        self._resize = None
        self._consumed_button = None
        self._cancelled_context = False
        self._moving = False
        self._hovering_endpoint = False
        if hasattr(view, "navigationModeChanged"):
            view.navigationModeChanged.connect(self.navigationChanged)

    def navigationChanged(self, mode):
        if self.view._adding_line:
            self.cancel()

    def restoreCursor(self):
        if hasattr(self.view, "setNavigationMode"):
            self.view.setNavigationMode(self.view._navigation_mode)
        else:
            self.view.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

    def cancel(self):
        if self.preview is not None and self.preview.scene() is not None:
            self.preview.scene().removeItem(self.preview)
        self.preview = None
        self.origin = None
        self.view._adding_line = False
        self.view._main_window.uiDrawLineAction.setChecked(False)
        self.restoreCursor()

    def reset(self):
        self.cancel()
        self._resize = None
        self._consumed_button = None
        self._moving = False
        self._cancelled_context = False
        self._hovering_endpoint = False

    def save(self, items):
        groups = getattr(self.view, "_groups", None)
        if groups is not None:
            groups.save(items)
        else:
            for item in items:
                item.updateDrawing()

    def edit(self, items):
        items = [item for item in items if not item.locked()]
        if items and LinePropertiesDialog(self.view, items).exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.save([item for item in items if not sip_is_deleted(item) and item.scene() is self.view.scene()])

    def endpointAt(self, position):
        groups = getattr(self.view, "_groups", None)
        for item in self.view.scene().items():
            if not isinstance(item, LineItem) or not item.isSelected() or not item.isVisible() or item.locked():
                continue
            if groups is not None and groups.target(item) is not item:
                continue
            ancestor = item.parentItem()
            while ancestor is not None:
                if getattr(ancestor, "locked", lambda: False)():
                    break
                if (ancestor.flags() & QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape and
                        not ancestor.shape().contains(ancestor.mapFromScene(position))):
                    break
                ancestor = ancestor.parentItem()
            if ancestor is not None:
                continue
            pixel = self.view.mapFromScene(position)
            endpoints = (item.line().p1(), item.line().p2())
            distances = [(self.view.mapFromScene(item.mapToScene(point)) - pixel).manhattanLength()
                         for point in endpoints]
            index = 0 if distances[0] <= distances[1] else 1
            delta = self.view.mapFromScene(item.mapToScene(endpoints[index])) - pixel
            if max(abs(delta.x()), abs(delta.y())) <= 7:
                return item, index
        return None

    def press(self, event):
        if self._resize is not None:
            # A second button must not turn an endpoint drag into selection or
            # lose the left-button release that commits it.
            event.accept()
            return True
        self._consumed_button = None
        self._cancelled_context = False
        self._moving = False
        button = event.button()
        position = self.view.mapToScene(event.position().toPoint())
        if self.view._adding_line:
            if button not in (QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.MouseButton.RightButton):
                return False
            self._consumed_button = button
            if button == QtCore.Qt.MouseButton.RightButton:
                self._cancelled_context = True
                self.cancel()
            elif self.origin is None:
                # A container's blank editing background is also an empty area.
                groups = getattr(self.view, "_groups", None)
                item = self.view.itemAt(event.position().toPoint())
                if item is None or (groups is not None and item is groups.editing):
                    self.origin = position
                    self.preview = QtWidgets.QGraphicsLineItem(QtCore.QLineF(position, position))
                    pen = QtGui.QPen(QtGui.QColor("#3484c6"), 2, QtCore.Qt.PenStyle.DashLine)
                    pen.setCosmetic(True)
                    self.preview.setPen(pen)
                    self.preview.setAcceptedMouseButtons(QtCore.Qt.MouseButton.NoButton)
                    self.preview.setZValue(1000000)
                    marker = QtWidgets.QGraphicsEllipseItem(-3, -3, 6, 6, self.preview)
                    marker.setPos(position)
                    marker.setBrush(QtGui.QColor("#3484c6"))
                    marker.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
                    marker.setAcceptedMouseButtons(QtCore.Qt.MouseButton.NoButton)
                    self.view.scene().addItem(self.preview)
            elif QtCore.QLineF(self.origin, position).length() > .001:
                start = QtCore.QPointF(self.origin)
                self.cancel()  # Consume the tool before opening a modal/focus change.
                item = self.view.createDrawingItem("line", start.x(), start.y(), 1, create=False)
                allowed = item._allow_snap_to_grid
                item._allow_snap_to_grid = False
                item.setPos(start)
                item._allow_snap_to_grid = allowed
                item.setLine(QtCore.QLineF(QtCore.QPointF(), position - start))
                self.view.scene().clearSelection()
                item.setSelected(True)
                if LinePropertiesDialog(self.view, [item]).exec() == QtWidgets.QDialog.DialogCode.Accepted:
                    item.create()
                else:
                    self.view.discardDraft(item)
            event.accept()
            return True
        adding = any((self.view._adding_link, self.view._adding_note,
                      self.view._adding_rectangle, self.view._adding_ellipse))
        if (adding or self.view._dragging or button != QtCore.Qt.MouseButton.LeftButton or
                event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier):
            return False
        groups = getattr(self.view, "_groups", None)
        if groups is not None and groups.resizeHandleAt(position):
            return False  # Existing container corner priority is unchanged.
        hit = self.endpointAt(position)
        if hit:
            item, index = hit
            inverse, invertible = item.sceneTransform().inverted()
            if invertible:
                if groups is not None:
                    groups.clearDrag()
                self._resize = (item, index, QtCore.QLineF(item.line()), inverse, position)
                self._consumed_button = button
                self.view.setCursor(QtCore.Qt.CursorShape.CrossCursor)
                event.accept()
                return True
        self._moving = isinstance(self.view.itemAt(event.position().toPoint()), LineItem)
        return False

    def move(self, event):
        position = self.view.mapToScene(event.position().toPoint())
        if self._resize is not None:
            item, index, original, inverse, start = self._resize
            if not sip_is_deleted(item) and item.scene() is self.view.scene():
                delta = inverse.map(position) - inverse.map(start)
                line = QtCore.QLineF(original)
                if index == 0:
                    line.setP1(original.p1() + delta)
                else:
                    line.setP2(original.p2() + delta)
                item.setLine(line)
            event.accept()
            return True
        if self.view._adding_line:
            if self.preview is not None:
                self.preview.setLine(QtCore.QLineF(self.origin, position))
            self.view.setCursor(QtCore.Qt.CursorShape.CrossCursor)
            event.accept()
            return True
        if not event.buttons() and not any((self.view._adding_link, self.view._adding_note,
                                           self.view._adding_rectangle, self.view._adding_ellipse)):
            groups = getattr(self.view, "_groups", None)
            if (groups is None or not groups.resizeHandleAt(position)) and self.endpointAt(position):
                self._hovering_endpoint = True
                self.view.setCursor(QtCore.Qt.CursorShape.CrossCursor)
                event.accept()
                return True
            if self._hovering_endpoint:
                self._hovering_endpoint = False
                self.restoreCursor()
        return False

    def endResize(self):
        if self._resize is not None:
            item = self._resize[0]
            self._resize = None
            if not sip_is_deleted(item) and item.scene() is self.view.scene():
                self.save([item])
            self.restoreCursor()

    def release(self, event):
        if self._resize is not None and event.button() != QtCore.Qt.MouseButton.LeftButton:
            event.accept()
            return True
        if event.button() == self._consumed_button:
            self._consumed_button = None
            self.endResize()
            event.accept()
            return True
        return False

    def finishMove(self):
        if self._moving and getattr(self.view, "_groups", None) is None:
            self.save([item for item in self.view.scene().selectedItems() if isinstance(item, LineItem) and not item.locked()])
        self._moving = False

    def contextMenu(self, event):
        if self._cancelled_context and event.reason() == QtGui.QContextMenuEvent.Reason.Mouse:
            self._cancelled_context = False
            event.accept()
            return True
        return False

    def focusOut(self):
        if self.view._adding_line:
            self.cancel()
        self.endResize()
