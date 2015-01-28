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
Graphical representation of an ellipse on the QGraphicsScene.
"""

from ..qt import QtCore, QtGui
from .shape_item import ShapeItem


class EllipseItem(ShapeItem, QtGui.QGraphicsEllipseItem):

    """
    Class to draw an ellipse on the scene.
    """

    def __init__(self, pos=None, width=200, height=200):

        QtGui.QGraphicsEllipseItem.__init__(self, 0, 0, width, height)
        ShapeItem.__init__(self)
        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.DashLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self.setPen(pen)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 255))  # default color is white and not transparent
        self.setBrush(brush)
        if pos:
            self.setPos(pos)

    def delete(self):
        """
        Deletes this ellipse.
        """

        self.scene().removeItem(self)
        from ..topology import Topology
        Topology.instance().removeEllipse(self)

    def paint(self, painter, option, widget=None):
        """
        Paints the contents of an item in local coordinates.

        :param painter: QPainter instance
        :param option: QStyleOptionGraphicsItem instance
        :param widget: QWidget instance
        """

        QtGui.QGraphicsEllipseItem.paint(self, painter, option, widget)
        self.drawLayerInfo(painter)

    def duplicate(self):
        """
        Duplicates this ellipse item.

        :return: EllipseItem instance
        """

        ellipse_item = EllipseItem(QtCore.QPointF(self.x() + 20, self.y() + 20), self.rect().width(), self.rect().height())
        ellipse_item.setPen(self.pen())
        ellipse_item.setBrush(self.brush())
        ellipse_item.setZValue(self.zValue())
        ellipse_item.setRotation(self.rotation())
        return ellipse_item
