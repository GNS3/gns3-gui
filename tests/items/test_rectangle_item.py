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
    assert float(svg.get("width")) ==  400.0
    assert float(svg.get("height")) ==  280.0

    rect = svg[0]
    assert float(rect.get("width")) ==  400.0
    assert float(rect.get("height")) ==  280.0
    assert rect.get("style") == "stroke-width:2;stroke:#000000;fill:#ffffff;"

    assert rect.get("stroke-dasharray") == "25, 25"


def test_create(project, controller):
    rect = RectangleItem(width=400, height=280, project=project)
    controller._http_client.createHTTPQuery.assert_called_with(
        "POST",
        "/projects/" + project.id() + "/shapes",
        rect._createShapeCallback,
        body={
            "x": 0,
            "y": 0,
            "z": 0,
            "svg": rect.toSvg()
        }
    )
