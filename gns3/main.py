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
import os
import traceback
import time
import locale
import argparse

import logging
log = logging.getLogger(__name__)


try:
    from gns3.qt import QtCore, QtGui, DEFAULT_BINDING
except ImportError:
    raise RuntimeError("Can't import Qt modules: Qt and/or PyQt is probably not installed correctly...")

from gns3.main_window import MainWindow
from gns3.version import __version__


def locale_check():
    """
    Checks if this application runs with a correct locale (i.e. supports UTF-8 encoding) and attempt to fix
    if this is not the case.

    This is to prevent UnicodeEncodeError with unicode paths when using standard library I/O operation
    methods (e.g. os.stat() or os.path.*) which rely on the system or user locale.

    More information can be found there: http://seasonofcode.com/posts/unicode-i-o-and-locales-in-python.html
    or there: http://robjwells.com/post/61198832297/get-your-us-ascii-out-of-my-face
    """

    # no need to check on Windows or when frozen
    if sys.platform.startswith("win") or hasattr(sys, "frozen"):
        return

    language = encoding = None
    try:
        language, encoding = locale.getlocale()
    except ValueError as e:
        log.error("could not determine the current locale: {}".format(e))
    if not language and not encoding:
        try:
            log.warn("could not find a default locale, switching to C.UTF-8...")
            locale.setlocale(locale.LC_ALL, ("C", "UTF-8"))
        except locale.Error as e:
            log.error("could not switch to the C.UTF-8 locale: {}".format(e))
            raise SystemExit
    elif encoding != "UTF-8":
        log.warn("your locale {}.{} encoding is not UTF-8, switching to the UTF-8 version...".format(language, encoding))
        try:
            locale.setlocale(locale.LC_ALL, (language, "UTF-8"))
        except locale.Error as e:
            log.error("could not set an UTF-8 encoding for the {} locale: {}".format(language, e))
            raise SystemExit
    else:
        log.info("current locale is {}.{}".format(language, encoding))


def main():
    """
    Entry point for GNS3 GUI.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', help="show the version", action='version', version=__version__)
    parser.add_argument('--debug', help="print out debug messages", action='store_true', default=False)
    options = parser.parse_args()
    exception_file_path = "exception.log"

    def exceptionHook(exception, value, tb):

        if exception == KeyboardInterrupt:
            sys.exit(0)

        lines = traceback.format_exception(exception, value, tb)
        print("****** Exception detected, traceback information saved in {} ******".format(exception_file_path))
        print("\nPLEASE REPORT ON https://community.gns3.com/community/support/bug\n")
        print("".join(lines))
        try:
            curdate = time.strftime("%d %b %Y %H:%M:%S")
            logfile = open(exception_file_path, "a")
            logfile.write("=== GNS3 {} traceback on {} ===\n".format(__version__, curdate))
            logfile.write("".join(lines))
            logfile.close()
        except OSError as e:
            print("Could not save traceback to {}: {}".format(exception_file_path, e))

        if not sys.stdout.isatty():
            # if stdout is not a tty (redirected to the console view),
            # then print the exception on stderr too.
            print("".join(lines), file=sys.stderr)

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

    # check for the correct locale
    # (UNIX/Linux only)
    locale_check()

    try:
        os.getcwd()
    except FileNotFoundError:
        log.critical("the current working directory doesn't exist")
        return

    # always use the INI format on Windows and OSX (because we don't like the registry and plist files)
    if sys.platform.startswith('win') or sys.platform.startswith('darwin'):
        QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)

    if sys.platform.startswith('win'):
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

        # save client logging info to a file
        logfile = os.path.join(os.path.dirname(QtCore.QSettings().fileName()), "GNS3_client.log")
        try:
            try:
                os.makedirs(os.path.dirname(QtCore.QSettings().fileName()))
            except FileExistsError:
                pass
            handler = logging.FileHandler(logfile, "w")
            if options.debug:
                root_logger = logging.getLogger()
                root_logger.setLevel(logging.DEBUG)
                if len(root_logger.handlers) > 0:
                    root_handler = root_logger.handlers[0]
                else:
                    root_handler = logging.StreamHandler()
                    root_logger.addHandler(root_handler)
                root_handler.setLevel(logging.DEBUG)
            else:
                handler.setLevel(logging.INFO)
            log.info('Log level: {}'.format(logging.getLevelName(log.getEffectiveLevel())))

            formatter = logging.Formatter("[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s",
                                          datefmt="%y%m%d %H:%M:%S")
            handler.setFormatter(formatter)
            log.addHandler(handler)
        except OSError as e:
            log.warn("could not log to {}: {}".format(logfile, e))

        # update the exception file path to have it in the same directory as the settings file.
        exception_file_path = os.path.join(os.path.dirname(QtCore.QSettings().fileName()), exception_file_path)

        mainwindow = MainWindow.instance()
        mainwindow.show()
        exit_code = app.exec_()
        delattr(MainWindow, "_instance")
        app.deleteLater()

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
