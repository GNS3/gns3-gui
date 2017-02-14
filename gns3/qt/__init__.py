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

"""
Compatibility layer for Qt bindings, so it is easier to switch to PySide if needed.
"""

# based on https://gist.github.com/remram44/5985681 and
# https://github.com/pyQode/pyqode.qt/blob/master/pyqode/qt/QtWidgets.py (MIT license)


import sys
import sip
import os
import re
import types
import functools
import inspect

import logging
log = logging.getLogger("qt/__init__.py")

from PyQt5 import QtCore, QtGui, QtNetwork, QtWidgets, Qt
sys.modules[__name__ + '.QtCore'] = QtCore
sys.modules[__name__ + '.QtGui'] = QtGui
sys.modules[__name__ + '.QtNetwork'] = QtNetwork
sys.modules[__name__ + '.QtWidgets'] = QtWidgets
sys.modules[__name__ + '.Qt'] = Qt

try:
    from PyQt5 import QtSvg
    sys.modules[__name__ + '.QtSvg'] = QtSvg
except ImportError:
    raise SystemExit("Please install the PyQt5.QtSvg module")

QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot
QtCore.Property = QtCore.pyqtProperty

from PyQt5.QtWidgets import QFileDialog as OldFileDialog


# Do not use system proxy because it could be a parental control, virus or "Security software"...
QtNetwork.QNetworkProxyFactory.setUseSystemConfiguration(False)


def sip_is_deleted(obj):
    """
    :return: True if object no longer exists
    """
    if obj is None or (isinstance(obj, sip.simplewrapper) and sip.isdeleted(obj)):
        return True
    return False


class QFileDialog(OldFileDialog):

    @staticmethod
    def getExistingDirectory(parent=None, caption='', dir='', options=OldFileDialog.ShowDirsOnly):
        path = OldFileDialog.getExistingDirectory(parent, caption, dir, options)
        if path:
            path = os.path.normpath(path)
        return path

    @staticmethod
    def getOpenFileName(parent=None, caption='', directory='', filter='', selectedFilter='', options=OldFileDialog.Options()):
        path, _ = OldFileDialog.getOpenFileName(parent, caption, directory, filter, selectedFilter, options)
        if path:
            path = os.path.normpath(path)
        return path, _

    @staticmethod
    def getOpenFileNames(parent=None, caption='', directory='', filter='', selectedFilter='', options=OldFileDialog.Options()):
        path, _ = OldFileDialog.getOpenFileNames(parent, caption, directory, filter, selectedFilter, options)
        if path:
            path = os.path.normpath(path)
        return path, _

    @staticmethod
    def getSaveFileName(parent=None, caption='', directory='', filter='', selectedFilter='', options=OldFileDialog.Options()):
        path, _ = OldFileDialog.getSaveFileName(parent, caption, directory, filter, selectedFilter, options)
        if path:
            path = os.path.normpath(path)
        return path, _

QtWidgets.QFileDialog = QFileDialog


class LogQMessageBox(QtWidgets.QMessageBox):
    """
    Replace the standard message box for logging errors to console. And
    show a stack trace when a critical message box is shown in debug mode
    """
    @staticmethod
    def critical(parent, title, message, *args):
        log.critical(re.sub(r"<[^<]+?>", "", message), stack_info=LogQMessageBox.stack_info())
        if sip_is_deleted(parent):
            return
        return super(QtWidgets.QMessageBox, QtWidgets.QMessageBox).critical(parent, title, message, *args)

    @staticmethod
    def warning(parent, title, message, *args):
        log.warning(re.sub(r"<[^<]+?>", "", message))
        if sip_is_deleted(parent):
            return
        return super(QtWidgets.QMessageBox, QtWidgets.QMessageBox).warning(parent, title, message, *args)

    @staticmethod
    def stack_info():
        """
        Show stack trace
        """
        return logging.getLogger().getEffectiveLevel() == logging.DEBUG

QtWidgets.QMessageBox = LogQMessageBox


# If we run from a test we replace the signal by a synchronous version
if hasattr(sys, '_called_from_test'):
    class FakeQtSignal:
        _instances = set()

        def __init__(self, *args):
            self._callbacks = set()
            self._instances.add(self)

        def connect(self, func, style=None):
            log.debug("{caller} connect to signal".format(caller=sys._getframe(1).f_code.co_name))
            self._callbacks.add(func)

        def disconnect(self, func):
            self._callbacks.remove(func)

        def emit(self, *args):
            log.debug("{caller} emit signal".format(caller=sys._getframe(1).f_code.co_name))
            for callback in list(self._callbacks):
                callback(*args)

        @classmethod
        def reset(cls):
            """Use to clean the listening signals between tests"""
            for instance in cls._instances:
                instance._callbacks = set()

    QtCore.Signal = FakeQtSignal
    QtCore.pyqtSignal = FakeQtSignal


class StatsQtWidgetsQWizard(QtWidgets.QWizard):
    """
    Send stats from all the QWizard
    """

    def __init__(self, *args):
        super().__init__(*args)

        from ..utils.analytics import AnalyticsClient
        name = self.__class__.__name__
        name = re.sub(r"([A-Z])", r" \1", name).strip()
        AnalyticsClient.instance().sendScreenView(name)

QtWidgets.QWizard = StatsQtWidgetsQWizard


class StatsQtWidgetsQMainWindow(QtWidgets.QMainWindow):
    """
    Send stats from all the QMainWindow
    """

    def __init__(self, *args):
        super().__init__(*args)

        from ..utils.analytics import AnalyticsClient
        name = self.__class__.__name__
        name = re.sub(r"([A-Z])", r" \1", name).strip()
        AnalyticsClient.instance().sendScreenView(name)

QtWidgets.QMainWindow = StatsQtWidgetsQMainWindow


class StatsQtWidgetsQDialog(QtWidgets.QDialog):
    """
    Send stats from all the QWizard
    """

    def __init__(self, *args):
        super().__init__(*args)

        from ..utils.analytics import AnalyticsClient
        name = self.__class__.__name__
        name = re.sub(r"([A-Z])", r" \1", name).strip()
        AnalyticsClient.instance().sendScreenView(name)

QtWidgets.QDialog = StatsQtWidgetsQDialog


def qpartial(func, *args, **kwargs):
    """
    A functools partial that you can use on qobject. If the targeted qobject is
    destroyed the partial is not called.
    """
    if func is None:
        return None

    if inspect.ismethod(func):
        if isinstance(func.__self__, QtCore.QObject):

            def partial(*args, **kwargs):
                if sip_is_deleted(func.__self__):
                    return
                return func(*args, **kwargs)
            return functools.partial(partial, *args, **kwargs)

    return functools.partial(func, *args, **kwargs)


def qslot(func):
    """
    Decorated slot are protected against already destroyed element
    in SIP but not in Python
    """
    def func_wrapper(*args, **kwargs):
        if len(args) > 0:
            if sip_is_deleted(args[0]):
                return lambda: True
        return func(*args, **kwargs)
    return func_wrapper
