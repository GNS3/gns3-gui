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

import xml.etree.ElementTree as ET

from ..qt import QtCore, QtWidgets, QtGui
from .drawing_item import DrawingItem
from .utils import colorFromSvg


import logging
log = logging.getLogger(__name__)


class TextItem(QtWidgets.QGraphicsTextItem, DrawingItem):
    """
    Text item for the QGraphicsView.
    """

    def __init__(self, svg=None, **kws):

        super().__init__(**kws)

        from ..main_window import MainWindow

        main_window = MainWindow.instance()
        view_settings = main_window.uiGraphicsView.settings()
        qt_font = QtGui.QFont()
        qt_font.fromString(view_settings["default_label_font"])
        self.setDefaultTextColor(QtGui.QColor(view_settings["default_label_color"]))
        self.setFont(qt_font)

        if svg:
            try:
                svg = self.fromSvg(svg)
            except ET.ParseError as e:
                log.warning(str(e))

        if self._id is None:
            self.create()

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
        else:
            self.updateDrawing()
        return super().focusOutEvent(event)

    def paint(self, painter, option, widget=None):
        """
        Paints the contents of an item in local coordinates.

        :param painter: QPainter instance
        :param option: QStyleOptionGraphicsItem instance
        :param widget: QWidget instance
        """

        super().paint(painter, option, widget)
        self.drawLayerInfo(painter)

    def toSvg(self):
        """
        Return an SVG version of the text
        """
        svg = ET.Element("svg")
        svg.set("width", str(int(self.boundingRect().width())))
        svg.set("height", str(int(self.boundingRect().height())))

        text = ET.SubElement(svg, "text")
        text.set("font-family", self.font().family())
        text.set("font-size", str(self.font().pointSizeF()))
        if self.font().italic():
            text.set("font-style", "italic")
        if self.font().bold():
            text.set("font-weight", "bold")
        if self.font().strikeOut():
            text.set("text-decoration", "line-through")
        elif self.font().underline():
            text.set("text-decoration", "underline")
        text.set("fill", "#" + hex(self.defaultTextColor().rgba())[4:])
        text.set("fill-opacity", str(self.defaultTextColor().alphaF()))
        text.text = self.toPlainText()

        svg = ET.tostring(svg, encoding="utf-8").decode("utf-8")
        return svg

    def fromSvg(self, svg):
        svg = ET.fromstring(svg)
        text = svg[0]

        font = QtGui.QFont()
        color = text.get("fill")
        if color:
            new_color = colorFromSvg(color)
            color = self.defaultTextColor()
            color.setBlue(new_color.blue())
            color.setRed(new_color.red())
            color.setGreen(new_color.green())
            self.setDefaultTextColor(color)

        opacity = text.get("fill-opacity")
        if opacity:
            color = self.defaultTextColor()
            color.setAlphaF(float(opacity))
            self.setDefaultTextColor(color)

        font.setPointSizeF(float(text.get("font-size", self.font().pointSizeF())))
        font.setFamily(text.get("font-family", self.font().family()))
        if text.get("font-style") == "italic":
            font.setItalic(True)
        if text.get("font-weight") == "bold":
            font.setBold(True)
        if text.get("text-decoration") == "underline":
            font.setUnderline(True)
        if text.get("text-decoration") == "line-through":
            font.setStrikeOut(True)

        self.setFont(font)
        self.setPlainText(text.text)

    def editable(self):
        """
        Returns either the note is editable or not.

        :return: boolean
        """

        return True

    def keyPressEvent(self, event):
        """
        Handles all key press events

        :param event: QKeyEvent
        """

        if not self.handleKeyPressEvent(event):
            super().keyPressEvent(event)
