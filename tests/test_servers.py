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

import sys
import json
import pytest
import binascii
import subprocess

from gns3.servers import Servers
from gns3.qt import QtWidgets
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def reset_server():
    Servers._instance = None


def testServers():
    servers = Servers.instance()
    http_server = servers.getRemoteServer("http", "localhost", 3080, None)
    assert len(servers.servers()) == 1


def test_getRemoteServer():
    servers = Servers.instance()
    http_server = servers.getRemoteServer("http", "localhost", 3080, None)
    assert http_server.protocol() == "http"
    assert http_server.host() == "localhost"
    assert http_server.port() == 3080
    assert http_server.user() is None


def test_getRemoteServerWithRamLimit():
    """
    Should ignore ram limit
    """
    servers = Servers.instance()
    http_server = servers.getRemoteServer("http", "localhost", 3080, None, {"ram_limit": 0})
    assert http_server.protocol() == "http"
    assert http_server.host() == "localhost"
    assert http_server.port() == 3080
    assert http_server.user() is None


def test_getServerFromString():

    servers = Servers.instance()
    server = servers.getServerFromString("127.0.0.1:4000")
    assert server.protocol() == "http"
    assert server.host() == "127.0.0.1"
    assert server.port() == 4000
    assert server.user() is None


def test_getServerFromString_with_user():

    servers = Servers.instance()
    server = servers.getServerFromString("http://root@127.0.0.1:4000")
    assert server.protocol() == "http"
    assert server.host() == "127.0.0.1"
    assert server.port() == 4000
    assert server.user() == "root"


def test_is_non_local_server_configured():

    servers = Servers.instance()

    assert servers.isNonLocalServerConfigured() is False
    servers._vm_server = object()
    assert servers.isNonLocalServerConfigured() is True
    servers._vm_server = None
    assert servers.isNonLocalServerConfigured() is False


def test_getServerInstance():
    servers = Servers.instance()
    # By default the controller is init for the test we erase it
    servers._controller_server = None

    server = servers._getServerInstance({"host": "example.com", "port": 42}, MagicMock(), controller=False)
    assert server.host() == "example.com"

    server = servers._getServerInstance({"host": "example2.com", "port": 42}, MagicMock(), controller=True)
    assert server.host() == "example2.com"
