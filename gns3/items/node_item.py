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

from ..qt import QtCore, QtGui, QtSvg


class NodeItem(QtSvg.QGraphicsSvgItem):
    """
    Node for the scene.

    :param node: Node instance.
    """

    def __init__(self, node):

        QtSvg.QGraphicsSvgItem.__init__(self)

        # attached node
        self._node = node

        # set graphical settings for this node
        self.setFlag(QtSvg.QGraphicsSvgItem.ItemIsMovable)
        self.setFlag(QtSvg.QGraphicsSvgItem.ItemIsSelectable)
        self.setFlag(QtSvg.QGraphicsSvgItem.ItemIsFocusable)
        self.setFlag(QtSvg.QGraphicsSvgItem.ItemSendsGeometryChanges)
        self.setAcceptsHoverEvents(True)
        self.setZValue(1)

        # create renderers using symbols paths/resources
        self._default_renderer = QtSvg.QSvgRenderer(node.defaultSymbol())
        self._hover_renderer = QtSvg.QSvgRenderer(node.hoverSymbol())
        self.setSharedRenderer(self._default_renderer)

        # connect signals to know about some events
        # e.g. when the node has been started, stopped or suspended etc.
        node.created_signal.connect(self.createdSlot)
        node.started_signal.connect(self.startedSlot)
        node.stopped_signal.connect(self.stoppedSlot)
        node.suspended_signal.connect(self.suspendedSlot)
        node.updated_signal.connect(self.updatedSlot)
        node.deleted_signal.connect(self.deletedSlot)
        node.delete_links_signal.connect(self.deleteLinksSlot)
        node.server_error_signal.connect(self.serverErrorSlot)

        # link items connected to this node item.
        self._links = []

        # used when a port has been selected from the contextual menu
        self._selected_port = None

        # says if the attached node has been initialized
        # by the server.
        self._initialized = False

        # contains the last error message received
        # from the server.
        self._last_error = None

    def setUnsavedState(self):
        """
        Indicates the project is in a unsaved state.
        """

        from ..main_window import MainWindow
        main_window = MainWindow.instance()
        main_window.setUnsavedState()

    def node(self):
        """
        Returns the node attached to this node item.

        :returns: Node instance
        """

        return self._node

    def addLink(self, link):
        """
        Adds a link items to this node item.

        :param link: LinkItem instance
        """

        self._links.append(link)
        self._node.updated_signal.emit()
        self.setUnsavedState()

    def removeLink(self, link):
        """
        Removes a link items from this node item.

        :param link: LinkItem instance
        """

        if link in self._links:
            self._links.remove(link)
        self.setUnsavedState()

    def links(self):
        """
        Returns all the link items attached to this node item.

        :returns: list of LinkItem instances
        """

        return self._links

    def createdSlot(self, node_id):
        """
        Slot to receive events from the attached Node instance
        when a the node has been created/initialized.

        :param node_id: node identifier (integer)
        """

        self._initialized = True
        self.update()
        self.showName()

    def startedSlot(self):
        """
        Slot to receive events from the attached Node instance
        when a the node has started.
        """

        for link in self._links:
            link.update()

    def stoppedSlot(self):
        """
        Slot to receive events from the attached Node instance
        when a the node has stopped.
        """

        for link in self._links:
            link.update()

    def suspendedSlot(self):
        """
        Slot to receive events from the attached Node instance
        when a the node has suspended.
        """

        for link in self._links:
            link.update()

    def updatedSlot(self):

        self.textItem.setPlainText(self._node.name())
        self.setUnsavedState()

    def deleteLinksSlot(self):
        """
        Slot to receive events from the attached Node instance
        when a all the links must be deleted.
        """

        for link in self._links.copy():
            link.delete()

    def deletedSlot(self):
        """
        Slot to receive events from the attached Node instance
        when the node has been deleted.
        """

        if self in self.scene().items():
            self.scene().removeItem(self)
        self.setUnsavedState()

    def serverErrorSlot(self, node_id, code, message):
        """
        Slot to receive events from the attached Node instance
        when the node has received an error from the server.

        :param node_id: node identifier
        :param code: error code
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

    def showName(self):
        """
        Shows the node name on the scene.
        """

        #TODO: possibility to change the Font size etc.
        self.textItem = QtGui.QGraphicsTextItem(self._node.name(), self)
        self.textItem.setFont(QtGui.QFont("TypeWriter", 10, QtGui.QFont.Bold))
        self.textItem.setFlag(self.textItem.ItemIsMovable)
        textrect = self.textItem.boundingRect()
        textmiddle = textrect.topRight() / 2
        noderect = self.boundingRect()
        nodemiddle = noderect.topRight() / 2
        self.default_name_xpos = nodemiddle.x() - textmiddle.x()
        self.default_name_ypos = -25
        self.textItem.setPos(self.default_name_xpos, self.default_name_ypos)

    def connectToPort(self, unavailable_ports=[]):
        """
        Shows a contextual menu for the user to choose port or auto-select one.

        :param unavailable_ports: list of port names that the user cannot choose

        :returns: Port instance corresponding to the selected port
        """

        self._selected_port = None
        menu = QtGui.QMenu()
        ports = self._node.ports()
        if not ports:
            QtGui.QMessageBox.critical(self.scene().parent(), "Link", "No port available, please configure this device")
            return None

        # sort by port name
        port_names = {}
        for port in ports:
            port_names[port.name()] = port
        ports = sorted(port_names.keys())

        # show a contextual menu for the user to choose a port
        for port in ports:
            port_object = port_names[port]
            if port in unavailable_ports:
                # this port cannot be chosen by the user (grayed out)
                action = menu.addAction(QtGui.QIcon(':/icons/led_green.svg'), port)
                action.setDisabled(True)
            elif port_object.isFree():
                menu.addAction(QtGui.QIcon(':/icons/led_red.svg'), port)
            else:
                menu.addAction(QtGui.QIcon(':/icons/led_green.svg'), port)

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

        # dynamically change the renderer when this node item is selected/unselected.
        if change == QtSvg.QGraphicsSvgItem.ItemSelectedChange:
            if value:
                self.setSharedRenderer(self._hover_renderer)
            else:
                self.setSharedRenderer(self._default_renderer)

        # adjust link item positions when this node is moving or has changed.
        if change == QtSvg.QGraphicsSvgItem.ItemPositionChange or change == QtSvg.QGraphicsSvgItem.ItemPositionHasChanged:
            self.setUnsavedState()
            for link in self._links:
                link.adjust()

        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def paint(self, painter, option, widget=None):
        """
        Paints the contents of an item in local coordinates.

        :param painter: QPainter instance.
        :param option: QStyleOptionGraphicsItem instance.
        :param widget: QWidget instance.
        """

        # don't show the selection rectangle
        option.state = QtGui.QStyle.State_None
        QtSvg.QGraphicsSvgItem.paint(self, painter, option, widget)

#TODO: show layer position on the node
#         # Don't draw if not activated
#         if globals.GApp.workspace.flg_showLayerPos == False:
#             return

        if not self._initialized:
            # Show layer level of this node
            brect = self.boundingRect()
            # center = self.mapFromItem(self, brect.width() / 2.0, brect.height() / 2.0)

            painter.setBrush(QtCore.Qt.red)
            painter.setPen(QtCore.Qt.red)
            painter.drawRect((brect.width() / 2.0) - 10, (brect.height() / 2.0) - 10, 20, 20)

            #painter.setPen(QtCore.Qt.black)
            #painter.setFont(QtGui.QFont("TypeWriter", 14, QtGui.QFont.Bold))
            #zval = str(int(self.zValue()))
            #painter.drawText(QtCore.QPointF(center.x() - 4, center.y() + 4), zval)

    def hoverEnterEvent(self, event):
        """
        Handles all hover enter events for this item.

        :param event: QGraphicsSceneHoverEvent instance
        """

        self.setCustomToolTip()
        # dynamically change the renderer when this node item is hovered.
        if not self.isSelected():
            self.setSharedRenderer(self._hover_renderer)

    def hoverLeaveEvent(self, event):
        """
        Handles all hover leave events for this item.

        :param event: QGraphicsSceneHoverEvent instance
        """

        # dynamically change the renderer back to the default when this node item is not hovered anymore.
        if not self.isSelected():
            self.setSharedRenderer(self._default_renderer)
