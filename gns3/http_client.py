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
import http
import uuid
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

    # Callback class used for displaying progress
    _progress_callback = None

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

        # create an unique ID
        self._id = HTTPClient._instance_count
        HTTPClient._instance_count += 1

    def notify_progress_start_query(self, query_id):
        """
        Called when a query start
        """
        if HTTPClient._progress_callback:
            HTTPClient._progress_callback.add_query_signal.emit(query_id, "Waiting for {scheme}://{host}:{port}".format(scheme=self.scheme, host=self.host, port=self.port))

    def notify_progress_end_query(cls, query_id):
        """
        Called when a query is over
        """

        if HTTPClient._progress_callback:
            HTTPClient._progress_callback.remove_query_signal.emit(query_id)

    @classmethod
    def setProgressCallback(cls, progress_callback):
        """
        :param progress_callback: A progress callback instance
        """
        cls._progress_callback = progress_callback

    @staticmethod
    def reset():
        """Reset HTTP client internal variables"""

        HTTPClient._instance_count = 0

    def url(self):
        """Returns current server url"""

        return "{scheme}://{host}:{port}".format(scheme=self.scheme, host=self.host, port=self.port)

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
                local_server = json_data.get("local", False)
                if version != __version__:
                    log.debug("Client version {} differs with server version {}".format(__version__, version))
                    return False
                if not local_server:
                    log.debug("Running server is not a GNS3 local server (not started with --local)")
                    return False
                return True
        except (OSError, urllib.error.HTTPError, http.client.BadStatusLine) as e:
            log.debug("No GNS3 server is already running on {}:{}: {}".format(self.host, self.port, e))
        return False

    def get(self, path, callback, context={}):
        """
        HTTP GET on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        """

        self.createHTTPQuery("GET", path, callback, context=context)

    def put(self, path, callback, body={}, context={}):
        """
        HTTP PUT on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param body: params to send (dictionary)
        """

        self.createHTTPQuery("PUT", path, callback, context=context, body=body)

    def post(self, path, callback, body={}, context={}):
        """
        HTTP POST on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param body: params to send (dictionary)
        """

        self.createHTTPQuery("POST", path, callback, context=context, body=body)

    def delete(self, path, callback, context={}):
        """
        HTTP DELETE on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        """

        self.createHTTPQuery("DELETE", path, callback, context=context)

    def _request(self, url):
        """
        Get a QNetworkRequest object. You can mock this
        if you want low level mocking.

        :param url: Url of remote ressource (QtCore.QUrl)
        :returns: QT Network request (QtNetwork.QNetworkRequest)
        """

        return QtNetwork.QNetworkRequest(url)

    def createHTTPQuery(self, method, path, callback, body={}, context={}):
        """
        Call the remote server, if not connected, check connection before

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary)
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        """

        if self._connected:
            self.executeHTTPQuery(method, path, callback, body, context=context)
        else:
            log.info("Connection to {}:{}".format(self.host, self.port))
            self.executeHTTPQuery("GET", "/version", partial(self._callbackConnect, method, path, callback, body, context), {})

    def _callbackConnect(self, method, path, callback, body, original_context, params, error=False, **kwargs):
        """
        Callback after /version response. Continue execution of query

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary)
        :param original_context: Original context
        :param callback: callback method to call when the server replies
        """

        if error is not False:
            msg = "Can't connect to server {}://{}:{}".format(self.scheme, self.host, self.port)
            if callback is not None:
                callback({"message": msg}, error=True, server=self)
            return
        if params["version"] != __version__:
            msg = "Client version {} differs with server version {}".format(__version__, params["version"])
            log.error(msg)
            if callback is not None:
                callback({"message": msg}, error=True, server=self)
            return

        self.executeHTTPQuery(method, path, callback, body, context=original_context)
        self._connected = True
        self._version = params["version"]

    def executeHTTPQuery(self, method, path, callback, body, context={}):
        """
        Call the remote server

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary)
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        """

        import copy
        context = copy.copy(context)
        context["query_id"] = str(uuid.uuid4())
        self.notify_progress_start_query(context["query_id"])
        log.debug("{method} {scheme}://{host}:{port}/v1{path} {body}".format(method=method, scheme=self.scheme, host=self.host, port=self.port, path=path, body=body))
        url = QtCore.QUrl("{scheme}://{host}:{port}/v1{path}".format(scheme=self.scheme, host=self.host, port=self.port, path=path))
        request = self._request(url)
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

        response.finished.connect(partial(self._processResponse, response, callback, context))

    def _processResponse(self, response, callback, context):

        if "query_id" in context:
            self.notify_progress_end_query(context["query_id"])
        if response.error() != QtNetwork.QNetworkReply.NoError:
            error_code = response.error()
            if error_code < 200:
                self._connected = False
            error_message = response.errorString()
            log.info("Response error: {}".format(error_message))
            body = bytes(response.readAll()).decode()
            content_type = response.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
            if callback is not None:
                if not body or content_type != "application/json":
                    callback({"message": error_message}, error=True, server=self, context=context)
                else:
                    log.debug(body)
                    callback(json.loads(body), error=True, server=self, context=context)
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
            if callback is not None:
                if status >= 400:
                    callback(params, error=True, server=self, context=context)
                else:
                    callback(params, server=self, context=context)
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

    def isCloud(self):
        return False
