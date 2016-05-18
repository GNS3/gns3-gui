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
def empty_config(tmpdir, images_dir, symbols_dir):
    config = {
        "Servers": {
            "local_server": {
                "allow_console_from_anywhere": False,
                "auto_start": False,
                "console_end_port_range": 5000,
                "console_start_port_range": 2001,
                "host": "127.0.0.1",
                "images_path": images_dir,
                "symbols_path": symbols_dir,
                "path": "",
                "port": 3080,
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
            ],
            "sparse_memory_support": True,
            "use_local_server": True
        },
        "IOU": {
            "devices": [
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


def test_add_appliance_iou(empty_config, iou_l3):
    with open("tests/registry/appliances/cisco-iou-l3.gns3a", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "image",
            "filename": "i86bi-linux-l3-adventerprisek9-15.4.1T.bin",
            "path": iou_l3
        }
    ]
    empty_config.add_appliance(config, "local")
    assert empty_config._config["IOU"]["devices"][0] == {
        "category": 0,
        "symbol": ":/symbols/router.svg",
        "server": "local",
        "name": "Cisco IOU L3",
        "l1_keepalives": False,
        "nvram": 128,
        "private_config": "",
        "ram": 256,
        "serial_adapters": 2,
        "ethernet_adapters": 2,
        "use_default_iou_values": True,
        "startup_config": "iou_l3_base_startup-config.txt",
        "image": os.path.basename(iou_l3),
        "path": os.path.basename(iou_l3)
    }


def test_add_appliance_docker(empty_config, iou_l3):
    with open("tests/registry/appliances/openvswitch.gns3a", encoding="utf-8") as f:
        config = json.load(f)

    empty_config.add_appliance(config, "local")
    assert empty_config._config["Docker"]["containers"][0] == {
        "name": "Open vSwitch",
        "image": "gns3/openvswitch",
        "category": 1,
        "symbol": ":/symbols/multilayer_switch.svg",
        "server": "local",
        "adapters": 16,
        "start_command": "",
        "environment": "",
        "usage": "By default all interfaces are connected to the br0",
        "console_type": "telnet",
        "console_http_port": 80,
        "console_http_path": "/"
    }



def test_add_appliance_dynamips(empty_config, cisco_3745):
    with open("tests/registry/appliances/cisco-3745.gns3a", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "image",
            "filename": "c3745-adventerprisek9-mz.124-25d.image",
            "path": cisco_3745,
            "idlepc": "0x60aa1da0"
        }
    ]
    empty_config.add_appliance(config, "local")
    assert empty_config._config["Dynamips"]["routers"][0] == {
        "auto_delete_disks": True,
        "category": 0,
        "chassis": "",
        "disk0": 0,
        "disk1": 0,
        "exec_area": 64,
        "idlemax": 500,
        "idlepc": "0x60aa1da0",
        "idlesleep": 30,
        "image": "c3745-adventerprisek9-mz.124-25d.image",
        "iomem": 5,
        "mac_addr": "",
        "mmap": True,
        "name": "Cisco 3745",
        "nvram": 256,
        "platform": "c3745",
        "private_config": "",
        "ram": 256,
        "server": "local",
        "slot0": "GT96100-FE",
        "slot1": "NM-1FE-TX",
        "slot2": "NM-4T",
        "slot3": "",
        "slot4": "",
        "sparsemem": True,
        "startup_config": "ios_base_startup-config.txt",
        "symbol": ":/symbols/router.svg",
        "system_id": "FTX0945W0MY",
        "wic0": "WIC-1T",
        "wic1": "WIC-1T",
        "wic2": "WIC-1T"
    }


def test_add_appliance_guest(empty_config, linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
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
        "initrd": "",
        "kernel_command_line": "",
        "kernel_image": "",
        "legacy_networking": False,
        "name": "Micro Core Linux",
        "options": "-nographic",
        "process_priority": "normal",
        "qemu_path": "qemu-system-i386",
        "usage": "Just start the appliance",
        "ram": 32,
        "server": "local",
        "hda_disk_interface": "ide",
        "hdb_disk_interface": "ide",
        "hdc_disk_interface": "ide",
        "hdd_disk_interface": "ide"
    }


def test_add_appliance_with_symbol(empty_config, linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]
    config["symbol"] = ":/symbols/asa.svg"
    empty_config.add_appliance(config, "local")
    assert empty_config._config["Qemu"]["vms"][0]["symbol"] == ":/symbols/asa.svg"


def test_add_appliance_with_symbol_from_symbols_dir(empty_config, linux_microcore_img, symbols_dir):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]
    config["symbol"] = "linux_guest.svg"

    symbol_path = os.path.join(symbols_dir, "linux_guest.svg")
    open(symbol_path, 'w+').close()

    empty_config.add_appliance(config, "local")
    assert empty_config._config["Qemu"]["vms"][0]["symbol"] == symbol_path


