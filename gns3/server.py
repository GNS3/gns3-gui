#!/usr/bin/env python
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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


from .qt import QtCore
from .network_client import getNetworkUrl

import logging
log = logging.getLogger(__name__)


class Server(QtCore.QObject):
    """
    An instance of Server
    """

    _instance_count = 0

    connection_connected_signal = QtCore.Signal()
    connection_closed_signal = QtCore.Signal()
    system_usage_updated_signal = QtCore.Signal()

    def __init__(self, settings, http_client):

        super().__init__()
        self._connected = False
        self._protocol = settings.get("protocol", "http")
        self._host = settings["host"]
        self._port = int(settings["port"])
        self._user = settings.get("user", None)
        self._password = settings.get("password", None)
        self._usage = None
        self._accept_insecure_certificate = settings.get("accept_insecure_certificate", None)
        self._local = True
        self._gns3_vm = False
        self._server_id = settings.get("server_id", self.url())
        self._http_client = http_client

        # Unique ID for dump in topology
        self._id = Server._instance_count
        Server._instance_count += 1

    def _updateServer(self):
        # TODO update server settings on the controller
        # emit a signal for that
        # or manage everything in servers?
        pass

    def host(self):
        """
        Host display to user
        """
        return self._host

    def setHostPort(self, host, port):
        """
        Change the host and the port with only
        one operation
        """
        self._host = host
        self._http_client.setHost(host)
        self._port = port
        self._http_client.setPort(port)
        self._updateServer()

    def port(self):
        """
        Port display to user
        """
        return self._port

    def protocol(self):
        """
        Transport protocol
        """
        return self._protocol

    def user(self):
        """
        User login display to GNS3 user
        """
        return self._user

    def password(self):
        """
        User login display to GNS3 user
        """
        return self._password

    def server_id(self):
        """
        Return the remote server identifier
        """
        return self._server_id

    def id(self):
        """
        Returns this Server identifier.
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

    def setGNS3VM(self, value):
        """
        Sets either this is a connection to the GNS3 VM or not.

        :param value: boolean
        """

        self._gns3_vm = value

    def isGNS3VM(self):
        """
        Returns either this is a connection to the GNS3 VM or not.

        :returns: boolean
        """

        return self._gns3_vm

    def acceptInsecureCertificate(self, certificate=None):
        """
        Does the server accept this insecure SSL certificate digest

        :param: Certificate digest
        """
        return self._accept_insecure_certificate

    def setAcceptInsecureCertificate(self, certificate):
        """
        Does the server accept this insecure SSL certificate digest

        :param: Certificate digest
        """
        self._accept_insecure_certificate = certificate
        self._http_client.setAcceptInsecureCertificate(certificate)
        self._updateServer()

    def settings(self):
        """
        Return a dictionary with server settings
        """
        settings = {"protocol": self.protocol(),
                    "host": self.host(),
                    "port": self.port(),
                    "user": self.user(),
                    "password": self._password}
        if self.protocol() == "https":
            settings["accept_insecure_certificate"] = self.acceptInsecureCertificate()
        return settings

    def url(self):
        """Returns current server url"""

        return getNetworkUrl(self.protocol(), self.host(), self.port(), self.user(), self.settings())

    def systemUsage(self):
        """
        Get information about current system usage

        :returns: None or dict
        """
        return self._usage

    def setSystemUsage(self, usage):
        if self._connected is False:
            self._connected = True
            self.connection_connected_signal.emit()
        self._usage = usage
        self.system_usage_updated_signal.emit()

    def dump(self):
        """
        Returns a representation of this server.
        :returns: dictionary
        """

        server = self.settings()
        server["id"] = self._id
        server["local"] = self._local
        server["vm"] = self._gns3_vm
        if "user" in server and self._local:
            del server["user"]
        if "password" in server:
            del server["password"]
        if server["protocol"] == "https":
            server["accept_insecure_certificate"] = self._accept_insecure_certificate
        return server

    @staticmethod
    def reset():
        """Reset HTTP client internal variables"""

        Server._instance_count = 0

    def get(self, *args, **kwargs):
        """
        Forward the query to the HTTP client
        """
        return self.createHTTPQuery("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Forward the query to the HTTP client
        """
        return self.createHTTPQuery("POST", *args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Forward the query to the HTTP client
        """
        return self.createHTTPQuery("PUT", *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Forward the query to the HTTP client
        """
        return self.createHTTPQuery("DELETE", *args, **kwargs)

    def createHTTPQuery(self, method, path, *args, **kwargs):
        """
        Forward the query to the HTTP client
        """
        path = "/compute" + path
        return self._http_client.createHTTPQuery(method, path, *args, server=self, **kwargs)

    def getSynchronous(self, path, *args, **kwargs):
        """
        Forward the query to the HTTP client
        """
        path = "compute/" + path
        return self._http_client.getSynchronous(path, *args, **kwargs)

    def connected(self):
        return self._connected

    def close(self):
        """
        Closes the connection with the server.
        """
        log.debug("Connection to %s closed", self.url())
        self._http_client.close()
        self._connected = False
        self.connection_closed_signal.emit()
