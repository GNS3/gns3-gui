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
Graphical representation of an Ethernet link for QGraphicsScene.
"""

from ..qt import QtCore, QtGui, QtWidgets
from .link_item import LinkItem
from .note_item import NoteItem
from ..ports.port import Port


class EthernetLinkItem(LinkItem):

    """
    Ethernet link for the scene.

    :param source_item: source NodeItem instance
    :param source_port: source Port instance
    :param destination_item: destination NodeItem instance
    :param destination_port: destination Port instance
    :param link: Link instance (contains back-end stuff for this link)
    :param adding_flag: indicates if this link is being added (no destination yet)
    :param multilink: used to draw multiple link between the same source and destination
    """

    def __init__(self, source_item, source_port, destination_item, destination_port, link=None, adding_flag=False, multilink=0):

        super().__init__(source_item, source_port, destination_item, destination_port, link, adding_flag, multilink)
        self._source_collision_offset = 0.0
        self._destination_collision_offset = 0.0

    def adjust(self):
        """
        Draws a line and compute offsets for status points.
        """

        LinkItem.adjust(self)

        if self._hovered:
            self.setPen(QtGui.QPen(QtCore.Qt.red, self._pen_width + 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        else:
            self.setPen(QtGui.QPen(QtCore.Qt.black, self._pen_width, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

        # draw a line between nodes
        path = QtGui.QPainterPath(self.source)
        path.lineTo(self.destination)
        self.setPath(path)

        # offset on the line for status points
        if self.length == 0:
            self.edge_offset = QtCore.QPointF(0, 0)
        else:
            self.edge_offset = QtCore.QPointF((self.dx * 40) / self.length, (self.dy * 40) / self.length)

    def shape(self):
        """
        Returns the shape of the item to the scene renderer.

        :returns: QPainterPath instance
        """

        path = QtWidgets.QGraphicsPathItem.shape(self)
        offset = self._point_size / 2
        if not self._adding_flag:
            if self.length:
                collision_offset = QtCore.QPointF((self.dx * self._source_collision_offset) / self.length, (self.dy * self._source_collision_offset) / self.length)
            else:
                collision_offset = QtCore.QPointF(0, 0)
            point = self.source + (self.edge_offset + collision_offset)
        else:
            point = self.source
        path.addEllipse(point.x() - offset, point.y() - offset, self._point_size, self._point_size)
        if not self._adding_flag:
            if self.length:
                collision_offset = QtCore.QPointF((self.dx * self._destination_collision_offset) / self.length, (self.dy * self._destination_collision_offset) / self.length)
            else:
                collision_offset = QtCore.QPointF(0, 0)
            point = self.destination - (self.edge_offset + collision_offset)
        else:
            point = self.destination
        path.addEllipse(point.x() - offset, point.y() - offset, self._point_size, self._point_size)
        return path

    def paint(self, painter, option, widget):
        """
        Draws the status points.

        :param painter: QPainter instance
        :param option: QStyleOptionGraphicsItem instance
        :param widget: QWidget instance.
        """

        QtWidgets.QGraphicsPathItem.paint(self, painter, option, widget)
        if not self._adding_flag and self._settings["draw_link_status_points"]:

            # points disappears if nodes are too close to each others.
            if self.length < 100:
                return

            if self._source_port.status() == Port.started:
                # port is active
                color = QtCore.Qt.green
            elif self._source_port.status() == Port.suspended:
                # port is suspended
                color = QtCore.Qt.yellow
            else:
                color = QtCore.Qt.red

            painter.setPen(QtGui.QPen(color, self._point_size, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.MiterJoin))
            point1 = QtCore.QPointF(self.source + self.edge_offset) + QtCore.QPointF((self.dx * self._source_collision_offset) / self.length, (self.dy * self._source_collision_offset) / self.length)

            # avoid any collision of the status point with the source node
            while self._source_item.contains(self.mapFromScene(self.mapToItem(self._source_item, point1))):
                self._source_collision_offset += 10
                point1 = QtCore.QPointF(self.source + self.edge_offset) + QtCore.QPointF((self.dx * self._source_collision_offset) / self.length, (self.dy * self._source_collision_offset) / self.length)

            # check with we can paint the status point more closely of the source node
            if not self._source_item.contains(self.mapFromScene(self.mapToItem(self._source_item, point1))):
                check_point = QtCore.QPointF(self.source + self.edge_offset) + QtCore.QPointF((self.dx * (self._source_collision_offset - 20)) / self.length, (self.dy * (self._source_collision_offset - 20)) / self.length)
                if not self._source_item.contains(self.mapFromScene(self.mapToItem(self._source_item, check_point))) and self._source_collision_offset > 0:
                    self._source_collision_offset -= 10

            source_port_label = self._source_port.label()
            if self._draw_port_labels:
                if source_port_label is None:
                    source_port_label = NoteItem(self._source_item)
                    if not self._source_port.isStub():
                        source_port_name = self._source_port.name().replace(self._source_port.longNameType(),
                                                                            self._source_port.shortNameType())
                    else:
                        source_port_name = self._source_port.name()
                    source_port_label.setPlainText(source_port_name)
                    source_port_label.setPos(self.mapToItem(self._source_item, point1))
                    self._source_port.setLabel(source_port_label)

                elif source_port_label and not source_port_label.isVisible():
                    source_port_label.show()

            elif source_port_label:
                source_port_label.hide()

            painter.drawPoint(point1)

            if self._destination_port.status() == Port.started:
                # port is active
                color = QtCore.Qt.green
            elif self._destination_port.status() == Port.suspended:
                # port is suspended
                color = QtCore.Qt.yellow
            else:
                color = QtCore.Qt.red

            painter.setPen(QtGui.QPen(color, self._point_size, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.MiterJoin))
            point2 = QtCore.QPointF(self.destination - self.edge_offset) - QtCore.QPointF((self.dx * self._destination_collision_offset) / self.length, (self.dy * self._destination_collision_offset) / self.length)

            # avoid any collision of the status point with the destination node
            while self._destination_item.contains(self.mapFromScene(self.mapToItem(self._destination_item, point2))):
                self._destination_collision_offset += 10
                point2 = QtCore.QPointF(self.destination - self.edge_offset) - QtCore.QPointF((self.dx * self._destination_collision_offset) / self.length, (self.dy * self._destination_collision_offset) / self.length)

            # check with we can paint the status point more closely of the destination node
            if not self._destination_item.contains(self.mapFromScene(self.mapToItem(self._destination_item, point2))):
                check_point = QtCore.QPointF(self.destination - self.edge_offset) - QtCore.QPointF((self.dx * (self._destination_collision_offset - 20)) / self.length, (self.dy * (self._destination_collision_offset - 20)) / self.length)
                if not self._destination_item.contains(self.mapFromScene(self.mapToItem(self._destination_item, check_point))) and self._destination_collision_offset > 0:
                    self._destination_collision_offset -= 10

            destination_port_label = self._destination_port.label()
            if self._draw_port_labels:
                if destination_port_label is None:
                    destination_port_label = NoteItem(self._destination_item)
                    if not self._destination_port.isStub():
                        destination_port_name = self._destination_port.name().replace(self._destination_port.longNameType(),
                                                                                      self._destination_port.shortNameType())
                    else:
                        destination_port_name = self._destination_port.name()
                    destination_port_label.setPlainText(destination_port_name)
                    destination_port_label.setPos(self.mapToItem(self._destination_item, point2))
                    self._destination_port.setLabel(destination_port_label)

                elif destination_port_label and not destination_port_label.isVisible():
                    destination_port_label.show()

            elif destination_port_label:
                destination_port_label.hide()

            painter.drawPoint(point2)

        self._drawCaptureSymbol()