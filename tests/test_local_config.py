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

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

from gns3.local_config import LocalConfig


@pytest.fixture
def config_file(tmpdir):
    with open(str(tmpdir / "test.cfg"), "w+") as f:
        f.write(json.dumps({
            "VirtualBox": {
                "use_local_server": True,
                "invalid_key": False,
            },
            "VPCS": {
                "vpcs_path": "/usr/local/bin/vpcs"
            },
            "type": "settings",
            "version": "1.4.0.dev1"}))
    return str(tmpdir / "test.cfg")


def test_loadSectionSettingsEmptyFile(local_config):

    assert local_config.loadSectionSettings("Test", {}) == {}
    assert local_config.loadSectionSettings("Test2", {"a": "b"}) == {"a": "b"}
    assert local_config.loadSectionSettings("Test3", {"a": {"b": 1}}) == {"a": {"b": 1}}


def test_loadSectionSettingsPartialConfig(local_config):

    local_config._settings = {
        "Test": {"a": "b"},
        "Test2": {"a": "c"},
        "Test3": {"a": {"b": 1}},
        "Servers": {
            "local_server": {"user": "root"},
            "remote_servers": [
                {"z": "x"}
            ]
        }
    }

    assert local_config.loadSectionSettings("Test", {}) == {"a": "b"}
    assert local_config.loadSectionSettings("Test2", {"a": "b"}) == {"a": "c"}
    assert local_config.loadSectionSettings("Test3", {"a": {"b": 1}}) == {"a": {"b": 1}}
    assert local_config.loadSectionSettings("Servers", {
        "local_server": {"user": "", "password": ""},
        "remote_servers": []
    }) == {
        "local_server": {"user": "root", "password": ""},
        "remote_servers": [
            {"z": "x"}
        ]
    }


def test_readConfig(config_file, local_config):
    local_config.setConfigFilePath(config_file)
    assert local_config.configFilePath() == config_file

    section = local_config.loadSectionSettings("VirtualBox", {
        "use_local_server": False
    })
    assert section["use_local_server"] == True
    assert "invalid_key" in section


def test_readConfigReload(config_file, tmpdir, local_config):

    local_config.setConfigFilePath(config_file)
    assert local_config.configFilePath() == config_file

    section = local_config.loadSectionSettings("VirtualBox", {
        "use_local_server": False
    })

    assert section["use_local_server"] == True

    with open(str(tmpdir / "test.cfg"), "w+") as f:
        f.write(json.dumps({
            "VirtualBox": {
                "use_local_server": False
            },
            "type": "settings",
            "version": "1.4.0.dev1"}))

    local_config._readConfig(config_file)
    assert local_config._settings["VirtualBox"]["use_local_server"] == False


@pytest.mark.skipif(sys.platform.startswith('darwin') is False, reason='Only on MacOS')
def test_migrateOldConfigOSX(tmpdir):

    with patch('os.path.expanduser', return_value=str(tmpdir)):

        os.makedirs(str(tmpdir / '.config' / 'gns3.net'))
        open(str(tmpdir / '.config' / 'gns3.net' / 'hello'), 'w+').close()

        local_config = LocalConfig()

        assert os.path.exists(str(tmpdir / '.config' / 'GNS3'))
        assert os.path.exists(str(tmpdir / '.config' / 'GNS3' / 'hello'))
        assert os.path.exists(str(tmpdir / '.config' / 'gns3.net'))

        # It should migrate only one time
        open(str(tmpdir / '.config' / 'gns3.net' / 'world'), 'w+').close()

        local_config._migrateOldConfigPath()
        assert os.path.exists(str(tmpdir / '.config' / 'GNS3' / 'hello'))
        assert not os.path.exists(str(tmpdir / '.config' / 'GNS3' / 'world'))


