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
import sip
import sys

from .qt import QtCore, QtGui, QtNetwork, QtWidgets, qpartial, qslot
from .items.node_item import NodeItem
from .dialogs.node_properties_dialog import NodePropertiesDialog
from .link import Link
from .node import Node
from .modules import MODULES
from .modules.module_error import ModuleError
from .settings import GRAPHICS_VIEW_SETTINGS
from .topology import Topology
from .appliance_manager import ApplianceManager
from .dialogs.style_editor_dialog import StyleEditorDialog
from .dialogs.text_editor_dialog import TextEditorDialog
from .dialogs.symbol_selection_dialog import SymbolSelectionDialog
from .dialogs.idlepc_dialog import IdlePCDialog
from .dialogs.console_command_dialog import ConsoleCommandDialog
from .dialogs.file_editor_dialog import FileEditorDialog
from .local_config import LocalConfig
from .progress import Progress
from .utils.server_select import server_select
from .compute_manager import ComputeManager

# link items
from .items.link_item import LinkItem
from .items.ethernet_link_item import EthernetLinkItem
from .items.serial_link_item import SerialLinkItem

# other items
from .items.note_item import NoteItem
from .items.text_item import TextItem
from .items.shape_item import ShapeItem
from .items.drawing_item import DrawingItem
from .items.rectangle_item import RectangleItem
from .items.line_item import LineItem
from .items.ellipse_item import EllipseItem
from .items.image_item import ImageItem

log = logging.getLogger(__name__)


