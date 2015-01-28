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

from ..qt import QtCore, QtGui
from .shape_item import ShapeItem


class RectangleItem(ShapeItem, QtGui.QGraphicsRectItem):

    """
    Class to draw a rectangle on the scene.
    """

    def __init__(self, pos=None, width=200, height=100):

        QtGui.QGraphicsRectItem.__init__(self, 0, 0, width, height)
        ShapeItem.__init__(self)
        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self.setPen(pen)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 255))  # default color is white and not transparent
        self.setBrush(brush)
        if pos:
            self.setPos(pos)

    def delete(self):
        """
        Deletes this rectangle.
        """

        self.scene().removeItem(self)
        from ..topology import Topology
        Topology.instance().removeRectangle(self)

    def paint(self, painter, option, widget=None):
        """
        Paints the contents of an item in local coordinates.

        :param painter: QPainter instance
        :param option: QStyleOptionGraphicsItem instance
        :param widget: QWidget instance
        """

        QtGui.QGraphicsRectItem.paint(self, painter, option, widget)
        self.drawLayerInfo(painter)

    def duplicate(self):
        """
        Duplicates this rectangle item.

        :return: RectangleItem instance
        """

        rectangle_item = RectangleItem(QtCore.QPointF(self.x() + 20, self.y() + 20), self.rect().width(), self.rect().height())
        rectangle_item.setPen(self.pen())
        rectangle_item.setBrush(self.brush())
        rectangle_item.setZValue(self.zValue())
        rectangle_item.setRotation(self.rotation())
        return rectangle_item
