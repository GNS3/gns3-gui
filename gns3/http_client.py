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

import sip
import json
import copy
import http
import uuid
import pathlib
import base64
import datetime
import ipaddress
import urllib.request

from .version import __version__, __version_info__
from .qt import QtCore, QtNetwork, qpartial, sip_is_deleted
from .utils import parse_version

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

    # How many times we need to retry a connection
    MAX_RETRY_CONNECTION = 5

    # Callback class used for displaying progress
    _progress_callback = None

    connection_connected_signal = QtCore.Signal()
    connection_disconnected_signal = QtCore.Signal()

    def __init__(self, settings, network_manager=None):

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
        # How many time we have retry connection
        self._retry = 0
        self._connected = False
        self._shutdown = False  # Shutdown in progress
        self._accept_insecure_certificate = settings.get("accept_insecure_certificate", None)

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
            HTTPClient._progress_callback.progress_signal.emit(query_id, sent, total)

    def _notify_progress_download(self, query_id, sent, total):
        """
        Called when a query download progress
        """
        if not sip_is_deleted(HTTPClient._progress_callback):
            # abs() for maxium because sometimes the system send negative
            # values
            HTTPClient._progress_callback.progress_signal.emit(query_id, sent, abs(total))

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
        :param params: Query arguments parameters
        :returns: QNetworkReply
        """

        if "dev" in __version__:
            assert QtCore.QThread.currentThread() == self.thread(), "HTTP request not started from the main thread"

        # Shutdown in progress do not execute the query
        if self._shutdown:
            return

        # We try to detect computer hibernation
        # if time between two query is too long we trigger a disconnect
        if self._max_time_difference_between_queries:
            now = datetime.datetime.now().timestamp()
            if self._last_query_timestamp is not None and now > self._last_query_timestamp + self._max_time_difference_between_queries:
                log.warning("Synchronisation lost with the server.")
                self.disconnect()
                self._last_query_timestamp = None
                return
            self._last_query_timestamp = now

        request = qpartial(self._executeHTTPQuery, method, path, qpartial(callback), body, context,
                           downloadProgressCallback=downloadProgressCallback,
                           showProgress=showProgress,
                           ignoreErrors=ignoreErrors,
                           progressText=progressText,
                           networkManager=networkManager,
                           server=server,
                           timeout=timeout,
                           prefix=prefix,
                           params=params)

        if self._connected:
            return request()
        else:
            self._query_waiting_connections.append((request, callback))
            # If we are not connected and we enqueue the first query we open the conection
            if len(self._query_waiting_connections) == 1:
                log.info("Connection to {}".format(self.url()))
                self._executeHTTPQuery("GET", "/version", self._callbackConnect, {}, server=server, timeout=5, showProgress=False)

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
                callback({"message": msg}, error=True, server=server)
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
            if self._retry < self.MAX_RETRY_CONNECTION:
                self._retryConnection(server=server)
                return
            for request, callback in self._query_waiting_connections:
                if callback is not None:
                    self._connectionError(callback)
            return

        if "version" not in params or "local" not in params:
            if self._retry < self.MAX_RETRY_CONNECTION:
                self._retryConnection(server=server)
                return
            msg = "The remote server {} is not a GNS3 server".format(self.url())
            log.error(msg)
            for request, callback in self._query_waiting_connections:
                if callback is not None:
                    callback({"message": msg}, error=True, server=server)
            self._query_waiting_connections = []
            return

        if params["version"].split("-")[0] != __version__.split("-")[0]:
            msg = "Client version {} differs with server version {}".format(__version__, params["version"])
            log.error(msg)
            # Stable release
            if __version_info__[3] == 0:
                for request, callback in self._query_waiting_connections:
                    if callback is not None:
                        callback({"message": msg}, error=True, server=server)
                return
            # We don't allow different major version to interact even with dev build
            elif parse_version(__version__)[:2] != parse_version(params["version"])[:2]:
                for request, callback in self._query_waiting_connections:
                    if callback is not None:
                        callback({"message": msg}, error=True, server=server)
                return
            log.warning("Use a different client and server version can create bugs. Use it at your own risk.")

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

    def _executeHTTPQuery(self, method, path, callback, body, context={}, downloadProgressCallback=None, showProgress=True, ignoreErrors=False, progressText=None, server=None, timeout=120, prefix="/v2", params={}, networkManager=None, **kwargs):
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
        :param params: Query arguments parameters
        :returns: QNetworkReply
        """

        try:
            ip = self._host.rsplit('%', 1)[0]
            ipaddress.IPv6Address(ip)  # remove any scope ID
            # this is an IPv6 address, we must surround it with brackets to be used with QUrl.
            host = "[{}]".format(ip)
        except ipaddress.AddressValueError:
            host = self._host

        if params == {}:
            query_string = ""
        else:
            query_string = "?" + urllib.parse.urlencode(params)

        log.debug("{method} {protocol}://{host}:{port}{prefix}{path} {body}{query_string}".format(method=method, protocol=self._protocol, host=host, port=self._port, path=path, body=body, prefix=prefix, query_string=query_string))
        if self._user:
            url = QtCore.QUrl("{protocol}://{user}@{host}:{port}{prefix}{path}{query_string}".format(protocol=self._protocol, user=self._user, host=host, port=self._port, path=path, prefix=prefix, query_string=query_string))
        else:
            url = QtCore.QUrl("{protocol}://{host}:{port}{prefix}{path}{query_string}".format(protocol=self._protocol, host=host, port=self._port, path=path, prefix=prefix, query_string=query_string))
        request = self._request(url)

        request = self._addAuth(request)

        request.setRawHeader(b"User-Agent", "GNS3 QT Client v{version}".format(version=__version__).encode())

        # By default QT doesn't support GET with body even if it's in the RFC that's why we need to use sendCustomRequest
        body = self._addBodyToRequest(body, request)

        if not networkManager:
            networkManager = self._network_manager

        response = networkManager.sendCustomRequest(request, method.encode(), body)

        context = copy.copy(context)
        context["query_id"] = str(uuid.uuid4())

        response.finished.connect(qpartial(self._processResponse, response, server, callback, context, body, ignoreErrors))
        response.error.connect(qpartial(self._processError, response, server, callback, context, body, ignoreErrors))

        if downloadProgressCallback is not None:
            response.readyRead.connect(qpartial(self._readyReadySlot, response, downloadProgressCallback, context, server))

        if not sip_is_deleted(HTTPClient._progress_callback) and HTTPClient._progress_callback.progress_dialog():
            request_canceled = qpartial(self._requestCanceled, response, context)
            HTTPClient._progress_callback.progress_dialog().canceled.connect(request_canceled)

        if showProgress:
            response.uploadProgress.connect(qpartial(self._notify_progress_upload, context["query_id"]))
            response.downloadProgress.connect(qpartial(self._notify_progress_download, context["query_id"]))
            # Should be the last operation otherwise we have race condition in Qt
            # where query start before finishing connect to everything
            self._notify_progress_start_query(context["query_id"], progressText, response)

        if timeout is not None:
            QtCore.QTimer.singleShot(timeout * 1000, qpartial(self._timeoutSlot, response))

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

    def _timeoutSlot(self, response):
        """
        Beware it's call for all request you need to check the status of the response
        """
        # We check if we received HTTP headers
        if not sip.isdeleted(response) and response.isRunning() and not len(response.rawHeaderList()) > 0:
            if not response.error() != QtNetwork.QNetworkReply.NoError:
                log.warn("Timeout request {}".format(response.url().toString()))
                response.abort()

    def disconnect(self):
        """
        Disconnect from the remote server
        """
        self.connection_disconnected_signal.emit()
        self.close()

    def _requestCanceled(self, response, context):

        if response.isRunning() and not response.error() != QtNetwork.QNetworkReply.NoError:
            log.warn("Aborting request for {}".format(response.url().toString()))
            response.abort()
        if "query_id" in context:
            self._notify_progress_end_query(context["query_id"])

    def _processError(self, response, server, callback, context, request_body, ignore_errors, error_code):
        if error_code != QtNetwork.QNetworkReply.NoError:
            error_message = response.errorString()

            if not ignore_errors:
                log.debug("Response error: %s for %s (error: %d)", error_message, response.url().toString(), error_code)

            if "query_id" in context:
                self._notify_progress_end_query(context["query_id"])

            if error_code < 200 or error_code == 403:
                if error_code == QtNetwork.QNetworkReply.OperationCanceledError:  # It's legit to cancel do not disconnect
                    error_message = "Operation timeout"  # It's more clear than cancel, because cancel is trigger by us when we timeout
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
                    log.debug(body)
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
            log.debug(body)
            if body and len(body.strip(" \n\t")) > 0 and content_type == "application/json":
                try:
                    params = json.loads(body)
                except ValueError:  # Partial JSON
                    raise HttpBadRequest(body)
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

    def getSynchronous(self, endpoint, timeout=2):
        """
        Synchronous check if a server is running

        :returns: Tuple (Status code, json of anwser). Status 0 is a non HTTP error
        """
        try:
            url = "{protocol}://{host}:{port}/v2/{endpoint}".format(protocol=self._protocol, host=self._host, port=self._port, endpoint=endpoint)

            if self._user is not None and len(self._user) > 0:
                log.debug("Synchronous get {} with user '{}'".format(url, self._user))
                auth_handler = urllib.request.HTTPBasicAuthHandler()
                auth_handler.add_password(realm="GNS3 server",
                                          uri=url,
                                          user=self._user,
                                          passwd=self._password)
                opener = urllib.request.build_opener(auth_handler)
                urllib.request.install_opener(opener)
            else:
                log.debug("Synchronous get {} (no authentication)".format(url))
            response = urllib.request.urlopen(url, timeout=timeout)
            content_type = response.getheader("CONTENT-TYPE")
            if response.status == 200:
                if content_type == "application/json":
                    content = response.read()
                    json_data = json.loads(content.decode("utf-8"))
                    return response.status, json_data
            else:
                return response.status, None
        except http.client.InvalidURL as e:
            log.warn("Invalid local server url: {}".format(e))
            return 0, None
        except urllib.error.URLError:
            # Connection refused. It's a normal behavior if server is not started
            return 0, None
        except urllib.error.HTTPError as e:
            log.debug("Error during get on {}:{}: {}".format(self.host(), self.port(), e))
            return e.code, None
        except (OSError, http.client.BadStatusLine, ValueError) as e:
            log.debug("Error during get on {}:{}: {}".format(self.host(), self.port(), e))
        return 0, None
