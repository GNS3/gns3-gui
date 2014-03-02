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
