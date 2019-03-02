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

import xml.etree.ElementTree as ET
from ..qt import QtCore, QtGui, QtWidgets
from .drawing_item import DrawingItem
from .utils import colorFromSvg

import logging
log = logging.getLogger(__name__)


class ShapeItem(DrawingItem):

    """
    Base class to draw shapes on the scene.
    """

    def __init__(self, width=200, height=200, svg=None, **kws):

        super().__init__(svg=svg, **kws)
        self.setAcceptHoverEvents(True)
        self._border = 5
        self._edge = None
        self._originally_movable = True

        if svg is None:
            self.setRect(0, 0, width, height)
            pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
            self.setPen(pen)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 255))  # default color is white and not transparent
            self.setBrush(brush)
        else:
            self.fromSvg(svg)
        if self._id is None:
            self.create()

    def mousePressEvent(self, event):
        """
        Handles all mouse press events.

        :param event: QMouseEvent instance
        """

        self.update()
        self._originally_movable = self.flags() & QtWidgets.QGraphicsItem.ItemIsMovable
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
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, self._originally_movable)
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

        # locked objects don't need cursors
        if not self.locked():
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

        # locked objects don't need cursors
        if not self.locked():
            self._graphics_view.setCursor(QtCore.Qt.ArrowCursor)

    def fromSvg(self, svg):
        """
        Import element informations from an SVG
        """
        svg = ET.fromstring(svg)
        width = float(svg.get("width", self.rect().width()))
        height = float(svg.get("height", self.rect().height()))
        self.setRect(0, 0, width, height)

        pen = QtGui.QPen()
        brush = QtGui.QBrush(QtCore.Qt.SolidPattern)

        if len(svg):
            pen = self._penFromSVGElement(svg[0])
            if svg[0].get("fill"):
                new_color = colorFromSvg(svg[0].get("fill"))
                color = brush.color()
                color.setBlue(new_color.blue())
                color.setRed(new_color.red())
                color.setGreen(new_color.green())
                brush.setColor(color)
            if svg[0].get("fill-opacity"):
                color = brush.color()
                color.setAlphaF(float(svg[0].get("fill-opacity")))
                brush.setColor(color)

        self.setPen(pen)
        self.setBrush(brush)
        self.update()
