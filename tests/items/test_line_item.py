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

from gns3.items.line_item import LineItem
from gns3.qt import QtGui, QtCore


def test_toSvg(project, controller):
    line = LineItem(dst=QtCore.QPointF(400, 280), project=project)
    pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
    pen.setStyle(QtCore.Qt.DashLine)
    line.setPen(pen)
    svg = ET.fromstring(line.toSvg())
    assert float(svg.get("width")) == 400.0
    assert float(svg.get("height")) == 280.0

    line = svg[0]
    assert float(line.get("x1")) == 0.0
    assert float(line.get("y1")) == 0.0
    assert float(line.get("x2")) == 400.0
    assert float(line.get("y2")) == 280.0
    assert line.get("stroke-width") == "2"
    assert line.get("stroke") == "#000000"
    assert line.get("stroke-dasharray") == "25, 25"


def test_toSvg_negative_y(project, controller):
    line = LineItem(dst=QtCore.QPointF(400, -280), project=project)
    pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
    pen.setStyle(QtCore.Qt.DashLine)
    line.setPen(pen)
    svg = ET.fromstring(line.toSvg())
    assert float(svg.get("width")) == 400.0
    assert float(svg.get("height")) == 280.0

    line = svg[0]
    assert float(line.get("x1")) == 0.0
    assert float(line.get("y1")) == 0.0
    assert float(line.get("x2")) == 400.0
    assert float(line.get("y2")) == -280.0
    assert line.get("stroke-width") == "2"
    assert line.get("stroke") == "#000000"
    assert line.get("stroke-dasharray") == "25, 25"


def test_fromSvg(project, controller):
    line = LineItem(project=project)
    line.setPos(50, 84)
    line.fromSvg('<svg height="150" width="250"><line x1="0" y1="0" x2="250" y2="150" stroke-width="5" stroke="#0000ff" stroke-dasharray="5, 25, 25" /></svg>')
    assert line.line().x1() == 0
    assert line.line().y1() == 0
    assert line.line().x2() == 250
    assert line.line().y2() == 150
    assert hex(line.pen().color().rgba()) == "0xff0000ff"
    assert line.pen().style() == QtCore.Qt.DashDotLine
    assert line.pos().x() == 50
    assert line.pos().y() == 84


def test_fromSvg_top_direction(project, controller):
    line = LineItem(project=project)
    line.setPos(50, 84)
    line.fromSvg('<svg height="150" width="250"><line x1="0" y1="150" x2="250" y2="0" stroke-width="5" stroke="#0000ff" stroke-dasharray="5, 25, 25" /></svg>')
    assert line.line().x1() == 0
    assert line.line().y1() == 150
    assert line.line().x2() == 250
    assert line.line().y2() == 0
    assert hex(line.pen().color().rgba()) == "0xff0000ff"
    assert line.pen().style() == QtCore.Qt.DashDotLine
    assert line.pos().x() == 50
    assert line.pos().y() == 84


def test_fromSvg_solid_stroke(project, controller):
    line = LineItem(project=project)
    line.fromSvg('<svg height="150" width="250"><line x1="0" y1="0" x2="250" y2="150" stroke-width="5" stroke="#0000ff" /></svg>')
    assert line.pen().style() == QtCore.Qt.SolidLine


def test_fromEmptySvg(project, controller):
    line = LineItem(project=project)
    line.fromSvg("<svg></svg>")


def test_create(project, controller):
    rect = LineItem(project=project)
    rect.create()
    controller._http_client.createHTTPQuery.assert_called_with(
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
