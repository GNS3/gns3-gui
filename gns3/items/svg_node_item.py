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
Graphical representation of a SVG node on the QGraphicsScene.
"""

from ..qt import QtSvg
from ..qt.qimage_svg_renderer import QImageSvgRenderer
from .node_item import NodeItem

import logging
log = logging.getLogger(__name__)


class SvgNodeItem(NodeItem, QtSvg.QGraphicsSvgItem):

    """
    SVG node for the scene.

    :param node: Node instance
    :param symbol: symbol for the node representation on the scene
    """

    def __init__(self, node, symbol=None):

        QtSvg.QGraphicsSvgItem.__init__(self)
        NodeItem.__init__(self, node)

        # create renderer using symbols path/resource
        if symbol:
            renderer = QImageSvgRenderer(symbol)
            if symbol != node.defaultSymbol():
                renderer.setObjectName(symbol)
        else:
            renderer = QImageSvgRenderer(node.defaultSymbol())
        self.setSharedRenderer(renderer)
