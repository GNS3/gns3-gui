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
import struct
import sys
from ..qt import QtCore, QtGui, QtWidgets, QtSvg

from ..node import Node


class SvgCaptureItem(QtSvg.QGraphicsSvgItem):

    def __init__(self, symbol, parent):

        QtSvg.QGraphicsSvgItem.__init__(self, symbol, parent)

    def mousePressEvent(self, event):

        self.parentItem().mousePressEvent(event)
        event.accept()


class LinkItem(QtWidgets.QGraphicsPathItem):

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

    _draw_port_labels = False

    def __init__(self, source_item, source_port, destination_item, destination_port, link=None, adding_flag=False, multilink=0):

        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)
        self._link = None

        from ..main_window import MainWindow
        self._main_window = MainWindow.instance()
        self._settings = self._main_window.uiGraphicsView.settings()

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

        # indicates if the link is being hovered
        self._hovered = False

        # QGraphicsSvgItem to indicate a capture
        self._capturing_item = None

        if not self._adding_flag:
            # there is a destination
            self._link = link
            self.setFlag(self.ItemIsFocusable)
            source_item.addLink(self)
            destination_item.addLink(self)
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

        if not self._source_port.isHotPluggable() and self._source_item.node().status() == Node.started:
            QtWidgets.QMessageBox.critical(self._main_window, "Connection", "A link cannot be removed because {} is running".format(self._source_item.node().name()))
            return False
        elif not self._destination_port.isHotPluggable() and self._destination_item.node().status() == Node.started:
            QtWidgets.QMessageBox.critical(self._main_window, "Connection", "A link cannot be removed because {} is running".format(self._destination_item.node().name()))
            return False

        # first delete the port labels if any
        if self._source_port.label():
            self._source_port.label().setParentItem(None)
            self.scene().removeItem(self._source_port.label())
        if self._destination_port.label():
            self._destination_port.label().setParentItem(None)
            self.scene().removeItem(self._destination_port.label())

        self._source_item.removeLink(self)
        self._destination_item.removeLink(self)
        self._link.deleteLink()
        if self in self.scene().items():
            self.scene().removeItem(self)

    def link(self):
        """
        Returns the link attached to this link item.

        :returns: Link instance
        """

        return self._link

    def setCustomToolTip(self):
        """
        Sets a custom tool tip for this link.
        """

        if self._link:
            self.setToolTip(str(self._link))

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

    @classmethod
    def showPortLabels(cls, state):
        """
        Shows or hides port labels.

        :param state: boolean
        """

        cls._draw_port_labels = state

    def resetPortLabels(self):
        """
        Resets the port label positions.
        """

        self._source_port.deleteLabel()
        self._destination_port.deleteLabel()

    def populateLinkContextualMenu(self, menu):
        """
        Adds device actions to the link contextual menu.

        :param menu: QMenu instance
        """

        if not self._source_port.capturing() or not self._destination_port.capturing():
            # start capture
            start_capture_action = QtWidgets.QAction("Start capture", menu)
            start_capture_action.setIcon(QtGui.QIcon(':/icons/capture-start.svg'))
            start_capture_action.triggered.connect(self._startCaptureActionSlot)
            menu.addAction(start_capture_action)

        if self._source_port.capturing() or self._destination_port.capturing():
            # stop capture
            stop_capture_action = QtWidgets.QAction("Stop capture", menu)
            stop_capture_action.setIcon(QtGui.QIcon(':/icons/capture-stop.svg'))
            stop_capture_action.triggered.connect(self._stopCaptureActionSlot)
            menu.addAction(stop_capture_action)

            # start wireshark
            start_wireshark_action = QtWidgets.QAction("Start Wireshark", menu)
            start_wireshark_action.setIcon(QtGui.QIcon(":/icons/wireshark.png"))
            start_wireshark_action.triggered.connect(self._startWiresharkActionSlot)
            menu.addAction(start_wireshark_action)

            if sys.platform.startswith("win") and struct.calcsize("P") * 8 == 64:
                # Windows 64-bit only (Solarwinds RTV limitation).
                analyze_action = QtWidgets.QAction("Analyze capture", menu)
                analyze_action.setIcon(QtGui.QIcon(':/icons/rtv.png'))
                analyze_action.triggered.connect(self._analyzeCaptureActionSlot)
                menu.addAction(analyze_action)

        # delete
        delete_action = QtWidgets.QAction("Delete", menu)
        delete_action.setIcon(QtGui.QIcon(':/icons/delete.svg'))
        delete_action.triggered.connect(self._deleteActionSlot)
        menu.addAction(delete_action)

    def mousePressEvent(self, event):
        """
        Called when the link is clicked and shows a contextual menu.

        :param: QGraphicsSceneMouseEvent instance
        """

        if event.button() == QtCore.Qt.RightButton:
            if self._adding_flag:
                # send a escape key to the main window to cancel the link addition
                from ..main_window import MainWindow
                key = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Escape, QtCore.Qt.NoModifier)
                QtWidgets.QApplication.sendEvent(MainWindow.instance(), key)
                return

            # create the contextual menu
            self.setAcceptHoverEvents(False)
            menu = QtWidgets.QMenu()
            self.populateLinkContextualMenu(menu)
            menu.exec_(QtGui.QCursor.pos())
            self.setAcceptHoverEvents(True)
            self._hovered = False
            self.adjust()

    def keyPressEvent(self, event):
        """
        Handles all key press events

        :param event: QKeyEvent
        """

        # On pressing backspace or delete key, the selected link gets deleted
        if event.key() == QtCore.Qt.Key_Delete or event.key() == QtCore.Qt.Key_Backspace:
            self._deleteActionSlot()
            return

    def _deleteActionSlot(self):
        """
        Slot to receive events from the delete action in the
        contextual menu.
        """

        self.delete()

    def _startCaptureActionSlot(self):
        """
        Slot to receive events from the start capture action in the
        contextual menu.
        """

        ports = {}
        if self._source_port.packetCaptureSupported() and not self._source_port.capturing():
            for dlt_name, dlt in self._source_port.dataLinkTypes().items():
                port = "{} port {} ({} encapsulation: {})".format(self._source_item.node().name(), self._source_port.name(), dlt_name, dlt)
                ports[port] = [self._source_item.node(), self._source_port, dlt]

        if self._destination_port.packetCaptureSupported() and not self._destination_port.capturing():
            for dlt_name, dlt in self._destination_port.dataLinkTypes().items():
                port = "{} port {} ({} encapsulation: {})".format(self._destination_item.node().name(), self._destination_port.name(), dlt_name, dlt)
                ports[port] = [self._destination_item.node(), self._destination_port, dlt]

        if not ports:
            QtWidgets.QMessageBox.critical(self._main_window, "Packet capture", "Packet capture is not supported on this link")
            return

        selection, ok = QtWidgets.QInputDialog.getItem(self._main_window, "Packet capture", "Please select a port:", list(ports.keys()), 0, False)
        if ok:
            if selection in ports:
                node, port, dlt = ports[selection]
                node.startPacketCapture(port, port.captureFileName(node.name()), dlt)

    def _stopCaptureActionSlot(self):
        """
        Slot to receive events from the stop capture action in the
        contextual menu.
        """

        if self._source_port.capturing() and self._destination_port.capturing():
            ports = {}
            source_port = "{} port {}".format(self._source_item.node().name(), self._source_port.name())
            ports[source_port] = [self._source_item.node(), self._source_port]
            destination_port = "{} port {}".format(self._destination_item.node().name(), self._destination_port.name())
            ports[destination_port] = [self._destination_item.node(), self._destination_port]
            selection, ok = QtWidgets.QInputDialog.getItem(self._main_window, "Packet capture", "Please select a port:", list(ports.keys()), 0, False)
            if ok:
                if selection in ports:
                    node, port = ports[selection]
                    node.stopPacketCapture(port)
        elif self._source_port.capturing():
            self._source_item.node().stopPacketCapture(self._source_port)
        elif self._destination_port.capturing():
            self._destination_item.node().stopPacketCapture(self._destination_port)

    def _startWiresharkActionSlot(self):
        """
        Slot to receive events from the start Wireshark action in the
        contextual menu.
        """

        try:
            if self._source_port.capturing() and self._destination_port.capturing():
                ports = ["{} port {}".format(self._source_item.node().name(), self._source_port.name()),
                         "{} port {}".format(self._destination_item.node().name(), self._destination_port.name())]
                selection, ok = QtWidgets.QInputDialog.getItem(self._main_window, "Packet capture", "Please select a port:", ports, 0, False)
                if ok:
                    if selection.endswith(self._source_port.name()):
                        self._source_port.startPacketCaptureReader(self._source_item.node().name())
                    else:
                        self._destination_port.startPacketCaptureReader(self._destination_item.node().name())
            elif self._source_port.capturing():
                self._source_port.startPacketCaptureReader(self._source_item.node().name())
            elif self._destination_port.capturing():
                self._destination_port.startPacketCaptureReader(self._destination_item.node().name())
        except OSError as e:
            QtWidgets.QMessageBox.critical(self._main_window, "Packet capture", "Cannot start Wireshark: {}".format(e))

    def _analyzeCaptureActionSlot(self):
        """
        Slot to receive events from the analyze capture action in the
        contextual menu.
        """

        try:
            if self._source_port.capturing() and self._destination_port.capturing():
                ports = ["{} port {}".format(self._source_item.node().name(), self._source_port.name()),
                         "{} port {}".format(self._destination_item.node().name(), self._destination_port.name())]
                selection, ok = QtWidgets.QInputDialog.getItem(self._main_window, "Capture analyzer", "Please select a port:", ports, 0, False)
                if ok:
                    if selection.endswith(self._source_port.name()):
                        self._source_port.startPacketCaptureAnalyzer()
                    else:
                        self._destination_port.startPacketCaptureAnalyzer()
            elif self._source_port.capturing():
                self._source_port.startPacketCaptureAnalyzer()
            elif self._destination_port.capturing():
                self._destination_port.startPacketCaptureAnalyzer()
        except OSError as e:
            QtWidgets.QMessageBox.critical(self._main_window, "Capture analyzer", "Cannot start the packet capture analyzer program: {}".format(e))

    def setHovered(self, value):
        """
        Sets the link as hovered or not.

        :param value: boolean
        """

        if value:
            self._hovered = True
        else:
            self._hovered = False
        self.adjust()

    def hoverEnterEvent(self, event):
        """
        Handles all hover enter events for this item.

        :param event: QGraphicsSceneHoverEvent instance
        """

        self.setHovered(True)

    def hoverLeaveEvent(self, event):
        """
        Handles all hover leave events for this item.

        :param event: QGraphicsSceneHoverEvent instance
        """

        self.setHovered(False)

    def adjust(self):
        """
        Computes the source point and destination point.
        Must be overloaded.
        """

        # links must always be below node items on the scene
        if not self._adding_flag:
            min_zvalue = min([self._source_item.zValue(), self._destination_item.zValue()])
            self.setZValue(min_zvalue - 1)

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

    def _drawCaptureSymbol(self):
        """
        Draws a capture symbol in the middle of the link to indicate a capture is active.
        """

        if not self._adding_flag:
            if (self._source_port.capturing() or self._destination_port.capturing()) and self.length >= 150:
                link_center = QtCore.QPointF(self.source.x() + self.dx / 2.0 - 11, self.source.y() + self.dy / 2.0 - 11)
                if self._capturing_item is None:
                    self._capturing_item = SvgCaptureItem(':/icons/inspect.svg', self)
                    self._capturing_item.setScale(0.6)
                self._capturing_item.setPos(link_center)
                if not self._capturing_item.isVisible():
                    self._capturing_item.show()
            elif self._capturing_item:
                self._capturing_item.hide()
