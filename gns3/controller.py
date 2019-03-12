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
import json
import pathlib

from .qt import QtCore, QtNetwork, QtGui, QtWidgets, QtWebSockets, qpartial, qslot
from .symbol import Symbol
from .local_server_config import LocalServerConfig
from .settings import LOCAL_SERVER_SETTINGS
from gns3.utils import parse_version

import logging
log = logging.getLogger(__name__)


class Controller(QtCore.QObject):
    """
    An instance of the server controller.
    """

    connected_signal = QtCore.Signal()
    disconnected_signal = QtCore.Signal()
    connection_failed_signal = QtCore.Signal()
    project_list_updated_signal = QtCore.Signal()

    def __init__(self):

        super().__init__()
        self._connected = False
        self._connecting = False
        self._version = None
        self._cache_directory = tempfile.TemporaryDirectory(suffix="-gns3")
        self._http_client = None
        self._first_error = True
        self._error_dialog = None
        self._display_error = True
        self._projects = []
        self._controller_websocket = QtWebSockets.QWebSocket()
        self._project_websocket = QtWebSockets.QWebSocket()

        # If we do multiple call in order to download the same symbol we queue them
        self._static_asset_download_queue = {}

    def host(self):

        return self._http_client.host()

    def version(self):
        return self._version

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
        :returns: HTTP client to connect to the controller
        """

        return self._http_client

    def setHttpClient(self, http_client):
        """
        :param http_client: Instance of HTTP client to communicate with the server
        """

        self._http_client = http_client
        if self._http_client:
            if self.isRemote():
                self._http_client.setMaxTimeDifferenceBetweenQueries(120)
            self._http_client.connection_connected_signal.connect(self._httpClientConnectedSlot)
            self._http_client.connection_disconnected_signal.connect(self._httpClientDisconnectedSlot)
            self._connectingToServer()

    def getHttpClient(self):
        """
        :return: Instance of HTTP client to communicate with the server
        """

        return self._http_client

    def setDisplayError(self, val):
        """
        Allow error to be visible or not
        """

        self._display_error = val
        self._first_error = True

    def _connectingToServer(self):
        """
        Connection process as started
        """

        self._connected = False
        self._connecting = True
        self.get('/version', self._versionGetSlot)

    def _httpClientDisconnectedSlot(self):
        if self._connected:
            self._connected = False
            self.disconnected_signal.emit()
            self._connectingToServer()
            self.stopListenNotifications()

    def _versionGetSlot(self, result, error=False, **kwargs):
        """
        Called after the initial version get
        """

        if error:
            if self._first_error:
                self._connecting = False
                self.connection_failed_signal.emit()
                if "message" in result and self._display_error:
                    self._error_dialog = QtWidgets.QMessageBox(self.parent())
                    self._error_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
                    self._error_dialog.setWindowTitle("Connection to server")
                    self._error_dialog.setText("Error when connecting to the GNS3 server:\n{}".format(result["message"]))
                    self._error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
                    self._error_dialog.show()
            # Try to connect again in 5 seconds
            QtCore.QTimer.singleShot(5000, qpartial(self.get, '/version', self._versionGetSlot, showProgress=self._first_error))
            self._first_error = False
        else:
            self._first_error = True
            if self._error_dialog:
                self._error_dialog.reject()
                self._error_dialog = None
            self._version = result.get("version")

    def _httpClientConnectedSlot(self):

        if not self._connected:
            self._connected = True
            self._connecting = False
            self.connected_signal.emit()
            self.refreshProjectList()
            self._startListenNotifications()

    def post(self, *args, **kwargs):
        return self.createHTTPQuery("POST", *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.createHTTPQuery("GET", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.createHTTPQuery("PUT", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.createHTTPQuery("DELETE", *args, **kwargs)

    def getCompute(self, path, compute_id, *args, **kwargs):
        """
        API get on a specific compute
        """

        compute_id = self.__fix_compute_id(compute_id)
        path = "/computes/{}{}".format(compute_id, path)
        return self.get(path, *args, **kwargs)

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
        when all the templates will be managed on server
        """

        #FIXME: remove this?
        if compute_id.startswith("http:") or compute_id.startswith("https:"):
            from .compute_manager import ComputeManager
            try:
                return ComputeManager.instance().getCompute(compute_id).id()
            except KeyError:
                return compute_id
        return compute_id

    def getEndpoint(self, path, compute_id, *args, **kwargs):
        """
        API post on a specific compute
        """

        compute_id = self.__fix_compute_id(compute_id)
        path = "/computes/endpoint/{}{}".format(compute_id, path)
        return self.get(path, *args, **kwargs)

    def putCompute(self, path, compute_id, *args, **kwargs):
        """
        API put on a specific compute
        """

        compute_id = self.__fix_compute_id(compute_id)
        path = "/computes/{}{}".format(compute_id, path)
        return self.put(path, *args, **kwargs)

    def createHTTPQuery(self, method, path, *args, **kwargs):
        """
        Forward the query to the HTTP client or controller depending of the path
        """

        if self._http_client:
            return self._http_client.createHTTPQuery(method, path, *args, **kwargs)

    def getSynchronous(self, endpoint, timeout=2):
        return self._http_client.getSynchronous(endpoint, timeout)

    def connectProjectWebSocket(self, path, *args):
        return self._http_client.connectWebSocket(self._project_websocket, path)

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of Controller.
        :returns: instance of Controller
        """

        if not hasattr(Controller, '_instance') or Controller._instance is None:
            Controller._instance = Controller()
        return Controller._instance

    def getStatic(self, url, callback, fallback=None):
        """
        Get a URL from the /static on controller and cache it on disk

        :param url: URL without the protocol and host part
        :param callback: Callback to call when file is ready
        :param fallback: Fallback url in case of error
        """

        if not self._http_client:
            return

        path = self.getStaticCachedPath(url)

        if os.path.exists(path):
            callback(path)
        elif path in self._static_asset_download_queue:
            self._static_asset_download_queue[path].append((callback, fallback, ))
        else:
            self._static_asset_download_queue[path] = [(callback, fallback, )]
            self._http_client.createHTTPQuery("GET", url, qpartial(self._getStaticCallback, url, path))

    def _getStaticCallback(self, url, path, result, error=False, raw_body=None, **kwargs):
        if path not in self._static_asset_download_queue:
            return

        if error:
            fallback_used = False
            for callback, fallback in self._static_asset_download_queue[path]:
                if fallback:
                    self.getStatic(fallback, callback)
                fallback_used = True
            if fallback_used:
                log.debug("Error while downloading file: {}".format(url))
            del self._static_asset_download_queue[path]
            return
        try:
            with open(path, "wb+") as f:
                f.write(raw_body)
        except OSError as e:
            log.error("Can't write to {}: {}".format(path, str(e)))
            return
        log.debug("File stored {} for {}".format(path, url))
        for callback, fallback in self._static_asset_download_queue[path]:
            callback(path)
        del self._static_asset_download_queue[path]

    def getStaticCachedPath(self, url):
        """
        Returns static cached (hashed) path

        :param url:
        """
        m = hashlib.md5()
        m.update(url.encode())
        if ".svg" in url:
            extension = ".svg"
        else:
            extension = ".png"
        path = os.path.join(self._cache_directory.name, m.hexdigest() + extension)
        return path

    def clearStaticCache(self):
        """
        Clear the cache directory.
        """

        for filename in os.listdir(self._cache_directory.name):
            if filename.endswith(".svg") or filename.endswith(".png"):
                try:
                    os.remove(os.path.join(self._cache_directory.name, filename))
                except OSError as e:
                    log.debug("Error deleting cached symbol '{}':{}".format(filename, e))
                    continue

    def getSymbolIcon(self, symbol_id, callback, fallback=None):
        """
        Get a QIcon for a symbol from the controller

        :param symbol_id: Symbol id
        :param callback: Callback to call when file is ready
        :param fallback: Fallback symbol if not found
        """
        if symbol_id is None:
            self.getStatic(Symbol(fallback).url(), qpartial(self._getIconCallback, callback))
        else:
            if fallback:
                fallback = Symbol(fallback).url()
            self.getStatic(Symbol(symbol_id).url(), qpartial(self._getIconCallback, callback), fallback=fallback)

    def _getIconCallback(self, callback, path):

        pixmap = QtGui.QPixmap(path)
        if pixmap.isNull():
            log.debug("Invalid symbol {}".format(path))
            path = ":/icons/cancel.svg"
        icon = QtGui.QIcon()
        icon.addFile(path)
        callback(icon)

    def uploadSymbol(self, symbol_id, path):

        self.post("/symbols/" + symbol_id + "/raw",
                  qpartial(self._finishSymbolUpload, path),
                  body=pathlib.Path(path), progressText="Uploading {}".format(symbol_id), timeout=None)

    def _finishSymbolUpload(self, path, result, error=False, **kwargs):

        if error:
            log.error("Error while uploading symbol: {}: {}".format(path, result.get("message", "unknown")))
            return

        # Refresh the templates list
        from .template_manager import TemplateManager
        TemplateManager.instance().templates_changed_signal.emit()

    def getSymbols(self, callback):
        self.get('/symbols', callback=callback)

    def deleteProject(self, project_id, callback=None):
        Controller.instance().delete("/projects/{}".format(project_id), qpartial(self._deleteProjectCallback, callback=callback, project_id=project_id))

    def _deleteProjectCallback(self, result, error=False, project_id=None, callback=None, **kwargs):
        if error:
            log.error("Error while deleting project: {}".format(result["message"]))
        else:
            self.refreshProjectList()

        self._projects = [p for p in self._projects if p["project_id"] != project_id]

        if callback:
            callback(result, error=error, **kwargs)

    @qslot
    def refreshProjectList(self, *args):
        self.get("/projects", self._projectListCallback)

    def _projectListCallback(self, result, error=False, **kwargs):
        if not error:
            self._projects = result
        self.project_list_updated_signal.emit()

    def projects(self):
        return self._projects

    def _startListenNotifications(self):
        if not self.connected():
            return

        # Due to bug in Qt on some version we need a dedicated network manager
        self._notification_network_manager = QtNetwork.QNetworkAccessManager()
        self._notification_stream = None

        # Qt websocket before Qt 5.6 doesn't support auth
        if parse_version(QtCore.QT_VERSION_STR) < parse_version("5.6.0") or parse_version(QtCore.PYQT_VERSION_STR) < parse_version("5.6.0"):
            self._notification_stream = Controller.instance().createHTTPQuery("GET", "/notifications", self._endListenNotificationCallback,
                                                                              downloadProgressCallback=self._event_received,
                                                                              networkManager=self._notification_network_manager,
                                                                              timeout=None,
                                                                              showProgress=False,
                                                                              ignoreErrors=True)

        else:
            self._notification_stream = self._http_client.connectWebSocket(self._controller_websocket, "/notifications/ws")
            self._notification_stream.textMessageReceived.connect(self._websocket_event_received)
            self._notification_stream.error.connect(self._websocket_error)

    def stopListenNotifications(self):
        if self._notification_stream:
            log.debug("Stop listening for notifications from controller")
            stream = self._notification_stream
            self._notification_stream = None
            stream.abort()
            self._notification_network_manager = None

    def _endListenNotificationCallback(self, result, error=False, **kwargs):
        """
        If notification stream disconnect we reconnect to it
        """
        if self._notification_stream:
            self._notification_stream = None
            self._startListenNotifications()

    @qslot
    def _websocket_error(self, error):
        if self._notification_stream:
            log.error(self._notification_stream.errorString())
            self._notification_stream = None
            self._startListenNotifications()

    @qslot
    def _websocket_event_received(self, event):
        try:
            self._event_received(json.loads(event))
        except ValueError as e:
            log.error("Invalid event received: {}".format(e))

    def _event_received(self, result, *args, **kwargs):

        # Log only relevant events
        if result["action"] not in ("ping", "compute.updated"):
            log.debug("Event received from controller stream: {}".format(result))
        if result["action"] == "template.created" or result["action"] == "template.updated":
            from gns3.template_manager import TemplateManager
            TemplateManager.instance().templateDataReceivedCallback(result["event"])
        elif result["action"] == "template.deleted":
            from gns3.template_manager import TemplateManager
            TemplateManager.instance().deleteTemplateCallback(result["event"])
        elif result["action"] == "compute.created" or result["action"] == "compute.updated":
            from .compute_manager import ComputeManager
            ComputeManager.instance().computeDataReceivedCallback(result["event"])
        elif result["action"] == "log.error":
            log.error(result["event"]["message"])
        elif result["action"] == "log.warning":
            log.warning(result["event"]["message"])
        elif result["action"] == "log.info":
            log.info(result["event"]["message"], extra={"show": True})
        elif result["action"] == "ping":
            pass
