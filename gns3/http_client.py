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

from .qt import sip
import json
import copy
import uuid
import pathlib
import base64
import ipaddress
import urllib.request
import urllib.parse

from .version import __version__, __version_info__
from .qt import QtCore, QtNetwork, QtWidgets, qpartial, sip_is_deleted
from .utils import parse_version

import logging
log = logging.getLogger(__name__)


class HttpBadRequest(Exception):

    """We raise bad request exception for logging them in Sentry"""
    pass


class HTTPClient(QtCore.QObject):

    """
    HTTP client.

    :param settings: Dictionary with connection information to the server
    :param network_manager: A QT network manager
    """

    # Callback class used for displaying progress
    _progress_callback = None

    connection_connected_signal = QtCore.Signal()
    connection_disconnected_signal = QtCore.Signal()

    def __init__(self, settings, network_manager=None, max_retry_connection=5):
        super().__init__()

        self._protocol = settings.get("protocol", "http")
        self._host = settings["host"]
        try:
            if self._host is None or self._host == "0.0.0.0":
                self._host = "127.0.0.1"
            elif ":" in self._host and ipaddress.IPv6Address(self._host) and str(ipaddress.IPv6Address(self._host)) == "::":
                self._host = "::1"
        except ipaddress.AddressValueError:
            log.error("Invalid host name %s", self._host)
        self._port = int(settings["port"])
        self._user = settings.get("user", None)
        self._password = settings.get("password", None)
        # How many time we have already retried connection
        self._retry = 0
        self._max_retry_connection = max_retry_connection
        self._connected = False
        self._shutdown = False  # Shutdown in progress
        self._accept_insecure_certificate = settings.get("accept_insecure_certificate", None)

        # Add custom CA
        # ssl_config = QtNetwork.QSslConfiguration.defaultConfiguration()
        # if ssl_config.addCaCertificates("/path/to/rootCA.crt"):
        #     log.debug("CA certificate added")
        # QtNetwork.QSslConfiguration.setDefaultConfiguration(ssl_config)

        if self._protocol == "https":
            if not QtNetwork.QSslSocket.supportsSsl():
                log.error("SSL is not supported")
            else:
                log.debug(f"SSL is supported, version: {QtNetwork.QSslSocket().sslLibraryBuildVersionString()}")

        # In order to detect computer hibernation we detect the date of the last
        # query and disconnect if time is too long between two query
        self._last_query_timestamp = None
        self._max_time_difference_between_queries = None
        if network_manager:
            self._network_manager = network_manager
        else:
            self._network_manager = QtNetwork.QNetworkAccessManager()
        # A buffer used by progress download
        self._buffer = {}

        # List of query waiting for the connection
        self._query_waiting_connections = []

        # To catch SSL errors
        self._network_manager.sslErrors.connect(self._sslErrorsSlot)

        # Store SSL error exceptions
        self._ssl_exceptions = {}

    def setMaxTimeDifferenceBetweenQueries(self, value):
        self._max_time_difference_between_queries = value

    def host(self):
        """
        Host display to user
        """
        return self._host

    def setHost(self, host):
        self._host = host

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
        return self._protocol

    def setAcceptInsecureCertificate(self, certificate):
        """
        Does the server accept this insecure SSL certificate digest

        :param: Certificate digest
        """
        self._accept_insecure_certificate = certificate

    def user(self):
        """
        User login display to GNS3 user
        """
        return self._user

    def url(self):
        """Returns current server url"""

        if ":" in self.host():
            return "{}://[{}]:{}".format(self.protocol(), self.host(), self.port())
        return "{}://{}:{}".format(self.protocol(), self.host(), self.port())

    def fullUrl(self):
        """Returns current server url including user and password"""
        host = self.host()
        if ":" in self.host():
            host = "[{}]".format(host)

        if self._user:
            return "{}://{}:{}@{}:{}".format(self.protocol(), self._user, self._password, host, self.port())
        else:
            return "{}://{}:{}".format(self.protocol(), host, self.port())

    def password(self):
        return self._password

    def setPassword(self, password):
        self._password = password

    def shutdown(self):
        """
        Stop the server and stop to accept queries
        """
        self.createHTTPQuery("POST", "/shutdown", None, showProgress=False)
        self._shutdown = True

    def getNetworkManager(self):
        """
        :return: instance of NetworkManager
        """
        return self._network_manager

    def setMaxRetryConnection(self, retries):
        """
        Sets how many times we need to retry a connection
        :param retries: integer
        """
        self._max_retry_connection = retries

    def getMaxRetryConnection(self):
        """
        Returns how many times we need to retry a connection
        """
        return self._max_retry_connection

    def _notify_progress_start_query(self, query_id, progress_text, response):
        """
        Called when a query start
        """
        if not sip_is_deleted(HTTPClient._progress_callback):
            if progress_text:
                HTTPClient._progress_callback.add_query_signal.emit(query_id, progress_text, response)
            else:
                HTTPClient._progress_callback.add_query_signal.emit(query_id, "Waiting for {}".format(self.url()), response)

    def _notify_progress_end_query(cls, query_id):
        """
        Called when a query is over
        """

        if not sip_is_deleted(HTTPClient._progress_callback):
            HTTPClient._progress_callback.remove_query_signal.emit(query_id)

    def _notify_progress_upload(self, query_id, sent, total):
        """
        Called when a query upload progress
        """
        if not sip_is_deleted(HTTPClient._progress_callback):
            HTTPClient._progress_callback.progress_signal.emit(query_id, str(abs(sent)), str(abs(total)))

    def _notify_progress_download(self, query_id, sent, total):
        """
        Called when a query download progress
        """
        if not sip_is_deleted(HTTPClient._progress_callback):
            # abs() for maximum because sometimes the system send negative
            # values
            HTTPClient._progress_callback.progress_signal.emit(query_id, str(abs(sent)), str(abs(total)))

    @classmethod
    def setProgressCallback(cls, progress_callback):
        """
        :param progress_callback: A progress callback instance
        """

        cls._progress_callback = progress_callback

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
        self._progress_callback.reset()

    def _request(self, url):
        """
        Get a QNetworkRequest object. You can mock this
        if you want low level mocking.

        :param url: Url of remote ressource (QtCore.QUrl)
        :returns: QT Network request (QtNetwork.QNetworkRequest)
        """

        return QtNetwork.QNetworkRequest(url)

    def _connect(self, query, server):
        """
        Initialize the connection

        :param query: The query to execute when all network stack is ready
        :param query: The Server to connect
        """

    def createHTTPQuery(self, method, path, callback, body={}, context={},
                        downloadProgressCallback=None,
                        showProgress=True,
                        ignoreErrors=False,
                        progressText=None,
                        timeout=120,
                        server=None,
                        prefix="/v2",
                        params={},
                        networkManager=None,
                        eventsHandler=None,
                        **kwargs):
        """
        Call the remote server, if not connected, check connection before

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary or pathlib.Path)
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param downloadProgressCallback: Callback called when received something, it can be an incomplete response
        :param showProgress: Display progress to the user
        :param progressText: Text display to user in the progress dialog. None for auto generated
        :param ignoreErrors: Ignore connection error (usefull to not closing a connection when notification feed is broken)
        :param server: The server where the query will run
        :param timeout: Delay in seconds before raising a timeout
        :param prefix: Prefix to the path
        :param networkManager: QNetworkAccessManager None use the default
        :param eventsHandler: Handler receiving and triggering events like `updated`, `cancelled`.
                              If not specified and showProgress is `True` then `ProgressDialog` receives them.
        :param params: Query arguments parameters
        :returns: QNetworkReply
        """

        if "dev" in __version__:
            assert QtCore.QThread.currentThread() == self.thread(), "HTTP request not started from the main thread"

        # Shutdown in progress do not execute the query
        if self._shutdown:
            return

        # TODO: clean this
        # We try to detect computer hibernation
        # if time between two query is too long we trigger a disconnect
        # if self._max_time_difference_between_queries:
        #     now = datetime.datetime.now().timestamp()
        #     if self._last_query_timestamp is not None and now > self._last_query_timestamp + self._max_time_difference_between_queries:
        #         log.warning("Synchronisation lost with the server.")
        #         self.disconnect()
        #         self._last_query_timestamp = None
        #         return
        #     self._last_query_timestamp = now

        request = qpartial(self._executeHTTPQuery, method, path, qpartial(callback), body, context,
                           downloadProgressCallback=downloadProgressCallback,
                           showProgress=showProgress,
                           ignoreErrors=ignoreErrors,
                           progressText=progressText,
                           networkManager=networkManager,
                           server=server,
                           timeout=timeout,
                           prefix=prefix,
                           eventsHandler=eventsHandler,
                           params=params)

        if self._connected:
            return request()
        else:
            self._query_waiting_connections.append((request, callback))
            # enqueue the first query and open the connection if we are not connected
            if len(self._query_waiting_connections) == 1:
                log.debug("Connection to {}".format(self.url()))
                self._executeHTTPQuery("GET", "/version", self._callbackConnect, {}, server=server, timeout=10, showProgress=False)

    def _connectionError(self, callback, msg="", server=None):
        """
        Return an error to user if connection failed

        :param callback: User callback
        :param msg: An optional additional message for the callback
        :param server: Server where the query is execute
        """

        if len(msg) > 0:
            msg = "Cannot connect to server {}: {}".format(self.url(), msg)
        else:
            msg = "Cannot connect to {}. Please check if GNS3 is allowed in your antivirus and firewall. And that server version is {}.".format(self.url(), __version__)
        for request, callback in self._query_waiting_connections:
            if callback is not None:
                callback({"message": msg}, error=True, server=server, connection_error=True)
        self._query_waiting_connections = []

    def _retryConnection(self, server=None):
        log.debug("Retry connection to {}".format(self.url()))
        self._retry += 1
        QtCore.QTimer.singleShot(1000, qpartial(self._executeHTTPQuery, "GET", "/version", self._callbackConnect, {}, server=server, timeout=5))

    def _callbackConnect(self, params, error=False, server=None, **kwargs):
        """
        Callback after /version response. Continue execution of query

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary or pathlib.Path)
        :param original_context: Original context
        :param callback: callback method to call when the server replies
        """

        if error is not False:
            if self._retry < self.getMaxRetryConnection():
                self._retryConnection(server=server)
                return
            for request, callback in self._query_waiting_connections:
                if callback is not None:
                    self._connectionError(callback)
            return

        if "version" not in params or "local" not in params:
            if self._retry < self.getMaxRetryConnection():
                self._retryConnection(server=server)
                return
            msg = "The remote server {} is not a GNS3 server".format(self.url())
            log.error(msg)
            for request, callback in self._query_waiting_connections:
                if callback is not None:
                    callback({"message": msg}, error=True, server=server)
            self._query_waiting_connections = []
            return

        if params["version"].split("+")[0] != __version__.split("+")[0]:
            msg = "Client version {} is not the same as server (controller) version {}".format(__version__, params["version"])
            # We don't allow different versions to interact even with dev build
            # (excepting post release corrections e.g 2.2.32.1, occassionally done when fixing a packaging problem)
            # TODO: we should probably follow this standard starting with v3.0: https://semver.org/
            if parse_version(__version__)[:3] != parse_version(params["version"])[:3]:
                log.error(msg)
                for request, callback in self._query_waiting_connections:
                    if callback is not None:
                        callback({"message": msg}, error=True, server=server)
                return
            log.warning("{}\nUsing different versions may result in unexpected problems. Please upgrade or use at your own risk.".format(msg))

        self._connected = True
        self._retry = 0
        self.connection_connected_signal.emit()
        for request, callback in self._query_waiting_connections:
            if request:
                request()
        self._query_waiting_connections = []

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
            request.setRawHeader(b"Content-Type", b"application/json")
            request.setRawHeader(b"Content-Length", str(len(body)).encode())
            data = QtCore.QByteArray(body.encode())
            body = QtCore.QBuffer(self)
            body.setData(data)
            body.open(QtCore.QIODevice.ReadOnly)
            return body
        elif isinstance(body, pathlib.Path):
            body = QtCore.QFile(str(body), self)
            body.open(QtCore.QFile.ReadOnly)
            request.setRawHeader(b"Content-Type", b"application/octet-stream")
            # QT is smart and will compute the Content-Lenght for us
            return body
        elif isinstance(body, str):
            request.setRawHeader(b"Content-Type", b"application/octet-stream")
            data = QtCore.QByteArray(body.encode())
            body = QtCore.QBuffer(self)
            body.setData(data)
            body.open(QtCore.QIODevice.ReadOnly)
            return body
        else:
            return None

    def _addAuth(self, request):
        """
        If require add basic auth header
        """
        if self._user:
            auth_string = "{}:{}".format(self._user, self._password)
            auth_string = base64.b64encode(auth_string.encode("utf-8"))
            auth_string = "Basic {}".format(auth_string.decode())
            request.setRawHeader(b"Authorization", auth_string.encode())
        return request

    def connectWebSocket(self, websocket, path, prefix="/v2"):
        """
        Path of the websocket endpoint
        """
        host = self._getHostForQuery()
        request = websocket.request()
        ws_protocol = "ws"
        if self._protocol == "https":
            ws_protocol = "wss"
        ws_url = "{protocol}://{host}:{port}{prefix}{path}".format(protocol=ws_protocol,
                                                                   host=host,
                                                                   port=self._port,
                                                                   path=path,
                                                                   prefix=prefix)
        log.debug("Connecting to WebSocket endpoint: {}".format(ws_url))
        request.setUrl(QtCore.QUrl(ws_url))
        self._addAuth(request)
        websocket.open(request)
        return websocket

    def _getHostForQuery(self):
        """
        Get hostname that could be use by Qt
        """
        try:
            ip = self._host.rsplit('%', 1)[0]
            ipaddress.IPv6Address(ip)  # remove any scope ID
            # this is an IPv6 address, we must surround it with brackets to be used with QUrl.
            host = "[{}]".format(ip)
        except ipaddress.AddressValueError:
            host = self._host
        return host

    def _paramsToQueryString(self, params):
        """
        :param params: Dictionary of query string parameters
        :returns: String of the query string
        """
        if params == {}:
            query_string = ""
        else:
            query_string = "?"
            params = params.copy()
            for key, value in params.copy().items():
                if value is None:
                    del params[key]
            query_string += urllib.parse.urlencode(params)
        return query_string

    def _executeHTTPQuery(self, method, path, callback, body, context={}, downloadProgressCallback=None, showProgress=True, ignoreErrors=False, progressText=None, server=None, timeout=120, prefix="/v2", params={}, networkManager=None, eventsHandler=None, **kwargs):
        """
        Call the remote server

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary)
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param downloadProgressCallback: Callback called when received something, it can be an incomplete response
        :param showProgress: Display progress to the user
        :param networkManager: The network manager to use. If None use default
        :param progressText: Text display to user in progress dialog. None for auto generated
        :param ignoreErrors: Ignore connection error (usefull to not closing a connection when notification feed is broken)
        :param server: The server where the query is executed
        :param timeout: Delay in seconds before raising a timeout
        :param eventsHandler: Handler receiving and triggering events like `updated`, `cancelled`.
                      If not specified and showProgress is `True` then `ProgressDialog` receives them.
        :param params: Query arguments parameters
        :returns: QNetworkReply
        """

        host = self._getHostForQuery()
        query_string = self._paramsToQueryString(params)

        log.debug("{method} {protocol}://{host}:{port}{prefix}{path} {body}{query_string}".format(method=method, protocol=self._protocol, host=host, port=self._port, path=path, body=body, prefix=prefix, query_string=query_string))
        url = QtCore.QUrl("{protocol}://{host}:{port}{prefix}{path}{query_string}".format(protocol=self._protocol, host=host, port=self._port, path=path, prefix=prefix, query_string=query_string))

        if self._user:
            url.setUserName(self._user)

        request = self._request(url)
        request = self._addAuth(request)
        request.setRawHeader(b"User-Agent", "GNS3 QT Client v{version}".format(version=__version__).encode())

        # By default QT doesn't support GET with body even if it's in the RFC that's why we need to use sendCustomRequest
        body = self._addBodyToRequest(body, request)

        if not networkManager:
            networkManager = self._network_manager

        try:
            response = networkManager.sendCustomRequest(request, method.encode(), body)
        except SystemError as e:
            log.error("Can't send query: {}".format(str(e)))
            return

        context = copy.copy(context)
        context["query_id"] = str(uuid.uuid4())

        response.finished.connect(qpartial(self._processResponse, response, server, callback, context, body, ignoreErrors))
        response.error.connect(qpartial(self._processError, response, server, callback, context, body, ignoreErrors))

        if downloadProgressCallback is not None:
            response.readyRead.connect(qpartial(self._readyReadySlot, response, downloadProgressCallback, context, server))

        request_canceled = qpartial(self._requestCanceled, response, context)

        if eventsHandler is not None:
            eventsHandler.canceled.connect(request_canceled)
        elif not sip_is_deleted(HTTPClient._progress_callback) and HTTPClient._progress_callback.progress_dialog():
            HTTPClient._progress_callback.progress_dialog().canceled.connect(request_canceled)

        if showProgress:
            response.uploadProgress.connect(qpartial(self._notify_progress_upload, context["query_id"]))
            response.downloadProgress.connect(qpartial(self._notify_progress_download, context["query_id"]))
            # Should be the last operation otherwise we have race condition in Qt
            # where query start before finishing connect to everything
            self._notify_progress_start_query(context["query_id"], progressText, response)

        if timeout is not None:
            QtCore.QTimer.singleShot(timeout * 1000, qpartial(self._timeoutSlot, response, timeout))

        return response

    def _readyReadySlot(self, response, callback, context, server, *args):
        """
        Process a packet receive on the notification feed.
        The feed can contains qpartial JSON. If we found a
        part of a JSON we keep it for the next packet
        """
        if response.error() != QtNetwork.QNetworkReply.NoError:
            return

        # HTTP error
        status = response.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
        if status >= 300:
            return

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
                    callback(answer, server=server, context=context)
                    content = content[index:]
            except ValueError:  # Partial JSON
                self._buffer[context["query_id"]] = content
        else:
            callback(content, server=server, context=context)

    def _timeoutSlot(self, response, timeout):
        """
        Beware it's call for all request you need to check the status of the response
        """
        # We check if we received HTTP headers
        if not sip.isdeleted(response) and response.isRunning() and not len(response.rawHeaderList()) > 0:
            if not response.error() != QtNetwork.QNetworkReply.NoError:
                log.warning("Timeout after {} seconds for request {}. Please check the connection is not blocked by a firewall or an anti-virus.".format(timeout, response.url().toString()))
                response.abort()

    def disconnect(self):
        """
        Disconnect from the remote server
        """
        self.connection_disconnected_signal.emit()
        self.close()

    def _requestCanceled(self, response, context):

        if response.isRunning() and not response.error() != QtNetwork.QNetworkReply.NoError:
            log.warning("Aborting request for {}".format(response.url().toString()))
            response.abort()
        if "query_id" in context:
            self._notify_progress_end_query(context["query_id"])

    def _processError(self, response, server, callback, context, request_body, ignore_errors, error_code):
        if error_code != QtNetwork.QNetworkReply.NoError:
            error_message = "{} ({}:{})".format(response.errorString(), self._host, self._port)

            if not ignore_errors:
                log.debug("Response error: %s for %s (error: %d)", error_message, response.url().toString(), error_code)

            if "query_id" in context:
                self._notify_progress_end_query(context["query_id"])

            if error_code < 200 or error_code == 403:
                if error_code == QtNetwork.QNetworkReply.OperationCanceledError:  # It's legit to cancel do not disconnect
                    error_message = "Operation timeout"  # It's clearer than cancel because cancel is triggered by us when we timeout
                elif error_code == QtNetwork.QNetworkReply.NetworkSessionFailedError:
                    # ignore the network session failed error to let the network manager recover from it
                    return
                elif not ignore_errors:
                    self.disconnect()
                if callback is not None:
                    callback({"message": error_message}, error=True, server=server, context=context)
                return
            else:
                status = response.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
                if status == 401:
                    log.error(error_message)

            try:
                body = bytes(response.readAll()).decode("utf-8").strip("\0")
                # Some time antivirus intercept our query and reply with garbage content
            except UnicodeError:
                body = None
            content_type = response.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
            if callback is not None:
                if not body or content_type != "application/json":
                    callback({"message": error_message}, error=True, server=server, context=context)
                else:
                    # log.debug(body)
                    try:
                        callback(json.loads(body), error=True, server=server, context=context)
                    except ValueError:
                        # It happens when an antivirus catch the communication and send is error page without changing the Content Type
                        callback({"message": error_message}, error=True, server=server, context=context)
            else:
                # Because nothing is configured to handle the error we display it to the user
                try:
                    log.error(json.loads(body)["message"])
                except (ValueError, KeyError):
                    log.error(error_message)

    def _processResponse(self, response, server, callback, context, request_body, ignore_errors):
        if request_body is not None:
            request_body.close()

        if "query_id" in context:
            self._notify_progress_end_query(context["query_id"])

        if response.error() == QtNetwork.QNetworkReply.NoError:
            status = response.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
            log.debug("Decoding response from {} response {}".format(response.url().toString(), status))
            try:
                raw_body = bytes(response.readAll())
                body = raw_body.decode("utf-8").strip("\0")
            # Some time anti-virus intercept our query and reply with garbage content
            except UnicodeDecodeError:
                body = None
            content_type = response.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
            if body and len(body.strip(" \n\t")) > 0 and content_type == "application/json":
                try:
                    params = json.loads(body)
                except ValueError:  # Partial JSON
                    params = {}
                    status = 504
            else:
                params = {}
            if callback is not None:
                if status >= 400:
                    callback(params, error=True, server=server, context=context)
                else:
                    callback(params, server=server, context=context, raw_body=raw_body)
            if status == 400:
                try:
                    params = json.loads(body)
                    e = HttpBadRequest(body)
                    e.fingerprint = params["path"]
                # If something goes wrong for a any reason just raise the bad request
                except Exception:
                    e = HttpBadRequest(body)
                raise e

    def getSynchronous(self, method, endpoint, prefix="/v2", timeout=5):
        """
        Synchronous check if a server is running

        :returns: Tuple (Status code, json of answer). Status 0 is a non HTTP error
        """

        host = self._getHostForQuery()

        log.debug("{method} {protocol}://{host}:{port}{prefix}{endpoint}".format(method=method, protocol=self._protocol, host=host, port=self._port, prefix=prefix, endpoint=endpoint))
        url = QtCore.QUrl("{protocol}://{host}:{port}{prefix}{endpoint}".format(protocol=self._protocol, host=host, port=self._port, prefix=prefix, endpoint=endpoint))

        if self._user:
            url.setUserName(self._user)

        request = self._request(url)
        request = self._addAuth(request)
        request.setRawHeader(b"User-Agent", "GNS3 QT Client v{version}".format(version=__version__).encode())

        try:
            response = self._network_manager.sendCustomRequest(request, method.encode())
        except SystemError as e:
            log.error("Can't send query: {}".format(str(e)))
            return

        loop = QtCore.QEventLoop()
        response.finished.connect(loop.quit)

        if timeout is not None:
            QtCore.QTimer.singleShot(timeout * 1000, qpartial(self._timeoutSlot, response, timeout))

        if not loop.isRunning():
            loop.exec_()

        status = response.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
        if response.error() != QtNetwork.QNetworkReply.NoError:
            log.debug("Error while connecting to local server {}".format(response.errorString()))
        else:
            content_type = response.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
            if status == 200 and content_type == "application/json":
                content = bytes(response.readAll())
                try:
                    json_data = json.loads(content.decode("utf-8"))
                except (UnicodeEncodeError, ValueError) as e:
                    log.warning("Could not read JSON data returned from {}: {}".format(url, e))
                else:
                    return status, json_data
        return status, None

    def _sslErrorsSlot(self, response, ssl_errors):

        self.handleSslError(response, ssl_errors)

    def handleSslError(self, response, ssl_errors):

        if self._accept_insecure_certificate:
            response.ignoreSslErrors()
            return

        url = response.request().url()
        host_port_key = f"{url.host()}:{url.port()}"

        # get the certificate digest
        ssl_config = response.sslConfiguration()
        peer_cert = ssl_config.peerCertificate()
        digest = peer_cert.digest()

        if host_port_key in self._ssl_exceptions:

            if self._ssl_exceptions[host_port_key] == digest:
                response.ignoreSslErrors()
                return

        from gns3.main_window import MainWindow
        main_window = MainWindow.instance()

        msgbox = QtWidgets.QMessageBox(main_window)
        msgbox.setWindowTitle("SSL error detected")
        msgbox.setText(f"This server could not prove that it is {url.host()}:{url.port()}. Please carefully examine the certificate to make sure the server can be trusted.")
        msgbox.setInformativeText(f"{ssl_errors[0].errorString()}")
        msgbox.setDetailedText(peer_cert.toText())
        msgbox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        connect_button = QtWidgets.QPushButton(f"&Connect to {url.host()}:{url.port()}", msgbox)
        msgbox.addButton(connect_button, QtWidgets.QMessageBox.YesRole)
        abort_button = QtWidgets.QPushButton("&Abort", msgbox)
        msgbox.addButton(abort_button, QtWidgets.QMessageBox.RejectRole)
        msgbox.setDefaultButton(abort_button)
        msgbox.setIcon(QtWidgets.QMessageBox.Critical)
        msgbox.exec_()

        if msgbox.clickedButton() == connect_button:
            self._ssl_exceptions[host_port_key] = digest
            response.ignoreSslErrors()
        else:
            for error in ssl_errors:
                log.error(f"SSL error detected: {error.errorString()}")
            main_window.close()

    @classmethod
    def fromUrl(cls, url, network_manager=None, base_settings=None):
        """
        Returns HttpClient instance based on the url
        :param url: Url to parse
        :param network_manager: Optional network_manager
        :param base_settings: Source of the settings, if necessary
        :return: HttpClient
        """
        settings = {}
        if base_settings is not None:
            settings.update(**base_settings)
        parse_results = urllib.parse.urlparse(url)
        settings['protocol'] = parse_results.scheme
        settings['host'] = parse_results.hostname
        settings['port'] = parse_results.port
        settings['user'] = parse_results.username
        settings['password'] = parse_results.password
        return cls(settings, network_manager)
