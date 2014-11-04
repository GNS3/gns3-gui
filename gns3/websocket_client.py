# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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

"""
Non-blocking Websocket client with JSON-RPC support to connect to GNS3 servers.
Based on the ws4py websocket client.
"""

import json
import socket
import urllib.request

from .version import __version__
from . import jsonrpc
from ws4py.client import WebSocketBaseClient
from ws4py import WS_VERSION
from .qt import QtCore
from .tunnel import tunnel

import logging
log = logging.getLogger(__name__)


class WebSocketClient(WebSocketBaseClient):
    """
    Websocket client.

    :param url: websocket URL to connect to the server
    """

    _instance_count = 1

    def __init__(self, url, protocols=None, extensions=None, 
                 heartbeat_freq=None, ssl_options=None, headers=None):

        WebSocketBaseClient.__init__(self, url,
                                     protocols,
                                     extensions,
                                     heartbeat_freq,
                                     ssl_options,
                                     headers)

        self.callbacks = {}
        self._connected = False
        self._local = False
        self._cloud = False
        self._version = ""
        self._fd_notifier = None
        self._heartbeat_timer = None
        self._tunnel = None

        # create an unique ID
        self._id = WebSocketClient._instance_count
        WebSocketClient._instance_count += 1

    def id(self):
        """
        Returns this WebSocket identifier.

        :returns: WebSocket identifier (integer)
        """

        return self._id

    def version(self):
        """
        Returns the received server version.

        :returns: server version (string)
        """

        return self._version

    @classmethod
    def reset(cls):
        """
        Reset the instance count.
        """

        cls._instance_count = 1

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

    def setCloud(self, value):
        self._cloud = value

    def isCloud(self):
        return self._cloud

    def opened(self):
        """
        Called when the connection with the server is successful.
        """

        log.info("connected to {}:{}".format(self.host, self.port))
        self._connected = True

    def connect(self):
        """
        Connects to the server.
        """
        self.use_auth = False
        self.use_ssl = False
        self.version_url = "http://{host}:{port}/version".format(host=self.host, port=self.port)
        self.websocket_url = "ws://{host}:{port}".format(host=self.host, port=self.port)

        self.https_handler = urllib.request.HTTPSHandler(check_hostname=False)
        self.cookie_processor = urllib.request.HTTPCookieProcessor()
        self.opener = urllib.request.build_opener(self.https_handler, self.cookie_processor)

        self._connect()
        self.check_server_version()

    def _connect(self):
        """
        Connect to the server.
        """
        try:
            WebSocketBaseClient.connect(self)
        except OSError:
            raise
        except Exception as e:
            log.error("could not to connect {}: {}".format(self.url, e))
            raise OSError("Websocket exception {}: {}".format(type(e), e))

    def check_server_version(self):
        """
        Check for a version match with the GNS3 server.

        This is an http (or https) request.
        """
        content = self.opener.open(self.version_url).read()
        try:
            json_data = json.loads(content.decode("utf-8"))
            self._version = json_data.get("version")
        except ValueError as e:
            log.error("could not get the server version: {}".format(e))

        #FIXME: temporary version check
        if self._version != __version__:
            if not self._version:
                raise OSError("Could not determine the server version")
            else:
                raise OSError("GUI version {} differs with the server version: {}".format(__version__, self._version))
            self.close_connection()

    def reconnect(self):
        """
        Reconnects to the server.
        """

        WebSocketBaseClient.__init__(self,
                                     self.url,
                                     self.protocols,
                                     self.extensions,
                                     self.heartbeat_freq,
                                     self.ssl_options,
                                     self.extra_headers)

        if self._local:
            # check the local host address is still valid
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind((self.host, 0))

        self.connect()

    def connected(self):
        """
        Returns if the client is connected.

        :returns: True or False
        """

        return self._connected

    def handshake_ok(self):
        """
        Called when the connection has been established with the server and
        monitors the connection using the QSocketNotifier.
        """

        fd = self.connection.fileno()
        # we are interested in all data received.
        self._fd_notifier = QtCore.QSocketNotifier(fd, QtCore.QSocketNotifier.Read)
        self._fd_notifier.activated.connect(self.data_received)
        self.opened()

    def closed(self, code, reason):
        """
        Called when the connection has been closed.

        :param code: code (integer)
        :param reason: reason (string)
        """

        log.info("connection closed down: {} (code {})".format(reason, code))
        if self._heartbeat_timer is not None:
            self._heartbeat_timer.stop()
        self._connected = False
        self._tunnel.disconnect()

    def received_message(self, message):
        """
        Called when a new message has been received from the server.

        :param message: message instance
        """

        # TODO: WSAEWOULDBLOCK on Windows
        if not message.is_text:
            log.warning("received data is not text")
            return

        try:
            reply = json.loads(message.data.decode("utf-8"))
        except:
            log.warning("received data is not valid JSON")
            return

        if "result" in reply:
        # This is a JSON-RPC result
            request_id = reply.get("id")
            result = reply.get("result")
            if request_id in self.callbacks:
                self.callbacks[request_id](result)
                if request_id in self.callbacks:  #FIXME: strange bug with cloud device setup callback, the request is received twice, bug in Qt?
                    del self.callbacks[request_id]
                else:
                    log.warning("JSON-RPC reply received twice: {}".format(reply))
            else:
                log.warning("unknown JSON-RPC request ID received {}".format(request_id))

        elif "error" in reply:
            # This is a JSON-RPC error
            error_message = reply["error"].get("message")
            error_code = reply["error"].get("code")
            request_id = reply.get("id")
            if request_id in self.callbacks:
                self.callbacks[request_id](reply["error"], True)
                del self.callbacks[request_id]
            else:
                log.warning("received JSON-RPC error {}: {} for request ID {}".format(error_code,
                                                                                      error_message,
                                                                                      request_id))
        elif "method" in reply:
            # This is a JSON-RPC notification
            method = reply.get("method")
            params = reply.get("params")

            # let the responsible module know about the notification
            from .modules import MODULES
            for module in MODULES:
                if method.startswith(module.__name__.lower()):
                    instance = module.instance()
                    instance.notification(method, params)
                    break

    def send_message(self, destination, params, callback):
        """
        Sends a message to the server.

        :param destination: server destination method
        :param params: params to send (dictionary)
        :param callback: callback method to call when the server replies.
        """

        if not self.connected():
            log.warning("connection with server {}:{} is down".format(self.host, self.port))
            return

        request = jsonrpc.JSONRPCRequest(destination, params)
        self.callbacks[request.id] = callback
        self.send(str(request))

    def send_notification(self, destination, params=None):
        """
        Sends a notification to the server. No reply is expected from the server.

        :param destination: server destination method
        :param params: params to send (dictionary)
        """

        if not self.connected():
            log.warning("connection with server {}:{} is down".format(self.host, self.port))
            return

        request = jsonrpc.JSONRPCNotification(destination, params)
        self.send(str(request))

    def close_connection(self):
        """
        Closes the connection to the server and remove the monitoring by
        the QSocketNotifier.
        """

        self._connected = False
        self._version = ""
        WebSocketBaseClient.close_connection(self)
        if self._fd_notifier:
            self._fd_notifier.setEnabled(False)
            self._fd_notifier = None
        log.info("connection closed with server {}:{}".format(self.host, self.port))

    def data_received(self, fd):
        """
        Callback called when data is received from the server.
        """

        # read the data, if successful received_message() is called by once()
        if self.once() == False:
            log.warning("lost connection with server {}:{}".format(self.host, self.port))
            self.close_connection()

    def dump(self):
        """
        Returns a representation of this server.

        :returns: dictionary
        """

        return {"id": self._id,
                "host": self.host,
                "port": self.port,
                "local": self._local}

    def _heartbeat(self):
        self.send_notification("deadman.heartbeat")

    def enableHeartbeatsAt(self, interval):
        self._heartbeat_timer = QtCore.QTimer()
        self._heartbeat_timer.timeout.connect(self._heartbeat)
        self._heartbeat_timer.start(interval)

    def setupTunnel(self):
        pass


