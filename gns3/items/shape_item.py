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
Base class for shape items (Rectangle, ellipse etc.).
"""

from ..qt import QtCore, QtGui


class ShapeItem:

    """
    Base class to draw shapes on the scene.
    """

    show_layer = False

    def __init__(self):

        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsFocusable | QtGui.QGraphicsItem.ItemIsSelectable)
        self.setAcceptsHoverEvents(True)
        self._border = 5
        self._edge = None

        from ..main_window import MainWindow
        self._graphics_view = MainWindow.instance().uiGraphicsView

    def keyPressEvent(self, event):
        """
        Handles all key press events

        :param event: QKeyEvent
        """

        key = event.key()
        modifiers = event.modifiers()
        if key in (QtCore.Qt.Key_P, QtCore.Qt.Key_Plus, QtCore.Qt.Key_Equal) and modifiers & QtCore.Qt.AltModifier \
                or key == QtCore.Qt.Key_Plus and modifiers & QtCore.Qt.AltModifier and modifiers & QtCore.Qt.KeypadModifier:
            if self.rotation() > -360.0:
                self.setRotation(self.rotation() - 1)
        elif key in (QtCore.Qt.Key_M, QtCore.Qt.Key_Minus) and modifiers & QtCore.Qt.AltModifier \
                or key == QtCore.Qt.Key_Minus and modifiers & QtCore.Qt.AltModifier and modifiers & QtCore.Qt.KeypadModifier:
            if self.rotation() < 360.0:
                self.setRotation(self.rotation() + 1)
        else:
            QtGui.QGraphicsItem.keyPressEvent(self, event)

    def mousePressEvent(self, event):
        """
        Handles all mouse press events.

        :param event: QMouseEvent instance
        """

        self.update()
        if event.pos().x() > (self.rect().right() - self._border):
            self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
            self._edge = "right"

        elif event.pos().x() < (self.rect().left() + self._border):
            self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
            self._edge = "left"

        elif event.pos().y() < (self.rect().top() + self._border):
            self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
            self._edge = "top"

        elif event.pos().y() > (self.rect().bottom() - self._border):
            self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
            self._edge = "bottom"

        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Handles all mouse release events.

        :param: QMouseEvent instance
        """

        self.update()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self._edge = None
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        Handles all mouse move events.

        :param event: QMouseEvent instance
        """

        self.update()
        if self._edge:
            r = self.rect()
            scenePos = event.scenePos()

            if self._edge == "top":
                diff = self.y() - scenePos.y()
                if r.height() - diff > 0:
                    self.setPos(self.x(), scenePos.y())
                    self.setRect(0, 0, self.rect().width(), self.rect().height() + diff)
                else:
                    self._edge = "bottom"
                    self.setPos(self.x(), self.y() + self.rect().height())
                    self.setRect(0, 0, self.rect().width(), diff - self.rect().height())
            elif self._edge == "left":
                diff = self.x() - scenePos.x()
                if r.width() - diff > 0:
                    self.setPos(scenePos.x(), self.y())
                    self.setRect(0, 0, r.width() + diff, self.rect().height())
                else:
                    self._edge = "right"
                    self.setPos(self.x() + self.rect().width(), self.y())
                    self.setRect(0, 0, diff - self.rect().width(), self.rect().height())
            elif self._edge == "bottom":
                if r.height() > 0:
                    pos = self.mapFromScene(scenePos)
                    self.setRect(0, 0, self.rect().width(), pos.y())
                else:
                    self.setRect(0, 0, self.rect().width(), abs(scenePos.y() - self.y()))
                    self.setPos(self.x(), scenePos.y())
                    self._edge = "top"
            elif self._edge == "right":
                if r.width() > 0:
                    pos = self.mapFromScene(scenePos)
                    self.setRect(0, 0, pos.x(), self.rect().height())
                else:
                    self.setRect(0, 0, abs(scenePos.x() - self.x()), self.rect().height())
                    self.setPos(scenePos.x(), self.y())
                    self._edge = "left"

        QtGui.QGraphicsItem.mouseMoveEvent(self, event)

    def hoverMoveEvent(self, event):
        """
        Handles all hover move events.

        :param event: QGraphicsSceneHoverEvent instance
        """

        # objects on the background layer don't need cursors
        if self.zValue() >= 0:
            if event.pos().x() > (self.rect().right() - self._border):
                self._graphics_view.setCursor(QtCore.Qt.SizeHorCursor)
            elif event.pos().x() < (self.rect().left() + self._border):
                self._graphics_view.setCursor(QtCore.Qt.SizeHorCursor)
            elif event.pos().y() < (self.rect().top() + self._border):
                self._graphics_view.setCursor(QtCore.Qt.SizeVerCursor)
            elif event.pos().y() > (self.rect().bottom() - self._border):
                self._graphics_view.setCursor(QtCore.Qt.SizeVerCursor)
            else:
                self._graphics_view.setCursor(QtCore.Qt.SizeAllCursor)

    def hoverLeaveEvent(self, event):
        """
        Handles all hover leave events.

        :param event: QGraphicsSceneHoverEvent instance
        """

        # objects on the background layer don't need cursors
        if self.zValue() >= 0:
            self._graphics_view.setCursor(QtCore.Qt.ArrowCursor)

    def drawLayerInfo(self, painter):
        """
        Draws the layer position.

        :param painter: QPainter instance
        """

        if self.show_layer is False:
            return

        brect = self.boundingRect()
        # don't draw anything if the object is too small
        if brect.width() < 20 or brect.height() < 20:
            return

        center = self.mapFromItem(self, brect.width() / 2.0, brect.height() / 2.0)
        painter.setBrush(QtCore.Qt.red)
        painter.setPen(QtCore.Qt.red)
        painter.drawRect((brect.width() / 2.0) - 10, (brect.height() / 2.0) - 10, 20, 20)
        painter.setPen(QtCore.Qt.black)
        zval = str(int(self.zValue()))
        painter.drawText(QtCore.QPointF(center.x() - 4, center.y() + 4), zval)

    def setZValue(self, value):
        """
        Sets a new Z value.

        :param value: Z value
        """

        QtGui.QGraphicsItem.setZValue(self, value)
        if self.zValue() < 0:
            self.setFlag(self.ItemIsSelectable, False)
            self.setFlag(self.ItemIsMovable, False)
        else:
            self.setFlag(self.ItemIsSelectable, True)
            self.setFlag(self.ItemIsMovable, True)

    def dump(self):
        """
        Returns a representation of this shape item.

        :returns: dictionary
        """

        shape_info = {"width": self.rect().width(),
                      "height": self.rect().height(),
                      "x": self.x(),
                      "y": self.y()}

        brush = self.brush()
        if brush.color() != QtCore.Qt.white:
            shape_info["color"] = brush.color().name()
        if brush.color().alpha() != 255:
            shape_info["transparency"] = brush.color().alpha()

        pen = self.pen()
        if pen.color() != QtCore.Qt.black:
            shape_info["border_color"] = pen.color().name()
        if pen.color().alpha() != 255:
            shape_info["border_transparency"] = pen.color().alpha()
        if pen.width() != 2:
            shape_info["border_width"] = pen.width()
        if pen.style() != QtCore.Qt.SolidLine:
            shape_info["border_style"] = pen.style()

        if self.rotation() != 0:
            shape_info["rotation"] = self.rotation()
        if self.zValue() != 0:
            shape_info["z"] = self.zValue()

        return shape_info

    def load(self, shape_info):
        """
        Loads a representation of this shape item.
        (from a topology file).

        :param shape_info: representation of the shape item (dictionary)
        """

        # load mandatory properties
        width = shape_info["width"]
        height = shape_info["height"]
        x = shape_info["x"]
        y = shape_info["y"]
        self.setRect(0, 0, width, height)
        self.setPos(x, y)

        # load optional properties
        z = shape_info.get("z")
        color = shape_info.get("color")
        transparency = shape_info.get("transparency")
        border_color = shape_info.get("border_color")
        border_transparency = shape_info.get("border_transparency")
        border_width = shape_info.get("border_width")
        border_style = shape_info.get("border_style")
        rotation = shape_info.get("rotation")

        if color:
            color = QtGui.QColor(color)
        else:
            color = QtGui.QColor(255, 255, 255)
        if transparency is not None:
            color.setAlpha(transparency)
        self.setBrush(QtGui.QBrush(color))

        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        if border_color:
            border_color = QtGui.QColor(border_color)
        else:
            border_color = pen.color()
        if border_transparency:
            border_color.setAlpha(border_transparency)
        pen.setColor(border_color)
        if border_width is not None:
            pen.setWidth(int(border_width))
        if border_style is not None:
            pen.setStyle(QtCore.Qt.PenStyle(border_style))
        self.setPen(pen)

        if rotation is not None:
            self.setRotation(rotation)
        if z is not None:
            self.setZValue(z)
