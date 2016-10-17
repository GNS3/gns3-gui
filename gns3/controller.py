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

from .qt import QtCore, QtGui, QtWidgets, qpartial
from .symbol import Symbol
from .local_server_config import LocalServerConfig
from .settings import LOCAL_SERVER_SETTINGS

import logging
log = logging.getLogger(__name__)


class Controller(QtCore.QObject):
    """
    An instance of the GNS3 server controller
    """
    connected_signal = QtCore.Signal()
    connection_failed_signal = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__()
        self._connected = False
        self._connecting = False
        self._cache_directory = tempfile.TemporaryDirectory()
        self._http_client = None
        # If it's the first error we display an alert box to the user
        self._first_error = True

    def host(self):
        return self._http_client.host()

    def isRemote(self):
        """
        :returns Boolean: True if the controller is remote
        """
        settings = LocalServerConfig.instance().loadSettings("Server", LOCAL_SERVER_SETTINGS)
        return not settings["auto_start"]

    def connecting(self):
        """
        :returns: True if connection is in progress
        """
        return self._connecting

    def connected(self):
        """
        Is the controller connected
        """
        return self._connected

    def httpClient(self):
        """
        :returns: HTTP client for connected to the controller
        """
        return self._http_client

    def setHttpClient(self, http_client):
        """
        :param http_client: Instance of HTTP client to communicate with the server
        """
        self._http_client = http_client
        if self._http_client:
            self._http_client.connection_connected_signal.connect(self._httpClientConnectedSlot)
            self._connected = False
            self._connecting = True
            self.get('/version', self._versionGetSlot)

    def _versionGetSlot(self, result, error=False, **kwargs):
        """
        Called after the inital version get
        """
        if error:
            if self._first_error:
                self._connecting = False
                self.connection_failed_signal.emit()
                if "message" in result:
                    QtWidgets.QMessageBox.critical(self.parent(), "Connection", result["message"])
            # Try to connect again in 1 seconds
            QtCore.QTimer.singleShot(1000, qpartial(self.get, '/version', self._versionGetSlot, showProgress=self._first_error))
            self._first_error = False
        else:
            self._first_error = True

    def _httpClientConnectedSlot(self):
        if not self._connected:
            self._connected = True
            self._connecting = False
            self.connected_signal.emit()

    def get(self, *args, **kwargs):
        return self.createHTTPQuery("GET", *args, **kwargs)

    def getCompute(self, path, compute_id, *args, **kwargs):
        """
        API get on a specific compute
        """
        compute_id = self.__fix_compute_id(compute_id)
        path = "/computes/{}{}".format(compute_id, path)
        return self.get(path, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.createHTTPQuery("POST", *args, **kwargs)

    def postCompute(self, path, compute_id, *args, **kwargs):
        """
        API post on a specific compute
        """
        compute_id = self.__fix_compute_id(compute_id)
        path = "/computes/{}{}".format(compute_id, path)
        return self.post(path, *args, **kwargs)

    def __fix_compute_id(self, compute_id):
        """
        Support for remote server <= 1.5
        This fix should be not require after the 2.1
        when all the appliance template will be managed
        on server
        """
        if compute_id.startswith("http:") or compute_id.startswith("https:"):
            from .compute_manager import ComputeManager
            return ComputeManager.instance().getCompute(compute_id).id()
        return compute_id

    def put(self, *args, **kwargs):
        return self.createHTTPQuery("PUT", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.createHTTPQuery("DELETE", *args, **kwargs)

    def createHTTPQuery(self, method, path, *args, **kwargs):
        """
        Forward the query to the HTTP client or controller depending of the path
        """
        if self._http_client:
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

        if not self._http_client:
            return

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
        log.debug("File stored {} for {}".format(path, url))
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
