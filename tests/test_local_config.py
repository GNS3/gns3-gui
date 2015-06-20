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
import json

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


def test_readConfig(config_file):
    config = LocalConfig()
    config._settings = {}
    config.setConfigFilePath(config_file)
    assert config.configFilePath() == config_file

    section = config.loadSectionSettings("VirtualBox", {
        "use_local_server": False
    })
    assert section["use_local_server"] == True
    assert "invalid_key" not in section


def test_readConfigReload(config_file, tmpdir):
    config = LocalConfig()
    config._settings = {}
    config.setConfigFilePath(config_file)
    assert config.configFilePath() == config_file

    section = config.loadSectionSettings("VirtualBox", {
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

    config._readConfig(config_file)
    assert config._settings["VirtualBox"]["use_local_server"] == False
