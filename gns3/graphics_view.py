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

import logging
import os
import pickle

from .qt import QtCore, QtGui, QtNetwork
from .servers import Servers
from .items.node_item import NodeItem
from .dialogs.node_configurator_dialog import NodeConfiguratorDialog
from .link import Link
from .node import Node
from .modules import MODULES
from .modules.builtin.cloud import Cloud
from .modules.module_error import ModuleError
from .settings import GRAPHICS_VIEW_SETTINGS, GRAPHICS_VIEW_SETTING_TYPES
from .topology import Topology
from .ports.port import Port
from .dialogs.style_editor_dialog import StyleEditorDialog
from .dialogs.text_editor_dialog import TextEditorDialog
from .dialogs.symbol_selection_dialog import SymbolSelectionDialog
from .dialogs.idlepc_dialog import IdlePCDialog
from .utils.connect_to_server import ConnectToServer

# link items
from .items.link_item import LinkItem
from .items.ethernet_link_item import EthernetLinkItem
from .items.serial_link_item import SerialLinkItem

# other items
from .items.note_item import NoteItem
from .items.shape_item import ShapeItem
from .items.rectangle_item import RectangleItem
from .items.ellipse_item import EllipseItem
from .items.image_item import ImageItem

log = logging.getLogger(__name__)


