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
Base class for link items (Ethernet, serial etc.).
Link items are graphical representation of a link on the QGraphicsScene
"""

import math
from ..qt import QtCore, QtGui


class LinkItem(QtGui.QGraphicsPathItem):
    """
    Base class for link items.

    :param source_item: source NodeItem instance
    :param source_port: source Port instance
    :param destination_item: destination NodeItem instance
    :param destination_port: destination Port instance
    :param link: Link instance (contains back-end stuff for this link)
    :param adding_flag: indicates if this link is being added (no destination yet)
    :param multilink: used to draw multiple link between the same source and destination
    """

    def __init__(self, source_item, source_port, destination_item, destination_port, link=None, adding_flag=False, multilink=0):

        QtGui.QGraphicsPathItem.__init__(self)
        self.setZValue(-1)
        self._link = None

        from ..main_window import MainWindow
        self._settings = MainWindow.instance().uiGraphicsView.settings()

        # indicates link is being added:
        # source has been chosen but not its destination yet
        self._adding_flag = adding_flag

        # status points size
        self._point_size = 10

        # default pen size
        self._pen_width = 2.0

        # indicates the link position when there are multiple links
        # between the same source and destination
        self._multilink = multilink

        # source & destination items and ports
        self._source_item = source_item
        self._destination_item = destination_item
        self._source_port = source_port
        self._destination_port = destination_port

        if not self._adding_flag:
            # there is a destination

            self._link = link

            # links must always be below node items on the scene
            min_zvalue = min([source_item.zValue(), destination_item.zValue()])
            self.setZValue(min_zvalue - 1)
            self.setFlag(self.ItemIsFocusable)

            source_item.addLink(self)
            destination_item.addLink(self)

            #TODO: capture support

#             source_item.node.nio_signal.connect(self.newNIOSlot)
#             destination_item.node.nio_signal.connect(self.newNIOSlot)
#             self._source_item.setCustomToolTip()
#             self._destination_item.setCustomToolTip()
#             self.capturing = False
#             self.capfile = None
#             self.captureInfo = None
#             self.tailProcess = None
#             self.capturePipeThread = None
#             # Set default tooltip

#             self.encapsulationTransform = { 'ETH': 'EN10MB',
#                                             'FR': 'FRELAY',
#                                             'HDLC': 'C_HDLC',
#                                             'PPP': 'PPP_SERIAL'}
            self.setCustomToolTip()

        else:
            source_rect = self._source_item.boundingRect()
            self.source = self.mapFromItem(self._source_item, source_rect.width() / 2.0, source_rect.height() / 2.0)
            self.destination = self._destination_item

        self.adjust()

    def delete(self):
        """
        Delete this link
        """

        self._source_item.removeLink(self)
        self._destination_item.removeLink(self)
        self._link.deleteLink()
        self.scene().removeItem(self)

    def setCustomToolTip(self):
        """
        Sets a custom tool tip for this link.
        """

        if self._link:
            self.setToolTip(self._link.description())

    def sourceItem(self):
        """
        Returns the source item for this link.

        :returns: NodeItem instance
        """

        return self._source_item

    def destinationItem(self):
        """
        Returns the destination item for this link.

        :returns: NodeItem instance
        """

        return self._destination_item

    def sourcePort(self):
        """
        Returns the source port for this link.

        :returns: Port instance
        """

        return self._source_port

    def destinationPort(self):
        """
        Returns the destination port for this link.

        :returns: Port instance
        """

        return self._destination_port

    def mousePressEvent(self, event):
        """
        Called when the link is clicked and shows a contextual menu.

        :param: QGraphicsSceneMouseEvent instance
        """

        if (event.button() == QtCore.Qt.RightButton):
            if self._adding_flag:
                # send a escape key to the main window to cancel the link addition
                from ..main_window import MainWindow
                key = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Escape, QtCore.Qt.NoModifier)
                QtGui.QApplication.sendEvent(MainWindow.instance(), key)
                return

            # create the contextual menu
            menu = QtGui.QMenu()
            delete_action = QtGui.QAction("Delete", menu)
            delete_action.setIcon(QtGui.QIcon(':/icons/delete.svg'))
            delete_action.triggered.connect(self._deleteActionSlot)
            menu.addAction(delete_action)
            menu.exec_(QtGui.QCursor.pos())

    def _deleteActionSlot(self):
        """
        Slot to receive events from the delete action in the
        contextual menu.
        """

        self.delete()

    def adjust(self):
        """
        Computes the source point and destination point.
        Must be overloaded.
        """

        self.prepareGeometryChange()
        source_rect = self._source_item.boundingRect()
        self.source = self.mapFromItem(self._source_item, source_rect.width() / 2.0, source_rect.height() / 2.0)

        # if source point is not a mouse point
        if not self._adding_flag:
            destination_rect = self._destination_item.boundingRect()
            self.destination = self.mapFromItem(self._destination_item, destination_rect.width() / 2.0, destination_rect.height() / 2.0)

        # compute vectors
        self.dx = self.destination.x() - self.source.x()
        self.dy = self.destination.y() - self.source.y()

        # compute the length of the line
        self.length = math.sqrt(self.dx * self.dx + self.dy * self.dy)

        # multi-link management
        if not self._adding_flag and self._multilink and self.length:
            angle = math.radians(90)
            self.dxrot = math.cos(angle) * self.dx - math.sin(angle) * self.dy
            self.dyrot = math.sin(angle) * self.dx + math.cos(angle) * self.dy
            offset = QtCore.QPointF((self.dxrot * (self._multilink * 5)) / self.length, (self.dyrot * (self._multilink * 5)) / self.length)
            self.source = QtCore.QPointF(self.source + offset)
            self.destination = QtCore.QPointF(self.destination + offset)

    def setMousePoint(self, scene_point):
        """
        Sets new mouse point coordinates.
        Used when adding a link and the destination is not yet chosen.

        :param scene_point: event position
        """

        self.destination = scene_point
        self.adjust()
        self.update()
