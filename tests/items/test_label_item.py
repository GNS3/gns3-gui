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

from gns3.qt import QtGui, QtCore


from gns3.items.label_item import LabelItem


def test_dump():
    label = LabelItem()
    label.setPlainText("Test")
    font = QtGui.QFont()
    font.setPointSizeF(55.8)
    font.setFamily("Verdana")
    font.setBold(True)
    font.setItalic(True)
    font.setUnderline(True)
    font.setStrikeOut(True)
    label.setFont(font)
    label.setDefaultTextColor(QtCore.Qt.red)

    assert label.dump() == {
        "text": "Test",
        "x": 0,
        "y": 0,
        "rotation": 0,
        "style": "font-family: Verdana;font-size: 55.8;font-style: italic;font-weight: bold;text-decoration: line-through;fill: #ff0000;fill-opacity: 1.0;"
    }


def test_setStyle():
    label = LabelItem()
    label.setPlainText("Test")
    font = QtGui.QFont()
    font.setPointSizeF(55.8)
    font.setFamily("Verdana")
    font.setBold(True)
    font.setItalic(True)
    font.setUnderline(True)
    font.setStrikeOut(False)
    label.setFont(font)
    label.setDefaultTextColor(QtCore.Qt.red)

    style = label.dump()["style"]
    label2 = LabelItem()
    label2.setStyle(style)
    assert label2.font().pointSizeF() == 55.8
    assert label2.font().family() == "Verdana"
    assert label2.font().italic()
    assert label2.font().bold()
    assert label2.font().strikeOut() is False
    assert label2.font().underline()
    assert label2.defaultTextColor() == QtCore.Qt.red
