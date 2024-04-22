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

from .qt import QtCore, QtGui, QtWebSockets, qpartial, qslot
from .symbol import Symbol
from .local_config import LocalConfig
from .settings import CONTROLLER_SETTINGS
from gns3.utils import parse_version
from gns3.http_client import HTTPClient

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
    image_list_updated_signal = QtCore.Signal()

    def __init__(self):

        super().__init__()
        self._connected = False
        self._connecting = False
        self._notification_stream = None
        self._version = None
        self._cache_directory = tempfile.TemporaryDirectory(suffix="-gns3")
        self._http_client = None
        self._first_error = True
        self._error_dialog = None
        self._display_error = True
        self._projects = []
        self._images = []
        self._websocket = QtWebSockets.QWebSocket()

        # If we do multiple call in order to download the same symbol we queue them
        self._static_asset_download_queue = {}

        self._loadSettings()

    def settings(self):
        """
        Returns the graphics view settings.

        :returns: settings dictionary
        """

        return self._settings

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        self._settings = LocalConfig.instance().loadSectionSettings(self.__class__.__name__, CONTROLLER_SETTINGS)

    def setSettings(self, new_settings):
        """
        Set new controller settings.

        :param new_settings: settings dictionary
        """

        # save the settings
        self._settings.update(new_settings)
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

    def host(self):

        return self._http_client.host()

    def version(self):

        return self._version

    def isRemote(self):
        """
        :returns Boolean: True if the controller is remote
        """

        return self._settings["remote"]

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
            self._http_client.connected_signal.connect(self._httpClientConnectedSlot)
            self._http_client.disconnected_signal.connect(self._httpClientDisconnectedSlot)
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

    def connect(self):
        """
        Connect to controller
        """

        self._http_client = HTTPClient(self._settings)
        Controller.instance().setHttpClient(self._http_client)

    def _connectingToServer(self):
        """
        Connection process as started
        """

        self._connected = False
        self._connecting = True
        self.httpClient().connectToServer()

    def _httpClientDisconnectedSlot(self):

        if self._connected:
            self._connected = False
            self.disconnected_signal.emit()
            self._connectingToServer()
            self.stopListenNotifications()

    def _httpClientConnectedSlot(self):

        if not self._connected:
            self._connected = True
            self._connecting = False
            self.connected_signal.emit()
            self.refreshProjectList()
            self._startListenNotifications()

    def post(self, *args, **kwargs):
        return self.request("POST", *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.request("GET", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request("PUT", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request("DELETE", *args, **kwargs)

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

    def request(self, method, path, *args, **kwargs):
        """
        Forward the query to the HTTP client or controller depending of the path
        """

        if self._http_client:
            return self._http_client.sendRequest(method, path, *args, **kwargs)

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
            self._http_client.sendRequest("GET", url, qpartial(self._getStaticCallback, url, path), raw=True)

    def _getStaticCallback(self, url, path, result, error=False, **kwargs):

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
                f.write(result)
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

        self.post(
            "/symbols/" + symbol_id + "/raw",
            qpartial(self._finishSymbolUpload, path),
            body=pathlib.Path(path),
            progress_text="Uploading {}".format(symbol_id),
            timeout=None,
            wait=True
        )

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


    def createDiskImage(self, disk_name, options, callback):
        """
        Create a disk image on the controller

        :param callback: callback for the reply from the server
        """

        self.post(f"/images/qemu/{disk_name}", callback, body=options)


    @qslot
    def refreshProjectList(self, *args):
        self.get("/projects", self._projectListCallback)

    def _projectListCallback(self, result, error=False, **kwargs):
        if not error:
            self._projects = result
        self.project_list_updated_signal.emit()

    def projects(self):
        return self._projects

    @qslot
    def refreshImageList(self, *args):
        self.get("/images", self._imageListCallback)

    def _imageListCallback(self, result, error=False, **kwargs):
        if not error:
            self._images = result
        self.image_list_updated_signal.emit()

    def images(self):
        return self._images

    def _startListenNotifications(self):
        if not self.connected():
            return

        self._notification_stream = None

        # Qt websocket before Qt 5.6 doesn't support auth
        if parse_version(QtCore.QT_VERSION_STR) < parse_version("5.6.0") or parse_version(QtCore.PYQT_VERSION_STR) < parse_version("5.6.0"):
            self._notification_stream = Controller.instance().request(
                "GET",
                "/notifications",
                self._endListenNotificationCallback,
                download_progress_callback=self._event_received,
                timeout=None,
                show_progress=False
            )
        else:
            self._notification_stream = self._http_client.connectWebSocket(self._websocket, "/notifications/ws")
            self._notification_stream.textMessageReceived.connect(self._websocket_event_received)
            self._notification_stream.error.connect(self._websocket_error)
            self._notification_stream.sslErrors.connect(self._sslErrorsSlot)
            self._notification_stream.disconnected.connect(self._websocket_disconnected)

    def _websocket_disconnected(self):

        self._connected = False
        self.disconnected_signal.emit()
        self.stopListenNotifications()

    def stopListenNotifications(self):
        if self._notification_stream:
            log.debug("Stop listening for notifications from controller")
            stream = self._notification_stream
            self._notification_stream = None
            stream.abort()

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
            log.error("Websocket controller notification stream error: {}".format(self._notification_stream.errorString()))
            self.stopListenNotifications()

    @qslot
    def _sslErrorsSlot(self, ssl_errors):

        self._http_client.handleSslError(self._notification_stream, ssl_errors)

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
        elif result["action"] == "project.closed":
            from .topology import Topology
            project = Topology.instance().project()
            if project and project.id() == result["event"]["project_id"]:
                Topology.instance().setProject(None)
        elif result["action"] == "project.updated":
            from .topology import Topology
            project = Topology.instance().project()
            if project and project.id() == result["event"]["project_id"]:
                project.projectUpdatedCallback(result["event"])
        elif result["action"] == "log.error" and result["event"].get("message"):
            log.error(result["event"].get("message"))
        elif result["action"] == "log.warning" and result["event"].get("message"):
            log.warning(result["event"].get("message"))
        elif result["action"] == "log.info" and result["event"].get("message"):
            log.info(result["event"].get("message"), extra={"show": True})
        elif result["action"] == "ping":
            pass
