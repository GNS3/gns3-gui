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

from gns3.items.rectangle_item import RectangleItem
from gns3.qt import QtGui, QtCore


def test_toSvg(project, controller):
    rect = RectangleItem(width=400, height=280, project=project)
    pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
    pen.setStyle(QtCore.Qt.DashLine)
    rect.setPen(pen)
    svg = ET.fromstring(rect.toSvg())
    assert float(svg.get("width")) == 400.0
    assert float(svg.get("height")) == 280.0

    rect = svg[0]
    assert float(rect.get("width")) == 400.0
    assert float(rect.get("height")) == 280.0
    assert rect.get("stroke-width") == "2"
    assert rect.get("stroke") == "#000000"
    assert rect.get("fill") == "#ffffff"
    assert rect.get("fill-opacity") == "1.0"

    assert rect.get("stroke-dasharray") == "25, 25"


def test_fromSvg(project, controller):
    rect = RectangleItem(project=project)
    rect.fromSvg('<svg height="150" width="250"><rect height="150" stroke-width="5" stroke="#0000ff" fill="#ff00ff" fill-opacity="0.5" width="150" stroke-dasharray="5, 25, 25" /></svg>')
    assert rect.rect().width() == 250
    assert rect.rect().height() == 150
    assert rect.pen().width() == 5
    assert hex(rect.pen().color().rgba()) == "0xff0000ff"
    assert hex(rect.brush().color().rgba()) == "0x80ff00ff"
    assert rect.pen().style() == QtCore.Qt.DashDotLine


def test_fromSvg_solid_stroke(project, controller):
    rect = RectangleItem(project=project)
    rect.fromSvg('<svg height="150" width="250"><rect height="150" stroke-width="5" stroke="#0000ff" fill="#ff00ff" width="150" /></svg>')
    assert rect.pen().style() == QtCore.Qt.SolidLine


def test_fromEmptySvg(project, controller):
    rect = RectangleItem(project=project)
    rect.fromSvg("<svg></svg>")


def test_create(project, controller):
    rect = RectangleItem(width=400, height=280, project=project)
    rect.create()
    controller._http_client.sendRequest.assert_called_with(
        "POST",
        "/projects/" + project.id() + "/drawings",
        rect._createDrawingCallback,
        body={
            "drawing_id": rect._id,
            "x": 0,
            "y": 0,
            "z": 0,
            "locked": rect.locked(),
            "svg": rect.toSvg(),
            "rotation": int(rect.rotation())
        }
    )
