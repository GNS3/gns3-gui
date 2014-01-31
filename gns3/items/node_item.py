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

from ..qt import QtGui, QtSvg


class NodeItem(QtSvg.QGraphicsSvgItem):
    """
    Node for the scene.

    :param node: Node instance.
    """

    def __init__(self, node):

        QtSvg.QGraphicsSvgItem.__init__(self)

        self._node = node
        self._name = "N/A"

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
        node.newname_signal.connect(self.newNameSlot)
        node.started_signal.connect(self.startedSlot)
        node.stopped_signal.connect(self.stoppedSlot)
        node.suspended_signal.connect(self.suspendedSlot)
        node.delete_links_signal.connect(self.deleteLinksSlot)
        node.delete_signal.connect(self.deleteSlot)

        # link items connected to this node item.
        self._links = []

        # used when a port has been selected from the contextual menu
        self._selected_port = None

    def node(self):
        """
        Returns the node attached to this node item.

        :returns: Node instance
        """

        return self._node

    def addLink(self, link):
        """
        Adds a link items to this node item.

        :param link: LinkItem object
        """

        self._links.append(link)

    def removeLink(self, link):
        """
        Removes a link items from this node item.

        :param link: LinkItem object
        """

        self._links.remove(link)

    def links(self):
        """
        Returns all the link items attached to this node item.

        :returns: list of LinkItem objects
        """

        return self._links

    def newNameSlot(self, name):
        """
        Slot to receive events from the attached Node instance
        when a the node has a new name.

        :param name: node new name
        """

        #TODO: finish this
        self._name = name
        #self.showName()

    def startedSlot(self):
        """
        Slot to receive events from the attached Node instance
        when a the node has started.
        """

        #TODO: finish this
        print("Node started!")

    def stoppedSlot(self):
        """
        Slot to receive events from the attached Node instance
        when a the node has stopped.
        """

        #TODO: finish this
        print("Node stopped!")

    def suspendedSlot(self):
        """
        Slot to receive events from the attached Node instance
        when a the node has suspended.
        """

        #TODO: finish this
        print("Node suspended")

    def deleteLinksSlot(self):
        """
        Slot to receive events from the attached Node instance
        when a all the links must be deleted.
        """

        for link in self._links.copy():
            link.delete()

    def deleteSlot(self):
        """
        Slot to receive events from the attached Node instance
        when the node has been deleted.
        """

        self.scene().removeItem(self)

    def setCustomToolTip(self):
        """
        Sets a new ToolTip.
        """

        self.setToolTip(self._name)

    def showName(self):
        """
        Shows the node name on the scene.
        """

        #TODO: possibility to change the Font size etc.
        self.textItem = QtGui.QGraphicsTextItem(self._name, self)
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

        :returns: Port object corresponding to the selected port
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
            port_names[port.name] = port
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

        :param action: QAction object
        """

        ports = self._node.ports()

        # get the Port object based on the selected port name.
        for port in ports:
            if port.name == str(action.text()):
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
            for link in self._links:
                link.adjust()

        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def paint(self, painter, option, widget=None):
        """
        Paints the contents of an item in local coordinates.

        :param painter: QPainter object.
        :param option: QStyleOptionGraphicsItem object.
        :param widget: QWidget object.
        """

        # don't show the selection rectangle
        option.state = QtGui.QStyle.State_None
        return QtSvg.QGraphicsSvgItem.paint(self, painter, option, widget)

#TODO: show layer position on the node
#         # Don't draw if not activated
#         if globals.GApp.workspace.flg_showLayerPos == False:
#             return
# 
#         # Show layer level of this node
#         brect = self.boundingRect()
#         center = self.mapFromItem(self, brect.width() / 2.0, brect.height() / 2.0)
# 
#         painter.setBrush(QtCore.Qt.red)
#         painter.setPen(QtCore.Qt.red)
#         painter.drawRect((brect.width() / 2.0) - 10, (brect.height() / 2.0) - 10, 20,20)
#         painter.setPen(QtCore.Qt.black)
#         painter.setFont(QtGui.QFont("TypeWriter", 14, QtGui.QFont.Bold))
#         zval = str(int(self.zValue()))
#         painter.drawText(QtCore.QPointF(center.x() - 4, center.y() + 4), zval)

    def hoverEnterEvent(self, event):
        """
        Handles all hover enter events for this item.

        :param event: QGraphicsSceneHoverEvent object
        """

        self.setCustomToolTip()

#TODO: finish tooptip support
        # update tool tip
#         try:
#             self.setCustomToolTip()
#         except:
#             print translate("AbstractNode", "Cannot communicate with %s, the server running this node may have crashed!" % self.hostname)

        # dynamically change the renderer when this node item is hovered.
        if not self.isSelected():
            self.setSharedRenderer(self._hover_renderer)

    def hoverLeaveEvent(self, event):
        """
        Handles all hover leave events for this item.

        :param event: QGraphicsSceneHoverEvent object
        """

        # dynamically change the renderer back to the default when this node item is not hovered anymore.
        if not self.isSelected():
            self.setSharedRenderer(self._default_renderer)
