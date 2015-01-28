import os
import sys
import socket
import paramiko
import logging
from io import StringIO
from .endpoint import Endpoint

log = logging.getLogger(__name__)

debug = True

if logging.getLogger().getEffectiveLevel() < 20:
    enable_debug = True

if debug:
    enable_debug = True

if enable_debug:
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log_level = logging.DEBUG
    log.setLevel(log_level)

    log_console = logging.StreamHandler()
    log_console.setFormatter(log_format)
    log_console.setLevel(log_level)
    log.addHandler(log_console)
    log.debug("DEBUG IS ENABLED")


class Tunnel(object):

    def __init__(self, hostname, port, username=None, password=None, client_key=None, server_key=None):
        """
        Sets up the ssl connection for tunnel support.

        params:
        client_key : String containing the rsa private key data
        server_key : String containing the rsa private key data
        """
        self.server = (hostname, int(port))

        self.auth_data = {}
        self.auth_data['username'] = username
        self.auth_data['password'] = password

        if client_key:
            self.auth_data['pkey'] = self._make_key_file(client_key)

        if server_key:
            self.auth_data['hostkey'] = self._make_key_file(server_key)

        self.transport = paramiko.Transport(self.server)
        self.transport.set_keepalive(30)

        self.end_points = {}
        self.connected = False

        self._connect()

    def _connect(self):
        """
        Makes the SSH connection to the remote server
        """

        log.info("Connecting to server: %s:%s" % (self.server))
        self.transport.connect(**self.auth_data)
        self.is_connected()

    def _make_key_file(self, data):
        if hasattr(data, 'readlines'):
            key_file = data
        else:
            key_file = StringIO()
            key_file.write(data)
            key_file.flush()
            key_file.seek(0)

        my_pkey = paramiko.RSAKey.from_private_key(
            key_file
        )

        return my_pkey

    def _find_unused_local_port(self):
        s = socket.socket()
        s.bind(('127.0.0.1', 0))
        return s.getsockname()

    def is_connected(self):
        """
        Verifies the SSH connection is up and authenticated
        """

        if self.transport.is_active() is False:
            log.critical("Connection is down: %s" % (self.server[0]))
            self.connected = False
            return self.connected

        if self.transport.is_authenticated() is False:
            log.critical("Authentication failed: %s" % (self.server[0]))
            self.connected = False
        else:
            log.info("Connection is up: %s" % (self.server[0]))
            self.connected = True

        return self.connected

    def disconnect(self):
        for name, end_point in self.end_points.items():
            self.remove_endpoint(name)
        self.transport.close()

    def add_endpoint(self, remote_ip, remote_port):
        remote_address = (remote_ip, int(remote_port))
        local_address = self._find_unused_local_port()

        new_endpoint = Endpoint(local_address, remote_address, self.transport)
        new_endpoint.enable()
        self.end_points[new_endpoint.getId()] = new_endpoint

        return new_endpoint

    def remove_endpoint(self, endpoint):
        if endpoint.getId() in self.end_points:
            self.end_points[endpoint.getId()].disable()

    def list_endpoints(self):
        remotes = {}
        for name, end_point in self.end_points.items():
            remotes[name] = end_point.get()

        return remotes