def test_add_appliance_with_symbol_from_web(empty_config, linux_microcore_img, symbols_dir):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]
    config["symbol"] = "linux_guest.svg"
    symbol_path = os.path.join(symbols_dir, "linux_guest.svg")

    with patch("urllib.request.urlretrieve") as mock:
        empty_config.add_appliance(config, "local")
        mock.assert_called_with("https://raw.githubusercontent.com/GNS3/gns3-registry/master/symbols/linux_guest.svg", symbol_path)
    assert empty_config._config["Qemu"]["vms"][0]["symbol"] == symbol_path


def test_add_appliance_with_symbol_from_web_error(empty_config, linux_microcore_img, symbols_dir):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]
    config["symbol"] = "linux_guest.svg"
    symbol_path = os.path.join(symbols_dir, "linux_guest.svg")

    with patch("urllib.request.urlretrieve") as mock:
        mock.side_effect = OSError
        empty_config.add_appliance(config, "local")
        mock.assert_called_with("https://raw.githubusercontent.com/GNS3/gns3-registry/master/symbols/linux_guest.svg", symbol_path)

    # In case of error we fallback on default symbol
    assert empty_config._config["Qemu"]["vms"][0]["symbol"] == ":/symbols/qemu_guest.svg"


def test_add_appliance_with_port_name_format(empty_config, linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]
    config["port_name_format"] = "eth{0}"
    empty_config.add_appliance(config, "local")
    assert empty_config._config["Qemu"]["vms"][0]["port_name_format"] == "eth{0}"


def test_add_appliance_with_boot_priority(empty_config, linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
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
            "filename": "a",
            "path": os.path.join(images_dir, "QEMU", "a")
        },
        {
            "type": "hdb_disk_image",
            "filename": "b",
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
        "initrd": "",
        "kernel_command_line": "",
        "kernel_image": "",
        "legacy_networking": False,
        "name": "Arista vEOS",
        "options": "-nographic",
        "process_priority": "normal",
        "qemu_path": "qemu-system-x86_64",
        "ram": 2048,
        "console_type": "telnet",
        "server": "local",
        "hda_disk_interface": "ide",
        "hdb_disk_interface": "ide",
        "hdc_disk_interface": "ide",
        "hdd_disk_interface": "ide"
    }


def test_add_appliance_uniq(empty_config, linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)

    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
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
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]

    empty_config.add_appliance(config, "local")
    assert empty_config._config["Qemu"]["vms"][0]["hda_disk_image"] == "linux-microcore-3.4.1.img"


def test_add_appliance_ova(empty_config, tmpdir, images_dir):
    with open("tests/registry/appliances/juniper-vsrx.gns3a", encoding="utf-8") as f:
        config = json.load(f)

    os.makedirs(os.path.join(images_dir, "QEMU", "junos-vsrx-12.1X47-D10.4-domestic.ova"))
    open(os.path.join(images_dir, "QEMU", "junos-vsrx-12.1X47-D10.4-domestic.ova", "junos-vsrx-12.1X47-D10.4-domestic-disk1.vmdk"), "w+").close()

    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "junos-vsrx-12.1X47-D10.4-domestic.ova/junos-vsrx-12.1X47-D10.4-domestic-disk1.vmdk",
            "path": os.path.join(images_dir, "QEMU", "junos-vsrx-12.1X47-D10.4-domestic.ova", "junos-vsrx-12.1X47-D10.4-domestic-disk1.vmdk")
        }
    ]

    empty_config.add_appliance(config, "local")
    assert empty_config._config["Qemu"]["vms"][0]["hda_disk_image"] == os.path.join("junos-vsrx-12.1X47-D10.4-domestic.ova", "junos-vsrx-12.1X47-D10.4-domestic-disk1.vmdk")


