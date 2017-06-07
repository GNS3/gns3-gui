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
Graphical representation of a note on the QGraphicsScene.
"""

from ..qt import QtCore, QtWidgets, QtGui
from .utils import colorFromSvg


class NoteItem(QtWidgets.QGraphicsTextItem):
    """
    Text note for the QGraphicsView.

    :param parent: optional parent
    """
    item_unselected_signal = QtCore.Signal()

    show_layer = False

    def __init__(self, parent=None):

        super().__init__(parent)

        from ..main_window import MainWindow

        main_window = MainWindow.instance()
        view_settings = main_window.uiGraphicsView.settings()
        qt_font = QtGui.QFont()
        qt_font.fromString(view_settings["default_label_font"])
        self.setDefaultTextColor(QtGui.QColor(view_settings["default_label_color"]))
        self.setFont(qt_font)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setZValue(2)
        self._editable = True

    def delete(self):
        """
        Deletes this note.
        """

        if not self.scene():
            # object already deleted by its parent
            return

        self.scene().removeItem(self)
        from ..topology import Topology

        Topology.instance().removeNote(self)

    def editable(self):
        """
        Returns either the note is editable or not.

        :return: boolean
        """

        return self._editable

    def setEditable(self, value):
        """
        Sets the note has editable or not.

        :param value: boolean
        """

        self._editable = value
        # if not self._editable:
        #    self.setFlag(self.ItemIsSelectable, enabled=False)
        # else:
        #    self.setFlag(self.ItemIsSelectable)

    def keyPressEvent(self, event):
        """
        Handles all key press events

        :param event: QKeyEvent
        """

        key = event.key()
        modifiers = event.modifiers()
        if key in (QtCore.Qt.Key_P, QtCore.Qt.Key_Plus, QtCore.Qt.Key_Equal) and modifiers & QtCore.Qt.AltModifier \
                or key == QtCore.Qt.Key_Plus and modifiers & QtCore.Qt.AltModifier and modifiers & QtCore.Qt.KeypadModifier:
            if self.rotation() > -360.0:
                self.setRotation(self.rotation() - 1)
        elif key in (QtCore.Qt.Key_M, QtCore.Qt.Key_Minus) and modifiers & QtCore.Qt.AltModifier \
                or key == QtCore.Qt.Key_Minus and modifiers & QtCore.Qt.AltModifier and modifiers & QtCore.Qt.KeypadModifier:
            if self.rotation() < 360.0:
                self.setRotation(self.rotation() + 1)
        else:
            super().keyPressEvent(event)

    def editText(self):
        """
        Edit mode for this note.
        """

        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setSelected(True)
        self.setFocus()
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.Document)
        self.setTextCursor(cursor)

    def mouseDoubleClickEvent(self, event):
        """
        Handles all mouse double click events.

        :param event: QMouseEvent instance
        """

        if self._editable:
            self.editText()

    def focusOutEvent(self, event):
        """
        Handles all focus out events.

        :param event: QFocusEvent instance
        """

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, False)
        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.clearSelection()
            self.setTextCursor(cursor)
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        if not self.toPlainText():
            # delete the note if empty
            self.delete()
            return
        return super().focusOutEvent(event)

    def paint(self, painter, option, widget=None):
        """
        Paints the contents of an item in local coordinates.

        :param painter: QPainter instance
        :param option: QStyleOptionGraphicsItem instance
        :param widget: QWidget instance
        """

        super().paint(painter, option, widget)

        if self.show_layer is False or self.parentItem():
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
        painter.drawText(QtCore.QPointF(center.x(), center.y()), zval)

    def setZValue(self, value):
        """
        Sets a new Z value.

        :param value: Z value
        """

        super().setZValue(value)
        if self.zValue() < 0:
            self.setFlag(self.ItemIsSelectable, False)
            self.setFlag(self.ItemIsMovable, False)
        else:
            self.setFlag(self.ItemIsSelectable, True)
            self.setFlag(self.ItemIsMovable, True)

    def setStyle(self, styles):
        """
        Set text style using a SVG style
        """
        font = QtGui.QFont()
        for style in styles.split(";"):
            if ":" in style:
                key, val = style.split(":")
                key = key.strip()
                val = val.strip()

                if key == "font-size":
                    font.setPointSizeF(float(val))
                elif key == "font-family":
                    font.setFamily(val)
                elif key == "font-style" and val == "italic":
                    font.setItalic(True)
                elif key == "font-weight" and val == "bold":
                    font.setBold(True)
                elif key == "text-decoration" and val == "underline":
                    font.setUnderline(True)
                elif key == "text-decoration" and val == "line-through":
                    font.setStrikeOut(True)
                elif key == "fill":
                    new_color = colorFromSvg(val)
                    color = self.defaultTextColor()
                    color.setBlue(new_color.blue())
                    color.setRed(new_color.red())
                    color.setGreen(new_color.green())
                    self.setDefaultTextColor(color)
                elif key == "fill-opacity":
                    color = self.defaultTextColor()
                    color.setAlphaF(float(val))
                    self.setDefaultTextColor(color)
        self.setFont(font)

    def itemChange(self, change, value):
        """
        Notifies this node item that some part of the item's state changes.

        :param change: GraphicsItemChange type
        :param value: value of the change
        """
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            if value == 0:
                self.item_unselected_signal.emit()
        return super().itemChange(change, value)

    def dump(self):
        """
        Returns a representation of this note.

        :returns: dictionary
        """

        note_info = {"text": self.toPlainText(),
                     "x": int(self.x()),
                     "y": int(self.y()),
                     "rotation": int(self.rotation())}

        style = ""

        style += "font-family: {};".format(self.font().family())
        style += "font-size: {};".format(self.font().pointSizeF())

        if self.font().italic():
            style += "font-style: italic;"

        if self.font().bold():
            style += "font-weight: bold;"

        if self.font().strikeOut():
            style += "text-decoration: line-through;"
        elif self.font().underline():
            style += "text-decoration: underline;"

        style += "fill: {};".format("#" + hex(self.defaultTextColor().rgba())[4:])
        style += "fill-opacity: {};".format(self.defaultTextColor().alphaF())

        note_info["style"] = style

        return note_info
