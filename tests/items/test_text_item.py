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

import xml.etree.ElementTree as ET

from gns3.items.text_item import TextItem
from gns3.qt import QtGui, QtCore


def test_toSvg(project, controller):
    text = TextItem(project=project)
    text.setPlainText("Hello")
    svg = ET.fromstring(text.toSvg())
    # Travis don't have the font it's broke the CI
    #assert float(svg.get("width")) ==  34.0
    #assert float(svg.get("height")) ==  20.0

    text = svg[0]
    assert text.get("font-family") == "TypeWriter"
    assert text.get("font-size") == "10.0"
    assert text.get("fill") == "#000000"
    assert text.get("fill-opacity") == "1.0"
    assert text.text == "Hello"


def test_fromSvg(project, controller):
    text = TextItem(project=project)
    font = QtGui.QFont()
    font.setPointSizeF(55.8)
    font.setFamily("Verdana")
    font.setBold(True)
    font.setItalic(True)
    font.setStrikeOut(True)
    text.setFont(font)
    text.setDefaultTextColor(QtCore.Qt.red)
    text.setPlainText("Hello")

    text2 = TextItem(project=project)
    text2.fromSvg(text.toSvg())
    assert text2.toPlainText() == "Hello"
    assert hex(text2.defaultTextColor().rgba()) == "0xffff0000"
    assert text2.font().pointSizeF() == 55.8
    assert text2.font().family() == "Verdana"
    assert text2.font().italic()
    assert text2.font().bold()
    assert text2.font().strikeOut()
