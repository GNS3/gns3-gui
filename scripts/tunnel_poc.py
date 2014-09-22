import os
import sys
import paramiko
import socket
import logging
from io import StringIO

log = logging.getLogger()

class EndPoint(object):
    def __init__(self, local_address, remote_address):
        """
        Store local and remote tunnel address information in the format:
        (ip, port) format.
        """

        self.local_address = local_address
        self.remote_address = remote_address

    def get(self):
        return ( self.local_address, self.remote_address )

class Tunnel(object):
    
    def __init__(self, hostname, port, username=None, password=None, client_key=None, server_key=None):
        """
        Sets up the ssl connection for tunnel support.

        params:
        client_key : String containing the rsa private key data
        server_key : String containing the rsa private key data
        """
        self.server = (hostname, int(port))
        
        self.auth_data={}
        self.auth_data['username'] = username
        self.auth_data['password'] = password

        if client_key:
            self.auth_data['pkey'] = self._make_key_file(client_key)

        if server_key:
            self.auth_data['hostkey'] = self._make_key_file(server_key)

        self.transport = paramiko.Transport(self.server)
        self.transport.set_keepalive(30)

        self.destinations = {}
        self.channels = {}
        self.connected = False

        self._connect()

    def _connect(self):

        self.transport.connect(**self.auth_data)
        self.is_connected()

    def _make_key_file(self, data):
        if hasattr(data, 'readlines'):
            key_file = data
        else:
            key_file = StringIO.StringIO()
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
        if self.transport.is_active() == False:
            log.critical("Connection is down: %s" %(self.server[0]))
            self.connected = False
            return self.connected

        if self.transport.is_authenticated() == False:
            log.critical("Authentication failed: %s" %(self.server[0]))
            self.connected = False
        else:
            self.connected = True

        return self.connected

    def reconnect(self):
        self._connect()

    def disconnect(self):
        self.transport.close()

    def _forward_port(self, local_address, remote_address):
        print("Local: %s:%s" %(local_address))
        print("Remote: %s:%s" % (remote_address))
        channel = self.transport.open_channel("direct-tcpip", 
                src_addr = local_address,
                dest_addr = remote_address,
            )

        return channel

    def add_destination(self, name, remote_ip, remote_port):
        remote_address = (remote_ip, int(remote_port))
        local_address = self._find_unused_local_port()

        new_endpoint = EndPoint(local_address, remote_address)
        self.destinations[name] = new_endpoint

        channel = self._forward_port(local_address, remote_address)
        self.channels[name] = channel

        return new_endpoint.get()

    def remove_destination(self, name):
        self.channels[name].close()
        del self.channels[name]
        del self.destinations[name]

    def list_endpoints(self):
        remotes = {}
        for name, end_point in self.destinations.iteritems():
            remotes[name] = end_point.get()

        return remotes

    def on_connect(self, callback):
        pass

    def on_disconnect(self, callback):
        pass