def test_add_appliance_path_non_relative_to_images_dir(empty_config, tmpdir, images_dir):
    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)

    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "a.img",
            "path": str(tmpdir / "a.img")
        }
    ]
    with open(str(tmpdir / "a.img"), "w+") as f:
        f.write("a")
    empty_config.add_appliance(config, "local")
    assert empty_config._config["Qemu"]["vms"][0]["hda_disk_image"] == "a.img"
    assert os.path.exists(os.path.join(images_dir, "QEMU", "a.img"))


def test_save(empty_config, linux_microcore_img):

    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)

    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]

    empty_config.add_appliance(config, "local")
    empty_config.save()
    with open(empty_config.path) as f:
        assert "Micro Core" in f.read()


def test_is_name_available(empty_config, linux_microcore_img):

    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)

    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]

    assert empty_config.is_name_available(config["name"]) is True
    empty_config.add_appliance(config, "local")
    empty_config.save()
    assert empty_config.is_name_available(config["name"]) is False


def test_relative_image_path(empty_config, images_dir, tmpdir):

    # Image in image directory no need to copy it
    open(os.path.join(images_dir, "QEMU", "a"), "w+").close()
    with patch("gns3.registry.image.Image.copy") as mock:
        assert empty_config._relative_image_path("QEMU", "a", os.path.join(images_dir, "QEMU", "a")) == "a"
        assert not mock.called

    # Image in image directory no need to copy it but with a different file name
    open(os.path.join(images_dir, "QEMU", "a"), "w+").close()
    with patch("gns3.registry.image.Image.copy") as mock:
        assert empty_config._relative_image_path("QEMU", "h", os.path.join(images_dir, "QEMU", "a")) == "a"
        assert not mock.called

    # Image outside image directory we need to copy it
    open(str(tmpdir / "b"), "w+").close()
    with patch("gns3.registry.image.Image.copy") as mock:
        assert empty_config._relative_image_path("QEMU", "b", str(tmpdir / "b")) == "b"
        assert mock.called

    # OVA in images directory no need to copy
    os.makedirs(os.path.join(images_dir, "QEMU", "c.ova"))
    open(os.path.join(images_dir, "QEMU", "c.ova", "c.vmdk"), "w+").close()
    with patch("gns3.registry.image.Image.copy") as mock:
        assert empty_config._relative_image_path("QEMU", "c.ova/c.vmdk", os.path.join(images_dir, "QEMU", "c.ova", "c.vmdk")) == os.path.join("c.ova", "c.vmdk")
        assert not mock.called

    # OVA outside images directory need to copy
    os.makedirs(os.path.join(str(tmpdir), "QEMU", "d.ova"))
    open(os.path.join(str(tmpdir), "QEMU", "d.ova", "d.vmdk"), "w+").close()
    with patch("gns3.registry.image.Image.copy") as mock:
        assert empty_config._relative_image_path("QEMU", "d.ova/d.vmdk", os.path.join(str(tmpdir), "QEMU", "d.ova", "d.vmdk")) == "d.ova/d.vmdk"
        assert mock.called

    # OVA in images directory no need to copy but with a different file name
    os.makedirs(os.path.join(images_dir, "QEMU", "e.ova"))
    open(os.path.join(images_dir, "QEMU", "e.ova", "c.vmdk"), "w+").close()
    with patch("gns3.registry.image.Image.copy") as mock:
        assert empty_config._relative_image_path("QEMU", "x.ova/c.vmdk", os.path.join(images_dir, "QEMU", "e.ova", "c.vmdk")) == os.path.join("e.ova", "c.vmdk")
        assert not mock.called