class SecureWebSocketClient(WebSocketClient):
    def __init__(self, url, protocols=None, extensions=None,
                 heartbeat_freq=None, ssl_options=None, headers=None):

        self.use_auth = True
        self.use_ssl = False

        # The url has to be set before the constructor is called
        scheme, rest = url.split(':', 1)
        if self.use_ssl:
            url = "wss:{}".format(rest)
        else:
            url = "ws:{}".format(rest)

        WebSocketClient.__init__(self, url,
                                     protocols,
                                     extensions,
                                     heartbeat_freq,
                                     ssl_options,
                                     headers)


    def setSecureOptions(self, ca_file, auth_user, auth_password, ssh_pkey):
        self._ca_file = ca_file
        self._auth_user = auth_user
        self._auth_password = auth_password
        self._ssh_pkey = ssh_pkey

    def connect(self):
        log.debug('In SecureWebSocketClient.connect()')

        import ssl
        import socket

        if self.use_ssl:
            self.login_url = "https://{host}:{port}/login".format(host=self.host, port=self.port)
            self.version_url = "https://{host}:{port}/version".format(host=self.host, port=self.port)
            self.ssl_options = {'ca_certs': self._ca_file}
            context = ssl._create_stdlib_context(cert_reqs=ssl.CERT_REQUIRED, cafile=self._ca_file)
            self.https_handler = urllib.request.HTTPSHandler(context=context, check_hostname=False)
        else:
            self.login_url = "http://{host}:{port}/login".format(host=self.host, port=self.port)
            self.version_url = "http://{host}:{port}/version".format(host=self.host, port=self.port)
            self.ssl_options = {}
            self.https_handler = urllib.request.HTTPHandler()

        self.cookie_processor = urllib.request.HTTPCookieProcessor()
        self.opener = urllib.request.build_opener(self.https_handler, self.cookie_processor)

        self.check_server_version()
        data = urllib.parse.urlencode({'name': self._auth_user, 'password': self._auth_password}).encode('utf-8')
        f = self.opener.open(self.login_url, data, socket._GLOBAL_DEFAULT_TIMEOUT)
        log.debug('login result: {}'.format(f.read()))

        self._connect()
        log.debug(self.sock)

        self._tunnel = tunnel.Tunnel(self.host, 22, username='root', client_key=self._ssh_pkey)
        log.debug('tunnel status: {}'.format(self._tunnel.is_connected()))

    @property
    def handshake_headers(self):
        """
        List of headers appropriate for the upgrade
        handshake.

        This code is copied from the ws4py library, then modified to include a
        cookie in the request.
        """
        cookies = self.cookie_processor.cookiejar._cookies[self.host]['/']
        user = cookies['user']
        headers = [
            ('Host', self.host),
            ('Cookie', '{}={}'.format(user.name, user.value)),
            ('Connection', 'Upgrade'),
            ('Upgrade', 'websocket'),
            ('Sec-WebSocket-Key', self.key.decode('utf-8')),
            ('Origin', self.url),
            ('Sec-WebSocket-Version', str(max(WS_VERSION)))
            ]

        if self.protocols:
            headers.append(('Sec-WebSocket-Protocol', ','.join(self.protocols)))

        if self.extra_headers:
            headers.extend(self.extra_headers)

        return headers

    @property
    def tunnel(self):
        return self._tunnel
