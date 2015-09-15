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
import os
from unittest.mock import MagicMock, patch

from gns3.registry.config import Config, ConfigException


@pytest.fixture(scope="function")
def empty_config(tmpdir, images_dir):
    config = {
        "Servers": {
            "local_server": {
                "allow_console_from_anywhere": False,
                "auto_start": False,
                "console_end_port_range": 5000,
                "console_start_port_range": 2001,
                "host": "127.0.0.1",
                "images_path": images_dir,
                "path": "",
                "port": 8000,
                "projects_path": str(tmpdir),
                "report_errors": False,
                "udp_end_port_range": 20000,
                "udp_start_port_range": 10000
            }
        },
        "Dynamips": {
            "allocate_aux_console_ports": False,
            "dynamips_path": "/Applications/GNS3.app/Contents/Resources/dynamips",
            "ghost_ios_support": True,
            "mmap_support": True,
            "routers": [
                {
                }
            ],
            "sparse_memory_support": True,
            "use_local_server": True
        },
        "IOU": {
            "appliances": [
                {
                }
            ],
            "iourc_path": "/Users/noplay/code/gns3/gns3-vagrant/images/iou/iourc.txt",
            "iouyap_path": "",
            "license_check": True,
            "use_local_server": False
        },
        "Qemu": {
            "use_local_server": True,
            "vms": [
            ]
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


def test_add_appliance_guest(empty_config, linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "path": linux_microcore_img
        }
    ]
    empty_config.add_appliance(config, "local")
    assert empty_config._config["Qemu"]["vms"][0] == {
        "adapter_type": "e1000",
        "adapters": 1,
        "category": 2,
        "cpu_throttling": 0,
        "console_type": "telnet",
        "symbol": ":/symbols/qemu_guest.svg",
        "hda_disk_image": "linux-microcore-3.4.1.img",
        "hdb_disk_image": "",
        "hdc_disk_image": "",
        "hdd_disk_image": "",
        "cdrom_image": "",
        "initrd_image": "",
        "kernel_command_line": "",
        "kernel_image": "",
        "legacy_networking": False,
        "name": "Micro Core Linux",
        "options": "",
        "process_priority": "normal",
        "qemu_path": "qemu-system-i386",
        "ram": 32,
        "server": "local"
    }


def test_add_appliance_with_symbol(empty_config, linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "path": linux_microcore_img
        }
    ]
    config["symbol"] = ":/symbols/asa.svg"
    empty_config.add_appliance(config, "local")
    assert empty_config._config["Qemu"]["vms"][0]["symbol"] == ":/symbols/asa.svg"


def test_add_appliance_with_boot_priority(empty_config, linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "path": linux_microcore_img
        }
    ]
    config["boot_priority"] = "dc"
    empty_config.add_appliance(config, "local")
    assert empty_config._config["Qemu"]["vms"][0]["boot_priority"] == "dc"


def test_add_appliance_router_two_disk(empty_config, images_dir):
    with open("tests/registry/appliances/arista-veos.json", encoding="utf-8") as f:
        config = json.load(f)


    config["images"] = [
        {
            "type": "hda_disk_image",
            "path": os.path.join(images_dir, "QEMU", "a")
        },
        {
            "type": "hdb_disk_image",
            "path": os.path.join(images_dir, "QEMU", "b")
        }
    ]

    empty_config.add_appliance(config, "local")

    assert empty_config._config["Qemu"]["vms"][0] == {
        "adapter_type": "e1000",
        "adapters": 8,
        "category": 0,
        "cpu_throttling": 0,
        "symbol": ":/symbols/router.svg",
        "hda_disk_image": "a",
        "hdb_disk_image": "b",
        "hdc_disk_image": "",
        "hdd_disk_image": "",
        "cdrom_image": "",
        "initrd_image": "",
        "kernel_command_line": "",
        "kernel_image": "",
        "legacy_networking": False,
        "name": "Arista vEOS",
        "options": "",
        "process_priority": "normal",
        "qemu_path": "qemu-system-x86_64",
        "ram": 2048,
        "console_type": "telnet",
        "server": "local"
    }


def test_add_appliance_uniq(empty_config, linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)

    config["images"] = [
        {
            "type": "hda_disk_image",
            "path": linux_microcore_img
        }
    ]
    empty_config.add_appliance(config, "local")

    config["qemu"]["adapters"] = 2

    with pytest.raises(ConfigException):
        empty_config.add_appliance(config, "local")

    assert len(empty_config._config["Qemu"]["vms"]) == 1
    assert empty_config._config["Qemu"]["vms"][0]["adapters"] == 1


def test_add_appliance_path_relative_to_images_dir(empty_config, tmpdir, linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)

    config["images"] = [
        {
            "type": "hda_disk_image",
            "path": linux_microcore_img
        }
    ]

    empty_config.add_appliance(config, "local")
    assert empty_config._config["Qemu"]["vms"][0]["hda_disk_image"] == "linux-microcore-3.4.1.img"


def test_add_appliance_path_non_relative_to_images_dir(empty_config, tmpdir, images_dir):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)

    config["images"] = [
        {
            "type": "hda_disk_image",
            "path": str(tmpdir / "a.img")
        }
    ]
    with open(str(tmpdir / "a.img"), "w+") as f:
        f.write("a")
    empty_config.add_appliance(config, "local")
    assert empty_config._config["Qemu"]["vms"][0]["hda_disk_image"] == "a.img"
    assert os.path.exists(os.path.join(images_dir, "QEMU", "a.img"))


def test_config_import_image(empty_config, images_dir, tmpdir):
    with open(str(tmpdir / "a.img"), "w+") as f:
        f.write("a")
    empty_config.import_image(str(tmpdir / "a.img"))

    assert os.path.exists(os.path.join(images_dir, "QEMU", "a.img"))


def test_save(empty_config, linux_microcore_img):

    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)

    config["images"] = [
        {
            "type": "hda_disk_image",
            "path": linux_microcore_img
        }
    ]

    empty_config.add_appliance(config, "local")
    empty_config.save()
    with open(empty_config.path) as f:
        assert "Micro Core" in f.read()
