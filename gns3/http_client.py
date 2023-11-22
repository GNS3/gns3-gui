# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 GNS3 Technologies Inc.
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
import pathlib
import ipaddress
import urllib.request
import urllib.parse
import copy
import uuid

from typing import List, Union, Callable, Optional
from .qt import sip
from .version import __version__, __version_info__
from .qt import QtCore, QtNetwork, QtWidgets, QtWebSockets, qpartial
from .utils import parse_version
from .dialogs.login_dialog import LoginDialog

from .http_client_error import (
    HttpClientError,
    HttpClientCancelledRequestError,
    HttpClientBadRequestError,
    HttpClientUnauthorizedError,
    HttpClientTimeoutError
)

import logging
log = logging.getLogger(__name__)


class QNetworkReplyWatcher(QtCore.QObject):
    """
    Synchronously wait for a QNetworkReply to be completed
    """

    def __init__(
            self,
            show_progress: bool = True,
            progress_text: str = None,
            parent: QtWidgets.QWidget = None
    ):

        if not parent:
            from gns3.main_window import MainWindow
            parent = MainWindow.instance()

        super().__init__(parent)

        if show_progress:
            if not progress_text:
                progress_text = "Waiting for controller..."
            self._progress = QtWidgets.QProgressDialog(progress_text, "Cancel", 0, 0, parent)
            self._progress.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
            self._progress.setWindowModality(QtCore.Qt.ApplicationModal)
        else:
            self._progress = None

    def _updateProgress(self, bytes_sent: int, bytes_total: int) -> None:
        """
        Update upload or download progress.
        """

        if bytes_total > 0:
            pass
            # FIXME the code below makes the progress bar to be stuck sometimes
            # if not self._progress.maximum():
            #     self._progress.setMaximum(100)
            # self._progress.setValue(int(100 * bytes_sent / bytes_total))

    def waitForReply(self, reply: QtNetwork.QNetworkReply, uploading: bool = False, timeout=60) -> None:
        """
        Wait for the QNetworkReply to be complete or for the timeout

        :param reply: QNetworkReply instance
        :param uploading: Whether the reply is uploading or not
        :param timeout: Number of seconds before timeout
        """

        loop = QtCore.QEventLoop()

        if timeout:
            timer = QtCore.QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: loop.exit(1))
            timer.start(timeout * 1000)

        reply.finished.connect(loop.quit)

        if self._progress:
            reply.finished.connect(self._progress.close)
            if uploading:
                reply.uploadProgress.connect(self._updateProgress)
            else:
                reply.downloadProgress.connect(self._updateProgress)
            self._progress.canceled.connect(reply.abort)
            self._progress.show()

        if not loop.isRunning():
            if loop.exec_() == 1:
                raise HttpClientTimeoutError(
                    f"Request to '{reply.url().toString()}' timed out after {timeout} seconds")

        if timeout and timer.isActive():
            timer.stop()


