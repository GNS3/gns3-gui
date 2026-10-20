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

"""Graphical representation of a visual line on the topology canvas."""

import xml.etree.ElementTree as ET

from ..qt import QtCore, QtGui, QtWidgets
from .drawing_item import DrawingItem


class LineItem(QtWidgets.QGraphicsLineItem, DrawingItem):
    """Line body movement is Qt's; endpoint drags belong to CanvasLines."""

    def __init__(self, dst=None, svg=None, **kws):
        super().__init__(svg=svg, **kws)
        self.setAcceptHoverEvents(True)
        if svg is None:
            self.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.black, 2,
                                  QtCore.Qt.PenStyle.SolidLine,
                                  QtCore.Qt.PenCapStyle.RoundCap,
                                  QtCore.Qt.PenJoinStyle.RoundJoin))
            if dst is not None:
                self.setLine(QtCore.QLineF(QtCore.QPointF(), QtCore.QPointF(dst)))
        else:
            self.fromSvg(svg)

    def boundingRect(self):
        # Include the painted endpoint handles, even for a thin horizontal line.
        return super().boundingRect().adjusted(-5, -5, 5, 5)

    def shape(self):
        path = QtGui.QPainterPath()
        path.moveTo(self.line().p1())
        path.lineTo(self.line().p2())
        stroker = QtGui.QPainterPathStroker()
        stroker.setWidth(max(8, self.pen().widthF()))
        return stroker.createStroke(path)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        self.drawLayerInfo(painter)
        if self.isSelected() and not self.locked():
            painter.save()
            painter.setPen(QtGui.QPen(QtGui.QColor('#3484c6'), 0))
            painter.setBrush(QtGui.QColor('white'))
            for point in (self.line().p1(), self.line().p2()):
                painter.drawRect(QtCore.QRectF(point.x() - 4, point.y() - 4, 8, 8))
            painter.restore()

    def toSvg(self):
        svg = ET.Element('svg')
        line = self.line()
        width = max(1, abs(line.dx()))
        height = max(1, abs(line.dy()))
        svg.set('width', format(width, '.15g'))
        svg.set('height', format(height, '.15g'))
        # Preserve negative endpoint coordinates and a nonzero SVG viewport for
        # horizontal/vertical lines. Stroke padding avoids clipping thick ends.
        padding = self.pen().widthF() / 2
        svg.set('viewBox', '{} {} {} {}'.format(
            min(line.x1(), line.x2()) - padding,
            min(line.y1(), line.y2()) - padding,
            width + 2 * padding, height + 2 * padding))
        element = ET.SubElement(svg, 'line')
        for name, value in [('x1', line.x1()), ('y1', line.y1()),
                            ('x2', line.x2()), ('y2', line.y2())]:
            element.set(name, format(value, '.15g'))
        self._styleSvg(element)
        element.set('stroke-opacity', str(self.pen().color().alphaF()))
        return ET.tostring(svg, encoding='unicode')

    def __json__(self):
        # The drawing API accepts integer positions. Keep the fractional part
        # in the SVG endpoints so an acknowledgment cannot shift a line drawn
        # or moved at high zoom. Works with rotated lines and Qt parents too.
        position = self.scenePos()
        origin = QtCore.QPointF(round(position.x()), round(position.y()))
        if position != origin:
            points = [self.mapToScene(point) for point in (self.line().p1(), self.line().p2())]
            allowed = self._allow_snap_to_grid
            self._allow_snap_to_grid = False
            try:
                parent = self.parentItem()
                self.setPos(parent.mapFromScene(origin) if parent else origin)
                self.setLine(QtCore.QLineF(*(self.mapFromScene(point) for point in points)))
            finally:
                self._allow_snap_to_grid = allowed
        data = super().__json__()
        data['x'], data['y'] = round(self.scenePos().x()), round(self.scenePos().y())
        return data

    def fromSvg(self, svg):
        root = ET.fromstring(svg)
        element = next((child for child in root.iter()
                        if child.tag.rsplit('}', 1)[-1] == 'line'), None)
        if element is None:
            self.setLine(0, 0, float(root.get('width', 0)), float(root.get('height', 0)))
            return
        self.setLine(*(float(element.get(name, 0)) for name in ('x1', 'y1', 'x2', 'y2')))
        pen = self._penFromSVGElement(element)
        color = pen.color()
        color.setAlphaF(max(0, min(1, float(element.get('stroke-opacity', 1)))))
        pen.setColor(color)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
        self.setPen(pen)

    def hoverMoveEvent(self, event):
        if not self.locked():
            self._graphics_view.setCursor(QtCore.Qt.CursorShape.SizeAllCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self._graphics_view._lines.restoreCursor()
        super().hoverLeaveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if not self.locked() and event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._graphics_view._lines.edit([self])
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
