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

import base64
import os

from . import QtCore
from . import QtSvg
from . import QtGui


class QImageSvgRenderer(QtSvg.QSvgRenderer):
    """
    Renderer pixmap and svg to SVG item
    """
    def __init__(self, path):
        super().__init__()
        super().load(path)

        # If we can't render a SVG we load and base64 the image to create a SVG
        if not self.isValid() and os.path.exists(path):
            image = QtGui.QImage(path)
            data = QtCore.QByteArray()
            buf = QtCore.QBuffer(data)
            image.save(buf, 'PNG')
            xml = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<image width="{width}" height="{height}" xlink:href="data:image/png;base64,{data}"/>
</svg>""".format(data=bytes(data.toBase64()).decode(),
                width=image.rect().width(),
                height=image.rect().height())
            super().load(xml.encode())

