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
import ipaddress
import uuid
import urllib.request
import pathlib
import base64
from functools import partial

from .version import __version__, __version_info__
from .qt import QtCore, QtNetwork
from .network_client import getNetworkUrl

import logging
log = logging.getLogger(__name__)


class HttpBadRequest(Exception):

    """We raise bad request exception for logging them in Sentry"""
    pass


class HTTPClient(QtCore.QObject):

    """
    HTTP client.

    :param settings: Dictionnary with connection information to the server
    :param network_manager: A QT network manager
    """

    _instance_count = 1

    # Callback class used for displaying progress
    _progress_callback = None

    connected_signal = QtCore.Signal()
    connection_error_signal = QtCore.Signal(str)

    def __init__(self, settings, network_manager):

        super().__init__()
        self._version = ""

        self._scheme = settings.get("protocol", "http")
        self._host = settings["host"]
        self._http_host = settings["host"]
        self._port = int(settings["port"])
        self._http_port = int(settings["port"])
        self._user = settings.get("user", None)
        self._password = settings.get("password", None)
        self._connected = False
        self._local = True
        self._cloud = False
        self._accept_insecure_certificate = settings.get("accept_insecure_certificate", False)

        self._network_manager = network_manager

        # A buffer used by progress download
        self._buffer = {}

        # create an unique ID
        self._id = HTTPClient._instance_count
        HTTPClient._instance_count += 1

    def getTunnel(self, port):
        """
        Get a tunnel to the remote port.
        For HTTP standard client it's the same port. For SSH it will create a new tunnel.

        :param port: Remote port
        :returns: Tuple host, port to connect
        """
        return self._host, port

    def releaseTunnel(self, port):
        """
        Release a tunnel to the remote port.
        For HTTP standard client it's do nothing

        :param port: Allocated remote port
        """
        pass

    def settings(self):
        """
        Return a dictionnary with server settings
        """
        settings = {"protocol": self.protocol(),
                    "host": self.host(),
                    "port": self.port(),
                    "user": self.user()}
        if self.protocol() == "https":
            settings["accept_insecure_certificate"] = self.acceptInsecureCertificate()
        return settings

    def acceptInsecureCertificate(self):
        """
        Does the server accept insecure SSL certificate
        """
        return self._accept_insecure_certificate

    def setAcceptInsecureCertificate(self, accept):
        self._accept_insecure_certificate = accept

    def host(self):
        """
        Host display to user
        """
        return self._host

    def port(self):
        """
        Port display to user
        """
        return self._port

    def setPort(self, port):
        self._port = port

    def protocol(self):
        """
        Transport protocol
        """
        return self._scheme

    def user(self):
        """
        User login display to GNS3 user
        """
        return self._user

    def progressCallbackDisable(self):
        """
        Disable the progress callback
        """
        HTTPClient._progress_callback.disable()

    def progressCallbackEnable(self):
        """
        Disable the progress callback
        """
        HTTPClient._progress_callback.enable()

    def notify_progress_start_query(self, query_id):
        """
        Called when a query start
        """
        if HTTPClient._progress_callback:
            if self._local:
                HTTPClient._progress_callback.add_query_signal.emit(query_id, "Waiting for local GNS3 server")
            else:
                HTTPClient._progress_callback.add_query_signal.emit(query_id, "Waiting for {}".format(self.url()))

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
        return getNetworkUrl(self.protocol(), self.host(), self.port(), self.user(), self.settings())

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
        log.info("Connection to %s closed", self.url())
        self._connected = False

    def isLocalServerRunning(self):
        """
        Check if a server is already running on this host.

        :returns: boolean
        """
        try:
            url = "{protocol}://{host}:{port}/v1/version".format(protocol=self._scheme, host=self._http_host, port=self._http_port)

            if self._user is not None:
                auth_handler = urllib.request.HTTPBasicAuthHandler()
                auth_handler.add_password(realm="GNS3 server",
                                          uri=url,
                                          user=self._user,
                                          passwd=self._password)
                opener = urllib.request.build_opener(auth_handler)
                urllib.request.install_opener(opener)

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
        except (OSError, urllib.error.HTTPError, http.client.BadStatusLine, ValueError) as e:
            log.debug("A non GNS3 server is already running on {}:{}: {}".format(self.host, self.port, e))
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

    def connect(self, query, callback):
        """
        Initialize the connection

        :param query: The query to execute when all network stack is ready
        :param callback: User callback when connection is finish
        """
        self.executeHTTPQuery("GET", "/version", query, {})

    def createHTTPQuery(self, method, path, callback, body={}, context={}, downloadProgressCallback=None, showProgress=True, ignoreErrors=False):
        """
        Call the remote server, if not connected, check connection before

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary or pathlib.Path)
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param downloadProgressCallback: Callback called when received something, it can be an incomplete response
        :param showProgress: Display progress to the user
        :param ignoreErrors: Ignore connection error (usefull to not closing a connection when notification feed is broken)
        :returns: QNetworkReply
        """

        if self._connected:
            return self.executeHTTPQuery(method, path, callback, body, context, downloadProgressCallback=downloadProgressCallback, showProgress=showProgress, ignoreErrors=ignoreErrors)
        else:
            log.info("Connection to {}".format(self.url()))
            query = partial(self._callbackConnect, method, path, callback, body, context, downloadProgressCallback=downloadProgressCallback, showProgress=showProgress, ignoreErrors=ignoreErrors)
            self.connect(query, callback)

    def _connectionError(self, callback, msg=""):
        """
        Return an error to user if connection failed

        :param callback: User callback
        :param msg: An optional additional message for the callback
        """

        if len(msg) > 0:
            msg = "Can't connect to server {}: {}".format(self.url(), msg)
        else:
            msg = "Can't connect to server {}".format(self.url())
        log.error(msg)
        if callback is not None:
            callback({"message": msg}, error=True, server=self)

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
            self._connectionError(callback)
            return

        if "version" not in params or "local" not in params:
            msg = "The remote server {} is not a GNS3 server".format(self.url())
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
            if self.isLocal():
                msg = "Running server is not a GNS3 local server (not started with --local)"
            else:
                msg = "Remote running server is started with --local. It is forbidden for security reasons"
            log.error(msg)
            if callback is not None:
                callback({"message": msg}, error=True, server=self)
            return

        self._connected = True
        self.executeHTTPQuery(method, path, callback, body, context=original_context)
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

    def addAuth(self, request):
        """
        If require add basic auth header
        """
        if self._user:
            auth_string = "{}:{}".format(self._user, self._password)
            auth_string = base64.b64encode(auth_string.encode("utf-8"))
            auth_string = "Basic {}".format(auth_string.decode())
            request.setRawHeader("Authorization", auth_string)
        return request

    def executeHTTPQuery(self, method, path, callback, body, context={}, downloadProgressCallback=None, showProgress=True, ignoreErrors=False):
        """
        Call the remote server

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary)
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param downloadProgressCallback: Callback called when received something, it can be an incomplete response
        :param showProgress: Display progress to the user
        :param ignoreErrors: Ignore connection error (usefull to not closing a connection when notification feed is broken)
        :returns: QNetworkReply
        """

        import copy
        context = copy.copy(context)
        query_id = str(uuid.uuid4())
        context["query_id"] = query_id
        if showProgress:
            self.notify_progress_start_query(context["query_id"])

        try:
            ip = self._http_host.rsplit('%', 1)[0]
            ipaddress.IPv6Address(ip)  # remove any scope ID
            # this is an IPv6 address, we must surround it with brackets to be used with QUrl.
            host = "[{}]".format(ip)
        except ipaddress.AddressValueError:
            host = self._http_host

        log.debug("{method} {protocol}://{host}:{port}/v1{path} {body}".format(method=method, protocol=self._scheme, host=host, port=self._http_port, path=path, body=body))
        url = QtCore.QUrl("{protocol}://{host}:{port}/v1{path}".format(protocol=self._scheme, host=host, port=self._http_port, path=path))
        request = self._request(url)

        request = self.addAuth(request)

        request.setRawHeader("Content-Type", "application/json")
        request.setRawHeader("Content-Length", str(len(body)))
        request.setRawHeader("User-Agent", "GNS3 QT Client v{version}".format(version=__version__))

        # By default QT doesn't support GET with body even if it's in the RFC that's why we need to use sendCustomRequest
        body = self._addBodyToRequest(body, request)

        response = self._network_manager.sendCustomRequest(request, method, body)

        if showProgress:
            response.uploadProgress.connect(partial(self.notify_progress_upload, query_id))
            response.downloadProgress.connect(partial(self.notify_progress_download, query_id))

        response.finished.connect(partial(self._processResponse, response, callback, context, body, ignoreErrors))
        if downloadProgressCallback is not None:
            response.downloadProgress.connect(partial(self._processDownloadProgress, response, downloadProgressCallback, context))
        return response

    def _processDownloadProgress(self, response, callback, context):
        """
        Process a packet receive on the notification feed.
        The feed can contains partial JSON. If we found a
        part of a JSON we keep it for the next packet
        """

        if response.error() == QtNetwork.QNetworkReply.NoError:
            content = bytes(response.readAll())
            content_type = response.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
            if content_type == "application/json":
                content = content.decode("utf-8")
                if context["query_id"] in self._buffer:
                    content = self._buffer[context["query_id"]] + content
                try:
                    while True:
                        content = content.lstrip(" \r\n\t")
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

    def _processResponse(self, response, callback, context, request_body, ignore_errors):

        if request_body is not None:
            request_body.close()

        status = None
        body = None

        if "query_id" in context:
            self.notify_progress_end_query(context["query_id"])

        if response.error() != QtNetwork.QNetworkReply.NoError:
            error_code = response.error()
            error_message = response.errorString()

            if not ignore_errors:
                log.info("Response error: %s (error: %d)", error_message, error_code)

            if error_code < 200:
                if not ignore_errors:
                    self.close()
                    callback({"message": error_message}, error=True, server=self, context=context)
                return
            else:
                status = response.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
                if status == 401:
                    print(error_message)

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

        server = self.settings()
        server["id"] = self._id
        server["local"] = self._local
        server["cloud"] = self._cloud
        if "user" in server and self._local:
            del server["user"]
        if server["protocol"] == "https":
            server["accept_insecure_certificate"] = self._accept_insecure_certificate
        return server

    def isCloud(self):
        return False
