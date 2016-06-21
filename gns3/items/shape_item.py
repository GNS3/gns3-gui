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

from ..qt import QtCore, QtGui, QtWidgets, QtSvg

import logging
log = logging.getLogger(__name__)


class ShapeItem:

    """
    Base class to draw shapes on the scene.
    """

    show_layer = False

    def __init__(self, project=None, **kws):

        assert project is not None
        self._id = None
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsFocusable | QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self._border = 5
        self._edge = None

        from ..main_window import MainWindow
        self._graphics_view = MainWindow.instance().uiGraphicsView

        self._project = project

    def createShapeOnController(self):
        if self._id is None:
            self._project.post("/shapes", self._createShapeCallback, body=self.__json__())

    def _createShapeCallback(self, result, error=False, **kwargs):
        """
        Callback for create.

        :param result: server response
        :param error: indicates an error (boolean)
        :returns: Boolean success or not
        """

        if error:
            log.error("Error while setting up shape: {}".format(result["message"]))
            return False
        self._id = result["shape_id"]

    def updateShapeOnController(self):
        if self._id:
            self._project.put("/shapes/" + self._id, None, body=self.__json__())

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
            QtWidgets.QGraphicsItem.keyPressEvent(self, event)

    def mousePressEvent(self, event):
        """
        Handles all mouse press events.

        :param event: QMouseEvent instance
        """

        self.update()
        if event.pos().x() > (self.rect().right() - self._border):
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
            self._edge = "right"

        elif event.pos().x() < (self.rect().left() + self._border):
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
            self._edge = "left"

        elif event.pos().y() < (self.rect().top() + self._border):
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
            self._edge = "top"

        elif event.pos().y() > (self.rect().bottom() - self._border):
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
            self._edge = "bottom"

        QtWidgets.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Handles all mouse release events.

        :param: QMouseEvent instance
        """

        self.update()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self._edge = None
        QtWidgets.QGraphicsItem.mouseReleaseEvent(self, event)

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

        QtWidgets.QGraphicsItem.mouseMoveEvent(self, event)

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

    def delete(self):
        """
        Deletes this rectangle.
        """

        self.scene().removeItem(self)
        from ..topology import Topology
        Topology.instance().removeShape(self)

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

        QtWidgets.QGraphicsItem.setZValue(self, value)
        if self.zValue() < 0:
            self.setFlag(self.ItemIsSelectable, False)
            self.setFlag(self.ItemIsMovable, False)
        else:
            self.setFlag(self.ItemIsSelectable, True)
            self.setFlag(self.ItemIsMovable, True)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            if not value:
                self.updateShapeOnController()
        return QtWidgets.QGraphicsItem.itemChange(self, change, value)

    def _styleSvg(self, element):
        """
        Add style from the shape item to the SVG element that we will
        export
        """
        style = ""
        pen = self.pen()
        style += "stroke-width:{};".format(pen.width())
        style += "stroke:#{};".format(hex(pen.color().rgba())[4:])

        if pen.style() == QtCore.Qt.SolidLine:
            pass
        elif pen.style() == QtCore.Qt.NoPen:
            style = ""
        elif pen.style() == QtCore.Qt.DashLine:
            element.set("stroke-dasharray", "25, 25")
        elif pen.style() == QtCore.Qt.DotLine:
            element.set("stroke-dasharray", "5, 25")
        elif pen.style() == QtCore.Qt.DashDotLine:
            element.set("stroke-dasharray", "5, 25, 25")
        elif pen.style() == QtCore.Qt.DashDotDotLine:
            element.set("stroke-dasharray", "25, 25, 5, 25, 5")

        style += "fill:#{};".format(hex(self.brush().color().rgba())[4:])
        element.set("style", style)
        return element

    def __json__(self):
        return {
            "x": int(self.pos().x()),
            "y": int(self.pos().y()),
            "z": int(0),
            "svg": self.toSvg()
        }

