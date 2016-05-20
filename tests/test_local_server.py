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

import sys
import json
import pytest
import subprocess
from unittest.mock import MagicMock, patch

from gns3.local_server import LocalServer
from gns3.local_server_config import LocalServerConfig


@pytest.fixture
def local_server_path(tmpdir):
    return str(tmpdir / "gns3server")


@pytest.fixture
def local_server(local_server_path, tmpdir):
    with patch("gns3.local_config.LocalConfig.configDirectory") as mock_local_config:
        mock_local_config.return_value = str(tmpdir)
        LocalServer._instance = None
        local_server = LocalServer.instance()
        local_server._settings = {
            "host": "127.0.0.1",
            "path": local_server_path,
            "port": 3080,
            "allow_console_from_anywhere": False
        }
        return local_server


def test_loadSettings_EmptySettings(tmpdir, local_server):

    with open(str(tmpdir / "test.cfg"), "w+") as f:
        f.write("")
    LocalServerConfig.instance().setConfigFile(str(tmpdir / "test.cfg"))

    assert local_server.localServerSettings()["port"] == 3080
    assert len(local_server.localServerSettings()["password"]) == 64
    assert local_server.localServerSettings()["user"] == "admin"



def test_loadSettings(tmpdir, local_server):
    with open(str(tmpdir / "test.cfg"), "w+") as f:
        f.write("""
[Server]
auth=True
user=world
password=hello""")

    LocalServerConfig.instance().setConfigFile(str(tmpdir / "test.cfg"))
    assert local_server.localServerSettings()["password"] == "hello"


def test_httpClient(local_server):
    client = local_server.httpClient()
    assert client.host() == "127.0.0.1"


@pytest.mark.skipif(sys.platform.startswith('win') is True, reason='Not for windows')
def test_startLocalServer(tmpdir, local_server, local_server_path):
    process_mock = MagicMock()
    with patch("subprocess.Popen", return_value=process_mock) as mock:

        # If everything work fine the command is still running and a timeout is raised
        process_mock.communicate.side_effect = subprocess.TimeoutExpired("test", 1)

        LocalServer.instance().startLocalServer()
        mock.assert_called_with([local_server_path,
                                 '--host=127.0.0.1',
                                 '--port=3080',
                                 '--local',
                                 '--controller',
                                 '--debug',
                                 '--log='  + str(tmpdir / "gns3_server.log"),
                                 '--pid=' + str(tmpdir / "gns3_server.pid")
                                ])


def test_killAlreadyRunningServer(local_server):
    with open(local_server._pid_path, "w+") as f:
        f.write("42")

    mock_process = MagicMock()
    with patch("psutil.Process", return_value=mock_process) as mock:
        LocalServer.instance()._killAlreadyRunningServer()
        mock.assert_called_with(pid=42)
        assert mock_process.kill.called


