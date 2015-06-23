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

import json
import pytest

from gns3.servers import Servers


def test_loadSettings_EmptySettings(local_config, tmpdir):

    with open(str(tmpdir / "test.cfg"), "w+") as f:
        json.dump({
            "version": "1.4"
        }, f)

    local_config.setConfigFilePath(str(tmpdir / "test.cfg"))

    Servers._instance = None
    servers = Servers.instance()

    assert servers.localServerSettings()["port"] == 8000
    assert len(servers.localServerSettings()["password"]) == 64
    assert len(servers.localServerSettings()["user"]) == 64

    with open(str(tmpdir / "test.cfg")) as f:
        conf = json.load(f)
        assert servers.localServerSettings()["password"] == conf["Servers"]["local_server"]["password"]
        assert servers.localServerSettings()["user"] == conf["Servers"]["local_server"]["user"]


def test_loadSettings(tmpdir, local_config):
    with open(str(tmpdir / "test.cfg"), "w+") as f:
        json.dump({
            "Servers": {
                "local_server": {
                    "auth": True,
                    "user": "world",
                    "password": "hello"
                }
            },
            "version": "1.4"
        }, f)

    local_config.setConfigFilePath(str(tmpdir / "test.cfg"))
    Servers._instance = None
    servers = Servers.instance()

    assert servers.localServerSettings()["password"] == "hello"


def test_getRemoteServer():
    servers = Servers.instance()
    http_server = servers.getRemoteServer("http", "localhost", 8000, None)
    assert http_server.protocol() == "http"
    assert http_server.host() == "localhost"
    assert http_server.port() == 8000
    assert http_server.user() is None

    ssh_server = servers.getRemoteServer("ssh", "127.0.0.1", 4000, "gns3", settings={"ssh_port": 22, "ssh_key": "/tmp/test.ssh"})
    assert ssh_server.protocol() == "ssh"
    assert ssh_server.host() == "127.0.0.1"
    assert ssh_server.port() == 4000
    assert ssh_server.user() == "gns3"
    assert ssh_server.ssh_port() == 22
    assert ssh_server.ssh_key() == "/tmp/test.ssh"


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


def test_getServerFromString_with_ssh():

    servers = Servers.instance()
    servers._addRemoteServer("ssh", "127.0.0.1", "4000", user="root", ssh_port=22, ssh_key="/tmp/test.ssh")
    server = servers.getServerFromString("ssh://root@127.0.0.1:22:4000")
    assert server.protocol() == "ssh"
    assert server.host() == "127.0.0.1"
    assert server.port() == 4000
    assert server.user() == "root"
    assert server.ssh_port() == 22
    assert server.ssh_key() == "/tmp/test.ssh"
