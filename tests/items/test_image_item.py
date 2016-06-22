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

import pytest
import xml.etree.ElementTree as ET

from gns3.items.image_item import ImageItem
from gns3.qt import QtGui, QtCore


@pytest.fixture
def image(project, controller):
    path = "resources/images/gns3_icon_128x128.png"
    return ImageItem(image_path=path, project=project)


def test_toSvg(image):
    svg = ET.fromstring(image.toSvg())
    assert float(svg.get("width")) ==  128.0
    assert float(svg.get("height")) ==  128.0


def test_fromSvg(image, project):
    image2 = ImageItem(svg=image.toSvg(), project=project)
    assert image2.toSvg() == image.toSvg()


def test_json(image):
    image._hash_svg = None
    assert "svg" in  image.__json__()
    # If we call the function twice and the svg didn't change we don't send the modification
    assert "svg" not in  image.__json__()


