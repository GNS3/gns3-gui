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
Graphical view on the scene where items are drawn.
"""


import pickle
from .qt import QtCore, QtGui
from .scene import Scene
from .items.node_item import NodeItem
from .node_configurator import NodeConfigurator
from .link import Link
from .modules.dynamips import Dynamips

# link items
from .items.ethernet_link_item import EthernetLinkItem
from .items.serial_link_item import SerialLinkItem

# ports
from .ports.ethernet_port import EthernetPort
from .ports.fastethernet_port import FastEthernetPort
from .ports.gigabitethernet_port import GigabitEthernetPort


class GraphicsView(QtGui.QGraphicsView):
    """
    Graphics view that displays the scene.

    :param parent: parent widget
    """

    def __init__(self, parent):

        QtGui.QGraphicsView.__init__(self, parent)

        self._adding_link = False
        self._newlink = None
        self._dragging = False
        self._last_mouse_position = None

        #FIXME: temporary location to store links
        self._links = {}

        # restore settings
        settings = QtCore.QSettings()
        width = settings.value("GUI/scene_width", 2000)
        height = settings.value("GUI/scene_height", 2000)

        # set the scene
        scene = Scene(parent=self)
        scene.setSceneRect(-(width / 2), -(height / 2), width, height)
        self.setScene(scene)

        # set the custom flags for this view
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

    def addingLinkSlot(self, enabled):
        """
        Slot to receive events from MainWindow
        when a user has clicked on "Add a link" button.

        :param enable: either the user is adding a link or not (boolean)
        """

        if enabled:
            self.setCursor(QtCore.Qt.CrossCursor)
        else:
            if self._newlink:
                self.scene().removeItem(self._newlink)
                self._newlink = None
            self.setCursor(QtCore.Qt.ArrowCursor)
        self._adding_link = enabled

    def addLink(self, source_node, source_port, destination_node, destination_port):
        """
        Creates a Link object representing a connection between 2 devices.

        :param source_node: source Node object
        :param source_port: source Port object
        :param destination_node: destination Node object
        :param destination_port: destination Port object
        """

        link = Link(source_node, source_port, destination_node, destination_port)

        # connect the signals that let the graphics view knows about events such as
        # a new link creation or deletion.
        link.add_link_signal.connect(self.addLinkSlot)
        link.delete_link_signal.connect(self.deleteLinkSlot)
        self._links[link.id] = link

    def addLinkSlot(self, link_id):
        """
        Slot to receive events from Link instances
        when a link has been created.

        :param link_id: link identifier
        """

        link = self._links[link_id]
        source_item = None
        destination_item = None
        source_port = link._source_port
        destination_port = link._destination_port

        # find the correct source and destination node items
        for item in self.scene().items():
            if isinstance(item, NodeItem):
                if item.node().id == link._source_node.id:
                    source_item = item
                if item.node().id == link._destination_node.id:
                    destination_item = item
            if source_item and destination_item:
                break

        if not source_item or not destination_item:
            print("Could not find a source or destination item for the link!")
            self.deleteLinkSlot(link_id)
            return

        # ugly multi-link management
        # FIXME: taken from old GNS3 and has a bug!
        multi = 0
        d1 = 0
        d2 = 1
        link_items = source_item.links()
        for link_item in link_items:
            if link_item.destinationItem().node().id == destination_item.node().id:
                d1 += 1
            if link_item.sourceItem().node().id == destination_item.node().id:
                d2 += 1

        if len(link_items) > 0:
            if d2 - d1 == 2:
                source_port, destination_port = destination_port, source_port
                source_item, destination_item = destination_item, source_item
                multi = d1 + 1
            elif d1 >= d2:
                source_port, destination_port = destination_port, source_port
                source_item, destination_item = destination_item, source_item
                multi = d2
            else:
                multi = d1

        # MAX 7 links on the scene between 2 nodes
        if multi > 3:
            multi = 0

        if source_item == destination_item:
            multi = 0

        if link._source_port.linkType() == "Serial":
            link_item = SerialLinkItem(source_item, source_port, destination_item, destination_port, link, multilink=multi)
        else:
            link_item = EthernetLinkItem(source_item, source_port, destination_item, destination_port, link, multilink=multi)
        self.scene().addItem(link_item)

    def deleteLinkSlot(self, link_id):
        """
        Slot to receive events from Link instances
        when a link has been deleted.

        :param link_id: link identifier
        """

        link = self._links[link_id]

        # disconnect the signals just in case...
        link.add_link_signal.disconnect()
        link.delete_link_signal.disconnect()
        del self._links[link_id]

    def mousePressEvent(self, event):
        """
        Handles all mouse press events.

        :param: QMouseEvent object
        """

        item = self.itemAt(event.pos())
#         if item and isinstance(item, NodeItem):
#             item.setSelected(True)

        # This statement checks to see if either the middle mouse is pressed
        # or a combination of the right and left mouse buttons is pressed to start dragging the view
        if (event.buttons() == QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.ControlModifier) or event.buttons() == QtCore.Qt.MidButton:
            self._last_mouse_position = self.mapFromGlobal(event.globalPos())
            self._dragging = True
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            return

        if event.modifiers() == QtCore.Qt.ShiftModifier and event.button() == QtCore.Qt.LeftButton and item and not self._adding_link:
            if item.isSelected():
                item.setSelected(False)
            else:
                item.setSelected(True)
        elif item and isinstance(item, NodeItem):
            item.setSelected(True)

        if item and isinstance(item, NodeItem) and self._adding_link and event.button() == QtCore.Qt.LeftButton:
            if not self._newlink:
                source_item = item
                source_port = source_item.connectToPort()
                if not source_port:
                    return
                if source_port.linkType() == "Serial":
                    self._newlink = SerialLinkItem(source_item, source_port, self.mapToScene(event.pos()), None, adding_flag=True)
                else:
                    self._newlink = EthernetLinkItem(source_item, source_port, self.mapToScene(event.pos()), None, adding_flag=True)
                self.scene().addItem(self._newlink)
            else:
                source_item = self._newlink.sourceItem()
                source_port = self._newlink.sourcePort()
                destination_item = item
                if source_item == destination_item:
                    QtGui.QMessageBox.critical(self, "Connection", "Cannot connect to itself!")
                    return
                destination_port = destination_item.connectToPort()
                if not destination_port:
                    return

                if source_port.isStub() or destination_port.isStub():
                    pass
                #FIXME
                elif type(source_port) in (EthernetPort, FastEthernetPort, GigabitEthernetPort) and \
                   not type(destination_port) in (EthernetPort, FastEthernetPort, GigabitEthernetPort):
                    QtGui.QMessageBox.critical(self, "Connection", "You must connect an Ethernet port to another Ethernet compatible port")
                    return
#                 elif type(source_port) != type(destination_port):
#                     QtGui.QMessageBox.critical(self, "Connection", "Cannot connect this port!")
#                     return

                self.scene().removeItem(self._newlink)
                self.addLink(source_item.node(), source_port, destination_item.node(), destination_port)
                self._newlink = None
        else:
            QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Handles all mouse release events.

        :param: QMouseEvent object
        """

        item = self.itemAt(event.pos())
        # If the left  mouse button is not still pressed TOGETHER with the CTRL key and neither is the middle button
        # this means the user is no longer trying to drag the view
        if self._dragging and not (event.buttons() == QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.ControlModifier) and not event.buttons() & QtCore.Qt.MidButton:
            self._dragging = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        else:
            if item is not None and not event.modifiers() & QtCore.Qt.ShiftModifier:
                item.setSelected(True)
                #for other_item in self.__topology.selectedItems():
                #    other_item.setSelected(False)
            QtGui.QGraphicsView.mouseReleaseEvent(self, event)

    def scaleView(self, scale_factor):
        """
        Scales the view (zoom in and out).
        """

        factor = self.matrix().scale(scale_factor, scale_factor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if (factor < 0.10 or factor > 10):
            return
        self.scale(scale_factor, scale_factor)

    def keyPressEvent(self, event):
        """
        Handles all key press events for this view.

        :param event: QKeyEvent
        """

        if event.matches(QtGui.QKeySequence.ZoomIn):
            # zoom in
            factor_in = pow(2.0, 120 / 240.0)
            self.scaleView(factor_in)
        elif event.matches(QtGui.QKeySequence.ZoomOut):
            # zoom out
            factor_out = pow(2.0, -120 / 240.0)
            self.scaleView(factor_out)
#         elif event.key() == QtCore.Qt.Key_Delete:
#             # check if we are editing an Annotation object, then send the Delete event to it
#             for item in self.__topology.selectedItems():
#                 if isinstance(item, Annotation) and item.hasFocus():
#                     QtGui.QGraphicsView.keyPressEvent(self, event)
#                     return
#             self.slotDeleteNode()
        else:
            QtGui.QGraphicsView.keyPressEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        Handles all mouse move events (mouse tracking has been enabled).

        :param: QMouseEvent object
        """

        if self._dragging:
            # This if statement event checks to see if the user is dragging the scene
            # if so it sets the value of the scene scroll bars based on the change between
            # the previous and current mouse position
            mapped_global_pos = self.mapFromGlobal(event.globalPos())
            hBar = self.horizontalScrollBar()
            vBar = self.verticalScrollBar()
            delta = mapped_global_pos - self._last_mouse_position
            hBar.setValue(hBar.value() + (delta.x() if QtGui.QApplication.isRightToLeft() else -delta.x()))
            vBar.setValue(vBar.value() - delta.y())
            self._last_mouse_position = mapped_global_pos
        if self._adding_link and self._newlink:
            # update the mouse position when the user is adding a link.
            self._newlink.setMousePoint(self.mapToScene(event.pos()))
            event.ignore()
        else:
            QtGui.QGraphicsView.mouseMoveEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        """
        Handles all mouse double click events.

        :param: QMouseEvent object
        """

        item = self.itemAt(event.pos())
        if not self._adding_link and isinstance(item, NodeItem):
            item.setSelected(True)
#             if (isinstance(item, IOSRouter) or isinstance(item, AnyEmuDevice)) and item.isStarted():
#                 self.slotConsole()
#             elif isinstance(item, AnyVBoxEmuDevice) and (item.isStarted() or item.isSuspended()) and not globals.addingLinkFlag:
#                 self.slotDisplayWindowFocus()
#             else:
            self.configureSlot()
        else:
            QtGui.QGraphicsView.mouseDoubleClickEvent(self, event)

    def configureSlot(self, items=None):
        """
        Opens the node configurator.
        """

        from .main_window import MainWindow
        if not items:
            items = self.scene().selectedItems()
        node_configurator = NodeConfigurator(items, MainWindow.instance())
        node_configurator.setModal(True)
        node_configurator.show()
        node_configurator.exec_()
        for item in items:
            item.setSelected(False)

    def dragMoveEvent(self, event):
        """
        Handles all drag move events.

        :param event: QDragMoveEvent object
        """

        # check if what is dragged is handled by this view
        if event.mimeData().hasFormat("application/x-gns3-node"):
            event.acceptProposedAction()
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Handles all drop events.

        :param event: QDropEvent object
        """

        # check if what has been dropped is handled by this view
        if event.mimeData().hasFormat("application/x-gns3-node"):
            data = event.mimeData().data("application/x-gns3-node")
            # load the pickled node class
            node_class = pickle.loads(data)
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            self.createNode(node_class, event.pos())
        else:
            event.ignore()

    def contextMenuEvent(self, event):
        """
        Handles all context menu events.

        :param event: QContextMenuEvent object
        """

        menu = QtGui.QMenu()
        self.populateContextMenu(menu)
        menu.exec_(event.globalPos())

    def populateContextMenu(self, menu):
        """
        Adds actions to the contextual menu.

        :param menu: QMenu object
        """

        items = self.scene().selectedItems()
        if not items:
            return

        start_action = QtGui.QAction("Start", menu)
        start_action.setIcon(QtGui.QIcon(':/icons/play.svg'))
        start_action.triggered.connect(self.startActionSlot)
        menu.addAction(start_action)

        stop_action = QtGui.QAction("Stop", menu)
        stop_action.setIcon(QtGui.QIcon(':/icons/stop.svg'))
        stop_action.triggered.connect(self.stopActionSlot)
        menu.addAction(stop_action)

        suspend_action = QtGui.QAction("Suspend", menu)
        suspend_action.setIcon(QtGui.QIcon(':/icons/pause.svg'))
        suspend_action.triggered.connect(self.suspendActionSlot)
        menu.addAction(suspend_action)

        configure_action = QtGui.QAction("Configure", menu)
        configure_action.setIcon(QtGui.QIcon(':/icons/configuration.svg'))
        configure_action.triggered.connect(self.configureActionSlot)
        menu.addAction(configure_action)

        delete_action = QtGui.QAction("Delete", menu)
        delete_action.setIcon(QtGui.QIcon(':/icons/delete.svg'))
        delete_action.triggered.connect(self.deleteActionSlot)
        menu.addAction(delete_action)

    def startActionSlot(self):
        """
        Slot to receive events from the start action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if hasattr(item.node(), "start"):
                item.node().start()

    def stopActionSlot(self):
        """
        Slot to receive events from the stop action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if hasattr(item.node(), "stop"):
                item.node().stop()

    def suspendActionSlot(self):
        """
        Slot to receive events from the suspend action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if hasattr(item.node(), "suspend"):
                item.node().suspend()

    def configureActionSlot(self):
        """
        Slot to receive events from the configure action in the
        contextual menu.
        """

        items = []
        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem):
                items.append(item)

        if items:
            self.configureSlot(items)

    def deleteActionSlot(self):
        """
        Slot to receive events from the delete action in the
        contextual menu.
        """

        items = []
        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem):
                item.node().delete()

    def createNode(self, node_class, pos):
        """
        Creates a new node on the scene.

        :param node_class: node class to be instanciated
        :param pos: position of the drop event
        """

        #TODO: node setup management with other modules
        dynamips = Dynamips.instance()
        node = dynamips.createNode(node_class)
        node_item = NodeItem(node)
        node_item.setPos(self.mapToScene(pos))
        self.scene().addItem(node_item)
        x = node_item.pos().x() - (node_item.boundingRect().width() / 2)
        y = node_item.pos().y() - (node_item.boundingRect().height() / 2)
        node_item.setPos(x, y)
        dynamips.setupNode(node)
