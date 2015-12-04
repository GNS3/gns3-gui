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

import paramiko

from gns3.http_client import HTTPClient
from gns3.tunnel.endpoint import Endpoint
from gns3.qt import QtCore

import logging
log = logging.getLogger(__name__)


class SSHConnectionThread(QtCore.QThread):
    error_signal = QtCore.pyqtSignal(str)
    connected_signal = QtCore.pyqtSignal()

    def __init__(self, ssh_client, parent=None):
        self._ssh_client = ssh_client
        super().__init__(parent)

    def run(self):
        port = Endpoint.find_unused_port(1000, 10000)
        if port is None:
            self.error_signal.emit("No port available in order to create SSH tunnel")
            return

        try:
            self._ssh_client.transport = paramiko.Transport((self._ssh_client.host(), self._ssh_client.ssh_port(), ))
            self._ssh_client.transport.set_keepalive(30)
            with open(self._ssh_client.ssh_key()) as f:
                self._ssh_client.transport.connect(username=self._ssh_client.user(), pkey=paramiko.RSAKey.from_private_key(f))

            endpoint = Endpoint(("127.0.0.1", port), ("127.0.0.1", self._ssh_client._http_port), self._ssh_client.transport)
            endpoint.enable()
            self._ssh_client._endpoints[port] = endpoint
        except (paramiko.ssh_exception.SSHException, OSError) as e:
            self.error_signal.emit(str(e))
            return

        self._ssh_client._http_port = port

        self.connected_signal.emit()


class SSHClient(HTTPClient):

    """
    SSH client.

    It's create an SSH tunnel and run HTTP query inside the tunnel

    :param settings: Settings to connect to the server
    :param network_manager: A QT network manager
    """

    def __init__(self, settings, network_manager):

        settings["protocol"] = "http"
        self._ssh_port = settings["ssh_port"]
        self._ssh_key = settings["ssh_key"]
        self._endpoints = {}
        assert settings["ssh_port"] is not None
        assert settings["ssh_key"] is not None
        super().__init__(settings, network_manager)

    def _connect(self, query):
        """
        Initialize the connection

        :param query: The query to execute when all network stack is ready
        :param callback: User callback when connection is finish
        """

        log.info("SSH connection to %s with key %s", self.url(), self.ssh_key())
        thread = SSHConnectionThread(self, parent=self)
        thread.error_signal.connect(lambda msg: self._connectionError(None, msg))
        thread.connected_signal.connect(lambda: super(SSHClient, self)._connect(query ))
        thread.start()

    def getTunnel(self, port):
        """
        Get a tunnel to the remote port.
        For HTTP standard client it's the same port. For SSH it will be different

        :param port: Remote port
        :returns: Tuple host, port to connect
        """

        new_port = Endpoint.find_unused_port(1000, 10000)

        endpoint = Endpoint(("127.0.0.1", new_port), ("127.0.0.1", port), self.transport)
        endpoint.enable()
        self._endpoints[new_port] = endpoint

        return ("127.0.0.1", new_port)

    def releaseTunnel(self, port):
        """
        Release a tunnel

        :param port: The previously allocated port
        """
        endpoint = self._endpoints[port]
        endpoint.disable()
        del self._endpoints[port]

    def settings(self):
        settings = super().settings()
        settings["ssh_port"] = self.ssh_port()
        settings["ssh_key"] = self.ssh_key()
        return settings

    def ssh_port(self):
        return self._ssh_port

    def ssh_key(self):
        return self._ssh_key

    def protocol(self):
        return "ssh"

    def close(self):
        """
        Close all remote connection
        """
        for endpoint in self._endpoints:
            endpoint.disable()
        super().close()
