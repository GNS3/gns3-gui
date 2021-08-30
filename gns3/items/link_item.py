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
from ..qt import QtCore, QtGui, QtWidgets, QtSvg, qslot, sip_is_deleted

from ..packet_capture import PacketCapture
from ..dialogs.filter_dialog import FilterDialog
from ..dialogs.style_editor_dialog_link import StyleEditorDialogLink
from ..utils.get_icon import get_icon


class SvgIconItem(QtSvg.QGraphicsSvgItem):

    def __init__(self, symbol, parent):

        QtSvg.QGraphicsSvgItem.__init__(self, symbol, parent)

    def mousePressEvent(self, event):

        if self.parentItem():
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
    """

    _draw_port_labels = False
    delete_link_item_signal = QtCore.pyqtSignal(str)

    def __init__(self, source_item, source_port, destination_item, destination_port, link=None, adding_flag=False):

        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setZValue(-0.5)
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

        # source & destination items and ports
        self._source_item = source_item
        self._destination_item = destination_item
        self._source_port = source_port
        self._destination_port = destination_port

        # indicates if the link is being hovered
        self._hovered = False

        # QGraphicsSvgItem to indicate a capture
        self._capturing_item = None
        # QGraphicsSvgItem to indicate a filter is applied
        self._filter_item = None
        # QGraphicsSvgItem to indicate we suspend a link
        self._suspend_item = None
        # QGraphicsSvgItem to indicate a filter is applied and a capture is active
        self._filter_capturing_item = None

        if not self._adding_flag:
            # there is a destination
            self._link = link
            self._link.updated_link_signal.connect(self._drawSymbol)
            self._link.delete_link_signal.connect(self._linkDeletedSlot)
            self.setFlag(self.ItemIsFocusable)
            source_item.addLink(self)
            destination_item.addLink(self)
            self.setCustomToolTip()
        else:
            source_rect = self._source_item.boundingRect()
            self.source = self.mapFromItem(self._source_item, source_rect.width() / 2.0, source_rect.height() / 2.0)
            self.destination = self._destination_item

        self.adjust()

    @qslot
    def _linkDeletedSlot(self, link_id, *args):
        # first delete the port labels if any

        if self._source_port.label():
            self._source_port.label().setParentItem(None)
            self.scene().removeItem(self._source_port.label())
        if self._destination_port.label():
            self._destination_port.label().setParentItem(None)
            self.scene().removeItem(self._destination_port.label())

        if self.scene():
            if self in self.scene().items():
                self.scene().removeItem(self)

    @qslot
    def _filterActionSlot(self, *args):
        dialog = FilterDialog(self._main_window, self._link)
        dialog.show()
        dialog.exec_()

    @qslot
    def _suspendActionSlot(self, *args):
        self._link.toggleSuspend()

    @qslot
    def _styleActionSlot(self, *args):
        style_dialog = StyleEditorDialogLink(self, self._main_window)
        style_dialog.show()
        style_dialog.exec_()

    def setLinkStyle(self, link_style):
        self._link._link_style["color"] = link_style["color"]
        self._link._link_style["width"] = link_style["width"]
        self._link._link_style["type"]  = link_style["type"]

        # This refers to functions in link.py!
        self._link.setLinkStyle(link_style)
        self._link.update()

    def delete(self):
        """
        Delete this link
        """
        self._link.deleteLink()

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

        if not self._link.capturing():
            # start capture
            start_capture_action = QtWidgets.QAction("Start capture", menu)
            start_capture_action.setIcon(get_icon('capture-start.svg'))
            start_capture_action.triggered.connect(self._startCaptureActionSlot)
            menu.addAction(start_capture_action)

        if self._link.capturing():
            # stop capture
            stop_capture_action = QtWidgets.QAction("Stop capture", menu)
            stop_capture_action.setIcon(get_icon('capture-stop.svg'))
            stop_capture_action.triggered.connect(self._stopCaptureActionSlot)
            menu.addAction(stop_capture_action)

            # start wireshark
            start_wireshark_action = QtWidgets.QAction("Start Wireshark", menu)
            start_wireshark_action.setIcon(QtGui.QIcon(":/icons/wireshark.png"))
            start_wireshark_action.triggered.connect(self._startWiresharkActionSlot)
            menu.addAction(start_wireshark_action)

            if PacketCapture.instance().packetAnalyzerAvailable():
                analyze_action = QtWidgets.QAction("Analyze capture", menu)
                analyze_action.setIcon(QtGui.QIcon(':/icons/rtv.png'))
                analyze_action.triggered.connect(self._analyzeCaptureActionSlot)
                menu.addAction(analyze_action)

        if self._link.suspended() is False:
            # Edit filters
            filter_action = QtWidgets.QAction("Packet filters", menu)
            filter_action.setIcon(get_icon('filter.svg'))
            filter_action.triggered.connect(self._filterActionSlot)
            menu.addAction(filter_action)

            # Suspend link
            suspend_action = QtWidgets.QAction("Suspend", menu)
            suspend_action.setIcon(get_icon('pause.svg'))
            suspend_action.triggered.connect(self._suspendActionSlot)
            menu.addAction(suspend_action)
        else:
            # Resume link
            resume_action = QtWidgets.QAction("Resume", menu)
            resume_action.setIcon(get_icon('start.svg'))
            resume_action.triggered.connect(self._suspendActionSlot)
            menu.addAction(resume_action)

        # style
        style_action = QtWidgets.QAction("Style", menu)
        style_action.setIcon(get_icon("node_conception.svg"))
        style_action.triggered.connect(self._styleActionSlot)
        menu.addAction(style_action)

        # delete
        delete_action = QtWidgets.QAction("Delete", menu)
        delete_action.setIcon(get_icon('delete.svg'))
        delete_action.triggered.connect(self._deleteActionSlot)
        menu.addAction(delete_action)

    @qslot
    def mousePressEvent(self, event):
        """
        Called when the link is clicked and shows a contextual menu.

        :param: QGraphicsSceneMouseEvent instance
        """

        if event.button() == QtCore.Qt.RightButton and self._adding_flag:
            # send a escape key to the main window to cancel the link addition
            from ..main_window import MainWindow
            key = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Escape, QtCore.Qt.NoModifier)
            QtWidgets.QApplication.sendEvent(MainWindow.instance(), key)
            return
        else:
            super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        """
        Handles all context menu events.

        :param event: QContextMenuEvent instance
        """

        if not sip_is_deleted(self):
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

        PacketCapture.instance().startCapture(self._link)

    def _stopCaptureActionSlot(self):
        """
        Slot to receive events from the stop capture action in the
        contextual menu.
        """

        PacketCapture.instance().stopCapture(self._link)

    def _startWiresharkActionSlot(self):
        """
        Slot to receive events from the start Wireshark action in the
        contextual menu.
        """

        PacketCapture.instance().startPacketCaptureReader(self._link)

    def _analyzeCaptureActionSlot(self):
        """
        Slot to receive events from the analyze capture action in the
        contextual menu.
        """

        try:
            PacketCapture.instance().startPacketCaptureAnalyzer(self._link)
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

    @qslot
    def adjust(self):
        """
        Computes the source point and destination point.
        Must be overloaded.
        """

        # links must always be below node items on the scene
        if not self._adding_flag:
            min_zvalue = min([self._source_item.zValue(), self._destination_item.zValue()])
            self.setZValue(min_zvalue - 0.5)

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

        multilink = self._computeMultiLink()

        # multi-link management
        if not self._adding_flag and multilink and self.length:
            angle = math.radians(90)
            self.dxrot = math.cos(angle) * self.dx - math.sin(angle) * self.dy
            self.dyrot = math.sin(angle) * self.dx + math.cos(angle) * self.dy
            offset = QtCore.QPointF((self.dxrot * (multilink * 5)) / self.length, (self.dyrot * (multilink * 5)) / self.length)
            self.source = QtCore.QPointF(self.source + offset)
            self.destination = QtCore.QPointF(self.destination + offset)

    def _computeMultiLink(self):
        # Multi-link management
        #
        # multi is the offset of the link
        # +------+       multi = -1    Link 2  +-------+
        # |      +-----------------------------+       |
        # |  R1  |                             |   R2  |
        # |      |        multi = 0    Link 1  |       |
        # |      +-----------------------------+       |
        # |      |        multi = 1    Link 3  |       |
        # +------+-----------------------------+-------+

        if self._source_item == self._destination_item:
            multi = 0
        elif not hasattr(self._destination_item, "node"):  # Could be temporary a qpointf during link creation
            multi = 0
        else:
            multi = 0
            link_items = self._source_item.links()
            for link_item in link_items:
                if link_item == self:
                    break
                if link_item.destinationItem().node().id() == self._destination_item.node().id():
                    multi += 1
                if link_item.sourceItem().node().id() == self._destination_item.node().id():
                    multi += 1

        # MAX 7 links on the scene between 2 nodes
        if multi > 7:
            multi = 0
        # Pair item represent the bottom links
        elif multi % 2 == 0:
            multi = multi // 2
        else:
            multi = -multi // 2
        return multi

    def setMousePoint(self, scene_point):
        """
        Sets new mouse point coordinates.
        Used when adding a link and the destination is not yet chosen.

        :param scene_point: event position
        """

        self.destination = scene_point
        self.adjust()
        self.update()

    @qslot
    def _drawSymbol(self, *args):
        """
        Draws a symbol in the middle of the link to indicate a capture, a suspend or a filter is active.
        """

        #FIXME: refactor ugly symbol management
        if not self._adding_flag:

            if self._link.suspended():
                if self.length >= 150:
                    link_center = QtCore.QPointF(self.source.x() + self.dx / 2.0 - 11, self.source.y() + self.dy / 2.0 - 11)
                    if self._suspend_item is None:
                        self._suspend_item = SvgIconItem(':/icons/pause.svg', self)
                        self._suspend_item.setScale(0.6)
                    if not self._suspend_item.isVisible():
                        self._suspend_item.show()
                    self._suspend_item.setPos(link_center)
                    if self._filter_item:
                        self._filter_item.hide()
                elif self._suspend_item:
                    self._suspend_item.hide()
                if self._filter_capturing_item:
                    self._filter_capturing_item.hide()
                if self._capturing_item:
                    self._capturing_item.hide()
                if self._filter_item:
                    self._filter_item.hide()

            elif self._link.capturing() and len(self._link.filters()) > 0:
                if self.length >= 150:
                    link_center = QtCore.QPointF(self.source.x() + self.dx / 2.0 - 11, self.source.y() + self.dy / 2.0 - 11)
                    if self._filter_capturing_item is None:
                        self._filter_capturing_item = SvgIconItem(':/icons/filter-capture.svg', self)
                        self._filter_capturing_item.setScale(0.6)
                    if not self._filter_capturing_item.isVisible():
                        self._filter_capturing_item.show()
                    self._filter_capturing_item.setPos(link_center)
                elif self._filter_capturing_item:
                    self._filter_capturing_item.hide()
                if self._capturing_item:
                    self._capturing_item.hide()
                if self._filter_item:
                    self._filter_item.hide()
                if self._suspend_item:
                    self._suspend_item.hide()

            elif self._link.capturing():
                if self.length >= 150:
                    link_center = QtCore.QPointF(self.source.x() + self.dx / 2.0 - 11, self.source.y() + self.dy / 2.0 - 11)
                    if self._capturing_item is None:
                        self._capturing_item = SvgIconItem(':/icons/inspect.svg', self)
                        self._capturing_item.setScale(0.6)
                    self._capturing_item.setPos(link_center)
                    if not self._capturing_item.isVisible():
                        self._capturing_item.show()
                elif self._capturing_item:
                    self._capturing_item.hide()
                if self._filter_capturing_item:
                    self._filter_capturing_item.hide()
                if self._suspend_item:
                    self._suspend_item.hide()

            elif len(self._link.filters()) > 0:
                if self.length >= 150:
                    link_center = QtCore.QPointF(self.source.x() + self.dx / 2.0 - 11, self.source.y() + self.dy / 2.0 - 11)
                    if self._filter_item is None:
                        self._filter_item = SvgIconItem(':/icons/filter.svg', self)
                        self._filter_item.setScale(0.6)
                    if not self._filter_item.isVisible():
                        self._filter_item.show()
                    self._filter_item.setPos(link_center)
                elif self._filter_item:
                    self._filter_item.hide()
                if self._filter_capturing_item:
                    self._filter_capturing_item.hide()
                if self._suspend_item:
                    self._suspend_item.hide()

            else:
                if self._capturing_item:
                    self._capturing_item.hide()
                if self._suspend_item:
                    self._suspend_item.hide()
                if self._filter_item:
                    self._filter_item.hide()
                if self._filter_capturing_item:
                    self._filter_capturing_item.hide()
