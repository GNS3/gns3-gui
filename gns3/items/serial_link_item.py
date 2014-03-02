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
from ..qt import QtCore, QtGui
from .link_item import LinkItem
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

        LinkItem.__init__(self, source_item, source_port, destination_item, destination_port, link, adding_flag, multilink)
        self.setPen(QtGui.QPen(QtCore.Qt.red, self._pen_width, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

    def adjust(self):
        """
        Draws a line and computes offsets for status points.
        """

        LinkItem.adjust(self)

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

        self.source = QtCore.QPointF(self.source.x() + scale_vect.x() / scale_coef, self.source.y() + scale_vect.y() / scale_coef)
        self.destination = QtCore.QPointF(self.destination.x() - scale_vect.x() / scale_coef, self.destination.y() - scale_vect.y() / scale_coef)

    def shape(self):
        """
        Returns the shape of the item to the scene renderer.

        :returns: QPainterPath instance
        """

        path = QtGui.QGraphicsPathItem.shape(self)
        offset = self._point_size / 2
        point = self.source
        path.addEllipse(point.x() - offset, point.y() - offset, self._point_size, self._point_size)
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

        QtGui.QGraphicsPathItem.paint(self, painter, option, widget)

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

#TODO: draw port labels
#             if globals.GApp.workspace.flg_showInterfaceNames:
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
#                         self.labelSouceIf.setPos(self.mapToItem(self.source, self.src))
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

            painter.drawPoint(self.source)
            #painter.drawPoint(self.source)

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

#TODO: draw port labels
#             if globals.GApp.workspace.flg_showInterfaceNames:
#                 if self.labelDestIf  == None:
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
#                         self.labelDestIf.setPos(self.mapToItem(self.dest, self.dst))
#                         #self.labelDestIf.autoGenerated = True
# 
#                     if self.labelDestIf:
#                         self.labelDestIf.deviceName = self.dest.hostname
#                         self.labelDestIf.deviceIf = self.destIf
# 
#                 if self.labelDestIf and not self.labelDestIf.isVisible():
#                     self.labelDestIf.show()
# 
# 
#             elif self.labelDestIf and globals.GApp.workspace.flg_showInterfaceNames == False:
#                 self.labelDestIf.hide()

            painter.drawPoint(self.destination)
