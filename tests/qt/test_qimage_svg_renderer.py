#!/usr/bin/env python
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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

from gns3.qt import QtGui
from gns3.qt.qimage_svg_renderer import QImageSvgRenderer


def test_render_svg():
    renderer = QImageSvgRenderer('resources/symbols/router.svg')
    assert renderer.isValid()


def test_render_png():
    renderer = QImageSvgRenderer('resources/images/gns3_icon_256x256.png')
    assert renderer.isValid()
