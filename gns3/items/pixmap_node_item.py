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
Graphical representation of a pixmap node on the QGraphicsScene.
"""

from ..qt import QtGui, QtWidgets
from .node_item import NodeItem

import logging
log = logging.getLogger(__name__)


class PixmapNodeItem(NodeItem, QtWidgets.QGraphicsPixmapItem):

    """
    Pixmap node for the scene.

    :param node: Node instance
    :param pixmap_symbol: symbol for the node representation on the scene
    """

    def __init__(self, node, pixmap_symbol_path):

        QtWidgets.QGraphicsPixmapItem.__init__(self)
        NodeItem.__init__(self, node)

        self._pixmap_symbol_path = pixmap_symbol_path
        pixmap = QtGui.QPixmap(pixmap_symbol_path)
        self.setPixmap(pixmap)

    def setPixmapSymbolPath(self, path):
        """
        Sets the pixmap path

        :param path: path to the Pixmap file.
        """

        self._pixmap_symbol_path = path

    def pixmapSymbolPath(self):
        """
        Returns the pixmap path

        :returns: path to the Pixmap file.
        """

        return self._pixmap_symbol_path
