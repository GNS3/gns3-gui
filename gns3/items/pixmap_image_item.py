# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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
Graphical representation of a Pixmap image on the QGraphicsScene.
"""

from ..qt import QtCore, QtWidgets
from .image_item import ImageItem


class PixmapImageItem(ImageItem, QtWidgets.QGraphicsPixmapItem):

    """
    Class to insert an pixmap image on the scene.
    """

    def __init__(self, pixmap, image_path, pos=None):

        QtWidgets.QGraphicsPixmapItem.__init__(self, pixmap)
        ImageItem.__init__(self, image_path, pos)
        self.setTransformationMode(QtCore.Qt.SmoothTransformation)

    def duplicate(self):
        """
        Duplicates this image item.

        :return: PixmapImageItem instance
        """

        image_item = PixmapImageItem(self.pixmap(), self._image_path, QtCore.QPointF(self.x() + 20, self.y() + 20))
        image_item.setZValue(self.zValue())
        return image_item
