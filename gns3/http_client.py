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

from .qt import sip
import json
import pathlib
import base64
import ipaddress
import urllib.request
import urllib.parse
import copy
import uuid

from typing import List
from .version import __version__, __version_info__
from .qt import QtCore, QtNetwork, QtWidgets, qpartial
from .utils import parse_version
from .dialogs.login_dialog import LoginDialog

from .http_client_error import (
    HttpClientError,
    HttpClientBadRequestError,
    HttpClientUnauthorizedError,
    HttpClientTimeoutError
)

import logging
log = logging.getLogger(__name__)


class QNetworkReplyWatcher(QtCore.QObject):

    def __init__(self, show_progress: bool = True, parent: QtWidgets.QWidget = None):

        if not parent:
            from gns3.main_window import MainWindow
            parent = MainWindow.instance()

        super().__init__(parent)

        if show_progress:
            self._progress = QtWidgets.QProgressDialog("Waiting for server", "Cancel", 0, 0, parent)
            self._progress.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
            self._progress.setWindowModality(QtCore.Qt.ApplicationModal)
            #self._progress.setMinimumDuration(0)
        else:
            self._progress = None

    def waitForReply(self, reply: QtNetwork.QNetworkReply, timeout=60) -> None:

        loop = QtCore.QEventLoop()

        if timeout:
            timer = QtCore.QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: loop.exit(1))
            timer.start(timeout * 1000)

        reply.finished.connect(loop.quit)

        if self._progress:
            reply.finished.connect(self._progress.close)
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
    HTTP client.

    :param settings: Dictionary with connection information to the server
    :param network_manager: A QT network manager
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
        self._jwt_token = None
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

        self._retry = 0  # how many time we have already retried connection
        self._max_retry_connection = max_retry_connection
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

        # A buffer used by progress download
        self._buffer = {}

        # List of query waiting for the connection
        self._query_waiting_connections = []

        # To catch SSL errors
        self._network_manager.sslErrors.connect(self.handleSslError)

        # Store SSL error exceptions
        self._ssl_exceptions = {}

    def host(self) -> str:
        """
        Host display to user
        """
        return self._host

    def setHost(self, host: str) -> None:

        self._host = host

    def port(self) -> int:
        """
        Port display to user
        """
        return self._port

    def setPort(self, port: int) -> None:

        self._port = port

    def protocol(self) -> str:
        """
        Transport protocol
        """

        return self._protocol

    def setAcceptInsecureCertificate(self, certificate: bool):
        """
        Does the server accept this insecure SSL certificate digest

        :param: Certificate digest
        """

        self._accept_insecure_certificate = certificate

    def user(self) -> str:
        """
        User login display to GNS3 user
        """
        return self._user

    def url(self) -> str:
        """
        Returns current server url
        """

        if ":" in self.host():
            return "{}://[{}]:{}".format(self.protocol(), self.host(), self.port())
        return "{}://{}:{}".format(self.protocol(), self.host(), self.port())

    def fullUrl(self) -> str:
        """
        Returns current server url including user and password
        """

        host = self.host()
        if ":" in self.host():
            host = "[{}]".format(host)

        if self._user:
            return "{}://{}:{}@{}:{}".format(self.protocol(), self._user, self._password, host, self.port())
        else:
            return "{}://{}:{}".format(self.protocol(), host, self.port())

    def password(self) -> str:

        return self._password

    def setPassword(self, password: str) -> None:

        self._password = password

    def shutdown(self) -> None:
        """
        Stop the server and stop to accept queries
        """

        self._shutdown = True
        self.sendRequest("POST", "/shutdown", show_progress=False)

    def connected(self) -> bool:
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

    def _request(self, url):
        """
        Get a QNetworkRequest object. You can mock this
        if you want low level mocking.

        :param url: Url of remote ressource (QtCore.QUrl)
        :returns: QT Network request (QtNetwork.QNetworkRequest)
        """

        return QtNetwork.QNetworkRequest(url)

    def sendRequest(
            self,
            method,
            endpoint,
            callback,
            body={},
            context={},
            downloadProgressCallback=None,
            show_progress=True,
            ignoreErrors=False,
            progressText=None,
            timeout=120,
            params={},
            raw=False,
            **kwargs
    ):
        """
        Call the remote server, if not connected, check connection before

        :param method: HTTP method
        :param endpoint: API endpoint
        :param body: params to send (dictionary or pathlib.Path)
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param downloadProgressCallback: Callback called when received something, it can be an incomplete response
        :param show_progress: Display progress to the user
        :param progressText: Text display to user in the progress dialog. None for auto generated
        :param ignoreErrors: Ignore connection error (usefull to not closing a connection when notification feed is broken)
        :param timeout: Delay in seconds before raising a timeout
        :param params: Query arguments parameters
        :returns: QNetworkReply
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
            #downloadProgressCallback=downloadProgressCallback,
            show_progress=show_progress,
            #ignoreErrors=ignoreErrors,
            #progressText=progressText,
            timeout=timeout,
            params=params,
            raw=raw
        )

        if self._connected:
            return request()
        else:
            self._query_waiting_connections.append((request, callback))
            # enqueue the first query and open the connection if we are not connected
            if len(self._query_waiting_connections) == 1:
                log.debug("Connection to {}".format(self.url()))
                self.connectToServer()
                #self._executeHTTPQuery("GET", "/version", self._callbackConnect, {}, timeout=10, show_progress=False)

    # def _connectionError(self, callback, msg="", server=None):
    #     """
    #     Return an error to user if connection failed
    #
    #     :param callback: User callback
    #     :param msg: An optional additional message for the callback
    #     :param server: Server where the query is execute
    #     """
    #
    #     if len(msg) > 0:
    #         msg = "Cannot connect to server {}: {}".format(self.url(), msg)
    #     else:
    #         msg = "Cannot connect to {}. Please check if GNS3 is allowed in your antivirus and firewall. And that server version is {}.".format(self.url(), __version__)
    #     for request, callback in self._query_waiting_connections:
    #         if callback is not None:
    #             callback({"message": msg}, error=True, server=server, connection_error=True)
    #     self._query_waiting_connections = []

    # def _retryConnection(self, server=None):
    #     log.debug("Retry connection to {}".format(self.url()))
    #     self._retry += 1
    #     QtCore.QTimer.singleShot(1000, qpartial(self._executeHTTPQuery, "GET", "/version", self._callbackConnect, {}, server=server, timeout=5))

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
        Add authentication information
        """

        if self._user:
            auth_string = "{}:{}".format(self._user, self._password)
            auth_string = base64.b64encode(auth_string.encode("utf-8"))
            auth_string = "Basic {}".format(auth_string.decode())
            request.setRawHeader(b"Authorization", auth_string.encode())

        if self._jwt_token:
            request.setRawHeader(b"Authorization", f"Bearer {self._jwt_token}".encode())
        return request

    def connectWebSocket(self, websocket, endpoint):
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

    def _readyReadySlot(self, response, callback, context, *args):
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
                    callback(answer, context=context)
                    content = content[index:]
            except ValueError:  # Partial JSON
                self._buffer[context["query_id"]] = content
        else:
            callback(content, context=context)

    def _timeoutSlot(self, reply, timeout):
        """
        Beware it's call for all request you need to check the status of the response
        """
        # We check if we received HTTP headers
        if not sip.isdeleted(reply) and reply.isRunning() and not len(reply.rawHeaderList()) > 0:
            if not reply.error() != QtNetwork.QNetworkReply.NoError:
                log.warning("Timeout after {} seconds for request {}. Please check the connection is not blocked by a firewall or an anti-virus.".format(timeout, reply.url().toString()))
                reply.abort()

    def disconnect(self):
        """
        Disconnect from the remote server
        """

        if not self.connected():
            self.disconnected_signal.emit()
            self.close()

    def _handleUnauthorizedRequest(self, reply: QtNetwork.QNetworkReply) -> None:

        login_dialog = LoginDialog(self._main_window)
        login_dialog.show()
        login_dialog.raise_()
        if login_dialog.exec_():
            username = login_dialog.getUsername()
            password = login_dialog.getPassword()
            if username and password:
                body = {
                    "username": username,
                    "password": password
                }
                content = self._executeHTTPQuery("POST", "/users/authenticate", body=body, wait=True)
                if content:
                    log.info(f"Authenticated with server")
                    token = content.get("access_token")
                    if token:
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

        if not version or not local:
            raise HttpClientBadRequestError(f"The remote server is not a GNS3 server: {content}")

        if version.split("-")[0] != __version__.split("-")[0]:
            msg = f"Client version {__version__} is not the same as server version {version}"
            # We don't allow different major version to interact even with dev build
            if __version_info__[3] == 0 or parse_version(__version__)[:2] != parse_version(version)[:2]:
                raise HttpClientError(msg)
            log.warning(f"{msg}\nUsing different versions may result in unexpected problems.\n"
                        "Please upgrade or use at your own risk.")

    def connectToServer(self) -> None:

        try:
            content = self._executeHTTPQuery("GET", "/version", timeout=60, wait=True)
            if not content:
                return  # operation cancelled
            self._validateServerVersion(content)
            self._executeHTTPQuery("GET", "/users/me", wait=True)
        except HttpClientError as e:
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
            self.connected_signal.emit()
            for request, callback in self._query_waiting_connections:
                if request:
                    request()
            self._query_waiting_connections = []

    def _prepareRequest(self, method, endpoint, params):

        protocol = self._protocol
        host = self._getHostForQuery()
        port = self._port
        user = self._user
        prefix = self._prefix
        query_string = self._paramsToQueryString(params)

        log.debug(f"{method} {protocol}://{host}:{port}{prefix}{endpoint}{query_string}")
        if user:
            url = QtCore.QUrl(f"{protocol}://{user}@{host}:{port}{prefix}{endpoint}{query_string}")
        else:
            url = QtCore.QUrl(f"{protocol}://{host}:{port}{prefix}{endpoint}{query_string}")

        request = self._request(url)
        request = self._addAuth(request)
        request.setRawHeader(b"User-Agent", "GNS3 QT Client v{version}".format(version=__version__).encode())
        return request

    def _executeHTTPQuery(
            self,
            method,
            endpoint,
            callback=None,
            body=None,
            context=None,
            params=None,
            show_progress=True,
            wait=False,
            ignore_erros=False,
            raw=False,
            timeout=60
    ):
        """
        Send HTTP request

        :param method: HTTP method
        :param endpoint: API endpoint
        :param body: params to send (dictionary)
        :param callback: callback method to call when the server replies
        :param context: Pass a context to the response callback
        :param downloadProgressCallback: Callback called when received something, it can be an incomplete response
        :param show_progress: Display progress to the user
        :param progressText: Text display to user in progress dialog. None for auto generated
        :param ignoreErrors: Ignore connection error (usefull to not closing a connection when notification feed is broken)
        :param timeout: Delay in seconds before raising a timeout
        :param params: Query arguments parameters
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

        if wait:
            QNetworkReplyWatcher(show_progress).waitForReply(reply, timeout)
            try:
                content = self._processReply(reply, ignore_erros, raw)
                if callback:
                    callback(content, context=None)
                else:
                    return content
            except HttpClientError as e:
                if callback:
                    callback({"message": str(e)}, error=True, context=context)
                else:
                    raise
        else:
            reply.finished.connect(qpartial(self._processAsyncReply, reply, callback, context, timeout, ignore_erros, raw))
            if timeout is not None:
                QtCore.QTimer.singleShot(timeout * 1000, qpartial(self._timeoutSlot, reply, timeout))

    def _processAsyncReply(
            self,
            reply: QtNetwork.QNetworkReply,
            callback,
            context=None,
            timeout=None,
            ignore_errors: bool = False,
            raw: bool = False
    ):

        try:
            content = self._processReply(reply, ignore_errors, raw)
            if callback:
                callback(content, context=context)
            if timeout is not None:
                QtCore.QTimer.singleShot(timeout * 1000, qpartial(self._timeoutSlot, reply, timeout))
        except HttpClientError as e:
            if callback:
                callback({"message": str(e)}, error=True, context=context)
            else:
                # Because no callback is configured to handle the error we display it to the user
                log.error(f"{e}")
        finally:
            reply.deleteLater()

    def _processReply(self, reply: QtNetwork.QNetworkReply, ignore_errors: bool = False, raw: bool = False):

        status = reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
        if reply.error() == QtNetwork.QNetworkReply.NoError:
            content_type = reply.header(QtNetwork.QNetworkRequest.ContentTypeHeader)
            try:
                content = bytes(reply.readAll())
                if raw is False:
                    content = content.decode("utf-8").strip(" \0\n\t")
                    if content and content_type == "application/json":
                        content = json.loads(content)
            except ValueError as e:
                raise HttpClientBadRequestError(f"Could not read data with content type '{content_type}' returned from"
                                                f" '{reply.url().toString()}': {e}")
            if status >= 400:
                raise HttpClientError(f"Request to '{reply.url().toString()}' has returned HTTP code {status}")
            return content
        elif reply.error() == QtNetwork.QNetworkReply.NetworkSessionFailedError:
            return  # ignore the network session failed error to let the network manager recover from it
        elif reply.error() != QtNetwork.QNetworkReply.OperationCanceledError:
            error_message = f"Error with request to '{reply.url().toString()}': " \
                            f"{reply.errorString()} (HTTP code {status})"
            log.debug(error_message)
            if status == 401:
                self._handleUnauthorizedRequest(reply)
            else:
                if not ignore_errors:
                    self.disconnect()
                raise HttpClientError(error_message)

    def handleSslError(self, reply: QtNetwork.QNetworkReply, ssl_errors: List[QtNetwork.QSslError]) -> None:

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
            reply.ignoreSslErrors()
        else:
            for error in ssl_errors:
                log.error(f"SSL error detected: {error.errorString()}")
            main_window.close()
