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
