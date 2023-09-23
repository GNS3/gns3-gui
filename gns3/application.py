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


import sys

from .qt import QtWidgets, QtGui, QtCore
from gns3.utils import parse_version
from gns3.local_config import LocalConfig
from .version import __version__

import logging
log = logging.getLogger(__name__)


class Application(QtWidgets.QApplication):
    file_open_signal = QtCore.pyqtSignal(str)

    def __init__(self, argv, hdpi=True):

        self.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
        # both Qt and PyQt must be version >= 5.6 in order to enable high DPI scaling
        if parse_version(QtCore.QT_VERSION_STR) >= parse_version("5.6") and parse_version(QtCore.PYQT_VERSION_STR) >= parse_version("5.6"):
            # only available starting Qt version 5.6
            if hdpi:
                if sys.platform.startswith("linux"):
                    local_config_path = LocalConfig.instance().configFilePath()
                    log.warning("HDPI mode is enabled. HDPI support on Linux is not fully stable and GNS3 may crash depending of your version of Linux. "
                                f"To disabled HDPI mode please edit '{local_config_path}' and set 'hdpi' to 'false'")
                self.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
                self.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
            else:
                log.info("HDPI mode is disabled")
                self.setAttribute(QtCore.Qt.AA_DisableHighDpiScaling)

        super().__init__(argv)

        # this is tell Wayland what is the name of the desktop file (gns3.desktop)
        self.setDesktopFileName("gns3")

        # this info is necessary for QSettings
        self.setOrganizationName("GNS3")
        self.setOrganizationDomain("gns3.net")
        self.setApplicationName("GNS3")
        self.setApplicationVersion(__version__)

        # File path if we have received the path to
        # a file on system via an OSX event
        self.open_file_at_startup = None

    def event(self, event):
        # When you double click file you receive an event
        # and not the file as command line parameter
        if sys.platform.startswith("darwin"):
            if isinstance(event, QtGui.QFileOpenEvent):
                self.open_file_at_startup = str(event.file())
                self.file_open_signal.emit(str(event.file()))
        return super().event(event)
