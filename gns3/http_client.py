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
import pathlib
from functools import partial

from .version import __version__, __version_info__
from .qt import QtCore, QtNetwork

import logging
log = logging.getLogger(__name__)


class HttpBadRequest(Exception):

    """We raise bad request exception for logging them in Sentry"""
    pass


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
        self.scheme = url_settings.scheme
        self.host = url_settings.netloc.split(":")[0]
        self.port = url_settings.port

        self._connected = False
        self._local = True
        self._cloud = False

        self._network_manager = network_manager

        # A buffer used by progress download
        self._buffer = {}

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

    def notify_progress_upload(self, query_id, sent, total):
        """
        Called when a query upload progress
        """
        if HTTPClient._progress_callback:
            HTTPClient._progress_callback.progress(query_id, sent, total)

    def notify_progress_download(self, query_id, sent, total):
        """
        Called when a query download progress
        """
        if HTTPClient._progress_callback:
            HTTPClient._progress_callback.progress(query_id, sent, total)

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

    def get(self, path, callback, body={}, context={}, downloadProgressCallback=None, showProgress=True):
        """
        HTTP GET on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param body: params to send (dictionary or pathlib.Path)
        :param downloadProgressCallback: Callback called when received something, it can be an incomplete response
        :param showProgress: Display progress to the user
        """

        self.createHTTPQuery("GET", path, callback, context=context, body=body, downloadProgressCallback=downloadProgressCallback, showProgress=showProgress)

    def put(self, path, callback, body={}, context={}, downloadProgressCallback=None, showProgress=True):
        """
        HTTP PUT on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param body: params to send (dictionary or pathlib.Path)
        :param downloadProgressCallback: Callback called when received something, it can be an incomplete response
        :param showProgress: Display progress to the user
        """

        self.createHTTPQuery("PUT", path, callback, context=context, body=body, downloadProgressCallback=downloadProgressCallback, showProgress=showProgress)

    def post(self, path, callback, body={}, context={}, downloadProgressCallback=None, showProgress=True):
        """
        HTTP POST on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param body: params to send (dictionary or pathlib.Path)
        :param downloadProgressCallback: Callback called when received something, it can be an incomplete response
        :param showProgress: Display progress to the user
        """

        self.createHTTPQuery("POST", path, callback, context=context, body=body, downloadProgressCallback=downloadProgressCallback, showProgress=showProgress)

    def delete(self, path, callback, context={}, downloadProgressCallback=None, showProgress=True):
        """
        HTTP DELETE on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param downloadProgressCallback: Callback called when received something, it can be an incomplete response
        :param showProgress: Display progress to the user
        """

        self.createHTTPQuery("DELETE", path, callback, context=context, downloadProgressCallback=downloadProgressCallback, showProgress=showProgress)

    def _request(self, url):
        """
        Get a QNetworkRequest object. You can mock this
        if you want low level mocking.

        :param url: Url of remote ressource (QtCore.QUrl)
        :returns: QT Network request (QtNetwork.QNetworkRequest)
        """

        return QtNetwork.QNetworkRequest(url)

    def createHTTPQuery(self, method, path, callback, body={}, context={}, downloadProgressCallback=None, showProgress=True):
        """
        Call the remote server, if not connected, check connection before

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary or pathlib.Path)
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param downloadProgressCallback: Callback called when received something, it can be an incomplete response
        :param showProgress: Display progress to the user
        :returns: QNetworkReply
        """

        if self._connected:
            return self.executeHTTPQuery(method, path, callback, body, context, downloadProgressCallback=downloadProgressCallback, showProgress=showProgress)
        else:
            log.info("Connection to {}:{}".format(self.host, self.port))
            return self.executeHTTPQuery("GET", "/version", partial(self._callbackConnect, method, path, callback, body, context), {}, downloadProgressCallback=downloadProgressCallback, showProgress=showProgress)

    def _callbackConnect(self, method, path, callback, body, original_context, params, error=False, **kwargs):
        """
        Callback after /version response. Continue execution of query

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary or pathlib.Path)
        :param original_context: Original context
        :param callback: callback method to call when the server replies
        """

        if error is not False:
            msg = "Can't connect to server {}://{}:{}".format(self.scheme, self.host, self.port)
            if callback is not None:
                callback({"message": msg}, error=True, server=self)
            return

        if "version" not in params or "local" not in params:
            msg = "The remote server {}://{}:{} is not a GNS 3 server".format(self.scheme, self.host, self.port)
            log.error(msg)
            if callback is not None:
                callback({"message": msg}, error=True, server=self)
            return

        if params["version"] != __version__:
            msg = "Client version {} differs with server version {}".format(__version__, params["version"])
            log.error(msg)
            # Official release
            if __version_info__[3] == 0:
                if callback is not None:
                    callback({"message": msg}, error=True, server=self)
                return
            else:
                print(msg)
                print("WARNING: Use a different client and server version can create bugs. Use it at your own risk.")

        if params["local"] != self.isLocal():
            msg = "Running server is not a GNS3 local server (not started with --local)"
            log.error(msg)
            if callback is not None:
                callback({"message": msg}, error=True, server=self)
            return

        self.executeHTTPQuery(method, path, callback, body, context=original_context)
        self._connected = True
        self._version = params["version"]

    def _addBodyToRequest(self, body, request):
        """
        Add the require headers for sending the body.
        It detect the type of body for sending the corresponding headers
        and methods.

        :param body: The body
        :returns: The body compatible with Qt
        """

        if body is None:
            return None

        if isinstance(body, dict):
            body = json.dumps(body)
            request.setRawHeader("Content-Type", "application/json")
            request.setRawHeader("Content-Length", str(len(body)))
            data = QtCore.QByteArray(body)
            body = QtCore.QBuffer(self)
            body.setData(data)
            body.open(QtCore.QIODevice.ReadOnly)
            return body
        elif isinstance(body, pathlib.Path):
            body = QtCore.QFile(str(body), self)
            body.open(QtCore.QFile.ReadOnly)
            request.setRawHeader("Content-Type", "application/octet-stream")
            # QT is smart and will compute the Content-Lenght for us
            return body
        else:
            return None

    def executeHTTPQuery(self, method, path, callback, body, context={}, downloadProgressCallback=None, showProgress=True):
        """
        Call the remote server

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary)
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param downloadProgressCallback: Callback called when received something, it can be an incomplete response
        :param showProgress: Display progress to the user
        :returns: QNetworkReply
        """

        import copy
        context = copy.copy(context)
        query_id = str(uuid.uuid4())
        context["query_id"] = query_id
        if showProgress:
            self.notify_progress_start_query(context["query_id"])
        log.debug("{method} {scheme}://{host}:{port}/v1{path} {body}".format(method=method, scheme=self.scheme, host=self.host, port=self.port, path=path, body=body))
        url = QtCore.QUrl("{scheme}://{host}:{port}/v1{path}".format(scheme=self.scheme, host=self.host, port=self.port, path=path))
        request = self._request(url)

        request.setRawHeader("User-Agent", "GNS3 QT Client v{version}".format(version=__version__))

        # By default QT doesn't support GET with body even if it's in the RFC that's why we need to use sendCustomRequest
        body = self._addBodyToRequest(body, request)

        response = self._network_manager.sendCustomRequest(request, method, body)

        if showProgress:
            response.uploadProgress.connect(partial(self.notify_progress_upload, query_id))
            response.downloadProgress.connect(partial(self.notify_progress_download, query_id))

        response.finished.connect(partial(self._processResponse, response, callback, context, body))
        if downloadProgressCallback is not None:
            response.downloadProgress.connect(partial(self._processDownloadProgress, response, downloadProgressCallback, context))
        return response

    def _processDownloadProgress(self, response, callback, context):
        """
        Process a packet receive on the notification feed.
        The feed can contains partial JSON. If we found a
        part of a JSON we keep it for the next packet
        """

        if response.error() != QtNetwork.QNetworkReply.NoError:  # FIXME: check for any side effects of this line
            content = bytes(response.readAll())
            content_type = response.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
            if content_type == "application/json":
                content = content.decode()
                if context["query_id"] in self._buffer:
                    content = self._buffer[context["query_id"]] + content
                try:
                    while True:
                        answer, index = json.JSONDecoder().raw_decode(content)
                        callback(answer, server=self, context=context)
                        content = content[index:]
                except ValueError:  # Partial JSON
                    self._buffer[context["query_id"]] = content
            else:
                callback(content, server=self, context=context)

            if HTTPClient._progress_callback and HTTPClient._progress_callback.progress_dialog():
                request_canceled = partial(self._requestCanceled, response, context)
                HTTPClient._progress_callback.progress_dialog().canceled.connect(request_canceled)

    def _requestCanceled(self, response, context):

        if response.isRunning():
            response.abort()
        if "query_id" in context:
            self.notify_progress_end_query(context["query_id"])

    def _processResponse(self, response, callback, context, request_body):

        if request_body is not None:
            request_body.close()

        status = None
        body = None

        if "query_id" in context:
            self.notify_progress_end_query(context["query_id"])

        if response.error() != QtNetwork.QNetworkReply.NoError:
            error_code = response.error()
            if error_code < 200:
                self._connected = False
            else:
                status = response.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
            error_message = response.errorString()
            log.info("Response error: {}".format(error_message))
            try:
                body = bytes(response.readAll()).decode("utf-8").strip("\0")
                # Some time antivirus intercept our query and reply with garbage content
            except UnicodeError:
                body = None
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
            body = bytes(response.readAll()).decode("utf-8").strip("\0")
            content_type = response.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
            log.debug(body)
            if body and len(body.strip(" \n\t")) > 0 and content_type == "application/json":
                params = json.loads(body)
            else:
                params = {}
            if callback is not None:
                if status >= 400:
                    callback(params, error=True, server=self, context=context)
                else:
                    callback(params, server=self, context=context)
        # response.deleteLater()
        if status == 400:
            raise HttpBadRequest(body)

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
