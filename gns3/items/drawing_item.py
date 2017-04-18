#!/usr/bin/env python
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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

from ..qt import QtCore, QtWidgets, qslot

import uuid
import logging
import binascii
log = logging.getLogger(__name__)


class DrawingItem:

    show_layer = False

    """
    Base class for non emulation item
    """

    def __init__(self, project=None, pos=None, drawing_id=None, svg=None, z=0, rotation=0, **kws):
        self._id = drawing_id
        if self._id is None:
            self._id = str(uuid.uuid4())
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsFocusable | QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)

        from ..main_window import MainWindow
        self._graphics_view = MainWindow.instance().uiGraphicsView
        self._main_window = MainWindow.instance()

        self._project = project

        # Store a hash of the SVG to avoid him
        # to be send if he doesn't change
        self._hash_svg = None

        if pos:
            self.setPos(pos)
        if z:
            self.setZValue(z)
        if rotation:
            self.setRotation(rotation)

    def drawing_id(self):
        return self._id

    def create(self):
        if self._project:
            self._project.post("/drawings", self._createDrawingCallback, body=self.__json__())

    def _createDrawingCallback(self, result, error=False, **kwargs):
        """
        Callback for create.

        :param result: server response
        :param error: indicates an error (boolean)
        :returns: Boolean success or not
        """

        if error:
            log.error("Error while setting up drawing: {}".format(result["message"]))
            return False
        self._id = result["drawing_id"]
        self.updateDrawingCallback(result)

    def updateDrawing(self):
        if self._id:
            self._project.put("/drawings/" + self._id, self.updateDrawingCallback, body=self.__json__())

    @qslot
    def updateDrawingCallback(self, result, error=False, **kwargs):
        """
        Callback for update.

        :param result: server response
        :param error: indicates an error (boolean)
        :returns: Boolean success or not
        """

        if error:
            log.error("Error while setting up drawing: {}".format(result["message"]))
            return False
        self.setPos(QtCore.QPoint(result["x"], result["y"]))
        self.setZValue(result["z"])
        self.setRotation(result["rotation"])
        if "svg" in result:
            self.fromSvg(result["svg"])

    def handleKeyPressEvent(self, event):
        """
        Handles all key press events

        :param event: QKeyEvent
        :return: Boolean True the event has been captured
        """
        key = event.key()
        modifiers = event.modifiers()
        if key in (QtCore.Qt.Key_P, QtCore.Qt.Key_Plus, QtCore.Qt.Key_Equal) and modifiers & QtCore.Qt.AltModifier \
                or key == QtCore.Qt.Key_Plus and modifiers & QtCore.Qt.AltModifier and modifiers & QtCore.Qt.KeypadModifier:
            if self.rotation() == 0:
                self.setRotation(359)
            else:
                self.setRotation(self.rotation() - 1)
            return True
        elif key in (QtCore.Qt.Key_M, QtCore.Qt.Key_Minus) and modifiers & QtCore.Qt.AltModifier \
                or key == QtCore.Qt.Key_Minus and modifiers & QtCore.Qt.AltModifier and modifiers & QtCore.Qt.KeypadModifier:
            if self.rotation() < 360.0:
                self.setRotation(self.rotation() + 1)
                return True
        return False

    def keyPressEvent(self, event):
        """
        Handles all key press events

        :param event: QKeyEvent
        """

        if not self.handleKeyPressEvent(event):
            QtWidgets.QGraphicsItem.keyPressEvent(self, event)

    def __json__(self):
        data = {
            "drawing_id": self._id,
            "x": int(self.pos().x()),
            "y": int(self.pos().y()),
            "z": int(self.zValue()),
            "rotation": int(self.rotation())
        }
        svg = self.toSvg()
        hash_svg = binascii.crc32(svg.encode())
        if hash_svg != self._hash_svg:
            data["svg"] = svg
            self._hash_svg = hash_svg
        return data

    def setZValue(self, value):
        """
        Sets a new Z value.

        :param value: Z value
        """

        QtWidgets.QGraphicsItem.setZValue(self, value)
        if self.zValue() < 0:
            self.setFlag(self.ItemIsSelectable, False)
            self.setFlag(self.ItemIsMovable, False)
        else:
            self.setFlag(self.ItemIsSelectable, True)
            self.setFlag(self.ItemIsMovable, True)

    def delete(self, skip_controller=False):
        """
        Deletes this drawing.

        :param skip_controller: Do not replicate change on the controller (usefull when it's already deleted on controller)
        """

        self.scene().removeItem(self)
        from ..topology import Topology
        Topology.instance().removeDrawing(self)
        if self._id and not skip_controller:
            self._project.delete("/drawings/" + self._id, None, body=self.__json__())

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged and self.isActive() and self._main_window.uiSnapToGridAction.isChecked():
            GRID_SIZE = 75
            mid_x = self.boundingRect().width() / 2
            tmp_x = (GRID_SIZE * round((self.x() + mid_x) / GRID_SIZE)) - mid_x
            mid_y = self.boundingRect().height() / 2
            tmp_y = (GRID_SIZE * round((self.y() + mid_y) / GRID_SIZE)) - mid_y
            if tmp_x != self.x() and tmp_y != self.y():
                self.setPos(tmp_x, tmp_y)

        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            if not value:
                self.updateDrawing()
        return QtWidgets.QGraphicsItem.itemChange(self, change, value)

    def updateNode(self):
        self.updateDrawing()

    def drawLayerInfo(self, painter):
        """
        Draws the layer position.

        :param painter: QPainter instance
        """

        if self.show_layer is False:
            return

        brect = self.boundingRect()
        # don't draw anything if the object is too small
        if brect.width() < 20 or brect.height() < 20:
            return

        center = self.mapFromItem(self, brect.width() / 2.0, brect.height() / 2.0)
        painter.setBrush(QtCore.Qt.red)
        painter.setPen(QtCore.Qt.red)
        painter.drawRect((brect.width() / 2.0) - 10, (brect.height() / 2.0) - 10, 20, 20)
        painter.setPen(QtCore.Qt.black)
        zval = str(int(self.zValue()))
        painter.drawText(QtCore.QPointF(center.x() - 4, center.y() + 4), zval)
