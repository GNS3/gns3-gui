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

import uuid


class Compute:
    """
    An instance of a compute.
    """

    def __init__(self, compute_id=None):

        if compute_id is None:
            compute_id = str(uuid.uuid4())
        self._compute_id = compute_id
        self._name = compute_id
        self._connected = False
        self._protocol = "http"
        self._host = None
        self._port = 3080
        self._user = None
        self._password = None
        self._cpu_usage_percent = None
        self._memory_usage_percent = None
        self._disk_usage_percent = None
        self._capabilities = {"node_types": []}
        self._last_error = None

    def id(self):
        """
        Returns the compute ID.

        :returns: compute identifier
        """

        return self._compute_id

    def name(self):
        """
        Returns the compute name.

        :returns: compute name
        """

        return self._name

    def setName(self, name):
        """
        Sets the compute name.

        :param name: compute name
        """

        self._name = name

    def connected(self):
        """
        Returns whether or not there is a connection to the compute.

        :returns: boolean
        """

        return self._connected

    def setConnected(self, value):
        """
        Sets whether or not there is a connection to the compute.

        :param value: boolean
        """

        self._connected = value

    def host(self):
        """
        Returns the compute host.

        :returns: host (string)
        """

        return self._host

    def setHost(self, host):
        """
        Sets the compute host.

        :param host: host (string)
        """

        self._host = host

    def port(self):
        """
        Returns the compute port number.

        :returns: port number (integer)
        """

        return self._port

    def setPort(self, port):
        """
        Sets the compute port number.

        :param port: port number (integer)
        """

        self._port = port

    def user(self):
        """
        Returns the compute user for HTTP authentication.

        :returns: user (string)
        """

        return self._user

    def setUser(self, user):
        """
        Sets the compute user for HTTP authentication.

        :param user: user (string)
        """

        self._user = user

    def setPassword(self, password):
        """
        Returns the compute password for HTTP authentication.

        :returns: password (string)
        """

        self._password = password

    def protocol(self):
        """
        Returns the compute protocol.

        :returns: protocol (string)
        """

        return self._protocol

    def setProtocol(self, protocol):
        """
        Sets the compute protocol.

        :param protocol: protocol (string)
        """

        self._protocol = protocol

    def cpuUsagePercent(self):
        """
        Returns the compute CPU usage.

        :returns: CPU usage (integer)
        """

        return self._cpu_usage_percent

    def setCpuUsagePercent(self, usage):
        """
        Sets the compute CPU usage.

        :param usage: CPU usage (integer)
        """

        self._cpu_usage_percent = usage

    def setMemoryUsagePercent(self, usage):
        """
        Returns the compute memory usage.

        :returns: memory usage (integer)
        """

        self._memory_usage_percent = usage

    def memoryUsagePercent(self):
        """
        Sets the compute memory usage.

        :param usage: memory usage (integer)
        """

        return self._memory_usage_percent

    def setDiskUsagePercent(self, usage):
        """
        Sets the compute disk usage.

        :returns: disk usage (integer)
        """

        self._disk_usage_percent = usage

    def diskUsagePercent(self):
        """
        Returns the compute disk usage.

        :param usage: disk usage (integer)
        """

        return self._disk_usage_percent

    def capabilities(self):
        """
        Returns the compute capabilities

        :returns: capabilities (dictionary)
        """

        return self._capabilities

    def setCapabilities(self, value):
        """
        Sets the compute capabilities

        :param value: capabilities (dictionary)
        """

        self._capabilities = value

    def setLastError(self, last_error):
        self._last_error = last_error

    def lastError(self):
        return self._last_error

    def __str__(self):

        return self._compute_id

    def __json__(self):

        return {"host": self._host,
                "port": self._port,
                "protocol": self._protocol,
                "user": self._user,
                "password": self._password,
                "name": self._name,
                "compute_id": self._compute_id}

    def __eq__(self, v):

        if isinstance(v, Compute):
            return self.__json__() == v.__json__()
        return False
