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


def test_loadSettings_EmptySettings(local_config, tmpdir):

    with open(str(tmpdir / "test.cfg"), "w+") as f:
        json.dump({
            "version": "1.4"
        }, f)

    local_config.setConfigFilePath(str(tmpdir / "test.cfg"))

    Servers._instance = None
    servers = Servers.instance()

    assert servers.localServerSettings()["port"] == 3080
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


def test_loadSettingsWith13LocalServerSetting(tmpdir, local_config):
    with open(str(tmpdir / "test.cfg"), "w+") as f:
        json.dump({
            "Servers": {
                "local_server": {
                    "auth": True,
                    "user": "world",
                    "password": "hello"
                }
            },
            "LocalServer": {
                "auth": False
            },
            "version": "1.4"
        }, f)

    local_config.setConfigFilePath(str(tmpdir / "test.cfg"))
    Servers._instance = None
    servers = Servers.instance()

    local_server = local_config.loadSectionSettings("LocalServer", {})

    assert local_server["auth"] == True
    assert local_server["user"] == "world"
    assert local_server["password"] == "hello"


def testServers():
    servers = Servers.instance()
    http_server = servers.getRemoteServer("http", "localhost", 3080, None)
    assert len(servers.servers()) == 2


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


def test_handle_handleSslErrors():
    """
    Simulate when user accept an insecure certificate. This should be save to the configuration
    """

    servers = Servers.instance()

    servers._addRemoteServer("https", "127.0.0.1", "443", user="root", password="toto")
    servers._saveSettings()
    assert servers._settings["remote_servers"] == [
        {
            'accept_insecure_certificate': None,
            'host': '127.0.0.1',
            'password': 'toto',
            'port': 443,
            'protocol': 'https',
            'url': 'https://root@127.0.0.1:443',
            'user': 'root'
        }
    ]

    reply = MagicMock()
    reply.url.return_value.toDisplayString.return_value = "https://root@127.0.0.1:443/v1/version"
    ssl_error = MagicMock()
    ssl_error.certificate.return_value.digest.return_value = binascii.unhexlify("cca0a932ced2fb1b1a18c823542cb065")
    errorList = [ssl_error]

    with patch("gns3.qt.QtWidgets.QMessageBox.warning") as message_box_mock:
        message_box_mock.return_value = QtWidgets.QMessageBox.Yes
        servers._handleSslErrors(reply, errorList)

    servers._saveSettings()
    assert len(servers._settings["remote_servers"]) == 1
    assert servers._settings["remote_servers"] == [
        {
            'accept_insecure_certificate': 'cca0a932ced2fb1b1a18c823542cb065',
            'host': '127.0.0.1',
            'password': 'toto',
            'port': 443,
            'protocol': 'https',
            'url': 'https://root@127.0.0.1:443',
            'user': 'root'
        }
    ]


@pytest.mark.skipif(sys.platform.startswith('win') is True, reason='Not for windows')
def test_startLocalServer(tmpdir, local_config):
    local_server_path = str(tmpdir / "gns3server")
    open(local_server_path, "w+").close()

    with open(str(tmpdir / "test.cfg"), "w+") as f:
        json.dump({
            "Servers": {
                "local_server": {
                    "path": local_server_path,
                }
            },
            "version": "1.4"
        }, f)

    local_config.setConfigFilePath(str(tmpdir / "test.cfg"))
    Servers._instance = None

    with patch("gns3.local_config.LocalConfig.configDirectory") as mock_local_config:
        mock_local_config.return_value = str(tmpdir)
        process_mock = MagicMock()
        with patch("subprocess.Popen", return_value=process_mock) as mock:

            # If everything work fine the command is still running and a timeout is raised
            process_mock.communicate.side_effect = subprocess.TimeoutExpired("test", 1)

            Servers.instance().startLocalServer()
            mock.assert_called_with([local_server_path,
                                     '--host=127.0.0.1',
                                     '--port=3080',
                                     '--local',
                                     '--controller',
                                     '--debug',
                                     '--log='  + str(tmpdir / "gns3_server.log"),
                                     '--pid=' + str(tmpdir / "gns3_server.pid")
                                    ])


def test_killAlreadyRunningServer(tmpdir):
    with patch("gns3.local_config.LocalConfig.configDirectory") as mock_local_config:
        mock_local_config.return_value = str(tmpdir)

        with open(str(tmpdir / "gns3_server.pid"), "w+") as f:
            f.write("42")

        mock_process = MagicMock()
        with patch("psutil.Process", return_value=mock_process) as mock:
            Servers.instance()._killAlreadyRunningServer()
            mock.assert_called_with(pid=42)
            assert mock_process.kill.called

