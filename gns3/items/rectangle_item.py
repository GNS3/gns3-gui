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
from .shape_item import ShapeItem


class RectangleItem(QtWidgets.QGraphicsRectItem, ShapeItem):

    """
    Class to draw a rectangle on the scene.
    """

    def __init__(self, width=200, height=100, **kws):
        self._rx = 0
        self._ry = 0
        super().__init__(width=width, height=height, **kws)

    def setHorizontalCornerRadius(self, radius: int):
        self._rx = radius

    def horizontalCornerRadius(self):
        return self._rx

    def setVerticalCornerRadius(self, radius: int):
        self._ry = radius

    def verticalCornerRadius(self):
        return self._ry

    def paint(self, painter, option, widget=None):
        """
        Paints the contents of an item in local coordinates.

        :param painter: QPainter instance
        :param option: QStyleOptionGraphicsItem instance
        :param widget: QWidget instance
        """

        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRoundedRect(self.rect(), self._rx, self._ry)
        self.drawLayerInfo(painter)

    def toSvg(self):
        """
        Return an SVG version of the shape
        """
        svg = ET.Element("svg")
        svg.set("width", str(int(self.rect().width())))
        svg.set("height", str(int(self.rect().height())))

        rect = ET.SubElement(svg, "rect")
        rect.set("width", str(int(self.rect().width())))
        rect.set("height", str(int(self.rect().height())))
        if self._rx:
            rect.set("rx", str(self._rx))
        if self._ry:
            rect.set("ry", str(self._ry))

        rect = self._styleSvg(rect)

        return ET.tostring(svg, encoding="utf-8").decode("utf-8")

    def fromSvg(self, svg):
        svg_elem = ET.fromstring(svg)
        if len(svg_elem):
            # handle horizontal corner radius and vertical corner radius (specific to rectangles)
            rx = svg_elem[0].get("rx")
            ry = svg_elem[0].get("ry")
            if rx:
                self._rx = int(rx)
            elif ry:
                self._rx = int(ry)  # defaults to ry if it is specified
            if ry:
                self._ry = int(ry)
            elif rx:
                self._ry = int(rx)  # defaults to rx if it is specified
        super().fromSvg(svg)
