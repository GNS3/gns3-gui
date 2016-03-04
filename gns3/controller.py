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

import logging
log = logging.getLogger(__name__)


class Controller(QtCore.QObject):
    """
    An instance of the GNS3 server controller
    """

    def __init__(self, http_client):
        """
        :param http_client: Instance of HTTP client to communicate with the server
        """
        super().__init__()
        self._http_client = http_client

    def get(self, *args, **kwargs):
        """
        Forward the query to the HTTP client
        """
        return self._http_client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Forward the query to the HTTP client
        """
        return self._http_client.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Forward the query to the HTTP client
        """
        return self._http_client.put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Forward the query to the HTTP client
        """
        return self._http_client.delete(*args, **kwargs)

    def addServer(self, server):
        log.debug("Add server %s to the controller", server.server_id())
        self.post("/servers", None, body={
            "server_id": server.server_id(),
            "protocol": server.protocol(),
            "host": server.host(),
            "port": server.port(),
            "user": server.user(),
            "password": server.password()
        })