class GraphicsView(QtWidgets.QGraphicsView):

    """
    Graphics view that displays the scene.

    :param parent: parent widget
    """

    def __init__(self, parent):

        # Our parent is the central widget which parent is the main window.
        self._main_window = parent.parent()

        super().__init__(parent)
        self._settings = {}
        self._loadSettings()

        self._adding_link = False
        self._adding_note = False
        self._adding_rectangle = False
        self._adding_ellipse = False
        self._adding_line = False
        self._newlink = None
        self._dragging = False
        self._last_mouse_position = None
        self._topology = Topology.instance()
        self._background_warning_msgbox = QtWidgets.QErrorMessage(self)
        self._background_warning_msgbox.setWindowTitle("Layer position")

        # set the scene
        scene = QtWidgets.QGraphicsScene(parent=self)
        width = self._settings["scene_width"]
        height = self._settings["scene_height"]
        self.setScene(scene)
        self.setSceneSize(width, height)

        # set the custom flags for this view
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)

        # default directories for QFileDialog
        self._import_configs_from_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        self._import_config_dir = ""
        self._export_configs_to_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        self._export_config_dir = ""

        self._local_addresses = ['0.0.0.0', '127.0.0.1', 'localhost', '::1', '0:0:0:0:0:0:0:1', '::', QtNetwork.QHostInfo.localHostName()]

    def setSceneSize(self, width, height):
        self.scene().setSceneRect(-(width / 2), -(height / 2), width, height)

    def setZoom(self, zoom):
        """
        Sets zoom of the Graphics View
        :param zoom:
        :return:
        """
        if zoom:
            factor = zoom / 100.
            self.scale(factor, factor)

    def setEnabled(self, enabled):

        if enabled is False:
            self.reset()
            item = QtWidgets.QGraphicsTextItem("Please create a project")
            item.setPos(0, 0)
            self.scene().addItem(item)
        super().setEnabled(enabled)

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

        # reset the topology
        self._topology.reset()

        # clear the topology summary
        self._main_window.uiTopologySummaryTreeWidget.clear()

        # clear all objects on the scene
        self.scene().clear()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings(self.__class__.__name__, GRAPHICS_VIEW_SETTINGS)

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
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

    def addingLinkSlot(self, enabled):
        """
        Slot to receive events from MainWindow
        when a user has clicked on "Add a link" button.

        :param enable: either the user is adding a link or not (boolean)
        """

        if enabled:
            self.setCursor(QtCore.Qt.CrossCursor)
        else:
            if self._newlink and self._newlink in self.scene().items():
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

    def addLine(self, state):
        """
        Adds a line.

        :param state: boolean
        """

        if state:
            self._adding_line = True
            self.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self._adding_line = False
            self.setCursor(QtCore.Qt.ArrowCursor)

    def addImage(self, image_path):
        """
        Adds an image.

        :param image_path: path to the image
        """

        image_item = ImageItem(image_path=image_path, project=self._topology.project())
        image_item.create()
        self.scene().addItem(image_item)
        self._topology.addDrawing(image_item)

    def addLink(self, source_node, source_port, destination_node, destination_port, **link_data):
        """
        Creates a Link instance representing a connection between 2 devices.

        :param source_node: source Node instance
        :param source_port: source Port instance
        :param destination_node: destination Node instance
        :param destination_port: destination Port instance
        :param link_data: information about link from the API
        :returns: Link
        """

        link = Link(source_node, source_port, destination_node, destination_port, **link_data)
        # connect the signals that let the graphics view knows about events such as
        # a new link creation or deletion.
        if self._topology.addLink(link):
            link.add_link_signal.connect(self.addLinkSlot)
            link.delete_link_signal.connect(self.deleteLinkSlot)

            if link.initialized():
                self.addLinkSlot(link.id())
        return link

    def addLinkSlot(self, link_id):
        """
        Slot to receive events from Link instances
        when a link has been created.

        :param link_id: link identifier
        """

        link = self._topology.getLink(link_id)
        if not link:
            return
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
            log.error("Could not find a source or destination item for the link!")
            self.deleteLinkSlot(link_id)
            return

        if link.sourcePort().linkType() == "Serial":
            link_item = SerialLinkItem(source_item, source_port, destination_item, destination_port, link)
        else:
            link_item = EthernetLinkItem(source_item, source_port, destination_item, destination_port, link)
        self.scene().addItem(link_item)

    def deleteLinkSlot(self, link_id):
        """
        Slot to receive events from Link instances
        when a link has been deleted.

        :param link_id: link identifier
        """

        link = self._topology.getLink(link_id)
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

            if source_port.link() is not None:
                QtWidgets.QMessageBox.warning(self, "Create link", "Can't create the link the port is not free")
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
            destination_port = destination_item.connectToPort()
            if not destination_port:
                return

            if destination_port.link() is not None:
                QtWidgets.QMessageBox.warning(self, "Create link", "Can't create the link the destination port is not free")
                return

            if self._newlink in self.scene().items():
                self.scene().removeItem(self._newlink)
            self._newlink = None
            self.addLink(source_item.node(), source_port, destination_item.node(), destination_port)

    def mousePressEvent(self, event):
        """
        Handles all mouse press events.

        :param event: QMouseEvent instance
        """

        is_not_link = True
        item = self.itemAt(event.pos())
        if item and sip.isdeleted(item):
            return

        if item and (isinstance(item, LinkItem) or isinstance(item.parentItem(), LinkItem)):
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
            if item and not sip.isdeleted(item):
                # Prevent right clicking on a selected item from de-selecting all other items
                if not item.isSelected():
                    if not event.modifiers() & QtCore.Qt.ControlModifier:
                        for it in self.scene().items():
                            it.setSelected(False)
                    if item.zValue() < 0:
                        item.setFlag(item.ItemIsSelectable, True)
                    item.setSelected(True)
                    self._showDeviceContextualMenu(QtGui.QCursor.pos())
                    if not sip.isdeleted(item) and item.zValue() < 0:
                        item.setFlag(item.ItemIsSelectable, False)

                else:
                    self._showDeviceContextualMenu(QtGui.QCursor.pos())
            # when more than one item is selected display the contextual menu even if mouse is not above an item
            elif len(self.scene().selectedItems()) > 1:
                self._showDeviceContextualMenu(QtGui.QCursor.pos())
        elif is_not_link and self._adding_link and event.button() == QtCore.Qt.RightButton:
            # send a escape key to the main window to cancel the link addition
            key = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Escape, QtCore.Qt.NoModifier)
            QtWidgets.QApplication.sendEvent(self._main_window, key)
        elif item and isinstance(item, NodeItem) and self._adding_link and event.button() == QtCore.Qt.LeftButton:
            self._userNodeLinking(event, item)
        elif event.button() == QtCore.Qt.LeftButton and self._adding_note:
            pos = self.mapToScene(event.pos())
            note = self.createDrawingItem("text", pos.x(), pos.y(), 1)
            pos_x = note.pos().x()
            pos_y = note.pos().y() - (note.boundingRect().height() / 2)
            note.setPos(pos_x, pos_y)
            note.editText()
            self._main_window.uiAddNoteAction.setChecked(False)
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._adding_note = False
        elif event.button() == QtCore.Qt.LeftButton and self._adding_rectangle:
            pos = self.mapToScene(event.pos())
            self.createDrawingItem("rect", pos.x(), pos.y(), 0)
            self._main_window.uiDrawRectangleAction.setChecked(False)
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._adding_rectangle = False
        elif event.button() == QtCore.Qt.LeftButton and self._adding_ellipse:
            pos = self.mapToScene(event.pos())
            self.createDrawingItem("ellipse", pos.x(), pos.y(), 0)
            self._main_window.uiDrawEllipseAction.setChecked(False)
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._adding_ellipse = False
        elif event.button() == QtCore.Qt.LeftButton and self._adding_line:
            pos = self.mapToScene(event.pos())
            self.createDrawingItem("line", pos.x(), pos.y(), 0)
            self._main_window.uiDrawLineAction.setChecked(False)
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._adding_line = False
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Handles all mouse release events.

        :param: QMouseEvent instance
        """

        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem):
                item.mouseRelease()

        # If the left  mouse button is not still pressed TOGETHER with the SHIFT key and neither is the middle button
        # this means the user is no longer trying to drag the view
        if self._dragging and not (event.buttons() == QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.ShiftModifier) and not event.buttons() & QtCore.Qt.MidButton:
            self._dragging = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        else:
            item = self.itemAt(event.pos())
            if item is not None and not event.modifiers() & QtCore.Qt.ControlModifier:
                item.setSelected(True)
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        """
        Handles zoom in or out using the mouse wheel.

        :param: QWheelEvent instance
        """

        if event.modifiers() == QtCore.Qt.ControlModifier:
            delta = event.angleDelta()
            if delta is not None and delta.x() == 0:
                # CTRL is pressed then use the mouse wheel to zoom in or out.
                self.scaleView(pow(2.0, delta.y() / 240.0))
                self._topology.project().setZoom(round(self.transform().m11() * 100))
                self._topology.project().update()
        else:
            super().wheelEvent(event)

    def scaleView(self, scale_factor):
        """
        Scales the view (zoom in and out).
        """

        factor = self.transform().scale(scale_factor, scale_factor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if factor < 0.10 or factor > 10:
            return
        self.scale(scale_factor, scale_factor)
        self._main_window.uiStatusBar.showMessage("Zoom: {}%".format(round(self.transform().m11() * 100)), 2000)

    def keyPressEvent(self, event):
        """
        Handles all key press events for this view.

        :param event: QKeyEvent
        """

        if event.key() == QtCore.Qt.Key_Delete:
            # check if we are editing an NoteItem instance, then send the delete key event to it
            for item in self.scene().selectedItems():
                if (isinstance(item, NoteItem) or isinstance(item, TextItem)) and item.hasFocus():
                    super().keyPressEvent(event)
                    return
            self.deleteActionSlot()
        super().keyPressEvent(event)

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
            hBar.setValue(hBar.value() + (delta.x() if QtWidgets.QApplication.isRightToLeft() else -delta.x()))
            vBar.setValue(vBar.value() - delta.y())
            self._last_mouse_position = mapped_global_pos
        if self._adding_link and self._newlink and self._newlink in self.scene().items():
            # update the mouse position when the user is adding a link.
            self._newlink.setMousePoint(self.mapToScene(event.pos()))
            event.ignore()
        else:
            item = self.itemAt(event.pos())
            if item:
                # show item coords in the status bar
                coords = "X: {} Y: {} Z: {}".format(item.x(), item.y(), item.zValue())
                self._main_window.uiStatusBar.showMessage(coords, 2000)

            # force the children to redraw because of a problem with QGraphicsEffect
            for item in self.scene().selectedItems():
                for child in item.childItems():
                    child.update()
            super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        """
        Handles all mouse double click events.

        :param event: QMouseEvent instance
        """

        item = self.itemAt(event.pos())

        if not self._adding_link:
            if isinstance(item, NodeItem) and item.node().initialized():
                item.setSelected(True)
                if item.node().status() == Node.stopped or item.node().isAlwaysOn():
                    self.configureSlot()
                    return
                else:
                    self.consoleFromItems(self.scene().selectedItems())
                    return
            elif isinstance(item, NoteItem) and isinstance(item.parentItem(), NodeItem):
                if item.parentItem().node().initialized():
                    item.parentItem().setSelected(True)
                    self.changeHostnameActionSlot()
                return
        super().mouseDoubleClickEvent(event)

    def configureSlot(self, items=None):
        """
        Opens the node properties dialog.
        """

        if not items:
            items = []
            for item in self.scene().selectedItems():
                if isinstance(item, NodeItem) and item.node().initialized() and hasattr(item.node(), "configPage"):
                    items.append(item)
        with Progress.instance().context(min_duration=0):
            node_properties = NodePropertiesDialog(items, self._main_window)
            node_properties.setModal(True)
            node_properties.show()
            node_properties.exec_()

    def dragMoveEvent(self, event):
        """
        Handles all drag move events.

        :param event: QDragMoveEvent instance
        """

        # check if what is dragged is handled by this view
        if event.mimeData().hasFormat("text/uri-list") \
                or event.mimeData().hasFormat("application/x-gns3-appliance"):
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
        if event.mimeData().hasFormat("application/x-gns3-appliance"):
            appliance_id = event.mimeData().data("application/x-gns3-appliance").data().decode()
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            if event.keyboardModifiers() == QtCore.Qt.ShiftModifier:
                max_nodes_per_line = 10  # max number of nodes on a single line
                offset = 100  # spacing between elements
                integer, ok = QtWidgets.QInputDialog.getInt(self, "Nodes", "Number of nodes:", 2, 1, 100, 1)
                if ok:
                    for node_number in range(integer):
                        x = event.pos().x() - (150 / 2) + (node_number % max_nodes_per_line) * offset
                        y = event.pos().y() - (70 / 2) + (node_number // max_nodes_per_line) * offset
                        self.createNodeFromApplianceId(appliance_id, QtCore.QPoint(x, y))
            else:
                self.createNodeFromApplianceId(appliance_id, event.pos())
        elif event.mimeData().hasFormat("text/uri-list") and event.mimeData().hasUrls():
            # This should not arrive but we received bug report with it...
            if len(event.mimeData().urls()) == 0:
                return
            if len(event.mimeData().urls()) > 1:
                QtWidgets.QMessageBox.critical(self, "Project files", "Please drop only one file")
                return
            path = event.mimeData().urls()[0].toLocalFile()
            if os.path.isfile(path):
                self._main_window.loadPath(path)
            event.acceptProposedAction()
        else:
            event.ignore()

    def _showDeviceContextualMenu(self, pos):
        """
        Create and display the device contextual menu on the view.

        :param pos: position where to display the menu
        """

        menu = QtWidgets.QMenu()
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

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "configPage"), items)):
            configure_action = QtWidgets.QAction("Configure", menu)
            configure_action.setIcon(QtGui.QIcon(':/icons/configuration.svg'))
            configure_action.triggered.connect(self.configureActionSlot)
            menu.addAction(configure_action)

        if True in list(map(lambda item: isinstance(item, NodeItem), items)):
            # Action: Change hostname
            change_hostname_action = QtWidgets.QAction("Change hostname", menu)
            change_hostname_action.setIcon(QtGui.QIcon(':/icons/show-hostname.svg'))
            change_hostname_action.triggered.connect(self.changeHostnameActionSlot)
            menu.addAction(change_hostname_action)

        if True in list(map(lambda item: isinstance(item, NodeItem), items)):
            # Action: Change symbol
            change_symbol_action = QtWidgets.QAction("Change symbol", menu)
            change_symbol_action.setIcon(QtGui.QIcon(':/icons/node_conception.svg'))
            change_symbol_action.triggered.connect(self.changeSymbolActionSlot)
            menu.addAction(change_symbol_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "nodeDir"), items)):
            # Action: Show in file manager
            show_in_file_manager_action = QtWidgets.QAction("Show in file manager", menu)
            show_in_file_manager_action.setIcon(QtGui.QIcon(':/icons/open.svg'))
            show_in_file_manager_action.triggered.connect(self.showInFileManagerSlot)
            menu.addAction(show_in_file_manager_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "console"), items)):
            console_action = QtWidgets.QAction("Console", menu)
            console_action.setIcon(QtGui.QIcon(':/icons/console.svg'))
            console_action.triggered.connect(self.consoleActionSlot)
            menu.addAction(console_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "console"), items)):
            console_edit_action = QtWidgets.QAction("Custom console", menu)
            console_edit_action.setIcon(QtGui.QIcon(':/icons/console_edit.svg'))
            console_edit_action.triggered.connect(self.customConsoleActionSlot)
            menu.addAction(console_edit_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "auxConsole"), items)):
            aux_console_action = QtWidgets.QAction("Auxiliary console", menu)
            aux_console_action.setIcon(QtGui.QIcon(':/icons/aux-console.svg'))
            aux_console_action.triggered.connect(self.auxConsoleActionSlot)
            menu.addAction(aux_console_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "configFiles"), items)):
            import_config_action = QtWidgets.QAction("Import config", menu)
            import_config_action.setIcon(QtGui.QIcon(':/icons/import_config.svg'))
            import_config_action.triggered.connect(self.importConfigActionSlot)
            menu.addAction(import_config_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "configFiles"), items)):
            export_config_action = QtWidgets.QAction("Export config", menu)
            export_config_action.setIcon(QtGui.QIcon(':/icons/export_config.svg'))
            export_config_action.triggered.connect(self.exportConfigActionSlot)
            menu.addAction(export_config_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "configFiles"), items)):
            export_config_action = QtWidgets.QAction("Edit config", menu)
            export_config_action.setIcon(QtGui.QIcon(':/icons/edit.svg'))
            export_config_action.triggered.connect(self.editConfigActionSlot)
            menu.addAction(export_config_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "idlepc"), items)):
            idlepc_action = QtWidgets.QAction("Idle-PC", menu)
            idlepc_action.setIcon(QtGui.QIcon(':/icons/calculate.svg'))
            idlepc_action.triggered.connect(self.idlepcActionSlot)
            menu.addAction(idlepc_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "idlepc"), items)):
            auto_idlepc_action = QtWidgets.QAction("Auto Idle-PC", menu)
            auto_idlepc_action.setIcon(QtGui.QIcon(':/icons/calculate.svg'))
            auto_idlepc_action.triggered.connect(self.autoIdlepcActionSlot)
            menu.addAction(auto_idlepc_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and not item.node().isAlwaysOn(), items)):
            start_action = QtWidgets.QAction("Start", menu)
            start_action.setIcon(QtGui.QIcon(':/icons/start.svg'))
            start_action.triggered.connect(self.startActionSlot)
            menu.addAction(start_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and not item.node().isAlwaysOn(), items)):
            suspend_action = QtWidgets.QAction("Suspend", menu)
            suspend_action.setIcon(QtGui.QIcon(':/icons/pause.svg'))
            suspend_action.triggered.connect(self.suspendActionSlot)
            menu.addAction(suspend_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and not item.node().isAlwaysOn(), items)):
            stop_action = QtWidgets.QAction("Stop", menu)
            stop_action.setIcon(QtGui.QIcon(':/icons/stop.svg'))
            stop_action.triggered.connect(self.stopActionSlot)
            menu.addAction(stop_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and not item.node().isAlwaysOn(), items)):
            reload_action = QtWidgets.QAction("Reload", menu)
            reload_action.setIcon(QtGui.QIcon(':/icons/reload.svg'))
            reload_action.triggered.connect(self.reloadActionSlot)
            menu.addAction(reload_action)

        if True in list(map(lambda item: isinstance(item, DrawingItem), items)):
            duplicate_action = QtWidgets.QAction("Duplicate", menu)
            duplicate_action.setIcon(QtGui.QIcon(':/icons/new.svg'))
            duplicate_action.triggered.connect(self.duplicateActionSlot)
            menu.addAction(duplicate_action)

        if True in list(map(lambda item: isinstance(item, NoteItem), items)):
            text_edit_action = QtWidgets.QAction("Text edit", menu)
            text_edit_action.setIcon(QtGui.QIcon(':/icons/show-hostname.svg'))
            text_edit_action.triggered.connect(self.textEditActionSlot)
            menu.addAction(text_edit_action)

        if True in list(map(lambda item: isinstance(item, TextItem), items)):
            text_edit_action = QtWidgets.QAction("Text edit", menu)
            text_edit_action.setIcon(QtGui.QIcon(':/icons/edit.svg'))
            text_edit_action.triggered.connect(self.textEditActionSlot)
            menu.addAction(text_edit_action)

        if True in list(map(lambda item: isinstance(item, ShapeItem) or isinstance(item, LineItem), items)):
            style_action = QtWidgets.QAction("Style", menu)
            style_action.setIcon(QtGui.QIcon(':/icons/drawing.svg'))
            style_action.triggered.connect(self.styleActionSlot)
            menu.addAction(style_action)

        if True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "commandLine"), items)):
            # Action: Get command line
            show_in_file_manager_action = QtWidgets.QAction("Command line", menu)
            show_in_file_manager_action.setIcon(QtGui.QIcon(':/icons/console.svg'))
            show_in_file_manager_action.triggered.connect(self.getCommandLineSlot)
            menu.addAction(show_in_file_manager_action)

        if sys.platform.startswith("win") and True in list(map(lambda item: isinstance(item, NodeItem) and hasattr(item.node(), "bringToFront"), items)):
            # Action: bring console or window to front (Windows only)
            bring_to_front_action = QtWidgets.QAction("Bring to front", menu)
            bring_to_front_action.setIcon(QtGui.QIcon(':/icons/console.svg'))
            bring_to_front_action.triggered.connect(self.bringToFrontSlot)
            menu.addAction(bring_to_front_action)

        if True in list(map(lambda item: isinstance(item, NoteItem), items)) and False in list(map(lambda item: item.parentItem() is None, items)):
            # action only for port labels
            reset_label_position_action = QtWidgets.QAction("Reset position", menu)
            reset_label_position_action.setIcon(QtGui.QIcon(':/icons/reset.svg'))
            reset_label_position_action.triggered.connect(self.resetLabelPositionActionSlot)
            menu.addAction(reset_label_position_action)

        # item must have no parent
        if True in list(map(lambda item: item.parentItem() is None, items)):

            if len(items) > 1:
                horizontal_align_action = QtWidgets.QAction("Align horizontally", menu)
                horizontal_align_action.setIcon(QtGui.QIcon(':/icons/horizontally.svg'))
                horizontal_align_action.triggered.connect(self.horizontalAlignmentSlot)
                menu.addAction(horizontal_align_action)

                vertical_align_action = QtWidgets.QAction("Align vertically", menu)
                vertical_align_action.setIcon(QtGui.QIcon(':/icons/vertically.svg'))
                vertical_align_action.triggered.connect(self.verticalAlignmentSlot)
                menu.addAction(vertical_align_action)

            raise_layer_action = QtWidgets.QAction("Raise one layer", menu)
            raise_layer_action.setIcon(QtGui.QIcon(':/icons/raise_z_value.svg'))
            raise_layer_action.triggered.connect(self.raiseLayerActionSlot)
            menu.addAction(raise_layer_action)

            lower_layer_action = QtWidgets.QAction("Lower one layer", menu)
            lower_layer_action.setIcon(QtGui.QIcon(':/icons/lower_z_value.svg'))
            lower_layer_action.triggered.connect(self.lowerLayerActionSlot)
            menu.addAction(lower_layer_action)

            delete_action = QtWidgets.QAction("Delete", menu)
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
            if isinstance(item, NodeItem) and item.node().initialized() and hasattr(item.node(), "configPage"):
                items.append(item)

        if items:
            self.configureSlot(items)

    def changeHostnameActionSlot(self):
        """
        Slot to receive events from the change hostname action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and item.node().initialized():
                new_hostname, ok = QtWidgets.QInputDialog.getText(self, "Change hostname", "Hostname:", QtWidgets.QLineEdit.Normal, item.node().name())
                if ok:
                    if hasattr(item.node(), "validateHostname"):
                        if not item.node().validateHostname(new_hostname):
                            QtWidgets.QMessageBox.critical(self, "Change hostname", "Invalid name detected for this node: {}".format(new_hostname))
                            continue
                    item.node().update({"name": new_hostname})

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

    def showInFileManagerSlot(self):
        """
        Slot to receive events from the show in file manager action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and hasattr(item.node(), "nodeDir") and item.node().initialized():
                node = item.node()
                node_dir = node.nodeDir()
                if node_dir is None:
                    QtWidgets.QMessageBox.critical(self, "Show in file manager", "This node has no working directory")
                    break

                if os.path.exists(node_dir):
                    log.debug("Open %s in file manager")
                    if QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(node_dir)) is False:
                        QtWidgets.QMessageBox.critical(self, "Show in file manager", "Failed to open {}".format(node_dir))
                        break
                else:
                    reply = QtWidgets.QMessageBox.information(self, "Show in file manager", "The device directory is located in {} on {}\n\nCopy path to clipboard?".format(node_dir, node.compute().name()), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    if reply == QtWidgets.QMessageBox.Yes:
                        QtWidgets.QApplication.clipboard().setText(node_dir)
                    break

    def consoleToNode(self, node, aux=False):
        """
        Start a console application to connect to a node.

        :param node: Node instance
        :param aux: auxiliary console mode

        :returns: False if the console application could not be started
        """

        if not hasattr(node, "console") or not node.initialized() or node.status() != Node.started:
            # returns True to ignore this node.
            return True

        if aux and not hasattr(node, "auxConsole"):
            # returns True to ignore this node.
            return True

        # TightVNC has lack support of IPv6 host at this moment
        if "vncviewer" in node.consoleCommand() and ":" in node.consoleHost():
            QtWidgets.QMessageBox.warning(
                self, "TightVNC", "TightVNC (vncviewer) may not start because of lack of IPv6 support.")

        try:
            node.openConsole(aux=aux)
        except (OSError, ValueError) as e:
            QtWidgets.QMessageBox.critical(self, "Console", "Cannot start console application: {}".format(e))
            return False
        return True

    def consoleFromItems(self, items):
        """
        Console from scene items.

        :param items: Item instances
        """

        nodes = {}
        node_initialized = False
        for item in items:
            if isinstance(item, NodeItem) and hasattr(item.node(), "console") and item.node().initialized():
                node_initialized = True
                if item.node().status() == Node.started:
                    node = item.node()
                    nodes[node.name()] = node

        if not nodes and node_initialized:
            if len(items) > 1:
                QtWidgets.QMessageBox.warning(self, "Console", "At least one node must be started before a console can be opened")
            else:
                QtWidgets.QMessageBox.warning(self, "Console", "This node must be started before a console can be opened")

        delay = self._main_window.settings()["delay_console_all"]
        counter = 0
        for name in sorted(nodes.keys()):
            node = nodes[name]
            callback = qpartial(self.consoleToNode, node)
            self._main_window.run_later(counter, callback)
            counter += delay

    def consoleActionSlot(self):
        """
        Slot to receive events from the console action in the
        contextual menu.
        """

        self.consoleFromItems(self.scene().selectedItems())

    def customConsoleActionSlot(self):
        """
        Allow user to use a custom console for this VM
        """

        current_cmd = None
        console_type = "telnet"
        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and hasattr(item.node(), "console") and item.node().initialized() and item.node().status() == Node.started:
                if item.node().consoleType() not in ("telnet", "serial", "vnc", "spice"):
                    continue
                current_cmd = item.node().consoleCommand()
                console_type = item.node().consoleType()

        (ok, cmd) = ConsoleCommandDialog.getCommand(self, console_type=console_type, current=current_cmd)
        if ok:
            for item in self.scene().selectedItems():
                if isinstance(item, NodeItem) and hasattr(item.node(), "console") and item.node().initialized() and item.node().status() == Node.started:
                    node = item.node()
                    if node.consoleType() not in ("telnet", "serial", "vnc", "spice"):
                        continue
                    try:
                        node.openConsole(command=cmd)
                    except (OSError, ValueError) as e:
                        QtWidgets.QMessageBox.critical(self, "Console", "Cannot start console application: {}".format(e))

    def auxConsoleFromItems(self, items):
        """
        Aux console from scene items.

        :param items: Item instances
        """

        nodes = {}
        node_initialized = False
        for item in items:
            if isinstance(item, NodeItem) and hasattr(item.node(), "auxConsole") and item.node().initialized():
                node_initialized = True
                if item.node().status() == Node.started:
                    node = item.node()
                    nodes[node.name()] = node

        if not nodes and node_initialized:
            if len(items) > 1:
                QtWidgets.QMessageBox.warning(self, "Console", "At least one node must be started before a console can be opened")
            else:
                QtWidgets.QMessageBox.warning(self, "Console", "This node must be started before a console can be opened")

        delay = self._main_window.settings()["delay_console_all"]
        counter = 0
        for name in sorted(nodes.keys()):
            node = nodes[name]
            callback = qpartial(self.consoleToNode, node, aux=True)
            self._main_window.run_later(counter, callback)
            counter += delay

    def auxConsoleActionSlot(self):
        """
        Slot to receive events from the auxiliary console action in the
        contextual menu.
        """

        self.auxConsoleFromItems(self.scene().selectedItems())

    def importConfigActionSlot(self):
        """
        Slot to receive events from the import config action in the
        contextual menu.
        """

        items = []
        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and hasattr(item.node(), "configFiles") and item.node().initialized():
                items.append(item)

        if not items:
            return

        for item in items:
            if len(item.node().configFiles()) == 1:
                config_file = item.node().configFiles()[0]
            else:
                config_file, ok = QtWidgets.QInputDialog.getItem(self, "Import file", "File to import?", item.node().configFiles(), 0, False)
                if not ok:
                    continue

            if not self._import_config_dir:
                self._import_config_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DownloadLocation)

            path, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            "Import {}".format(os.path.basename(config_file)),
                                                            self._import_config_dir,
                                                            "All files (*.*);;Config files (*.cfg)",
                                                            "Config files (*.cfg)")
            self._import_config_dir = os.path.dirname(path)
            item.node().importFile(config_file, path)

    def editConfigActionSlot(self):
        """
        Slot to receive event to edit the configuration file
        """

        items = []
        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and hasattr(item.node(), "configFiles") and item.node().initialized():
                items.append(item)

        if not items:
            return

        for item in items:
            if len(item.node().configFiles()) == 1:
                config_file = item.node().configFiles()[0]
            else:
                config_file, ok = QtWidgets.QInputDialog.getItem(self, "Edit file", "File to edit?", item.node().configFiles(), 0, False)
                if not ok:
                    continue
            dialog = FileEditorDialog(item.node(), config_file, parent=self)
            dialog.show()
            dialog.exec_()

    def exportConfigActionSlot(self):
        """
        Slot to receive events from the export config action in the
        contextual menu.
        """

        items = []
        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and hasattr(item.node(), "configFiles") and item.node().initialized():
                items.append(item)

        if not items:
            return

        if not self._export_configs_to_dir:
            self._export_configs_to_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DownloadLocation)

        for item in items:
            for config_file in item.node().configFiles():
                path, ok = QtWidgets.QFileDialog.getSaveFileName(self, "Export file", os.path.join(self._export_configs_to_dir, item.node().name() + "_" + os.path.basename(config_file)), "All files (*.*);;Config files (*.cfg)")

                if not path:
                    continue

                self._export_configs_to_dir = os.path.dirname(path)

                item.node().exportFile(config_file, path)

    def getCommandLineSlot(self):
        """
        Slot to receive events from the get command line action in the
        contextual menu.
        """

        items = self.scene().selectedItems()
        if len(items) != 1:
            QtWidgets.QMessageBox.critical(self, "Command line", "Please select only one router")
            return
        item = items[0]
        if isinstance(item, NodeItem) and hasattr(item.node(), "commandLine"):
            router = item.node()
            if router.commandLine() is None:
                QtWidgets.QMessageBox.warning(self, "Command line", "Get command line is not supported for this type of node.")
            elif router.commandLine() == '':
                QtWidgets.QMessageBox.warning(self, "Command line", "Please start the node in order to get the command line.")
            else:
                dialog = QtWidgets.QInputDialog(self)
                dialog.setOptions(QtWidgets.QInputDialog.NoButtons)
                dialog.setLabelText("Command used to start the VM:")
                dialog.setTextValue(router.commandLine())
                dialog.show()
                dialog.exec_()

    def bringToFrontSlot(self):
        """
        Slot to receive events from the bring to front action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem) and hasattr(item.node(), "bringToFront"):
                item.node().bringToFront()

    def idlepcActionSlot(self):
        """
        Slot to receive events from the idlepc action in the
        contextual menu.
        """

        items = self.scene().selectedItems()
        if len(items) != 1:
            QtWidgets.QMessageBox.critical(self, "Idle-PC", "Please select only one router")
            return
        item = items[0]
        if isinstance(item, NodeItem) and hasattr(item.node(), "idlepc") and item.node().initialized():
            router = item.node()
            router.computeIdlepcs(self._idlepcCallback)

    def _idlepcCallback(self, result, error=False, context={}, **kwargs):
        """
        Slot to allow the user to select an idle-pc value.
        """

        if error:
            QtWidgets.QMessageBox.critical(self, "Idle-PC", "Error: {}".format(result["message"]))
        else:
            router = context["router"]
            log.debug("{} has received Idle-PC proposals".format(router.name()))
            idlepcs = result
            if idlepcs and idlepcs[0] != "0x0":
                dialog = IdlePCDialog(router, idlepcs, parent=self)
                dialog.show()
                dialog.exec_()
            else:
                QtWidgets.QMessageBox.critical(self, "Idle-PC", "Sorry no Idle-PC values could be computed, please check again with Cisco IOS in a different state")

    def autoIdlepcActionSlot(self):
        """
        Slot to receive events from the auto idlepc action in the
        contextual menu.
        """

        items = self.scene().selectedItems()
        if len(items) != 1:
            QtWidgets.QMessageBox.critical(self, "Auto Idle-PC", "Please select only one router")
            return
        item = items[0]
        if isinstance(item, NodeItem) and hasattr(item.node(), "idlepc") and item.node().initialized():
            router = item.node()
            router.computeAutoIdlepc(self._autoIdlepcCallback)

    def _autoIdlepcCallback(self, result, error=False, context={}, **kwargs):
        """
        Slot to allow the user to select an idlepc value.
        """

        if error:
            QtWidgets.QMessageBox.critical(self, "Auto Idle-PC", "Error: {}".format(result["message"]))
        else:
            router = context["router"]
            idlepc = result["idlepc"]
            log.debug("{} has received the auto idle-pc value: {}".format(router.name(), idlepc))
            router.setIdlepc(idlepc)
            # apply Idle-PC to all routers with the same IOS image
            ios_image = os.path.basename(router.settings()["image"])
            for node in Topology.instance().nodes():
                if hasattr(node, "idlepc") and node.settings()["image"] == ios_image:
                    node.setIdlepc(idlepc)
            # apply the idle-pc to templates with the same IOS image
            router.module().updateImageIdlepc(ios_image, idlepc)
            QtWidgets.QMessageBox.information(self, "Auto Idle-PC", "Idle-PC value {} has been applied on {} and all routers with IOS image {}".format(idlepc,
                                                                                                                                                       router.name(),
                                                                                                                                                       ios_image))

    def duplicateActionSlot(self):
        """
        Slot to receive events from the duplicate action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if isinstance(item, DrawingItem):
                if isinstance(item, EllipseItem):
                    type = "ellipse"
                elif isinstance(item, TextItem):
                    type = "text"
                elif isinstance(item, RectangleItem):
                    type = "rect"
                else:
                    type = "image"
                self.createDrawingItem(type, item.pos().x() + 20, item.pos().y() + 20, item.zValue(), rotation=item.rotation(), svg=item.toSvg())

    def styleActionSlot(self):
        """
        Slot to receive events from the style action in the
        contextual menu.
        """

        items = []
        for item in self.scene().selectedItems():
            if isinstance(item, ShapeItem) or isinstance(item, LineItem):
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
            if isinstance(item, NoteItem) or isinstance(item, TextItem):
                items.append(item)
        if items:
            text_edit_dialog = TextEditorDialog(self._main_window, items)
            text_edit_dialog.show()
            text_edit_dialog.exec_()

    def resetLabelPositionActionSlot(self):
        """
        Slot to receive events from the reset label position action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if isinstance(item, NoteItem) and item.parentItem():
                links = item.parentItem().links()
                for port in item.parentItem().node().ports():
                    # find the correct port associated with the label
                    if port.label() == item:
                        port.deleteLabel()
                        break
                # adjust all node links to force to re-display the label
                for link in links:
                    link.adjust()

    def horizontalAlignmentSlot(self):
        """
        Slot to receive events from the horizontal align action in the
        contextual menu.
        """

        horizontal_pos = None
        for item in self.scene().selectedItems():
            if item.parentItem() is None:
                if horizontal_pos is None:
                    horizontal_pos = item.y() + item.boundingRect().height() / 2
                item.setX(item.x())
                item.setY(horizontal_pos - item.boundingRect().height() / 2)
                item.updateNode()

    def verticalAlignmentSlot(self):
        """
        Slot to receive events from the vertical align action in the
        contextual menu.
        """

        vertical_position = None
        for item in self.scene().selectedItems():
            if item.parentItem() is None:
                if vertical_position is None:
                    vertical_position = item.x() + item.boundingRect().width() / 2
                item.setX(vertical_position - item.boundingRect().width() / 2)
                item.setY(item.y())
                item.updateNode()

    def raiseLayerActionSlot(self):
        """
        Slot to receive events from the raise one layer action in the
        contextual menu.
        """

        for item in self.scene().selectedItems():
            if item.parentItem() is None:
                current_zvalue = item.zValue()
                item.setZValue(current_zvalue + 1)
                item.updateNode()
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
                item.updateNode()
                item.update()

                if item.zValue() == -1:
                    self._background_warning_msgbox.showMessage("Object moved to a background layer. You will now have to use the right-click action to select this object in the future and raise it to layer 0 to be able to move it")

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
            reply = QtWidgets.QMessageBox.question(self, "Delete", question,
                                                   QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                return
        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem):
                item.node().delete()
                self._topology.removeNode(item.node())
            elif item.parentItem() is None:
                item.delete()

    def allocateCompute(self, node_data, module_instance):
        """
        Allocates a server.
        :returns: allocated compute node
        """

        from .main_window import MainWindow
        mainwindow = MainWindow.instance()

        if "server" in node_data:
            try:
                return ComputeManager.instance().getCompute(node_data["server"])
            except KeyError:
                raise ModuleError("Compute {} doesn't exists".format(node_data["server"]))

        server = server_select(mainwindow, node_data.get("node_type"))
        if server is None:
            raise ModuleError("Please select a server")
        return server

    def createNodeFromApplianceId(self, appliance_id, pos):
        """
        Ask the server to create a node using this appliance
        """
        pos = self.mapToScene(pos)
        ApplianceManager().instance().createNodeFromApplianceId(self._topology.project(), appliance_id, pos.x(), pos.y())

    def createNodeItem(self, node, symbol, x, y):
        node.setSymbol(symbol)
        node.setPos(x, y)
        node_item = NodeItem(node)

        self.scene().addItem(node_item)
        self._topology.addNode(node)

        node.error_signal.connect(self._displayNodeErrorSlot)
        node.server_error_signal.connect(self._displayNodeErrorSlot)

        return node_item

    @qslot
    def _displayNodeErrorSlot(self, node_id, message, *args):
        """
        Show error send by a node to the user
        """
        node = Topology.instance().getNode(node_id)
        name = "Node"
        if node:
            if node.name():
                name = node.name()
        if self._main_window and not sip.isdeleted(self._main_window):
            QtWidgets.QMessageBox.critical(self._main_window, name, message.strip())

    def createDrawingItem(self, type, x, y, z, rotation=0, svg=None, drawing_id=None):

        if type == "ellipse":
            item = EllipseItem(pos=QtCore.QPoint(x, y), z=z, rotation=rotation, project=self._topology.project(), drawing_id=drawing_id, svg=svg)
        elif type == "rect":
            item = RectangleItem(pos=QtCore.QPoint(x, y), z=z, rotation=rotation, project=self._topology.project(), drawing_id=drawing_id, svg=svg)
        elif type == "line":
            item = LineItem(pos=QtCore.QPoint(x, y), dst=QtCore.QPoint(200, 0), z=z, rotation=rotation, project=self._topology.project(), drawing_id=drawing_id, svg=svg)
        elif type == "image":
            item = ImageItem(pos=QtCore.QPoint(x, y), z=z, rotation=rotation, project=self._topology.project(), drawing_id=drawing_id, svg=svg)
        elif type == "text":
            item = TextItem(pos=QtCore.QPoint(x, y), z=z, rotation=rotation, project=self._topology.project(), drawing_id=drawing_id, svg=svg)

        if drawing_id is None:
            item.create()

        self.scene().addItem(item)
        self._topology.addDrawing(item)
        return item

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        if self._main_window.uiShowGridAction.isChecked():
            gridSize = 75
            painter.save()
            painter.setPen(QtGui.QPen(QtGui.QColor(190, 190, 190)))

            left = int(rect.left()) - (int(rect.left()) % gridSize)
            top = int(rect.top()) - (int(rect.top()) % gridSize)

            x = left
            while x < rect.right():
                painter.drawLine(x, rect.top(), x, rect.bottom())
                x += gridSize
            y = top
            while y < rect.bottom():
                painter.drawLine(rect.left(), y, rect.right(), y)
                y += gridSize
            painter.restore()
