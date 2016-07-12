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

import os
import hashlib
import tempfile

from .qt import QtCore, QtGui, qpartial
from .symbol import Symbol


import logging
log = logging.getLogger(__name__)


class Controller(QtCore.QObject):
    """
    An instance of the GNS3 server controller
    """
    connected_signal = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self._connected = False
        self._cache_directory = tempfile.TemporaryDirectory()

    def connected(self):
        """
        Is the controller connected
        """
        return self._connected

    def setHttpClient(self, http_client):
        """
        :param http_client: Instance of HTTP client to communicate with the server
        """
        self._http_client = http_client
        self._http_client.connection_connected_signal.connect(self._httpClientConnectedSlot)
        self.get('/version', None)

    def _httpClientConnectedSlot(self):
        if not self._connected:
            self._connected = True
            self.connected_signal.emit()

    def get(self, *args, **kwargs):
        return self.createHTTPQuery("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.createHTTPQuery("POST", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.createHTTPQuery("PUT", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.createHTTPQuery("DELETE", *args, **kwargs)

    def createHTTPQuery(self, method, path, *args, **kwargs):
        """
        Forward the query to the HTTP client or controller depending of the path
        """
        return self._http_client.createHTTPQuery(method, path, *args, **kwargs)

    def getSynchronous(self, endpoint, timeout=2):
        return self._http_client.getSynchronous(endpoint, timeout)

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of Controller.
        :returns: instance of Controller
        """

        if not hasattr(Controller, '_instance') or Controller._instance is None:
            Controller._instance = Controller()
        return Controller._instance

    def getStatic(self, url, callback):
        """
        Get a URL from the /static on controller and cache it on disk

        :param url: URL without the protocol and host part
        :param callback: Callback to call when file is ready
        """
        m = hashlib.md5()
        m.update(url.encode())
        if ".svg" in url:
            extension = ".svg"
        else:
            extension = ".png"
        path = os.path.join(self._cache_directory.name, m.hexdigest() + extension)
        if os.path.exists(path):
            callback(path)
        else:
            self._http_client.createHTTPQuery("GET", url, qpartial(self._getStaticCallback, callback, url, path))

    def _getStaticCallback(self, callback, url, path, result, error=False, raw_body=None, **kwargs):
        if error:
            log.error("Error while downloading file: {}".format(url))
            return
        with open(path, "wb+") as f:
            f.write(raw_body)
        callback(path)

    def getSymbolIcon(self, symbol_id, callback):
        """
        Get a QIcon for a symbol from the controller

        :param url: URL without the protocol and host part
        :param callback: Callback to call when file is ready
        """
        self.getStatic(Symbol(symbol_id).url(), qpartial(self._getIconCallback, callback))

    def _getIconCallback(self, callback, path):
        icon = QtGui.QIcon()
        icon.addFile(path)
        callback(icon)
