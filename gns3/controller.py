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

from .qt import QtCore

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

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of Controller.
        :returns: instance of Controller
        """

        if not hasattr(Controller, '_instance') or Controller._instance is None:
            Controller._instance = Controller()
        return Controller._instance
