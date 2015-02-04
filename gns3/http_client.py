# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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


import json
import urllib.parse
import urllib.request
from functools import partial

from .version import __version__
from .qt import QtCore, QtNetwork

import logging
log = logging.getLogger(__name__)


class HTTPClient(QtCore.QObject):

    """
    HTTP client.

    :param url: URL to connect to the server
    :param network_manager: A QT network manager
    """

    _instance_count = 1
    connected_signal = QtCore.Signal()
    connection_error_signal = QtCore.Signal(str)

    def __init__(self, url, network_manager):

        super().__init__()
        self._url = url
        self._version = ""

        url_settings = urllib.parse.urlparse(url)

        # TODO: move this to properties? (many references to .host and .port in the code)
        self.scheme = url_settings.scheme
        self.host = url_settings.netloc.split(":")[0]
        self.port = url_settings.port

        self._connected = False
        self._local = True
        self._cloud = False

        self._network_manager = network_manager
        # self.check_server_version()

        # create an unique ID
        self._id = HTTPClient._instance_count
        HTTPClient._instance_count += 1

    def id(self):
        """
        Returns this HTTP Client identifier.
        :returns: HTTP client identifier (string)
        """

        return self._id

    def setLocal(self, value):
        """
        Sets either this is a connection to a local server or not.
        :param value: boolean
        """

        self._local = value

    def isLocal(self):
        """
        Returns either this is a connection to a local server or not.
        :returns: boolean
        """

        return self._local

    def connected(self):
        """
        Returns if the client is connected.
        :returns: True or False
        """

        return self._connected

    def close(self):
        """
        Closes the connection with the server.
        """

        self._connected = False

    def isServerRunning(self):
        """
        Check if a server is already running on this host.

        :returns: boolean
        """

        try:
            url = "{scheme}://{host}:{port}/v1/version".format(scheme=self.scheme, host=self.host, port=self.port)
            response = urllib.request.urlopen(url, timeout=2)
            content_type = response.getheader("CONTENT-TYPE")
            if response.status == 200 and content_type == "application/json":
                content = response.read()
                json_data = json.loads(content.decode("utf-8"))
                version = json_data.get("version")
                if version != __version__:
                    log.debug("Client version {} differs with server version {}".format(__version__, version))
                    return False
                return True
        except urllib.request.URLError as e:
            log.debug("No server is already running: {}".format(e))
        return False

    def connect(self):
        """
        Connects to the server.
        """

        client_version = {"version": __version__}
        self.post("/version", self._connectCallback, body=client_version, connecting=True)

    def _connectCallback(self, result, error=False):
        """
        Callback for the connection.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            self.connection_error_signal.emit(result["message"])
        else:
            self._version = result["version"]
            self._connected = True
            self.connected_signal.emit()

    def send_message(self, destination, params, callback):
        """
        Sends a message to the server.

        :param destination: server destination method
        :param params: params to send (dictionary)
        :param callback: callback method to call when the server replies.
        """

        log.error("OLD Send message. Destination {destination}, {params}".format(destination=destination, params=params))
        # TODO : Remove this method when migration to rest api is done

    def send_notification(self, destination, params=None):
        """
        Sends a notification to the server. No reply is expected from the server.

        :param destination: server destination method
        :param params: params to send (dictionary)
        """
        log.error("OLD Send notification. Destination {destination}, {params}".format(destination=destination, params=params))
        # TODO : Remove this method when migration to rest api is done

    def get(self, path, callback):
        """
        HTTP GET on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        """

        self._createHTTPQuery("GET", path, callback)

    def put(self, path, callback, body={}):
        """
        HTTP PUT on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)
        :param check_connected: check if connected to a server
        """

        self._createHTTPQuery("PUT", path, callback, body=body)

    def post(self, path, callback, body={}, connecting=False):
        """
        HTTP POST on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)
        :param connecting: indicates this is an initial connection to the server
        """

        self._createHTTPQuery("POST", path, callback, body=body, connecting=connecting)

    def delete(self, path, callback):
        """
        HTTP DELETE on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        """

        self._createHTTPQuery("DELETE", path, callback)

    def _createHTTPQuery(self, method, path, callback, body={}, connecting=False):
        """
        Call the remote server

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary)
        :param callback: callback method to call when the server replies
        :param connecting: indicates this is an initial connection to the server
        """

        if not connecting and not self._connected:
            log.error("Not connected to {}:{}".format(self.host, self.port))
            return

        log.debug("{method} {scheme}://{host}:{port}/v1{path} {body}".format(method=method, scheme=self.scheme, host=self.host, port=self.port, path=path, body=body))
        url = QtCore.QUrl("{scheme}://{host}:{port}/v1{path}".format(scheme=self.scheme, host=self.host, port=self.port, path=path))
        request = QtNetwork.QNetworkRequest(url)
        request.setRawHeader("Content-Type", "application/json")
        request.setRawHeader("Content-Length", str(len(body)))
        request.setRawHeader("User-Agent", "GNS3 QT Client v{version}".format(version=__version__))

        if method == "GET":
            response = self._network_manager.get(request)

        if method == "PUT":
            body = json.dumps(body)
            request.setRawHeader("Content-Type", "application/json")
            request.setRawHeader("Content-Length", str(len(body)))
            response = self._network_manager.put(request, body)

        if method == "POST":
            body = json.dumps(body)
            request.setRawHeader("Content-Type", "application/json")
            request.setRawHeader("Content-Length", str(len(body)))
            response = self._network_manager.post(request, body)

        if method == "DELETE":
            response = self._network_manager.deleteResource(request)

        response.finished.connect(partial(self._processResponse, response, callback))

    def _processResponse(self, response, callback):

        if response.error() != QtNetwork.QNetworkReply.NoError:
            error_code = response.error()
            if error_code < 200:
                self._connected = False
            error_message = response.errorString()
            log.info("Response error: {}".format(error_message))
            body = bytes(response.readAll()).decode()
            content_type = response.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
            if not body or content_type != "application/json":
                callback({"message": error_message}, error=True)
            else:
                log.debug(body)
                callback(json.loads(body), error=True)
        else:
            status = response.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
            log.debug("Decoding response from {} response {}".format(response.url().toString(), status))
            body = bytes(response.readAll()).decode()
            content_type = response.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
            log.debug(body)
            if body and content_type == "application/json":
                params = json.loads(body)
            else:
                params = {}
            if status >= 400:
                callback(params, error=True)
            else:
                callback(params)
        response.deleteLater()

    def dump(self):
        """
        Returns a representation of this server.
        :returns: dictionary
        """

        return {"id": self._id,
                "host": self.host,
                "port": self.port,
                "local": self._local,
                "cloud": self._cloud}
