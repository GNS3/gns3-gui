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
Graphical representation of a node on the QGraphicsScene.
"""

import sip

from ..qt import QtCore, QtGui, QtWidgets, QtSvg, qslot
from ..qt.qimage_svg_renderer import QImageSvgRenderer
from .note_item import NoteItem
from ..symbol import Symbol
from ..controller import Controller


import logging
log = logging.getLogger(__name__)


class NodeItem(QtSvg.QGraphicsSvgItem):

    """
    Node for the scene.

    :param node: Node instance
    """

    show_layer = False
    GRID_SIZE = 75

    def __init__(self, node):
        super().__init__()

        # attached node
        self._node = node
        # link items connected to this node item.
        self._links = []
        self._symbol = None

        # says if the attached node has been initialized
        # by the server.
        self._initialized = False

        # node label
        self._node_label = None

        self.setPos(QtCore.QPoint(self._node.x(), self._node.y()))
        self.setZValue(self._node.z())

        # Temporary symbol during loading
        renderer = QImageSvgRenderer(":/icons/reload.svg")
        renderer.setObjectName("symbol_loading")
        self.setSharedRenderer(renderer)

        effect = QtWidgets.QGraphicsColorizeEffect()
        effect.setColor(QtGui.QColor("black"))
        effect.setStrength(0.8)
        self.setGraphicsEffect(effect)
        self.graphicsEffect().setEnabled(False)

        # set graphical settings for this node
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # connect signals to know about some events
        # e.g. when the node has been started, stopped or suspended etc.
        node.created_signal.connect(self.createdSlot)
        node.started_signal.connect(self.startedSlot)
        node.stopped_signal.connect(self.stoppedSlot)
        node.suspended_signal.connect(self.suspendedSlot)
        node.updated_signal.connect(self.updatedSlot)
        node.deleted_signal.connect(self.deletedSlot)
        node.error_signal.connect(self.errorSlot)
        node.server_error_signal.connect(self.serverErrorSlot)

        # used when a port has been selected from the contextual menu
        self._selected_port = None

        # contains the last error message received
        # from the server.
        self._last_error = None

        from ..main_window import MainWindow
        self._main_window = MainWindow.instance()
        if self._main_window.uiSnapToGridAction.isChecked():
            self._snapToGrid()
        self._settings = self._main_window.uiGraphicsView.settings()

        if node.initialized():
            self.createdSlot(node.id())

    def _snapToGrid(self):
        mid_x = self.boundingRect().width() / 2
        x = (self.GRID_SIZE * round((self.x() + mid_x) / self.GRID_SIZE)) - mid_x
        mid_y = self.boundingRect().height() / 2
        y = (self.GRID_SIZE * round((self.y() + mid_y) / self.GRID_SIZE)) - mid_y
        self.setPos(x, y)

    def updateNode(self):
        """
        Sync change to the node
        """
        if self._initialized:
            self._node.setGraphics(self)

    @qslot
    def setSymbol(self, symbol):
        """
        :param symbol: Change the symbol path
        """
        # create renderer using symbols path/resource
        if symbol is None:
            symbol = self._node.defaultSymbol()
        if self._symbol != symbol:
            self._symbol = symbol

            # Temporary symbol during loading
            renderer = QImageSvgRenderer(":/icons/reload.svg")
            renderer.setObjectName("symbol_loading")
            self.setSharedRenderer(renderer)

            Controller.instance().getStatic(Symbol(symbol_id=symbol).url(), self._symbolLoadedCallback)

    def symbol(self):
        return self._symbol

    @qslot
    def _symbolLoadedCallback(self, path, *args):
        renderer = QImageSvgRenderer(path, fallback=":/icons/cancel.svg")
        renderer.setObjectName(path)
        self.setSharedRenderer(renderer)
        if self._node.settings().get("symbol") != self._symbol:
            self.updateNode()
        if not self._initialized:
            self._showLabel()
            self._initialized = True
            self.updateNode()

    def node(self):
        """
        Returns the node attached to this node item.

        :returns: Node instance
        """

        return self._node

    def setPos(self, *args):
        super().setPos(*args)
        self._node.setSettingValue("x", int(self.x()))
        self._node.setSettingValue("y", int(self.y()))

    @qslot
    def addLink(self, link_item, *args):
        """
        Adds a link items to this node item.

        :param link: LinkItem instance
        """

        if not sip.isdeleted(link_item):
            self._links.append(link_item)
            link_item.link().delete_link_signal.connect(self._removeLink)
            link_item.link().updated_link_signal.connect(self._linkUpdatedSlot)
            self._node.updated_signal.emit()

    @qslot
    def _linkUpdatedSlot(self, *args):
        """
        When a link change we also notify the listener of the node
        """
        self._node.updated_signal.emit()

    @qslot
    def _removeLink(self, link_id, *args):
        """
        Removes a link items from this node item.

        :param link: LinkItem instance
        """

        for link_item in self._links:
            if link_item.link().id() == link_id:
                self._links.remove(link_item)
                return

    def links(self):
        """
        Returns all the link items attached to this node item.

        :returns: list of LinkItem instances
        """

        return self._links

    @qslot
    def createdSlot(self, base_node_id, *args):
        """
        Slot to receive events from the attached Node instance
        when a the node has been created/initialized.

        :param base_node_id: base node identifier (integer)
        """

        self.setPos(QtCore.QPoint(self._node.x(), self._node.y()))
        self.setSymbol(self._node.symbol())
        self.update()

    @qslot
    def startedSlot(self, *args):
        """
        Slot to receive events from the attached Node instance
        when a the node has started.
        """

        for link in self._links:
            link.update()

    @qslot
    def stoppedSlot(self, *args):
        """
        Slot to receive events from the attached Node instance
        when a the node has stopped.
        """

        for link in self._links:
            link.update()

    @qslot
    def suspendedSlot(self, *args):
        """
        Slot to receive events from the attached Node instance
        when a the node has suspended.
        """

        for link in self._links:
            link.update()

    @qslot
    def updatedSlot(self, *args):
        """
        Slot to receive events from the attached Node instance
        when a the node has been updated.
        """

        self.setSymbol(self._node.settings().get("symbol"))
        self.setPos(self._node.settings().get("x", 0), self._node.settings().get("y", 0))
        self.setZValue(self._node.settings().get("z", 0))

        self._updateLabel()

        # update the link tooltips in case the
        # node name has changed
        for link in self._links:
            link.setCustomToolTip()

    @qslot
    def deletedSlot(self, *args):
        """
        Slot to receive events from the attached Node instance
        when the node has been deleted.
        """

        if not self.scene():
            return
        if self in self.scene().items():
            self.scene().removeItem(self)

    @qslot
    def serverErrorSlot(self, base_node_id, message, *args):
        """
        Slot to receive events from the attached Node instance
        when the node has received an error from the server.

        :param base_node_id: base node identifier
        :param message: error message
        """

        self._last_error = "{message}".format(message=message)

    @qslot
    def errorSlot(self, base_node_id, message, *args):
        """
        Slot to receive events from the attached Node instance
        when the node wants to report an error.

        :param base_node_id: base node identifier
        :param message: error message
        """

        self._last_error = "{message}".format(message=message)

    def setCustomToolTip(self):
        """
        Sets a new ToolTip.
        """

        if not self._initialized:
            if not self._last_error:
                error = "unknown error"
            else:
                error = self._last_error
            self.setToolTip("This node isn't initialized\n{}".format(error))
        else:
            self.setToolTip(self._node.info())

    def label(self):
        """
        Returns the node label.

        :return: NoteItem instance.
        """

        return self._node_label

    def _labelUnselectedSlot(self):
        """
        Called when user unselect the label
        """
        self.updateNode()

    def _centerLabel(self):
        """
        Centers the node label.
        """

        text_rect = self._node_label.boundingRect()
        text_middle = text_rect.topRight() / 2
        node_rect = self.boundingRect()
        node_middle = node_rect.topRight() / 2
        label_x_pos = node_middle.x() - text_middle.x()
        label_y_pos = -25
        self._node_label.setPos(label_x_pos, label_y_pos)
        return

    def _showLabel(self):
        """
        Shows the node label on the scene.
        """

        if not self._node_label:
            self._node_label = NoteItem(self)
            self._node_label.item_unselected_signal.connect(self._labelUnselectedSlot)
            self._node_label.setEditable(False)
            self._updateLabel()
            self._node.setSettingValue("label", self._node_label.dump())

    def _updateLabel(self):
        """
        Update the label using the informations stored in the node
        """
        if not self._node_label:
            return
        self._node_label.setPlainText(self._node.name())
        label_data = self._node.settings().get("label")

        if self._node_label.toPlainText() != label_data["text"]:
            self._node_label.setPlainText(label_data["text"])
        self._node_label.setStyle(label_data.get("style", ""))
        self._node_label.setRotation(label_data.get("rotation", 0))
        if label_data["x"] is None:
            self._centerLabel()
            self.updateNode()
        else:
            self._node_label.setPos(label_data["x"], label_data["y"])

    def connectToPort(self, unavailable_ports=[]):
        """
        Shows a contextual menu for the user to choose port or auto-select one.

        :param unavailable_ports: list of port names that the user cannot choose

        :returns: Port instance corresponding to the selected port
        """

        self._selected_port = None
        menu = QtWidgets.QMenu()
        ports = self._node.ports()
        if not ports:
            QtWidgets.QMessageBox.critical(self.scene().parent(), "Link", "No port available, please configure this device")
            return None

        # sort the ports
        ports_dict = {}
        for port in ports:
            if port.adapterNumber() is not None:
                # make the port number unique (special case with WICs).
                port_number = port.portNumber()
                if port_number >= 16:
                    port_number *= 8
                ports_dict[(port.adapterNumber() * 16) + port_number] = port
            elif port.portNumber()is not None:
                ports_dict[port.portNumber()] = port
            else:
                ports_dict[port.name()] = port
        try:
            ports = sorted(ports_dict.keys(), key=int)
        except ValueError:
            ports = sorted(ports_dict.keys())

        # show a contextual menu for the user to choose a port
        for port in ports:
            port_object = ports_dict[port]
            log.debug("Node '{}' Port {} Type {}".format(self.node(), port_object.name(), type(port_object.name())))
            if port in unavailable_ports:
                # this port cannot be chosen by the user (grayed out)
                action = menu.addAction(QtGui.QIcon(':/icons/led_green.svg'), port_object.name())
                action.setDisabled(True)
            elif port_object.isFree():
                menu.addAction(QtGui.QIcon(':/icons/led_red.svg'), port_object.name())
            else:
                menu.addAction(QtGui.QIcon(':/icons/led_green.svg'), port_object.name())

        menu.triggered.connect(self.selectedPortSlot)
        menu.exec_(QtGui.QCursor.pos())
        return self._selected_port

    def selectedPortSlot(self, action):
        """
        Slot to receive events when a port has been selected in the
        contextual menu.

        :param action: QAction instance
        """

        ports = self._node.ports()

        # get the Port instance based on the selected port name.
        for port in ports:
            if port.name() == str(action.text()):
                self._selected_port = port
                break

    def itemChange(self, change, value):
        """
        Notifies this node item that some part of the item's state changes.

        :param change: GraphicsItemChange type
        :param value: value of the change
        """

        if change == QtWidgets.QGraphicsItem.ItemPositionChange and self.isActive() and self._main_window.uiSnapToGridAction.isChecked():
            mid_x = self.boundingRect().width() / 2
            value.setX((self.GRID_SIZE * round((value.x() + mid_x) / self.GRID_SIZE)) - mid_x)
            mid_y = self.boundingRect().height() / 2
            value.setY((self.GRID_SIZE * round((value.y() + mid_y) / self.GRID_SIZE)) - mid_y)

        # dynamically change the renderer when this node item is selected/unselected.
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            if value:
                self.graphicsEffect().setEnabled(True)
            else:
                self.graphicsEffect().setEnabled(False)
                self.updateNode()

        # adjust link item positions when this node is moving or has changed.
        if change == QtWidgets.QGraphicsItem.ItemPositionChange or change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            for link in self._links:
                link.adjust()

        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        """
        Paints the contents of an item in local coordinates.

        :param painter: QPainter instance
        :param option: QStyleOptionGraphicsItem instance
        :param widget: QWidget instance
        """

        # don't show the selection rectangle
        if not self._settings["draw_rectangle_selected_item"]:
            option.state = QtWidgets.QStyle.State_None
        super().paint(painter, option, widget)

        if not self._initialized or self.show_layer:
            brect = self.boundingRect()
            center = self.mapFromItem(self, brect.width() / 2.0, brect.height() / 2.0)
            painter.setBrush(QtCore.Qt.red)
            painter.setPen(QtCore.Qt.red)
            painter.drawRect((brect.width() / 2.0) - 10, (brect.height() / 2.0) - 10, 20, 20)
            painter.setPen(QtCore.Qt.black)
            if self.show_layer:
                text = str(int(self.zValue()))  # Z value
            elif self._last_error:
                text = "E"  # error
            else:
                text = "S"  # initialization
            painter.drawText(QtCore.QPointF(center.x() - 4, center.y() + 4), text)

    def setZValue(self, value):
        """
        Sets a new Z value.

        :param value: Z value
        """

        super().setZValue(value)
        if self.zValue() < 0:
            self.setFlag(self.ItemIsSelectable, False)
            self.setFlag(self.ItemIsMovable, False)
            if self._node_label:
                self._node_label.setFlag(self.ItemIsSelectable, False)
                self._node_label.setFlag(self.ItemIsMovable, False)
        else:
            self.setFlag(self.ItemIsSelectable, True)
            self.setFlag(self.ItemIsMovable, True)
            if self._node_label:
                self._node_label.setFlag(self.ItemIsSelectable, True)
                self._node_label.setFlag(self.ItemIsMovable, True)
        for link in self._links:
            link.adjust()

    def hoverEnterEvent(self, event):
        """
        Handles all hover enter events for this item.

        :param event: QGraphicsSceneHoverEvent instance
        """

        self.setCustomToolTip()
        if not self.isSelected():
            self.graphicsEffect().setEnabled(True)

    def hoverLeaveEvent(self, event):
        """
        Handles all hover leave events for this item.

        :param event: QGraphicsSceneHoverEvent instance
        """

        if not self.isSelected():
            self.graphicsEffect().setEnabled(False)

    def mouseRelease(self):
        """
        Handle all mouse release for this item.
        It the item is select but mouse is not on it the event
        is send also
        """
        self.updateNode()
