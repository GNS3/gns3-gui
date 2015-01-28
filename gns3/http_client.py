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

"""
Non-blocking HTTP client with JSON support to connect to GNS3 servers.
"""

import json
import socket
import urllib.request
from functools import partial
from urllib.parse import urlparse

from .version import __version__
from .qt import QtCore, QtNetwork

import logging
log = logging.getLogger(__name__)


class HTTPClient:

    """
    HTTP client.

    :param url: URL to connect to the server
    :param network_manager: A QT network manager
    """

    _instance_count = 1

    def __init__(self, url, network_manager):

        self._url = url
        self._version = ""

        url_settings = urlparse(url)
        self.scheme = url_settings.scheme
        self.host = url_settings.netloc.split(":")[0]
        self.port = url_settings.port

        # TODO: Should be False at startup
        self._connected = True

        self._local = True
        self._cloud = False

        self._network_manager = network_manager
        # self.check_server_version()

        # create an unique ID
        self._id = HTTPClient._instance_count
        HTTPClient._instance_count += 1

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

        # FIXME: temporary version check
        if self._version != __version__:
            if not self._version:
                raise OSError("Could not determine the server version")
            else:
                raise OSError("GUI version {} differs with the server version: {}".format(__version__, self._version))
            self.close_connection()

    def send_message(self, destination, params, callback):
        """
        Sends a message to the server.

        :param destination: server destination method
        :param params: params to send (dictionary)
        :param callback: callback method to call when the server replies.
        """

        log.error("OLD Send message. Destination {destination}, {params}".format(destination=destination, params=params))
        # TODO : Remove this method when migration to rest api is done

    def send_notification(self, destination, params=None):
        """
        Sends a notification to the server. No reply is expected from the server.

        :param destination: server destination method
        :param params: params to send (dictionary)
        """
        log.error("OLD Send notification. Destination {destination}, {params}".format(destination=destination, params=params))
        # TODO : Remove this method when migration to rest api is done

    def post(self, path, body, callback):
        """
        HTTP post on the remote server

        :param path: Remote path
        :param body: params to send (dictionary)
        :param callback: callback method to call when the server replies.
        """

        self._create_http_query("POST", path, body, callback)

    def _create_http_query(self, method, path, body, callback):
        """
        Call the remote server

        :param method: HTTP method
        :param path: Remote path
        :param body: params to send (dictionary)
        :param callback: callback method to call when the server replies.
        """

        if len(body):
            body = json.dumps(body)
        log.debug("{method} {scheme}://{host}:{port}{path} {body}".format(method=method, scheme=self.scheme, host=self.host, port=self.port, path=path, body=body))
        url = QtCore.QUrl("{scheme}://{host}:{port}{path}".format(scheme=self.scheme, host=self.host, port=self.port, path=path))
        request = QtNetwork.QNetworkRequest(url)
        request.setRawHeader("Content-Type", "application/json")
        request.setRawHeader("Content-Length", str(len(body)))
        request.setRawHeader("User-Agent", "GNS3 QT Client {version}".format(version=__version__))

        if method == "POST":
            response = self._network_manager.post(request, body)

        response.finished.connect(partial(self.response_process, response, callback))

    def response_process(self, response, callback):
        if response.error() != QtNetwork.QNetworkReply.NoError:
            log.debug("Response error: {}".format(response.errorString()))
            body = bytes(response.readAll()).decode()
            log.debug(body)
        else:
            status = response.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
            log.debug("Decoding response from {} response {}".format(response.url().toString(), status))
            body = bytes(response.readAll()).decode()
            log.debug(body)
            if len(body):
                params = json.loads(body)
            else:
                params = {}
            if status >= 400:
                callback(params, error=True)
            else:
                callback(params)

    def dump(self):
        """
        Returns a representation of this server.
        :returns: dictionary
        """

        return {"id": self._id,
                "host": self.host,
                "port": self.port,
                "local": self._local,
                "cloud": self._cloud}
