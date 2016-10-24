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

from ..qt import QtGui


def colorFromSvg(value):
    """
    Transform a color coming from a SVG file to a Qcolor
    """
    value = value.strip('#')
    if value == "":
        value = "000000"
    if len(value) == 6:  # If alpha channel is missing
        value = "ff" + value
    value = int(value, base=16)
    return QtGui.QColor.fromRgba(value)
