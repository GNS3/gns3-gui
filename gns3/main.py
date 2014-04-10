#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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

import datetime
import sys
import logging
import traceback
import time

try:
    from gns3.qt import QtCore, QtGui, DEFAULT_BINDING
except ImportError:
    raise RuntimeError("Can't import Qt modules: Qt and/or PyQt is probably not installed correctly...")

from gns3.main_window import MainWindow
from gns3.version import __version__


def main():
    """
    Entry point for GNS3 GUI.
    """

    def exceptionHook(exception, value, tb):

        lines = traceback.format_exception(exception, value, tb)
        print("---------Traceback lines (saved in exception.log)----------")
        print("\n" . join(lines))
        print("-----------------------------------------------------------")
        try:
            curdate = time.strftime("%d %b %Y %H:%M:%S")
            logfile = open('exception.log', 'a')
            logfile.write("=== GNS3 {} traceback on {} ===\n".format(__version__, curdate))
            logfile.write("\n" . join(lines))
            logfile.close()
        except OSError as e:
            print("Could not save in exception.log: {}".format(e))

    # catch exceptions to write them in a file
    sys.excepthook = exceptionHook

    current_year = datetime.date.today().year
    print("GNS3 GUI version {}".format(__version__))
    print("Copyright (c) 2007-{} GNS3 Technologies Inc.".format(current_year))

    # we only support Python 2 version >= 2.7 and Python 3 version >= 3.3
    if sys.version_info < (2, 7):
        raise RuntimeError("Python 2.7 or higher is required")
    elif sys.version_info[0] == 3 and sys.version_info < (3, 3):
        raise RuntimeError("Python 3.3 or higher is required")

    version = lambda version_string: [int(i) for i in version_string.split('.')]

    if version(QtCore.QT_VERSION_STR) < version("4.6"):
        raise RuntimeError("Requirement is Qt version 4.6 or higher, got version {}".format(QtCore.QT_VERSION_STR))

    # 4.8.3 because of QSettings (http://pyqt.sourceforge.net/Docs/PyQt4/pyqt_qsettings.html)
    if DEFAULT_BINDING == "PyQt" and version(QtCore.BINDING_VERSION_STR) < version("4.8.3"):
        raise RuntimeError("Requirement is PyQt version 4.8.3 or higher, got version {}".format(QtCore.BINDING_VERSION_STR))

    if DEFAULT_BINDING == "PySide" and version(QtCore.BINDING_VERSION_STR) < version("1.0"):
        raise RuntimeError("Requirement is PySide version 1.0 or higher, got version {}".format(QtCore.BINDING_VERSION_STR))

    try:
        # if tornado is present then enable pretty logging.
        import tornado.log
        tornado.log.enable_pretty_logging()
    except ImportError:
        pass

    # default logging level
    logging.basicConfig(level=logging.INFO)

    # don't use the registry to store settings on Windows
    # because we don't like it!
    if sys.platform.startswith('win'):
        QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)

        try:
            import win32console
            import win32con
            import win32gui
        except ImportError:
            raise RuntimeError("Python for Windows extensions must be installed.")

        try:
            win32console.AllocConsole()
            console_window = win32console.GetConsoleWindow()
            win32gui.ShowWindow(console_window, win32con.SW_HIDE)
        except win32console.error as e:
            print("warning: could not allocate console: {}".format(e))

    exit_code = MainWindow.exit_code_reboot
    while exit_code == MainWindow.exit_code_reboot:

        exit_code = 0
        app = QtGui.QApplication(sys.argv)

        # this info is necessary for QSettings
        app.setOrganizationName("GNS3")
        app.setOrganizationDomain("gns3.net")
        app.setApplicationName("GNS3")
        app.setApplicationVersion(__version__)

        mainwindow = MainWindow.instance()
        mainwindow.show()
        exit_code = app.exec_()
        delattr(MainWindow, "_instance")
        app.deleteLater()

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
