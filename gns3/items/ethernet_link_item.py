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

from ..qt import QtCore, QtGui
from .link_item import LinkItem


class EthernetLinkItem(LinkItem):
    """
    Ethernet link for the scene.

    :param source_item: source NodeItem object
    :param source_port: source Port object
    :param destination_item: destination NodeItem object
    :param destination_port: destination Port object
    :param link: Link object (contains back-end stuff for this link)
    :param adding_flag: indicates if this link is being added (no destination yet)
    :param multilink: used to draw multiple link between the same source and destination
    """

    def __init__(self, source_item, source_port, destination_item, destination_port, link=None, adding_flag=False, multilink=0):

        LinkItem.__init__(self, source_item, source_port, destination_item, destination_port, link, adding_flag, multilink)
        self.setPen(QtGui.QPen(QtCore.Qt.black, self._pen_width, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        self._source_collision_offset = 0.0
        self._destination_collision_offset = 0.0

    def adjust(self):
        """
        Draws a line and compute offsets for status points.
        """

        LinkItem.adjust(self)

        # draw a line between nodes
        self.path = QtGui.QPainterPath(self.source)
        self.path.lineTo(self.destination)
        self.setPath(self.path)

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

        path = QtGui.QGraphicsPathItem.shape(self)
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

        :param painter: QPainter object
        :param option: QStyleOptionGraphicsItem object
        :param widget: QWidget object.
        """

        QtGui.QGraphicsPathItem.paint(self, painter, option, widget)

        if not self._adding_flag and self._show_status_points:

            # points disappears if nodes are too close to each others.
            if self.length < 100:
                return

            if self._source_port_status == 'up':
                color = QtCore.Qt.green
            elif self._source_port_status == 'suspended':
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

#TODO: draw port labels
#             if self._show_port_names:
#                 if self.labelSouceIf == None:
#  
#                     if globals.interfaceLabels.has_key(self.source.hostname + ' ' + self.srcIf):
#                         self.labelSouceIf = Annotation(self.source)
#                         annotation = globals.interfaceLabels[self.source.hostname + ' ' + self.srcIf]
#                         self.labelSouceIf.setZValue(annotation.zValue())
#                         self.labelSouceIf.setDefaultTextColor(annotation.defaultTextColor())
#                         self.labelSouceIf.setFont(annotation.font())
#                         self.labelSouceIf.setPlainText(annotation.toPlainText())
#                         self.labelSouceIf.setPos(annotation.x(), annotation.y())
#                         self.labelSouceIf.rotation = annotation.rotation
#                         self.labelSouceIf.rotate(annotation.rotation)
#                         del globals.interfaceLabels[self.source.hostname + ' ' + self.srcIf]
#                     elif not globals.GApp.workspace.flg_showOnlySavedInterfaceNames:
#                         self.labelSouceIf = Annotation(self.source)
#                         self.labelSouceIf.setPlainText(self.srcIf)
#                         self.labelSouceIf.setPos(self.mapToItem(self.source, point1))
#                         #self.labelSouceIf.autoGenerated = True
#  
#                     if self.labelSouceIf:
#                         self.labelSouceIf.deviceName = self.source.hostname
#                         self.labelSouceIf.deviceIf = self.srcIf
#  
#                 if self.labelSouceIf and not self.labelSouceIf.isVisible():
#                     self.labelSouceIf.show()
#  
#             elif self.labelSouceIf and globals.GApp.workspace.flg_showInterfaceNames == False:
#                 self.labelSouceIf.hide()

            painter.drawPoint(point1)

            if self._destination_port_status == 'up':
                color = QtCore.Qt.green
            elif self._destination_port_status == 'suspended':
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

#TODO: draw port labels
#             if globals.GApp.workspace.flg_showInterfaceNames:
#                 if self.labelDestIf == None:
# 
#                     if globals.interfaceLabels.has_key(self.dest.hostname + ' ' + self.destIf):
#                         self.labelDestIf = Annotation(self.dest)
#                         annotation = globals.interfaceLabels[self.dest.hostname + ' ' + self.destIf]
#                         self.labelDestIf.setZValue(annotation.zValue())
#                         self.labelDestIf.setDefaultTextColor(annotation.defaultTextColor())
#                         self.labelDestIf.setFont(annotation.font())
#                         self.labelDestIf.setPlainText(annotation.toPlainText())
#                         self.labelDestIf.setPos(annotation.x(), annotation.y())
#                         self.labelDestIf.rotation = annotation.rotation
#                         self.labelDestIf.rotate(annotation.rotation)
#                         del globals.interfaceLabels[self.dest.hostname + ' ' + self.destIf]
#                     elif not globals.GApp.workspace.flg_showOnlySavedInterfaceNames:
#                         self.labelDestIf = Annotation(self.dest)
#                         self.labelDestIf.setPlainText(self.destIf)
#                         self.labelDestIf.setPos(self.mapToItem(self.dest, point2))
#                         #self.labelDestIf.autoGenerated = True
# 
#                     if self.labelDestIf:
#                         self.labelDestIf.deviceName = self.dest.hostname
#                         self.labelDestIf.deviceIf = self.destIf
# 
#                 if self.labelDestIf and not self.labelDestIf.isVisible():
#                     self.labelDestIf.show()
# 
#             elif self.labelDestIf and globals.GApp.workspace.flg_showInterfaceNames == False:
#                 self.labelDestIf.hide()

            painter.drawPoint(point2)