class HTTPClient(QtCore.QObject):
    """
    HTTP client to communicate with the controller REST API

    :param settings: Dictionary with connection information to the server
    :param max_retry_connection: Number of time to try to connect to the server
    :param prefix: API version (prefix)
    """

    connected_signal = QtCore.Signal()
    disconnected_signal = QtCore.Signal()

    def __init__(self, settings: dict, max_retry_connection: int = 5, prefix: str = "/v3"):

        super().__init__()
        from gns3.main_window import MainWindow
        self._main_window = MainWindow.instance()

        self._protocol = settings.get("protocol", "http")
        self._host = settings["host"]
        self._prefix = prefix
        self._auth_attempted = False
        self._jwt_token = None
        try:
            if self._host is None or self._host == "0.0.0.0":
                self._host = "127.0.0.1"
            elif ":" in self._host and ipaddress.IPv6Address(self._host) and str(ipaddress.IPv6Address(self._host)) == "::":
                self._host = "::1"
        except ipaddress.AddressValueError:
            log.error("Invalid host name %s", self._host)

        self._port = int(settings["port"])
        self._username = settings.get("username")
        self._password = settings.get("password")
        self._retry = 0  # how many times we have already retried connection
        self._max_retry_connection = max_retry_connection
        self._retry_connection = False
        self._connected = False
        self._shutdown = False  # shutdown in progress
        self._accept_insecure_certificate = settings.get("accept_insecure_certificate", False)

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

        self._network_manager = QtNetwork.QNetworkAccessManager()

        # Allow to follow redirections
        #self._network_manager.setRedirectPolicy(QtNetwork.QNetworkRequest.SameOriginRedirectPolicy)

        # Buffer for JSON notifications
        self._buffer = {}

        # List of query waiting for the connection
        self._query_waiting_connections = []

        # To catch SSL errors
        self._network_manager.sslErrors.connect(self.handleSslError)

        # Store SSL error exceptions
        self._ssl_exceptions = {}

    def host(self) -> str:
        """
        Return the server IP or hostname
        """

        return self._host

    def setHost(self, host: str) -> None:
        """
        Set the server IP or hostname
        """

        self._host = host

    def port(self) -> int:
        """
        Return the server port
        """

        return self._port

    def setPort(self, port: int) -> None:
        """
        Set the server port
        """

        self._port = port

    def protocol(self) -> str:
        """
        Return the transport protocol (HTTP, HTTPS)
        """

        return self._protocol

    def setAcceptInsecureCertificate(self, certificate: bool) -> None:
        """
        Does the server accept this insecure SSL certificate digest
        """

        self._accept_insecure_certificate = certificate

    def url(self) -> str:
        """
        Returns current server url
        """

        if ":" in self.host():
            return "{}://[{}]:{}".format(self.protocol(), self.host(), self.port())
        return "{}://{}:{}".format(self.protocol(), self.host(), self.port())

    def fullUrl(self) -> str:
        """
        Returns current server URL
        """

        host = self.host()
        if ":" in self.host():
            host = "[{}]".format(host)

        return "{}://{}:{}".format(self.protocol(), host, self.port())

    def shutdown(self) -> None:
        """
        Stop the server and stop to accept queries
        """

        self._shutdown = True
        self.sendRequest("POST", "/shutdown", callback=None, wait=False)

    def connected(self) -> bool:
        """
        Return whether the client is connected or not
        """

        return self._connected

    def close(self) -> None:
        """
        Closes the connection with the server
        """

        self._connected = False

    def _request(self, url: str) -> QtNetwork.QNetworkRequest:
        """
        Return a QNetworkRequest object. You can mock this
        if you want low level mocking.

        :param url: URL for the request
        :returns: QtNetwork.QNetworkRequest instance
        """

        return QtNetwork.QNetworkRequest(QtCore.QUrl(url))

    def sendRequest(
            self,
            method: str,
            endpoint: str,
            callback: Callable = None,
            body: Union[dict, pathlib.Path, str] = None,
            context: dict = None,
            download_progress_callback: Callable = None,
            show_progress: bool = True,
            progress_text: str = None,
            disconnect_on_error: bool = False,
            timeout: int = 120,
            params: dict = None,
            raw: bool = False,
            wait: bool = False
    ) -> Optional[Union[str, bytes]]:
        """
        Send a request to the server

        :param method: HTTP method
        :param endpoint: API endpoint
        :param callback: callback method to call when the server replies
        :param body: Body to send (dictionary, string or pathlib.Path)
        :param context: Pass a context to the response callback
        :param download_progress_callback: Callback called when received something, it can be an incomplete reply
        :param show_progress: Display a progress bar dialog
        :param progress_text: Custom text to display in the progress bar dialog
        :param disconnect_on_error: Disconnect from server if there is an error
        :param timeout: Delay in seconds before raising a timeout
        :param params: Query parameters
        :param raw: Return the raw server reply body (bytes)
        :param wait: Wait for server reply asynchronously
        """

        # Shutdown in progress do not execute the request
        if self._shutdown:
            return

        request = qpartial(
            self._executeHTTPQuery,
            method,
            endpoint,
            qpartial(callback),
            body,
            context=context,
            download_progress_callback=download_progress_callback,
            show_progress=show_progress,
            disconnect_on_error=disconnect_on_error,
            progress_text=progress_text,
            timeout=timeout,
            params=params,
            raw=raw,
            wait=wait
        )

        if self._connected:
            return request()
        else:
            self._query_waiting_connections.append((request, callback))
            # enqueue the first query and open the connection if we are not connected
            if len(self._query_waiting_connections) == 1:
                log.debug("Connection to {}".format(self.url()))
                self.connectToServer()

    def _addBodyToRequest(
            self,
            body: Optional[Union[dict, pathlib.Path, str]],
            request: QtNetwork.QNetworkRequest
    ) -> Optional[Union[QtCore.QBuffer, QtCore.QFile]]:
        """
        Add the required headers for sending the body.

        :param body: body to send in request
        :returns: body compatible with Qt
        """

        if body is None:
            return None

        if isinstance(body, dict):
            body = json.dumps(body)
            data = QtCore.QByteArray(body.encode())
            body = QtCore.QBuffer(self)
            body.setData(data)
            body.open(QtCore.QIODevice.ReadOnly)
            request.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, "application/json")
            request.setHeader(QtNetwork.QNetworkRequest.ContentLengthHeader, str(data.size()))
            #request.setRawHeader(b"Content-Length", str(data.size()).encode())
            return body
        elif isinstance(body, pathlib.Path):
            body = QtCore.QFile(str(body), self)
            body.open(QtCore.QFile.ReadOnly)
            request.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, "application/octet-stream")
            request.setHeader(QtNetwork.QNetworkRequest.ContentLengthHeader, str(body.size()))
            #request.setRawHeader(b"Content-Length", str(body.size()).encode())
            return body
        elif isinstance(body, str):
            data = QtCore.QByteArray(body.encode())
            body = QtCore.QBuffer(self)
            body.setData(data)
            body.open(QtCore.QIODevice.ReadOnly)
            request.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, "application/octet-stream")
            #request.setRawHeader(b"Content-Length", str(data.size()).encode())
            return body
        else:
            return None

    def _addAuth(self, request: QtNetwork.QNetworkRequest) -> QtNetwork.QNetworkRequest:
        """
        Add the JWT token in the authentication header
        """

        if self._jwt_token:
            request.setRawHeader(b"Authorization", f"Bearer {self._jwt_token}".encode())
        return request

    def connectWebSocket(self, websocket: QtWebSockets.QWebSocket, endpoint: str) -> QtWebSockets.QWebSocket:
        """
        Connect to websocket endpoint
        """

        ws_protocol = "ws"
        if self._protocol == "https":
            ws_protocol = "wss"
        host = self._getHostForQuery()
        port = self._port
        prefix = self._prefix
        jwt_token = self._jwt_token
        request = websocket.request()
        ws_url = f"{ws_protocol}://{host}:{port}{prefix}{endpoint}?token={jwt_token}"
        log.debug(f"Connecting to WebSocket: {ws_url}")
        request.setUrl(QtCore.QUrl(ws_url))
        websocket.open(request)
        return websocket

    def _getHostForQuery(self) -> str:
        """
        Get a hostname that can be used by Qt
        """

        try:
            ip = self._host.rsplit('%', 1)[0]
            ipaddress.IPv6Address(ip)  # remove any scope ID
            # this is an IPv6 address, we must surround it with brackets to be used with QUrl.
            host = "[{}]".format(ip)
        except ipaddress.AddressValueError:
            host = self._host
        return host

    def _paramsToQueryString(self, params: dict) -> str:
        """
        :param params: Dictionary of query string parameters
        :returns: String of the query string
        """

        if not params:
            query_string = ""
        else:
            query_string = "?"
            params = params.copy()
            for key, value in params.copy().items():
                if value is None:
                    del params[key]
            query_string += urllib.parse.urlencode(params)
        return query_string

    def _dataReadySlot(self, reply, callback, context):
        """
        Process a packet received on the notification feed.
        The feed can contain qpartial JSON. If we find fragmented
        JSON, we keep it for the next packet
        """

        if reply.error() != QtNetwork.QNetworkReply.NoError:
            return

        # HTTP error
        status = reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
        if status >= 300:
            return

        content = bytes(reply.readAll())
        if not content:
            return
        content_type = reply.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
        if content_type == "application/json":
            content = content.decode("utf-8")
            if context["query_id"] in self._buffer:
                content = self._buffer[context["query_id"]] + content
            try:
                while True:
                    content = content.lstrip(" \r\n\t")
                    answer, index = json.JSONDecoder().raw_decode(content)
                    callback(answer, context=context)
                    content = content[index:]
            except ValueError:  # Partial JSON
                self._buffer[context["query_id"]] = content
        else:
            callback(content, context=context)

    def _timeoutSlot(self, reply: QtNetwork.QNetworkReply, timeout: int) -> None:
        """
        Call for all requests, you need to check the status of the response
        """

        # We check if we received HTTP headers
        if not sip.isdeleted(reply) and reply.isRunning() and not len(reply.rawHeaderList()) > 0:
            if not reply.error() != QtNetwork.QNetworkReply.NoError:
                log.warning(f"Timeout after {timeout} seconds for request {reply.url().toString()}. \
                Please check the connection is not blocked by a firewall or an anti-virus.")
                reply.abort()

    def disconnect(self) -> None:
        """
        Disconnect from the server
        """

        if self.connected():
            self.disconnected_signal.emit()
            self.close()

    def _requestCredentialsFromUser(self):
        """
        Request credentials from user

        :return: username, password
        """

        username = password = None
        login_dialog = LoginDialog(self._main_window)
        if self._username:
            login_dialog.setUsername(self._username)
        login_dialog.show()
        login_dialog.raise_()
        if login_dialog.exec_():
            username = login_dialog.getUsername()
            password = login_dialog.getPassword()
        return username, password

    def _handleUnauthorizedRequest(self, reply: QtNetwork.QNetworkReply) -> None:
        """
        Request the username / password to authenticate with the server
        """

        if not self._username or not self._password or self._auth_attempted is True:
            username, password = self._requestCredentialsFromUser()
        else:
            username = self._username
            password = self._password

        if username and password:
            body = {
                "username": username,
                "password": password
            }
            self._auth_attempted = True
            content = self._executeHTTPQuery("POST", "/access/users/authenticate", body=body, wait=True)
            if content:
                log.info(f"Authenticated with controller {self._host} on port {self._port}")
                token = content.get("access_token")
                if token:
                    self._auth_attempted = False
                    self._jwt_token = token
                    return
        else:
            raise HttpClientUnauthorizedError(f"{reply.errorString()}")

    def _validateServerVersion(self, content: dict) -> None:
        """
        Validate the server version.
        """

        version = content.get("version")
        local = content.get("local")

        if version is None or local is None:
            raise HttpClientBadRequestError(f"The server is not a GNS3 server: {content}")

        if version.split("+")[0] != __version__.split("+")[0]:
            msg = f"Client version {__version__} is not the same as server version {version}"
            # We don't allow different major version to interact even with dev build
            if __version_info__[3] == 0 or parse_version(__version__)[:2] != parse_version(version)[:2]:
                raise HttpClientError(msg)
            log.warning(f"{msg}\nUsing different versions may result in unexpected problems.\n"
                        "Please upgrade or use at your own risk.")

    def _retryConnectionToServer(self, wait_time: int = 5) -> bool:
        """
        Retry a connection.
        """

        self._retry += 1
        loop = QtCore.QEventLoop()
        progress = QtWidgets.QProgressDialog(
            f"Retrying connection to controller (#{self._retry}/{self._max_retry_connection})",
            "Cancel",
            0,
            0,
            self._main_window
        )
        progress.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        progress.setWindowModality(QtCore.Qt.ApplicationModal)
        progress.canceled.connect(loop.quit)
        progress.show()
        timer = QtCore.QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(wait_time * 1000)
        loop.exec_()
        if progress.wasCanceled():
            return False
        progress.close()
        return self.connectToServer()

    def checkServerRunning(self) -> bool:
        """
        Check if server is running.
        """

        try:
            content = self._executeHTTPQuery("GET", "/version", wait=True, show_progress=False, timeout=2)
            self._validateServerVersion(content)
        except HttpClientError:
            return False
        return True

    def connectToServer(self) -> bool:
        """
        Connect to the GNS3 server
        """

        try:
            self._retry_connection = True
            content = self._executeHTTPQuery("GET", "/version", wait=True)
            self._validateServerVersion(content)
            self._retry_connection = False
            self._executeHTTPQuery("GET", "/access/users/me", wait=True)
        except HttpClientCancelledRequestError:
            return False  # operation cancelled by user
        except HttpClientError as e:
            if self._retry_connection and self._retry < self._max_retry_connection:
                return self._retryConnectionToServer()
            for request, callback in self._query_waiting_connections:
                if callback is not None:
                    callback({"message": str(e)}, error=True)
            self._query_waiting_connections = []
            self.disconnect()
            error_dialog = QtWidgets.QMessageBox(self._main_window)
            error_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            error_dialog.setWindowTitle("Connecting to server")
            error_dialog.setText(f"Error while connecting to the server")
            error_dialog.setDetailedText(f"{e}")
            error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
            error_dialog.show()
        else:
            self._connected = True
            self._retry = 0
            self.connected_signal.emit()
            for request, callback in self._query_waiting_connections:
                if request:
                    request()
            self._query_waiting_connections = []
            return True
        return False

    def _prepareRequest(self, method: str, endpoint: str, params: dict) -> QtNetwork.QNetworkRequest:
        """
        Return a QtNetwork.QNetworkRequest() instance
        """

        protocol = self._protocol
        host = self._getHostForQuery()
        port = self._port
        prefix = self._prefix
        query_string = self._paramsToQueryString(params)

        log.debug(f"{method} {protocol}://{host}:{port}{prefix}{endpoint}{query_string}")
        url = QtCore.QUrl(f"{protocol}://{host}:{port}{prefix}{endpoint}{query_string}")

        request = self._request(url)
        request = self._addAuth(request)
        request.setHeader(QtNetwork.QNetworkRequest.UserAgentHeader, f"GNS3 QT Client v{__version__}")
        return request

    def _executeHTTPQuery(
            self,
            method: str,
            endpoint: str,
            callback: Callable = None,
            body: Union[dict, pathlib.Path, str] = None,
            context: dict = None,
            download_progress_callback: Callable = None,
            show_progress: bool = True,
            progress_text: str = None,
            disconnect_on_error: bool = False,
            timeout: int = 60,
            params: dict = None,
            raw: bool = False,
            wait: bool = False,

    ) -> Optional[Union[str, bytes]]:
        """
        Send an HTTP request

        :param method: HTTP method
        :param endpoint: API endpoint
        :param callback: callback method to call when the server replies
        :param body: Body to send (dictionary, string or pathlib.Path)
        :param context: Pass a context to the response callback
        :param download_progress_callback: Callback called when received something, it can be an incomplete reply
        :param show_progress: Display a progress bar dialog
        :param progress_text: Custom text to display in the progress bar dialog
        :param disconnect_on_error: Disconnect from server if there is an error
        :param timeout: Delay in seconds before raising a timeout
        :param params: Query parameters
        :param raw: Return the raw server reply body (bytes)
        :param wait: Wait for server reply asynchronously
        """

        request = self._prepareRequest(method, endpoint, params)

        # By default Qt doesn't support GET with body
        # even if it's in the RFC that's why we need to use sendCustomRequest
        body = self._addBodyToRequest(body, request)

        try:
            reply = self._network_manager.sendCustomRequest(request, method.encode(), body)
        except SystemError as e:
            log.error("Can't send query: {}".format(str(e)))
            return

        if context:
            context = copy.copy(context)
            context["query_id"] = str(uuid.uuid4())

        if download_progress_callback is not None:
            reply.readyRead.connect(qpartial(self._dataReadySlot, reply, download_progress_callback, context))

        if wait:
            uploading = False
            if request.header(QtNetwork.QNetworkRequest.ContentTypeHeader) == "application/octet-stream":
                uploading = True

            QNetworkReplyWatcher(show_progress, progress_text).waitForReply(reply, uploading, timeout)
            try:
                content = self._processReply(reply, disconnect_on_error, raw)
                if callback:
                    callback(content, context=context)
                else:
                    return content
            except HttpClientError as e:
                if callback:
                    callback({"message": str(e)}, error=True, context=context)
                else:
                    raise
        else:
            reply.finished.connect(
                qpartial(self._processAsyncReply, reply, callback, body, context, timeout, disconnect_on_error, raw)
            )

            if timeout is not None:
                QtCore.QTimer.singleShot(timeout * 1000, qpartial(self._timeoutSlot, reply, timeout))

    def _processAsyncReply(
            self,
            reply: QtNetwork.QNetworkReply,
            callback: Callable,
            body: Union[dict, pathlib.Path, str] = None,
            context: dict = None,
            timeout: int = None,
            disconnect_on_error: bool = False,
            raw: bool = False
    ) -> None:

        if body is not None:
            body.close()

        try:
            content = self._processReply(reply, disconnect_on_error, raw)
            if callback:
                callback(content, context=context)
            if timeout is not None:
                QtCore.QTimer.singleShot(timeout * 1000, qpartial(self._timeoutSlot, reply, timeout))
        except HttpClientCancelledRequestError:
            return  # operation cancelled by user
        except HttpClientError as e:
            if callback:
                callback({"message": str(e)}, error=True, context=context)
            else:
                # display error because no callback is configured to handle it
                log.error(f"{e}")
        finally:
            reply.deleteLater()

    def _processReply(
            self,
            reply: QtNetwork.QNetworkReply,
            disconnect_on_error: bool = False,
            raw: bool = False
    ) -> Optional[Union[str, bytes]]:
        """
        Process the information returned by QtNetwork.QNetworkReply
        """

        status = reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
        content_type = reply.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
        if reply.error() == QtNetwork.QNetworkReply.NoError:
            try:
                content = bytes(reply.readAll())
                if raw is False:
                    content = content.decode("utf-8").strip(" \0\n\t")
                    if content and content_type == "application/json":
                        content = json.loads(content)
            except ValueError as e:
                raise HttpClientBadRequestError(f"Could not read data with content type '{content_type}' returned from"
                                                f" '{reply.url().toString()}': {e} (raw={raw})")
            if status >= 400:
                raise HttpClientError(f"Request to '{reply.url().toString()}' has returned HTTP code {status}")
            return content
        elif reply.error() == QtNetwork.QNetworkReply.NetworkSessionFailedError:
            return  # ignore the network session failed error to let the network manager recover from it
        elif reply.error() == QtNetwork.QNetworkReply.OperationCanceledError:
            raise HttpClientCancelledRequestError("Request cancelled")
        else:
            error_message = f"{reply.errorString()} (HTTP code {status})"
            if content_type == "application/json":
                try:
                    custom_error_message = json.loads(bytes(reply.readAll()).decode("utf-8")).get("message")
                    if custom_error_message:
                        error_message = custom_error_message
                except ValueError as e:
                    log.debug(f"Could not read server error message: {e}")
            log.debug(error_message)
            if status == 401 and reply.rawHeader(b"WWW-Authenticate") == b"Bearer":
                self._handleUnauthorizedRequest(reply)
            else:
                if disconnect_on_error:
                    self.disconnect()
                raise HttpClientError(error_message)

    def handleSslError(self, reply: QtNetwork.QNetworkReply, ssl_errors: List[QtNetwork.QSslError]) -> None:
        """
        Handle SSL errors
        """

        if self._accept_insecure_certificate:
            reply.ignoreSslErrors()
            return

        url = reply.request().url()
        host_port_key = f"{url.host()}:{url.port()}"

        # get the certificate digest
        ssl_config = reply.sslConfiguration()
        peer_cert = ssl_config.peerCertificate()
        digest = peer_cert.digest()

        if host_port_key in self._ssl_exceptions:

            if self._ssl_exceptions[host_port_key] == digest:
                reply.ignoreSslErrors()
                return

        msgbox = QtWidgets.QMessageBox(self._main_window)
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
            reply.ignoreSslErrors()
        else:
            for error in ssl_errors:
                log.error(f"SSL error detected: {error.errorString()}")
            self._main_window.close()
