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

from ..qt import QtCore, QtGui


class ImageItem(QtGui.QGraphicsPixmapItem):

    """
    Class to insert an image on the scene.
    """

    show_layer = False

    def __init__(self, pixmap, image_path, pos=None):

        QtGui.QGraphicsPixmapItem.__init__(self, pixmap)
        self.setFlags(self.ItemIsMovable | self.ItemIsSelectable)
        self.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self._image_path = image_path
        if pos:
            self.setPos(pos)

    def delete(self):
        """
        Deletes this image item.
        """

        self.scene().removeItem(self)
        from ..topology import Topology
        Topology.instance().removeImage(self)

    def duplicate(self):
        """
        Duplicates this image item.

        :return: ImageItem instance
        """

        image_item = ImageItem(self.pixmap(), self._image_path, QtCore.QPointF(self.x() + 20, self.y() + 20))
        image_item.setZValue(self.zValue())
        return image_item

    def paint(self, painter, option, widget=None):
        """
        Paints the contents of an item in local coordinates.

        :param painter: QPainter instance
        :param option: QStyleOptionGraphicsItem instance
        :param widget: QWidget instance
        """

        QtGui.QGraphicsPixmapItem.paint(self, painter, option, widget)

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

        QtGui.QGraphicsPixmapItem.setZValue(self, value)
        if self.zValue() < 0:
            self.setFlag(self.ItemIsSelectable, False)
            self.setFlag(self.ItemIsMovable, False)
        else:
            self.setFlag(self.ItemIsSelectable, True)
            self.setFlag(self.ItemIsMovable, True)

    def dump(self):
        """
        Returns a representation of this image item.

        :returns: dictionary
        """

        image_info = {"path": self._image_path,
                      "x": self.x(),
                      "y": self.y()}

        if self.zValue() != 0:
            image_info["z"] = self.zValue()

        return image_info

    def load(self, image_info):
        """
        Loads an image representation
        (from a topology file).

        :param image_info: representation of the image item (dictionary)
        """

        # load mandatory properties
        x = image_info["x"]
        y = image_info["y"]
        self.setPos(x, y)

        # load optional properties
        z = image_info.get("z")
        if z is not None:
            self.setZValue(z)
