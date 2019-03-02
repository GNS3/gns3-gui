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
Graphical representation of a rectangle on the QGraphicsScene.
"""

import xml.etree.ElementTree as ET

from ..qt import QtCore, QtGui, QtWidgets
from .drawing_item import DrawingItem


class LineItem(QtWidgets.QGraphicsLineItem, DrawingItem):

    """
    Class to draw a rectangle on the scene.
    """

    def __init__(self, dst=None, svg=None, **kws):
        super().__init__(svg=svg, **kws)
        self.setAcceptHoverEvents(True)

        self._edge = None
        self._border = 20

        if svg is None:
            if dst is not None:
                self.setLine(0,
                             0,
                             dst.x(),
                             dst.y())
                pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
                self.setPen(pen)
        else:
            self.fromSvg(svg)
        if self._id is None:
            self.create()

    def paint(self, painter, option, widget=None):
        """
        Paints the contents of an item in local coordinates.

        :param painter: QPainter instance
        :param option: QStyleOptionGraphicsItem instance
        :param widget: QWidget instance
        """

        super().paint(painter, option, widget)
        self.drawLayerInfo(painter)

    def toSvg(self):
        """
        Return an SVG version of the shape
        """
        svg = ET.Element("svg")
        width = abs(self.line().x1() - self.line().x2())
        height = abs(self.line().y1() - self.line().y2())
        svg.set("width", str(int(width)))
        svg.set("height", str(int(height)))

        line = ET.SubElement(svg, "line")
        line.set("x1", str(int(self.line().x1())))
        line.set("x2", str(int(self.line().x2())))
        line.set("y1", str(int(self.line().y1())))
        line.set("y2", str(int(self.line().y2())))
        line = self._styleSvg(line)

        return ET.tostring(svg, encoding="utf-8").decode("utf-8")

    def fromSvg(self, svg):
        """
        Import element informations from an SVG
        """
        svg = ET.fromstring(svg)
        width = float(svg.get("width", 0))
        height = float(svg.get("height", 0))

        # Backup the pos and restore it
        pos = self.pos()
        y1 = self.line().y1()
        self.setLine(0, 0, width, height)

        pen = QtGui.QPen()

        if len(svg):
            pen = self._penFromSVGElement(svg[0])
            self.setLine(
                float(svg[0].get("x1")),
                float(svg[0].get("y1")),
                float(svg[0].get("x2")),
                float(svg[0].get("y2"))
            )
        self.setPos(pos)
        self.setPen(pen)
        self.update()

    def _isHorizontalLine(self):
        return abs(self.line().x1() - self.line().x2()) > abs(self.line().y1() - self.line().y2())

    def hoverMoveEvent(self, event):
        """
        Handles all hover move events.

        :param event: QGraphicsSceneHoverEvent instance
        """

        # locked objects don't need cursors
        if not self.locked():

            if self._isHorizontalLine():
                if event.pos().x() > (self.line().x2() - self._border):
                    self._graphics_view.setCursor(QtCore.Qt.SizeHorCursor)
                elif event.pos().x() < self._border:
                    self._graphics_view.setCursor(QtCore.Qt.SizeHorCursor)
                else:
                    self._graphics_view.setCursor(QtCore.Qt.SizeAllCursor)
            # Vertical line
            else:
                if event.pos().y() > (self.line().y2() - self._border):
                    self._graphics_view.setCursor(QtCore.Qt.SizeVerCursor)
                elif event.pos().y() < self._border:
                    self._graphics_view.setCursor(QtCore.Qt.SizeVerCursor)
                else:
                    self._graphics_view.setCursor(QtCore.Qt.SizeAllCursor)

    def mouseMoveEvent(self, event):
        """
        Handles all mouse move events.

        :param event: QMouseEvent instance
        """

        self.update()
        if self._edge:
            scenePos = event.scenePos()
            if self._edge == "left" or self._edge == "bottom":
                diff_x = self.x() - scenePos.x()
                diff_y = self.y() - scenePos.y()
                self.setPos(scenePos.x(), scenePos.y())
                self.setLine(
                    0,
                    0,
                    self.line().x2() + diff_x,
                    self.line().y2() + diff_y)
            elif self._edge == "right" or self._edge == "top":
                pos = self.mapFromScene(scenePos)
                self.setLine(
                    0,
                    0,
                    pos.x(),
                    pos.y())
                self.setPos(self.x(), self.y())
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """
        Handles all mouse press events.

        :param event: QMouseEvent instance
        """

        self.update()
        if self._isHorizontalLine():
            if event.pos().x() > (self.line().x2() - self._border):
                self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
                self._edge = "right"
            elif event.pos().x() < (self.line().x1() + self._border):
                self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
                self._edge = "left"
        else:
            if event.pos().y() > (self.line().y2() - self._border):
                self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
                self._edge = "top"
            elif event.pos().y() < (self.line().y1() + self._border):
                self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
                self._edge = "bottom"
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Handles all mouse release events.

        :param: QMouseEvent instance
        """

        self.update()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

        self._edge = None
        super().mouseReleaseEvent(event)

    def hoverLeaveEvent(self, event):
        """
        Handles all hover leave events.

        :param event: QGraphicsSceneHoverEvent instance
        """

        # locked objects don't need cursors
        if not self.locked():
            self._graphics_view.setCursor(QtCore.Qt.ArrowCursor)
