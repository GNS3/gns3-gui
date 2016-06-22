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

from ..qt import QtCore, QtGui, QtWidgets, QtSvg

import logging
import binascii
log = logging.getLogger(__name__)


class VisualItem:

    """
    Base class for non emulation item
    """

    def __init__(self, project=None, pos=None, shape_id=None, svg=None, z=0, rotation=0, **kws):
        self._id = shape_id
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsFocusable | QtWidgets.QGraphicsItem.ItemIsSelectable)

        from ..main_window import MainWindow
        self._graphics_view = MainWindow.instance().uiGraphicsView

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


    def shape_id(self):
        return self._id

    def create(self):
        self._project.post("/shapes", self._createShapeCallback, body=self.__json__())

    def _createShapeCallback(self, result, error=False, **kwargs):
        """
        Callback for create.

        :param result: server response
        :param error: indicates an error (boolean)
        :returns: Boolean success or not
        """

        if error:
            log.error("Error while setting up shape: {}".format(result["message"]))
            return False
        self._id = result["shape_id"]

    def updateShape(self):
        if self._id:
            self._project.put("/shapes/" + self._id, self.updateShapeCallback, body=self.__json__())

    def updateShapeCallback(self, result, error=False, **kwargs):
        """
        Callback for update.

        :param result: server response
        :param error: indicates an error (boolean)
        :returns: Boolean success or not
        """

        if error:
            log.error("Error while setting up shape: {}".format(result["message"]))
            return False
        self.setPos(QtCore.QPoint(result["x"], result["y"]))
        self.setZValue(result["z"])
        self.setRotation(result["rotation"])
        if "svg" in result:
            self.fromSvg(result["svg"])

    def keyPressEvent(self, event):
        """
        Handles all key press events

        :param event: QKeyEvent
        """

        key = event.key()
        modifiers = event.modifiers()
        if key in (QtCore.Qt.Key_P, QtCore.Qt.Key_Plus, QtCore.Qt.Key_Equal) and modifiers & QtCore.Qt.AltModifier \
                or key == QtCore.Qt.Key_Plus and modifiers & QtCore.Qt.AltModifier and modifiers & QtCore.Qt.KeypadModifier:
            if self.rotation() == 0:
                self.setRotation(359)
            else:
                self.setRotation(self.rotation() - 1)
        elif key in (QtCore.Qt.Key_M, QtCore.Qt.Key_Minus) and modifiers & QtCore.Qt.AltModifier \
                or key == QtCore.Qt.Key_Minus and modifiers & QtCore.Qt.AltModifier and modifiers & QtCore.Qt.KeypadModifier:
            if self.rotation() < 360.0:
                self.setRotation(self.rotation() + 1)
        else:
            QtWidgets.QGraphicsItem.keyPressEvent(self, event)

    def _colorFromSvg(self, value):
        value = value.strip('#')
        if len(value) == 6: # If alpha channel is missing
            value = "ff" + value
        value = int(value, base=16)
        return QtGui.QColor.fromRgba(value)

    def __json__(self):
        data = {
            "x": int(self.pos().x()),
            "y": int(self.pos().y()),
            "z": int(self.zValue()),
            "rotation": int(self.rotation())
        }
        svg = self.toSvg()
        hash_svg = binascii.crc32(svg.encode())
        print(hash_svg)
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
        Deletes this shape.

        :param skip_controller: Do not replicate change on the controller (usefull when it's already deleted on controller
        """

        self.scene().removeItem(self)
        from ..topology import Topology
        Topology.instance().removeShape(self)
        if self._id and not skip_controller:
            self._project.delete("/shapes/" + self._id, None, body=self.__json__())

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            if not value:
                self.updateShape()
        return QtWidgets.QGraphicsItem.itemChange(self, change, value)

