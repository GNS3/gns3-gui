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
Graphical representation of a Serial link on the QGraphicsScene.
"""

import math
from ..qt import QtCore, QtGui, QtWidgets
from .link_item import LinkItem
from .note_item import NoteItem
from ..ports.port import Port


class SerialLinkItem(LinkItem):

    """
    Serial link for the scene.

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

    def adjust(self):
        """
        Draws a line and computes offsets for status points.
        """

        LinkItem.adjust(self)

        if self._hovered:
            self.setPen(QtGui.QPen(QtCore.Qt.red, self._pen_width + 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        else:
            self.setPen(QtGui.QPen(QtCore.Qt.darkRed, self._pen_width, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

        # get source to destination angle
        vector_angle = math.atan2(self.dy, self.dx)

        # get minimum vector and its angle
        rot_angle = - math.pi / 4.0
        vectrot = QtCore.QPointF(math.cos(vector_angle + rot_angle), math.sin(vector_angle + rot_angle))

        # get the rotated point positions
        angle_source = QtCore.QPointF(self.source.x() + self.dx / 2.0 + 15 * vectrot.x(), self.source.y() + self.dy / 2.0 + 15 * vectrot.y())
        angle_destination = QtCore.QPointF(self.destination.x() - self.dx / 2.0 - 15 * vectrot.x(), self.destination.y() - self.dy / 2.0 - 15 * vectrot.y())

        # draw the path
        self.path = QtGui.QPainterPath(self.source)
        self.path.lineTo(angle_source)
        self.path.lineTo(angle_destination)
        self.path.lineTo(self.destination)
        self.setPath(self.path)

        # set the interface status points positions
        scale_vect = QtCore.QPointF(angle_source.x() - self.source.x(), angle_source.y() - self.source.y())
        scale_vect_diag = math.sqrt(scale_vect.x() ** 2 + scale_vect.y() ** 2)
        scale_coef = scale_vect_diag / 40.0

        self.source_point = QtCore.QPointF(self.source.x() + scale_vect.x() / scale_coef, self.source.y() + scale_vect.y() / scale_coef)
        self.destination_point = QtCore.QPointF(self.destination.x() - scale_vect.x() / scale_coef, self.destination.y() - scale_vect.y() / scale_coef)

    def shape(self):
        """
        Returns the shape of the item to the scene renderer.

        :returns: QPainterPath instance
        """

        path = QtWidgets.QGraphicsPathItem.shape(self)
        offset = self._point_size / 2
        point = self.source_point
        path.addEllipse(point.x() - offset, point.y() - offset, self._point_size, self._point_size)
        point = self.destination_point
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
            if self.length < 80:
                return

            # source point color
            if self._source_port.status() == Port.started:
                # port is active
                color = QtCore.Qt.green
            elif self._source_port.status() == Port.suspended:
                # port is suspended
                color = QtCore.Qt.yellow
            else:
                color = QtCore.Qt.red

            painter.setPen(QtGui.QPen(color, self._point_size, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.MiterJoin))

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
                    source_port_label.setPos(self.mapToItem(self._source_item, self.source))
                    self._source_port.setLabel(source_port_label)

                elif source_port_label and not source_port_label.isVisible():
                    source_port_label.show()

            elif source_port_label:
                source_port_label.hide()

            painter.drawPoint(self.source_point)

            # destination point color
            if self._destination_port.status() == Port.started:
                # port is active
                color = QtCore.Qt.green
            elif self._destination_port.status() == Port.suspended:
                # port is suspended
                color = QtCore.Qt.yellow
            else:
                color = QtCore.Qt.red

            painter.setPen(QtGui.QPen(color, self._point_size, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.MiterJoin))

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
                    destination_port_label.setPos(self.mapToItem(self._destination_item, self.destination))
                    self._destination_port.setLabel(destination_port_label)

                elif destination_port_label and not destination_port_label.isVisible():
                    destination_port_label.show()

            elif destination_port_label:
                destination_port_label.hide()

            painter.drawPoint(self.destination_point)

        self._drawCaptureSymbol()
