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
        if pos:
            self.setPos(pos)

    def delete(self):
        """
        Deletes this ellipse.
        """

        self.scene().removeItem(self)
        from ..topology import Topology
        Topology.instance().removeEllipse(self)

    # def paint(self, painter, option, widget=None):
    #
    #     QtGui.QGraphicsEllipseItem.paint(self, painter, option, widget)
    #     self.drawLayerInfo(painter)

    def dump(self):
        """
        Returns a representation of this ellipse.

        :returns: dictionary
        """

        return {"width": self.rect().width(),
                "height": self.rect().height(),
                "x": self.x(),
                "y": self.y(),
                "z": self.zValue()}

    def load(self, rectangle_info):
        """
        Loads an ellipse representation
        (from a topology file).

        :param rectangle_info: representation of the ellipse (dictionary)
        """

        width = rectangle_info["width"]
        height = rectangle_info["height"]
        x = rectangle_info["x"]
        y = rectangle_info["y"]
        z = rectangle_info["z"]
        self.rect().setWidth(width)
        self.rect().setHeight(height)
        self.setPos(x, y)
        self.setZValue(z)

    def duplicate(self):
        """
        Duplicates this ellipse item.

        :return: EllipseItem instance
        """

        ellipse_item = EllipseItem()
        ellipse_item.rect().setWidth(self.rect().width())
        ellipse_item.rect().setHeight(self.rect().height())
        ellipse_item.setPos(self.x() + 20, self.y() + 20)
        ellipse_item.setZValue(self.zValue())
        return ellipse_item
