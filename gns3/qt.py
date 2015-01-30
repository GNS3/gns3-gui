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
Compatibility layer for Qt bindings, so it is easier to switch from PyQt4 to PySide and
vice-versa. Possibility to add PyQt5 in the future as well. Current default is PyQt4.
"""

# based on https://gist.github.com/remram44/5985681

import sys
import sip

import logging
log = logging.getLogger(__name__)


DEFAULT_BINDING = 'PyQt'

if DEFAULT_BINDING == 'PyQt':
    sip.setapi('QDate', 2)
    sip.setapi('QDateTime', 2)
    sip.setapi('QString', 2)
    sip.setapi('QTextStream', 2)
    sip.setapi('QTime', 2)
    sip.setapi('QUrl', 2)
    sip.setapi('QVariant', 2)

    from PyQt4 import QtCore, QtGui, QtNetwork, QtSvg
    sys.modules[__name__ + '.QtCore'] = QtCore
    sys.modules[__name__ + '.QtGui'] = QtGui
    sys.modules[__name__ + '.QtNetwork'] = QtNetwork
    sys.modules[__name__ + '.QtSvg'] = QtSvg

    try:
        from PyQt4 import QtWebKit
        sys.modules[__name__ + '.QtWebKit'] = QtWebKit
    except ImportError:
        pass

    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
    QtCore.Property = QtCore.pyqtProperty
    QtCore.BINDING_VERSION_STR = QtCore.PYQT_VERSION_STR

elif DEFAULT_BINDING == 'PySide':

    from PySide import QtCore, QtGui, QtNetwork, QtSvg, __version__
    sys.modules[__name__ + '.QtCore'] = QtCore
    sys.modules[__name__ + '.QtGui'] = QtGui
    sys.modules[__name__ + '.QtNetwork'] = QtNetwork
    sys.modules[__name__ + '.QtSvg'] = QtSvg

    try:
        from PySide import QtWebKit
        sys.modules[__name__ + '.QtWebKit'] = QtWebKit
    except ImportError:
        pass

    QtCore.QT_VERSION_STR = QtCore.__version__
    QtCore.BINDING_VERSION_STR = __version__

else:
    raise ImportError("Python binding not specified.")


# If we run from a test we replace the signal by a synchronous version
if hasattr(sys, '_called_from_test'):
    class FakeQtSignal:
        _instances = set()

        def __init__(self, *args):
            self._callbacks = set()
            self._instances.add(self)

        def connect(self, func):
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
