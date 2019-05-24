# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 GNS3 Technologies Inc.
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

from ..qt import QtCore, QtGui


def get_icon(filename):

    from gns3.main_window import MainWindow
    style_name = MainWindow.instance().settings().get("style")

    if style_name.startswith("Charcoal"):
        style_dir = ":/charcoal_icons/"
    elif style_name == "Classic":
        style_dir = ":/classic_icons/"
    else:
        style_dir = ":/icons/"

    icon_path = style_dir + filename
    if not QtCore.QFile(style_dir + filename).exists():
        # fall back to the default legacy style if the icon file doesn't exist
        icon_path = ":/icons/{}".format(filename)
    return QtGui.QIcon(icon_path)