class GraphicsView(QtGui.QGraphicsView):
    """
    Graphics view that displays the scene.

    :param parent: parent widget
    """

    def __init__(self, parent):

        # Our parent is the central widget which parent
        # is the main window.
        self._main_window = parent.parent()

        QtGui.QGraphicsView.__init__(self, parent)
        self._settings = {}
        self._loadSettings()

        self._adding_link = False
        self._adding_note = False
        self._adding_rectangle = False
        self._adding_ellipse = False
        self._newlink = None
        self._dragging = False
        self._last_mouse_position = None
        self._topology = Topology.instance()

        # set the scene
        scene = QtGui.QGraphicsScene(parent=self)
        width = self._settings["scene_width"]
        height = self._settings["scene_height"]
        scene.setSceneRect(-(width / 2), -(height / 2), width, height)
        self.setScene(scene)

        # set the custom flags for this view
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        self._local_addresses = ['0.0.0.0', '127.0.0.1', 'localhost', '::1', '0:0:0:0:0:0:0:1', '::', QtNetwork.QHostInfo.localHostName()]

    def reset(self):
        """
        Remove all the items from the scene and
        reset the instances count.
        """

        # reset the modules
        for module in MODULES:
            instance = module.instance()
            instance.reset()

        # reset instance IDs for
        # nodes, links and ports
        Node.reset()
        Link.reset()
        Port.reset()

        # reset the topology
        self._topology.reset()

        # clear the topology summary
        self._main_window.uiTopologySummaryTreeWidget.clear()

        # clear all objects on the scene
        self.scene().clear()

    def updateProjectFilesDir(self, path):
        """
        Updates the project files directory path for all modules.

        :param path: path to the local project files directory.
        """

        try:
            for module in MODULES:
                instance = module.instance()
                instance.setProjectFilesDir(path)
        except ModuleError as e:
            QtGui.QMessageBox.critical(self, "Local projects directory", "{}".format(e))

    def updateImageFilesDir(self, path):
        """
        Updates the image files directory path for all modules.

        :param path: path to the local images files directory.
        """

        try:
            for module in MODULES:
                instance = module.instance()
                instance.setImageFilesDir(path)
        except ModuleError as e:
            QtGui.QMessageBox.critical(self, "Local images directory", "{}".format(e))

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        # restore settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in GRAPHICS_VIEW_SETTINGS.items():
            self._settings[name] = settings.value(name, value, type=GRAPHICS_VIEW_SETTING_TYPES[name])
        settings.endGroup()

    def settings(self):
        """
        Returns the graphics view settings.

        :returns: settings dictionary
        """

        return self._settings

    def setSettings(self, new_settings):
        """
        Set new graphics view settings.

        :param new_settings: settings dictionary
        """

        # save the settings
        self._settings.update(new_settings)
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in self._settings.items():
            settings.setValue(name, value)
        settings.endGroup()

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

    def addNote(self, state):
        """
        Adds a note.

        :param state: boolean
        """

        if state:
            self._adding_note = True
            self.setCursor(QtCore.Qt.IBeamCursor)
        else:
            self._adding_note = False
            self.setCursor(QtCore.Qt.ArrowCursor)

    def addRectangle(self, state):
        """
        Adds a rectangle.

        :param state: boolean
        """

        if state:
            self._adding_rectangle = True
            self.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self._adding_rectangle = False
            self.setCursor(QtCore.Qt.ArrowCursor)

    def addEllipse(self, state):
        """
        Adds an ellipse.

        :param state: boolean
        """

        if state:
            self._adding_ellipse = True
            self.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self._adding_ellipse = False
            self.setCursor(QtCore.Qt.ArrowCursor)

    def addImage(self, pixmap, image_path):
        """
        Adds an image.

        :param pixmap: QPixmap instance
        :param image_path: path to the image
        """

        image_item = ImageItem(pixmap, image_path)
        # center the image on the scene
        x = image_item.pos().x() - (image_item.boundingRect().width() / 2)
        y = image_item.pos().y() - (image_item.boundingRect().height() / 2)
        image_item.setPos(x, y)
        self.scene().addItem(image_item)
        self._topology.addImage(image_item)

    def addLink(self, source_node, source_port, destination_node, destination_port):
        """
        Creates a Link instance representing a connection between 2 devices.

        :param source_node: source Node instance
        :param source_port: source Port instance
        :param destination_node: destination Node instance
        :param destination_port: destination Port instance
        """

        link = Link(source_node, source_port, destination_node, destination_port)

        # connect the signals that let the graphics view knows about events such as
        # a new link creation or deletion.
        link.add_link_signal.connect(self.addLinkSlot)
        link.delete_link_signal.connect(self.deleteLinkSlot)
        self._topology.addLink(link)

    def addLinkSlot(self, link_id):
        """
        Slot to receive events from Link instances
        when a link has been created.

        :param link_id: link identifier
        """

        link = self._topology.getLink(link_id)
        source_item = None
        destination_item = None
        source_port = link.sourcePort()
        destination_port = link.destinationPort()

        # find the correct source and destination node items
        for item in self.scene().items():
            if isinstance(item, NodeItem):
                if item.node().id() == link.sourceNode().id():
                    source_item = item
                if item.node().id() == link.destinationNode().id():
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
            if link_item.destinationItem().node().id() == destination_item.node().id():
                d1 += 1
            if link_item.sourceItem().node().id() == destination_item.node().id():
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

        if link.sourcePort().linkType() == "Serial" or (source_port.isStub() and link.destinationPort().linkType() == "Serial"):
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

        link = self._topology.getLink(link_id)
        # disconnect the signals just in case...
        link.add_link_signal.disconnect()
        link.delete_link_signal.disconnect()
        self._topology.removeLink(link)

    def _userNodeLinking(self, event, item):
        """
        Handles node linking by the user.

        :param event: QMouseEvent instance
        :param item: NodeItem instance
        """

        # link addition code
        if not self._newlink:
            source_item = item
            source_port = source_item.connectToPort()
            if not source_port:
                return
            if not source_item.node().initialized():
                QtGui.QMessageBox.critical(self, "Connection", "This node hasn't been initialized correctly")
                return
            if not source_port.isFree():
                QtGui.QMessageBox.critical(self, "Connection", "Port {} isn't free".format(source_port.name()))
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
            if not destination_item.node().initialized():
                QtGui.QMessageBox.critical(self, "Connection", "This node hasn't been initialized correctly")
                return
            if not destination_port.isFree():
                QtGui.QMessageBox.critical(self, "Connection", "Port {} isn't free".format(destination_port.name()))
                return
            if source_port.isStub() or destination_port.isStub():
                pass
            elif source_port.linkType() != destination_port.linkType():
                QtGui.QMessageBox.critical(self, "Connection", "Cannot connect this port!")
                return

            if isinstance(source_item.node(), Cloud) and isinstance(destination_item.node(), Cloud):
                QtGui.QMessageBox.critical(self, "Connection", "Sorry, you cannot connect a cloud to another cloud!")
                return

            source_host = source_item.node().server().host
            destination_host = destination_item.node().server().host

            # check that the node can be connected to a cloud
            if (isinstance(source_item.node(), Cloud) or isinstance(destination_item.node(), Cloud)) and source_host != destination_host:
                QtGui.QMessageBox.critical(self, "Connection", "This device can only be connected to a cloud on the same host")
                return

            # check if the 2 nodes can communicate
            if (source_host in self._local_addresses and destination_host not in self._local_addresses) or \
               (destination_host in self._local_addresses and source_host not in self._local_addresses):
                QtGui.QMessageBox.critical(self, "Connection", "Server {} cannot communicate with server {}, most likely because your local server host binding is set to a local address".format(source_host, destination_host))
                return

            self.scene().removeItem(self._newlink)
            self.addLink(source_item.node(), source_port, destination_item.node(), destination_port)
            self._newlink = None

    def mousePressEvent(self, event):
        """
        Handles all mouse press events.

        :param event: QMouseEvent instance
        """

        is_not_link = True
        item = self.itemAt(event.pos())
        if item and isinstance(item, LinkItem):
            is_not_link = False
        else:
            for it in self.scene().items():
                if isinstance(it, LinkItem):
                    it.setHovered(False)

        if (event.buttons() == QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.ShiftModifier) or event.buttons() == QtCore.Qt.MidButton:
            # checks to see if either the middle mouse is pressed
            # or a combination of left mouse button and SHIT key are pressed to start dragging the view
            self._last_mouse_position = self.mapFromGlobal(event.globalPos())
            self._dragging = True
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            return

        if is_not_link and item and event.modifiers() == QtCore.Qt.ControlModifier and event.button() == QtCore.Qt.LeftButton and item and not self._adding_link:
            # manual selection using CTRL
            if item.isSelected():
                item.setSelected(False)
            else:
                item.setSelected(True)
        elif is_not_link and event.button() == QtCore.Qt.RightButton and not self._adding_link:
            if item:
                #Prevent right clicking on a selected item from de-selecting all other items
                if not item.isSelected():
                    if not event.modifiers() & QtCore.Qt.ControlModifier:
                        for it in self.scene().items():
                            it.setSelected(False)
                    if item.zValue() < 0:
                        item.setFlag(item.ItemIsSelectable, True)
                    item.setSelected(True)
                    self._showDeviceContextualMenu(QtGui.QCursor.pos())
                    if item.zValue() < 0:
                        item.setFlag(item.ItemIsSelectable, False)

                else:
                    self._showDeviceContextualMenu(QtGui.QCursor.pos())
            # when more than one item is selected display the contextual menu even if mouse is not above an item
            elif len(self.scene().selectedItems()) > 1:
                self._showDeviceContextualMenu(QtGui.QCursor.pos())
        elif item and isinstance(item, NodeItem) and self._adding_link and event.button() == QtCore.Qt.LeftButton:
            self._userNodeLinking(event, item)
        elif event.button() == QtCore.Qt.LeftButton and self._adding_note:
            note = NoteItem()
            note.setPos(self.mapToScene(event.pos()))
            pos_x = note.pos().x()
            pos_y = note.pos().y() - (note.boundingRect().height() / 2)
            note.setPos(pos_x, pos_y)
            self.scene().addItem(note)
            self._topology.addNote(note)
            note.editText()
            self._main_window.uiAddNoteAction.setChecked(False)
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._adding_note = False
        elif event.button() == QtCore.Qt.LeftButton and self._adding_rectangle:
            rectangle = RectangleItem(self.mapToScene(event.pos()))
            self.scene().addItem(rectangle)
            self._topology.addRectangle(rectangle)
            self._main_window.uiDrawRectangleAction.setChecked(False)
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._adding_rectangle = False
        elif event.button() == QtCore.Qt.LeftButton and self._adding_ellipse:
            ellipse = EllipseItem(self.mapToScene(event.pos()))
            self.scene().addItem(ellipse)
            self._topology.addEllipse(ellipse)
            self._main_window.uiDrawEllipseAction.setChecked(False)
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._adding_ellipse = False
        else:
            QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Handles all mouse release events.

        :param: QMouseEvent instance
        """

        item = self.itemAt(event.pos())
        # If the left  mouse button is not still pressed TOGETHER with the SHIFT key and neither is the middle button
        # this means the user is no longer trying to drag the view
        if self._dragging and not (event.buttons() == QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.ShiftModifier) and not event.buttons() & QtCore.Qt.MidButton:
            self._dragging = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        else:
            if item is not None and not event.modifiers() & QtCore.Qt.ControlModifier:
                item.setSelected(True)
            QtGui.QGraphicsView.mouseReleaseEvent(self, event)

    def wheelEvent(self, event):
        """
        Handles zoom in or out using the mouse wheel.

        :param: QWheelEvent instance
        """

        if event.modifiers() == QtCore.Qt.ControlModifier and event.orientation() == QtCore.Qt.Vertical:
            # CTRL is pressed then use the mouse wheel to zoom in or out.
            self.scaleView(pow(2.0, event.delta() / 240.0))
        else:
            QtGui.QGraphicsView.wheelEvent(self, event)

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

        if event.key() == QtCore.Qt.Key_Delete:
            # check if we are editing an NoteItem instance, then send the delete key event to it
            for item in self.scene().selectedItems():
                if isinstance(item, NoteItem) and item.hasFocus():
                    QtGui.QGraphicsView.keyPressEvent(self, event)
                    return
            self.deleteActionSlot()
        else:
            QtGui.QGraphicsView.keyPressEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        Handles all mouse move events (mouse tracking has been enabled).

        :param event: QMouseEvent instance
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
            item = self.itemAt(event.pos())
            if item:
                # show item coords in the status bar
                coords = "X: {} Y: {} Z: {}".format(item.x(), item.y(), item.zValue())
                self._main_window.uiStatusBar.showMessage(coords, 2000)
            QtGui.QGraphicsView.mouseMoveEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        """
        Handles all mouse double click events.

        :param event: QMouseEvent instance
        """

        item = self.itemAt(event.pos())
        if not self._adding_link and isinstance(item, NodeItem) and item.node().initialized():
            item.setSelected(True)
            if isinstance(item, NodeItem):
                self.consoleToNode(item.node())
            else:
                self.configureSlot()
        else:
            QtGui.QGraphicsView.mouseDoubleClickEvent(self, event)

    def configureSlot(self, items=None):
        """
        Opens the node configurator.
        """

        if not items:
            items = self.scene().selectedItems()
        node_configurator = NodeConfiguratorDialog(items, self._main_window)
        node_configurator.setModal(True)
        node_configurator.show()
        node_configurator.exec_()
        for item in items:
            item.setSelected(False)

    def dragMoveEvent(self, event):
        """
        Handles all drag move events.

        :param event: QDragMoveEvent instance
        """

        # check if what is dragged is handled by this view
        if event.mimeData().hasFormat("application/x-gns3-node") or event.mimeData().hasFormat("text/uri-list"):
            event.acceptProposedAction()
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Handles all drop events.

        :param event: QDropEvent instance
        """

        # check if what has been dropped is handled by this view
        if event.mimeData().hasFormat("application/x-gns3-node"):
            data = event.mimeData().data("application/x-gns3-node")
            # load the pickled node data
            node_data = pickle.loads(data)
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            if event.keyboardModifiers() == QtCore.Qt.ShiftModifier:
                max_nodes_per_line = 10  # max number of nodes on a single line
                offset = 100  # spacing between elements
                integer, ok = QtGui.QInputDialog.getInteger(self, "Nodes", "Number of nodes:", 2, 1, 100, 1)
                if ok:
                    for node_number in range(integer):
                        node_item = self.createNode(node_data, event.pos())
                        if node_item is None:
                            # stop if there is any error
                            break
                        x = node_item.pos().x() - (node_item.boundingRect().width() / 2) + (node_number % max_nodes_per_line) * offset
                        y = node_item.pos().y() - (node_item.boundingRect().height() / 2) + (node_number // max_nodes_per_line) * offset
                        node_item.setPos(x, y)
            else:
                self.createNode(node_data, event.pos())
        elif event.mimeData().hasFormat("text/uri-list") and event.mimeData().hasUrls():
            if len(event.mimeData().urls()) > 1:
                QtGui.QMessageBox.critical(self, "Project files", "Please drop only one file")
                return
            path = event.mimeData().urls()[0].toLocalFile()
            if os.path.isfile(path) and self._main_window.checkForUnsavedChanges():
                self._main_window.loadProject(path)
            event.acceptProposedAction()
        else:
            event.ignore()

    def _showDeviceContextualMenu(self, pos):
        """
        Create and display the device contextual menu on the view.

        :param pos: position where to display the menu
        """

        menu = QtGui.QMenu()
        self.populateDeviceContextualMenu(menu)
        menu.exec_(pos)
        menu.clear()

    def populateDeviceContextualMenu(self, menu):
        """
        Adds device actions to the device contextual menu.

        :param menu: QMenu instance
        """

        items = self.scene().selectedItems()
        if not items:
            return

        if True in list(map(lambda item: isinstance(item, NodeItem), items)):
            configure_action = QtGui.QAction("Configure", menu)
            configure_action.setIcon(QtGui.QIcon(':/icons/configuration.svg'))
            configure_action.triggered.connect(self.configureActionSlot)
            menu.addAction(configure_action)

            # Action: Change symbol
            change_symbol_action = QtGui.QAction("Change symbol", menu)
            change_symbol_action.setIcon(QtGui.QIcon(':/icons/node_conception.svg'))
            self.connect(change_symbol_action, QtCore.SIGNAL('triggered()'), self.changeSymbolActionSlot)
            menu.addAction(change_symbol_action)


        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "console"), items)):
            console_action = QtGui.QAction("Console", menu)
            console_action.setIcon(QtGui.QIcon(':/icons/console.svg'))
            console_action.triggered.connect(self.consoleActionSlot)
            menu.addAction(console_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "startPacketCapture"), items)):
            capture_action = QtGui.QAction("Capture", menu)
            capture_action.setIcon(QtGui.QIcon(':/icons/inspect.svg'))
            capture_action.triggered.connect(self.captureActionSlot)
            menu.addAction(capture_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "idlepcs"), items)):
            idlepc_action = QtGui.QAction("Idle-PC", menu)
            idlepc_action.setIcon(QtGui.QIcon(':/icons/calculate.svg'))
            idlepc_action.triggered.connect(self.idlepcActionSlot)
            menu.addAction(idlepc_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "start"), items)):
            start_action = QtGui.QAction("Start", menu)
            start_action.setIcon(QtGui.QIcon(':/icons/play.svg'))
            start_action.triggered.connect(self.startActionSlot)
            menu.addAction(start_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "suspend"), items)):
            suspend_action = QtGui.QAction("Suspend", menu)
            suspend_action.setIcon(QtGui.QIcon(':/icons/pause.svg'))
            suspend_action.triggered.connect(self.suspendActionSlot)
            menu.addAction(suspend_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "stop"), items)):
            stop_action = QtGui.QAction("Stop", menu)
            stop_action.setIcon(QtGui.QIcon(':/icons/stop.svg'))
            stop_action.triggered.connect(self.stopActionSlot)
            menu.addAction(stop_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "reload"), items)):
            reload_action = QtGui.QAction("Reload", menu)
            reload_action.setIcon(QtGui.QIcon(':/icons/reload.svg'))
            reload_action.triggered.connect(self.reloadActionSlot)
            menu.addAction(reload_action)

        if True in list(map(lambda item: isinstance(item, NoteItem) or isinstance(item, ShapeItem) or isinstance(item, ImageItem), items)):
            duplicate_action = QtGui.QAction("Duplicate", menu)
            duplicate_action.setIcon(QtGui.QIcon(':/icons/new.svg'))
            duplicate_action.triggered.connect(self.duplicateActionSlot)
            menu.addAction(duplicate_action)

        if True in list(map(lambda item: isinstance(item, NoteItem), items)):
            text_edit_action = QtGui.QAction("Text edit", menu)
            text_edit_action.setIcon(QtGui.QIcon(':/icons/show-hostname.svg'))  # TODO: change icon for text edit
            text_edit_action.triggered.connect(self.textEditActionSlot)
            menu.addAction(text_edit_action)

        if True in list(map(lambda item: isinstance(item, ShapeItem), items)):
            style_action = QtGui.QAction("Style", menu)
            style_action.setIcon(QtGui.QIcon(':/icons/drawing.svg'))
            style_action.triggered.connect(self.styleActionSlot)
            menu.addAction(style_action)

        # item must have no parent
        if True in list(map(lambda item: item.parentItem() is None, items)):

            raise_layer_action = QtGui.QAction("Raise one layer", menu)
            raise_layer_action.setIcon(QtGui.QIcon(':/icons/raise_z_value.svg'))
            raise_layer_action.triggered.connect(self.raiseLayerActionSlot)
            menu.addAction(raise_layer_action)

            lower_layer_action = QtGui.QAction("Lower one layer", menu)
            lower_layer_action.setIcon(QtGui.QIcon(':/icons/lower_z_value.svg'))
            lower_layer_action.triggered.connect(self.lowerLayerActionSlot)
            menu.addAction(lower_layer_action)

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
            if isinstance(item, NodeItem) and hasattr(item.node(), "start") and item.node().initialized():
                item.node().start()

    def stopActionSlot(self):
        """
        Slot to receive events from the stop action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and hasattr(item.node(), "stop") and item.node().initialized():
                item.node().stop()

    def suspendActionSlot(self):
        """
        Slot to receive events from the suspend action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and hasattr(item.node(), "suspend") and item.node().initialized():
                item.node().suspend()

    def reloadActionSlot(self):
        """
        Slot to receive events from the reload action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and hasattr(item.node(), "reload") and item.node().initialized():
                item.node().reload()

    def configureActionSlot(self):
        """
        Slot to receive events from the configure action in the
        contextual menu.
        """

        items = []
        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and item.node().initialized():
                items.append(item)

        if items:
            self.configureSlot(items)

    def changeSymbolActionSlot(self):
        """
        Slot to receive events from the change symbol action in the
        contextual menu.
        """

        items = []
        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and item.node().initialized():
                items.append(item)
        if items:
            dialog = SymbolSelectionDialog(self, items)
            dialog.show()
            dialog.exec_()

    def consoleToNode(self, node):
        """
        Start a console application to connect to a node.

        :param node: Node instance

        :returns: False if the console application could not be started
        """

        if not hasattr(node, "console") or not node.initialized() or node.status() != Node.started:
            # returns True to ignore this node.
            return True

        if hasattr(node, "serialConsole") and node.serialConsole():
            try:
                from .serial_console import serialConsole
                serialConsole(node.name())
            except (OSError, ValueError) as e:
                QtGui.QMessageBox.critical(self, "Console", "Cannot start serial console application: {}".format(e))
                return False
        else:
            name = node.name()
            console_port = node.console()
            console_host = node.server().host
            try:
                from .telnet_console import telnetConsole
                telnetConsole(name, console_host, console_port)
            except (OSError, ValueError) as e:
                QtGui.QMessageBox.critical(self, "Console", "Cannot start console application: {}".format(e))
                return False
        return True

    def consoleActionSlot(self):
        """
        Slot to receive events from the console action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem):
                if self.consoleToNode(item.node()):
                    continue

    def captureActionSlot(self):
        """
        Slot to receive events from the capture action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and hasattr(item.node(), "startPacketCapture") and item.node().initialized():
                node = item.node()
                ports = {}
                for port in node.ports():
                    if not port.isFree() and port.packetCaptureSupported() and not port.capturing():
                        for dlt_name, dlt in port.dataLinkTypes().items():
                            key = "Port {} ({} encapsulation: {})".format(port.name(), dlt_name, dlt)
                            ports[key] = [port, dlt]
                if ports:
                    selection, ok = QtGui.QInputDialog.getItem(self, "Capture on {}".format(node.name()), "Please select a port:", list(ports.keys()), 0, False)
                    if ok:
                        if selection in ports:
                            port, dlt = ports[selection]
                            node.startPacketCapture(port, port.captureFileName(node.name()), dlt)
                else:
                    QtGui.QMessageBox.warning(self, "Capture", "No port available for packet capture on {}".format(node.name()))

    def idlepcActionSlot(self):
        """
        Slot to receive events from the idlepc action in the
        contextual menu.
        """

        items = self.scene().selectedItems()
        if len(items) != 1:
            QtGui.QMessageBox.critical(self, "Idle-PC", "Please select only one router")
            return
        item = items[0]
        if isinstance(item, NodeItem) and hasattr(item.node(), "idlepcs") and item.node().initialized():
            router = item.node()
            idlepc = router.idlepc()
            router.computeIdlepcs()

            #TODO: improve to show progress over 10 seconds
            self._idlepc_progress_dialog = QtGui.QProgressDialog("Computing values...", "Cancel", 0, 0, parent=self)
            self._idlepc_progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            self._idlepc_progress_dialog.setWindowTitle("Idle-PC")

            def cancel():
                router.idlepc_signal.disconnect(self._showIdlepcProposals)
                router.server_error_signal.disconnect(self._showIdlepcError)
                router.setIdlepc(idlepc)

            self._idlepc_progress_dialog.canceled.connect(cancel)
            router.idlepc_signal.connect(self._showIdlepcProposals)
            router.server_error_signal.connect(self._showIdlepcError)
            self._idlepc_progress_dialog.show()

    def _showIdlepcError(self, node_id, code, message):
        """
        Shows an error message if the Idle-PC values cannot be computed.
        """

        self._idlepc_progress_dialog.reject()
        QtGui.QMessageBox.critical(self, "Idle-PC", "Error: {}".format(message))
        router = self.scene().selectedItems()[0].node()
        router.server_error_signal.disconnect(self._showIdlepcError)
        router.idlepc_signal.disconnect(self._showIdlepcProposals)

    def _showIdlepcProposals(self):
        """
        Slot to allow the user to select an idlepc value.
        """

        self._idlepc_progress_dialog.accept()
        router = self.scene().selectedItems()[0].node()
        router.idlepc_signal.disconnect(self._showIdlepcProposals)
        router.server_error_signal.disconnect(self._showIdlepcError)
        idlepcs = router.idlepcs()
        if idlepcs and idlepcs[0] != "0x0":
            dialog = IdlePCDialog(router, idlepcs, parent=self)
            dialog.show()
            dialog.exec_()
        else:
            QtGui.QMessageBox.critical(self, "Idle-PC", "Sorry no Idle-PC values could be computed, please check again with Cisco IOS in a different state")

    def duplicateActionSlot(self):
        """
        Slot to receive events from the duplicate action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if isinstance(item, NoteItem):
                note_item = item.duplicate()
                self.scene().addItem(note_item)
                self._topology.addNote(note_item)
            elif isinstance(item, RectangleItem):
                rectangle_item = item.duplicate()
                self.scene().addItem(rectangle_item)
                self._topology.addRectangle(rectangle_item)
            elif isinstance(item, EllipseItem):
                ellipse_item = item.duplicate()
                self.scene().addItem(ellipse_item)
                self._topology.addEllipse(ellipse_item)
            elif isinstance(item, ImageItem):
                image_item = item.duplicate()
                self.scene().addItem(image_item)
                self._topology.addImage(image_item)

    def styleActionSlot(self):
        """
        Slot to receive events from the style action in the
        contextual menu.
        """

        items = []
        for item in self.scene().selectedItems():
            if isinstance(item, ShapeItem):
                items.append(item)
        if items:
            style_dialog = StyleEditorDialog(self._main_window, items)
            style_dialog.show()
            style_dialog.exec_()

    def textEditActionSlot(self):
        """
        Slot to receive events from the text edit action in the
        contextual menu.
        """

        items = []
        for item in self.scene().selectedItems():
            if isinstance(item, NoteItem):
                items.append(item)
        if items:
            text_edit_dialog = TextEditorDialog(self._main_window, items)
            text_edit_dialog.show()
            text_edit_dialog.exec_()

    def raiseLayerActionSlot(self):
        """
        Slot to receive events from the raise one layer action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if item.parentItem() is None:
                current_zvalue = item.zValue()
                item.setZValue(current_zvalue + 1)
                item.update()

    def lowerLayerActionSlot(self):
        """
        Slot to receive events from the lower one layer action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if item.parentItem() is None:
                current_zvalue = item.zValue()
                item.setZValue(current_zvalue - 1)
                item.update()

    def deleteActionSlot(self):
        """
        Slot to receive events from the delete action in the
        contextual menu.
        """

        selected_nodes = []
        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem):
                selected_nodes.append(item.node())
        if selected_nodes:
            if len(selected_nodes) > 1:
                question = "Do you want to permanently delete these {} nodes?".format(len(selected_nodes))
            else:
                question = "Do you want to permanently delete {}?".format(selected_nodes[0].name())
            reply = QtGui.QMessageBox.question(self, "Delete", question,
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.No:
                return
        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem):
                item.node().delete()
                self._topology.removeNode(item.node())
            elif item.parentItem() is None:
                item.delete()

    def createNode(self, node_data, pos):
        """
        Creates a new node on the scene.

        :param node_data: node data to create a new node
        :param pos: position of the drop event

        :returns: NodeItem instance
        """

        try:
            log.debug('In createNode')
            node_module = None
            for module in MODULES:
                instance = module.instance()
                node_class = module.getNodeClass(node_data["class"])
                if node_class in instance.classes():
                    node_module = instance
                    break

            if not node_module:
                raise ModuleError("Could not find any module for {}".format(node_class))

            if not "server" in node_data:
                server = node_module.allocateServer(node_class)
            elif node_data["server"] == "local":
                server = Servers.instance().localServer()
            elif node_data["server"] == "cloud":
                server = Servers.instance().anyCloudServer()
            else:
                try:
                    host, port = node_data["server"].rsplit(":", 1)
                except ValueError:
                    raise ModuleError("Wrong format for server: '{}', please recreate the node in preferences".format(node_data["server"]))
                server = Servers.instance().getRemoteServer(host, port)
            if not server.connected() and ConnectToServer(self, server) is False:
                return

            node = node_module.createNode(node_class, server)
            node.error_signal.connect(self._main_window.uiConsoleTextEdit.writeError)
            node.warning_signal.connect(self._main_window.uiConsoleTextEdit.writeWarning)
            node.server_error_signal.connect(self._main_window.uiConsoleTextEdit.writeServerError)
            node_item = NodeItem(node, node_data["default_symbol"], node_data["hover_symbol"])
            node_module.setupNode(node, node_data["name"])
        except ModuleError as e:
            QtGui.QMessageBox.critical(self, "Node creation", "{}".format(e))
            return

        node_item.setPos(self.mapToScene(pos))
        self.scene().addItem(node_item)
        x = node_item.pos().x() - (node_item.boundingRect().width() / 2)
        y = node_item.pos().y() - (node_item.boundingRect().height() / 2)
        node_item.setPos(x, y)
        self._topology.addNode(node)
        self._main_window.uiTopologySummaryTreeWidget.addNode(node)
        return node_item
