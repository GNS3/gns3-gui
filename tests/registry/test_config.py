#!/usr/bin/env python
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

from gns3.registry.config import Config
from gns3.settings import LOCAL_SERVER_SETTINGS


@pytest.fixture(scope="function")
def empty_config(tmpdir, images_dir, symbols_dir, local_server_config):
    settings = local_server_config.loadSettings("Server", LOCAL_SERVER_SETTINGS)
    settings["images_path"] = images_dir
    settings["symbols_path"] = symbols_dir
    local_server_config.saveSettings("Server", settings)
    config = {
        "Servers": {
        },
        "Dynamips": {
            "allocate_aux_console_ports": False,
            "dynamips_path": "/Applications/GNS3.app/Contents/MacOS/dynamips",
            "ghost_ios_support": True,
            "mmap_support": True,
            "routers": [
            ],
            "sparse_memory_support": True,
            "use_local_server": True
        },
        "IOU": {
            "devices": [
            ],
            "license_check": True,
            "use_local_server": False
        },
        "Qemu": {
            "use_local_server": True,
            "vms": [
            ]
        },
        "Docker": {
            "containers": []
        }
    }
    path = str(tmpdir / "config")
    with open(path, "w+", encoding="utf-8") as f:
        json.dump(config, f)
    return Config(path)


def test_list_servers(empty_config):
    assert empty_config.servers == ["local"]


def test_list_servers_vm_enable(tmpdir):
    config = {
        "Servers": {
            "vm": {
                "auto_start": True,
            }
        }
    }
    path = str(tmpdir / "config")
    with open(path, "w+", encoding="utf-8") as f:
        json.dump(config, f)
    config = Config(path)
    assert config.servers == ["local", "vm"]


def test_list_servers_remote_servers(tmpdir):
    config = {
        "Servers": {
            "remote_servers": [
                {
                    "url": "http://darkside.moon:4242"
                }
            ]
        }
    }
    path = str(tmpdir / "config")
    with open(path, "w+", encoding="utf-8") as f:
        json.dump(config, f)
    config = Config(path)
    assert config.servers == ["local", "http://darkside.moon:4242"]
