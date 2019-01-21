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

import os
import re
import xml.etree.ElementTree as ET

from . import QtCore
from . import QtSvg
from . import QtGui

import logging
log = logging.getLogger(__name__)


class QImageSvgRenderer(QtSvg.QSvgRenderer):
    """
    Renderer pixmap and svg to SVG item

    :param path_or_data: Svg element of path to a SVG
    :param fallback: Image to display if the image is not working
    """

    def __init__(self, path_or_data=None, fallback=None):

        super().__init__()
        self._fallback = fallback
        self._svg = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}"></svg>"""
        self.load(path_or_data)

    def load(self, path_or_data):

        try:
            path_exists = os.path.exists(path_or_data)
        except ValueError:  # On windows we can get an error because the path is too long (it's the svg data)
            path_exists = False

        if not path_exists and not path_or_data.startswith(":"):
            self._svg = path_or_data
            path_or_data = path_or_data.encode("utf-8")
            return super().load(path_or_data)

        try:
            # We load the SVG with ElementTree before
            # because Qt when failing loading send noise to logs
            # and their is no way to prevent that
            if not path_or_data.startswith(":") and path_exists:
                ET.parse(path_or_data)
            res = super().load(path_or_data)
            # If we can't render a SVG we load and base64 the image to create a SVG
            if self.isValid():
                if not path_or_data.startswith(":") and path_exists:
                    try:
                        with open(path_or_data, "rb") as f:
                            self._svg = f.read().decode()
                    except UnicodeError as e:
                        log.error("Could not decode '{}' content: {}".format(path_or_data, e))
                    except OSError as e:
                        log.error("Could not read '{}': {}".format(path_or_data, e))
                return res
        except ET.ParseError:
            pass

        image = QtGui.QImage(path_or_data)
        data = QtCore.QByteArray()
        buf = QtCore.QBuffer(data)
        image.save(buf, 'PNG')
        if image.rect().width() > 0:
            self._svg = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}">
    <image width="{width}" height="{height}" xlink:href="data:image/png;base64,{data}"/>
    </svg>""".format(data=bytes(data.toBase64()).decode(),
                     width=image.rect().width(),
                     height=image.rect().height())
            res = super().load(self._svg.encode())
        elif self._fallback:
            log.error("Invalid or corrupted image file")
            res = super().load(self._fallback)
        else:
            self._svg = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                           </svg>"""
            res = super().load(self._svg.encode())
        return res

    def resize(self, new_height, new_width=None):

        if not self.isValid():
            log.error("QSvgRenderer is not valid")
            return

        size = self.defaultSize()
        height = size.height()
        width = size.width()

        if not new_width:
            new_width = round(width / height * new_height)

        add_attr = []
        svg_header, svg_tag, svg_data = re.split(r'(<svg[^>]*>)', self._svg, maxsplit=1)

        attr = 'height="{}"'.format(new_height)
        svg_tag, count = re.subn(r'height="[^"]*"', attr, svg_tag, count=1)
        if not count:
            add_attr.append(attr)

        attr = 'width="{}"'.format(new_width)
        svg_tag, count = re.subn(r'width="[^"]*"', attr, svg_tag, count=1)
        if not count:
            add_attr.append(attr)

        if 'viewBox="' not in svg_tag:
            add_attr.append('viewBox="0 0 {} {}"'.format(width, height))

        if add_attr:
            svg_tag = svg_tag.replace('<svg', '<svg ' + ' '.join(add_attr), 1)

        svg_image = svg_header + svg_tag + svg_data
        res = super().load(svg_image.encode())
        if res is False:
            log.error("Could not resize QSvgRenderer")

    def svg(self):
        """
        :returns: SVG source code
        """
        return self._svg
