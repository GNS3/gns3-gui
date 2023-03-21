# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GNS3 Technologies Inc.
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

import sys
from setuptools import setup

if sys.platform.startswith('linux'):
    data_files = [
        ("share/applications/", ["resources/linux/applications/gns3.desktop"]),
        ("share/mime/packages", ["resources/linux/gns3-gui.xml"]),
        ("share/icons/hicolor/16x16/apps", ["resources/linux/icons/hicolor/16x16/apps/gns3.png"]),
        ("share/icons/hicolor/32x32/apps", ["resources/linux/icons/hicolor/32x32/apps/gns3.png"]),
        ("share/icons/hicolor/48x48/apps", ["resources/linux/icons/hicolor/48x48/apps/gns3.png"]),
        ("share/icons/hicolor/48x48/mimetypes", ["resources/linux/icons/hicolor/48x48/mimetypes/application-x-gns3.png",
                                                 "resources/linux/icons/hicolor/48x48/mimetypes/application-x-gns3appliance.png",
                                                 "resources/linux/icons/hicolor/48x48/mimetypes/application-x-gns3project.png"]),
        ("share/icons/hicolor/scalable/apps", ["resources/linux/icons/hicolor/scalable/apps/gns3.svg"]),
        ("share/icons/hicolor/scalable/mimetypes", ["resources/linux/icons/hicolor/scalable/mimetypes/application-x-gns3.svg",
                                                    "resources/linux/icons/hicolor/scalable/mimetypes/application-x-gns3appliance.svg",
                                                    "resources/linux/icons/hicolor/scalable/mimetypes/application-x-gns3project.svg"]),
    ]
else:
    data_files = []

# TODO: find an alternative for installing data_files
setup(data_files=data_files)  # required with setuptools below version 64.0.0
