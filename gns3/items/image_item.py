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
Graphical representation of an image on the QGraphicsScene.
"""

import math
import xml.etree.ElementTree as ET
from ..qt import QtSvgWidgets, QtCore, QtGui, QtWidgets
from ..qt.qimage_svg_renderer import QImageSvgRenderer

ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
from .drawing_item import DrawingItem


class ImageItem(QtSvgWidgets.QGraphicsSvgItem, DrawingItem):

    """
    Class to insert an image on the scene.
    """

    def __init__(self, image_path=None, pos=None, svg=None, **kws):

        self._image_path = image_path
        self.keep_aspect = True
        self._resize_edge = None
        self._resize_data = None
        # Because we call the Qt C++ code we need to handle the case of pos is None otherwise we will get a conversion error
        if pos:
            super().__init__(pos=pos, **kws)
        else:
            super().__init__(**kws)

        if self._image_path:
            self._image_renderer = QImageSvgRenderer(image_path)
            self.setSharedRenderer(self._image_renderer)
            self.fromSvg(self._image_renderer.svg())

        # By default center the image
        if pos is None:
            x = self.pos().x() - (self.boundingRect().width() / 2)
            y = self.pos().y() - (self.boundingRect().height() / 2)
            self.setPos(x, y)

        if svg:
            svg = self.fromSvg(svg)

        self.setAcceptHoverEvents(True)
        if 'z' in kws.keys():
            self.setZValue(kws['z'])

    def paint(self, painter, option, widget=None):
        """
        Paints the contents of an item in local coordinates.

        :param painter: QPainter instance
        :param option: QStyleOptionGraphicsItem instance
        :param widget: QWidget instance
        """

        super().paint(painter, option, widget)
        self.drawLayerInfo(painter)
        if self.isSelected() and not self.locked():
            painter.save()
            painter.setPen(QtGui.QPen(QtGui.QColor('#3484c6'), 0))
            painter.setBrush(QtGui.QColor('white'))
            r = self.boundingRect().adjusted(4, 4, -4, -4)
            for point in (r.topLeft(), r.topRight(), r.bottomLeft(), r.bottomRight()):
                painter.drawRect(QtCore.QRectF(point.x() - 3, point.y() - 3, 6, 6))
            painter.restore()

    def fromSvg(self, svg):
        root = ET.fromstring(svg)
        # The v2 server extracts direct image children into raster files and
        # regenerates their intrinsic size, losing drawing dimensions/metadata.
        # A group preserves the complete SVG without changing its rendering.
        images = [child for child in root if child.tag.rsplit('}', 1)[-1] == 'image']
        for child in images:
            index = list(root).index(child)
            root.remove(child)
            wrapper = ET.Element('{http://www.w3.org/2000/svg}g')
            wrapper.append(child)
            root.insert(index, wrapper)
        svg = ET.tostring(root, encoding='unicode')
        renderer = QImageSvgRenderer(svg)
        self.setSharedRenderer(renderer)
        self._image_renderer = renderer
        self.keep_aspect = root.get('data-gns3-keep-aspect', 'true') != 'false'

    def setDimensions(self, width, height):
        if any(not math.isfinite(value) or not 1 <= value <= 1000000 for value in (width, height)):
            raise ValueError('Image dimensions must be between 1 and 1000000')
        root = ET.fromstring(self.renderer().svg())
        old = self.boundingRect()
        if not root.get('viewBox'):
            root.set('viewBox', '0 0 {} {}'.format(old.width(), old.height()))
        root.set('width', str(width))
        root.set('height', str(height))
        root.set('preserveAspectRatio', 'none')
        root.set('data-gns3-keep-aspect', 'true' if self.keep_aspect else 'false')
        self.prepareGeometryChange()
        self.fromSvg(ET.tostring(root, encoding='unicode'))
        self.update()

    def resizeEdgeAt(self, point):
        if self.locked():
            return None
        tolerance = 7 / max(.01, self._graphics_view.transform().m11())
        r = self.boundingRect()
        horizontal = 'l' if abs(point.x() - r.left()) <= tolerance else 'r' if abs(point.x() - r.right()) <= tolerance else ''
        vertical = 't' if abs(point.y() - r.top()) <= tolerance else 'b' if abs(point.y() - r.bottom()) <= tolerance else ''
        return vertical + horizontal or None

    def hoverMoveEvent(self, event):
        edge = self.resizeEdgeAt(event.pos())
        if edge:
            cursor = (QtCore.Qt.CursorShape.SizeFDiagCursor if edge in ('tl', 'br') else
                      QtCore.Qt.CursorShape.SizeBDiagCursor if len(edge) == 2 else
                      QtCore.Qt.CursorShape.SizeHorCursor if edge in ('l', 'r') else QtCore.Qt.CursorShape.SizeVerCursor)
            self._graphics_view.setCursor(cursor)
        else:
            self._graphics_view.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        self._resize_edge = self.resizeEdgeAt(event.pos()) if event.button() == QtCore.Qt.MouseButton.LeftButton else None
        if self._resize_edge:
            self.setSelected(True)
            self._resize_data = (QtCore.QRectF(self.boundingRect()), self.scenePos(), event.pos(), self.sceneTransform().inverted()[0])
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resize_edge:
            rect, origin, press, original_inverse = self._resize_data
            # Work in the original item's axes; mapFromScene also handles nested
            # containers and rotation, unlike subtracting canvas x/y directly.
            delta = original_inverse.map(event.scenePos()) - press
            width = max(1, min(1000000, rect.width() + (-delta.x() if 'l' in self._resize_edge else delta.x() if 'r' in self._resize_edge else 0)))
            height = max(1, min(1000000, rect.height() + (-delta.y() if 't' in self._resize_edge else delta.y() if 'b' in self._resize_edge else 0)))
            if self.keep_aspect:
                sx, sy = width / rect.width(), height / rect.height()
                scale = sy if self._resize_edge in ('t', 'b') or (len(self._resize_edge) == 2 and abs(sy - 1) > abs(sx - 1)) else sx
                scale = max(max(1 / rect.width(), 1 / rect.height()), min(scale, 1000000 / rect.width(), 1000000 / rect.height()))
                width, height = rect.width() * scale, rect.height() * scale
            shift = QtCore.QPointF(rect.width() - width if 'l' in self._resize_edge else 0,
                                  rect.height() - height if 't' in self._resize_edge else 0)
            from .group_item import set_scene_position
            # Preserve the opposite corner in scene coordinates.
            movement = self.mapToScene(shift) - self.mapToScene(QtCore.QPointF())
            self.setDimensions(width, height)
            set_scene_position(self, origin + movement)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._resize_edge:
            self._resize_edge = None
            self._resize_data = None
            self._graphics_view._groups.save([self])
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def toSvg(self):
        """
        Return an SVG version of the shape
        """
        return self.renderer().svg()
