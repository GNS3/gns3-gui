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

from gns3.items.ellipse_item import EllipseItem
from gns3.qt import QtGui, QtCore


def test_toSvg(project, controller):
    ellipse = EllipseItem(width=400, height=100, project=project)
    pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
    pen.setStyle(QtCore.Qt.DashLine)
    ellipse.setPen(pen)
    svg = ET.fromstring(ellipse.toSvg())
    assert float(svg.get("width")) ==  400.0
    assert float(svg.get("height")) ==  100.0

    ellipse = svg[0]
    assert float(ellipse.get("cx")) ==  200.0
    assert float(ellipse.get("rx")) ==  200.0
    assert float(ellipse.get("cy")) ==  50.0
    assert float(ellipse.get("ry")) ==  50.0
    assert ellipse.get("stroke-width") == "2"
    assert ellipse.get("stroke") == "#000000"
    assert ellipse.get("fill", "#ffffff")

    assert ellipse.get("stroke-dasharray") == "25, 25"


def test_fromSvg(project, controller):
    ellipse = EllipseItem(project=project)
    ellipse.fromSvg('<svg height="150" width="250"><ellipse height="150" stroke-width="5" stroke="#0000ff" fill="#ff00ff" width="150" stroke-dasharray="5, 25, 25" /></svg>')
    assert ellipse.rect().width() == 250
    assert ellipse.rect().height() == 150
    assert ellipse.pen().width() == 5