def test_migrate13Config(tmpdir):
    local_config = LocalConfig()

    config_file = str(tmpdir / "gns3_gui.conf")

    server_config = {
        "allow_console_from_anywhere": True,
        "auth": False,
        "auto_start": True,
        "console_end_port_range": 5000,
        "console_start_port_range": 2001,
        "host": "127.0.0.1",
        "images_path": "/home/gns3/GNS3/images",
        "password": "",
        "path": "/bin/gns3server",
        "port": 8001,
        "projects_path": "/home/gns3/GNS3/projects",
        "report_errors": False,
        "udp_end_port_range": 20000,
        "udp_start_port_range": 10000,
        "user": ""
    }

    with open(config_file, "w+") as f:
        f.write(json.dumps({
            "LocalServer": server_config,
            "RemoteServers": [
                server_config
            ],
            "GUI": {
                "hide_getting_started_dialog": True
            },
            "type": "settings",
            "version": "1.3.7"}))

    local_config._readConfig(config_file)
    local_config._migrateOldConfig()

    # The old config should not be erased in order to avoid losing data when rollback to 1.3
    assert local_config._settings["LocalServer"] == server_config
    assert local_config._settings["RemoteServers"] == [server_config]
    assert local_config._settings["Servers"]["local_server"] == server_config
    assert local_config._settings["Servers"]["remote_servers"] == [server_config]
    assert local_config._settings["MainWindow"]["hide_getting_started_dialog"] == True

    # When the file is migrated to 1.4 we should not try to modify it
    with open(config_file, "w+") as f:
        f.write(json.dumps({
            "LocalServer": {"host": "error"},
            "type": "settings",
            "version": "1.4.2"}))

    local_config._readConfig(config_file)
    local_config._migrateOldConfig()

    assert local_config._settings["LocalServer"]["host"] == "error"
    assert local_config._settings["Servers"]["local_server"]["host"] == "127.0.0.1"


def test_migrate13ConfigOldOsxServerPath(tmpdir):
    local_config = LocalConfig()

    config_file = str(tmpdir / "gns3_gui.conf")

    server_config = {
        "allow_console_from_anywhere": True,
        "auth": False,
        "auto_start": True,
        "console_end_port_range": 5000,
        "console_start_port_range": 2001,
        "host": "127.0.0.1",
        "images_path": "/home/gns3/GNS3/images",
        "password": "",
        "path": "/Applications/GNS3.app/Contents/Resources/server/Contents/MacOS/gns3server",
        "port": 8001,
        "projects_path": "/home/gns3/GNS3/projects",
        "report_errors": False,
        "udp_end_port_range": 20000,
        "udp_start_port_range": 10000,
        "user": ""
    }

    with open(config_file, "w+") as f:
        f.write(json.dumps({
            "LocalServer": server_config,
            "RemoteServers": [
                server_config
            ],
            "type": "settings",
            "version": "1.3.7"}))

    local_config._readConfig(config_file)
    local_config._migrateOldConfig()

    # The old config should not be erased in order to avoid losing data when rollback to 1.3
    assert local_config._settings["LocalServer"]["path"] == "/Applications/GNS3.app/Contents/Resources/server/Contents/MacOS/gns3server"
    assert local_config._settings["Servers"]["local_server"]["path"] == "/Applications/GNS3.app/Contents/MacOS/gns3server"


def test_isMainGui_pid_file_not_exist(tmpdir):
    with patch("gns3.local_config.LocalConfig.configDirectory") as mock_config_directory:
        mock_config_directory.return_value = str(tmpdir)
        assert LocalConfig().isMainGui() is True
        assert os.path.exists(str(tmpdir / "gns3_gui.pid"))


def test_isMainGui_pid_file_exist_but_different(tmpdir):
    with open(str(tmpdir / "gns3_gui.pid"), "w+") as f:
        f.write("42")

    mock_process = MagicMock()
    mock_process.name.return_value = "gns3.exe"
    mock_process.uids.return_value = (os.getuid(), os.getuid(), os.getuid())
    with patch("psutil.Process", return_value=mock_process) as mock:
        with patch("gns3.local_config.LocalConfig.configDirectory") as mock_config_directory:
            mock_config_directory.return_value = str(tmpdir)
            assert LocalConfig().isMainGui() is False


def test_isMainGui_pid_file_exist_but_different_proces_dead(tmpdir):
    with open(str(tmpdir / "gns3_gui.pid"), "w+") as f:
        f.write("42")

    mock_process = MagicMock()
    with patch("psutil.Process", return_value=mock_process) as mock:
        mock.name.side_effect = (lambda: exec('raise(OSError())'))
        with patch("gns3.local_config.LocalConfig.configDirectory") as mock_config_directory:
            mock_config_directory.return_value = str(tmpdir)
            assert LocalConfig().isMainGui() is True


def test_isMainGui_pid_file_exist_but_same_pid(tmpdir):
    with open(str(tmpdir / "gns3_gui.pid"), "w+") as f:
        f.write("42")

    with patch("os.getpid", return_value=42):
        with patch("gns3.local_config.LocalConfig.configDirectory") as mock_config_directory:
            mock_config_directory.return_value = str(tmpdir)
            assert LocalConfig().isMainGui() is True
