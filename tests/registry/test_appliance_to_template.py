#!/usr/bin/env python
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

from gns3.registry.config import Config
from gns3.settings import LOCAL_SERVER_SETTINGS
from gns3.registry.appliance_to_template import ApplianceToTemplate


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


@pytest.mark.parametrize(
    "appliance_file",
    [
        "cisco-iou-l3.gns3a",
        "cisco-iou-l3-v8.gns3a"
    ]
)
def test_add_appliance_iou(iou_l3, appliance_file):
    with open("tests/registry/appliances/{}".format(appliance_file), encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "image",
            "filename": "i86bi-linux-l3-adventerprisek9-15.4.1T.bin",
            "path": iou_l3
        }
    ]
    new_template = ApplianceToTemplate().new_template(config, "local", "15.4.1T")
    assert new_template == {
        "category": "router",
        "template_type": "iou",
        "symbol": ":/symbols/router.svg",
        "compute_id": "local",
        "name": "Cisco IOU L3",
        "nvram": 128,
        "ram": 256,
        "serial_adapters": 2,
        "ethernet_adapters": 2,
        "startup_config": "iou_l3_base_startup-config.txt",
        "image": os.path.basename(iou_l3),
        "path": os.path.basename(iou_l3)
    }


@pytest.mark.parametrize(
    "appliance_file",
    [
        "openvswitch.gns3a",
        "openvswitch-v8.gns3a"
    ]
)
def test_add_appliance_docker(appliance_file):
    with open("tests/registry/appliances/{}".format(appliance_file), encoding="utf-8") as f:
        config = json.load(f)

    new_template = ApplianceToTemplate().new_template(config, "local")
    assert new_template == {
        "name": "Open vSwitch",
        "template_type": "docker",
        "image": "gns3/openvswitch:latest",
        "category": "switch",
        "symbol": ":/symbols/multilayer_switch.svg",
        "compute_id": "local",
        "adapters": 16,
        "usage": "By default all interfaces are connected to the br0"
    }


@pytest.mark.parametrize(
    "appliance_file",
    [
        "cisco-3745.gns3a",
        "cisco-3745-v8.gns3a"
    ]
)
def test_add_appliance_dynamips(cisco_3745, appliance_file):
    with open("tests/registry/appliances/{}".format(appliance_file), encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "image",
            "filename": "c3745-adventerprisek9-mz.124-25d.image",
            "path": cisco_3745,
            "idlepc": "0x60aa1da0"
        }
    ]

    new_template = ApplianceToTemplate().new_template(config, "local", "124-25d")
    assert new_template == {
        "template_type": "dynamips",
        "category": "router",
        "chassis": "",
        "idlepc": "0x60aa1da0",
        "image": "c3745-adventerprisek9-mz.124-25d.image",
        "name": "Cisco 3745",
        "nvram": 256,
        "platform": "c3745",
        "ram": 256,
        "compute_id": "local",
        "slot0": "GT96100-FE",
        "slot1": "NM-1FE-TX",
        "slot2": "NM-4T",
        "slot3": "",
        "slot4": "",
        "startup_config": "ios_base_startup-config.txt",
        "symbol": ":/symbols/router.svg",
        "wic0": "WIC-1T",
        "wic1": "WIC-1T",
        "wic2": "WIC-1T"
    }


def test_add_appliance_guest(linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.gns3a", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]

    new_template = ApplianceToTemplate().new_template(config, "local")
    assert new_template == {
        "template_type": "qemu",
        "adapter_type": "e1000",
        "adapters": 1,
        "category": "guest",
        "console_type": "telnet",
        "symbol": ":/symbols/qemu_guest.svg",
        "hda_disk_image": "linux-microcore-3.4.1.img",
        "name": "Micro Core Linux",
        "qemu_path": "qemu-system-i386",
        "usage": "Just start the appliance",
        "ram": 32,
        "compute_id": "local"
    }


def test_add_appliance_with_symbol(linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.gns3a", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]
    config["symbol"] = ":/symbols/asa.svg"
    new_template = ApplianceToTemplate().new_template(config, "local")
    assert new_template["symbol"] == ":/symbols/asa.svg"


def test_add_appliance_with_symbol_from_symbols_dir(empty_config, linux_microcore_img, symbols_dir):
    with open("tests/registry/appliances/microcore-linux.gns3a", encoding="utf-8") as f:
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

    new_template = ApplianceToTemplate().new_template(config, "local")
    assert new_template["symbol"] == "linux_guest.svg"


def test_add_appliance_with_port_name_format(linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.gns3a", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]
    config["port_name_format"] = "eth{0}"
    new_template = ApplianceToTemplate().new_template(config, "local")
    assert new_template["port_name_format"] == "eth{0}"


def test_add_appliance_with_boot_priority(linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.gns3a", encoding="utf-8") as f:
        config = json.load(f)
    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]
    config["qemu"]["boot_priority"] = "dc"
    new_template = ApplianceToTemplate().new_template(config, "local")
    assert new_template["boot_priority"] == "dc"


@pytest.mark.parametrize(
    "appliance_file",
    [
        "arista-veos.gns3a",
        "arista-veos-v8.gns3a"
    ]
)
def test_add_appliance_router_two_disk(images_dir, appliance_file):
    with open("tests/registry/appliances/{}".format(appliance_file), encoding="utf-8") as f:
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

    new_template = ApplianceToTemplate().new_template(config, "local", "4.13.8M")
    expected_result = {
        "template_type": "qemu",
        "adapter_type": "e1000",
        "adapters": 8,
        "category": "router",
        "symbol": ":/symbols/router.svg",
        "hda_disk_image": "a",
        "hdb_disk_image": "b",
        "name": "Arista vEOS",
        "qemu_path": "qemu-system-x86_64",
        "ram": 2048,
        "console_type": "telnet",
        "compute_id": "local"
    }
    if "v8" in appliance_file:
        expected_result["platform"] = "x86_64"  # platform was added in v8
    assert new_template == expected_result


def test_add_appliance_v8_default_properties_inheritance(images_dir):
    with open("tests/registry/appliances/empty-vm-v8.gns3a", encoding="utf-8") as f:
        config = json.load(f)

    # check that default properties are used
    new_template = ApplianceToTemplate().new_template(config, "local", "8G")
    expected_result = {
        "name": "Empty VM",
        "template_type": "qemu",
        "symbol": ":/symbols/qemu_guest.svg",
        "category": "guest",
        "adapter_type": "e1000",
        "adapters": 1,
        "ram": 1024,
        "qemu_path": "qemu-system-x86_64",
        "hda_disk_interface": "sata",
        "platform": "x86_64",
        "console_type": "vnc",
        "boot_priority": "d",
        "compute_id": "local",
        "usage": "Default at first boot the VM will start from the cdrom."
    }
    assert new_template == expected_result

    # check that specific properties are used along with default properties
    new_template = ApplianceToTemplate().new_template(config, "local", "30G")
    expected_result.update(
        {
            "adapters": 8,
            "qemu_path": "qemu-system-i386",
            "platform": "i386",
        }
    )
    assert new_template == expected_result

    # check that specific properties are used along without default properties
    new_template = ApplianceToTemplate().new_template(config, "local", "100G")
    expected_result = {
        "name": "Empty VM",
        "template_type": "qemu",
        "symbol": ":/symbols/qemu_guest.svg",
        "category": "guest",
        "ram": 512,
        "qemu_path": "qemu-system-arm",
        "platform": "arm",
        "compute_id": "local",
        "usage": "Default at first boot the VM will start from the cdrom."
    }
    assert new_template == expected_result

    # check that specific properties are used with "usage", "symbol" and "category" defined at the version level
    new_template = ApplianceToTemplate().new_template(config, "local", "200G")
    expected_result.update(
        {
            "usage": "This is how to use this version",
            "symbol": "ethernet_switch",
            "category": "switch"
        }
    )
    assert new_template == expected_result


def test_add_appliance_path_relative_to_images_dir(tmpdir, linux_microcore_img):
    with open("tests/registry/appliances/microcore-linux.gns3a", encoding="utf-8") as f:
        config = json.load(f)

    config["images"] = [
        {
            "type": "hda_disk_image",
            "filename": "linux-microcore-3.4.1.img",
            "path": linux_microcore_img
        }
    ]

    new_template = ApplianceToTemplate().new_template(config, "local")
    assert new_template["hda_disk_image"] == "linux-microcore-3.4.1.img"


def test_add_appliance_path_non_relative_to_images_dir(tmpdir, images_dir):
    with open("tests/registry/appliances/microcore-linux.gns3a", encoding="utf-8") as f:
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
    new_template = ApplianceToTemplate().new_template(config, "local")
    assert new_template["hda_disk_image"] == "a.img"


def test_relative_image_path(images_dir, tmpdir):

    # Image in image directory no need to copy it
    open(os.path.join(images_dir, "QEMU", "a"), "w+").close()
    assert ApplianceToTemplate()._relative_image_path("QEMU", os.path.join(images_dir, "QEMU", "a")) == "a"

    # Image in image directory no need to copy it but with a different file name
    open(os.path.join(images_dir, "QEMU", "a"), "w+").close()
    assert ApplianceToTemplate()._relative_image_path("QEMU", os.path.join(images_dir, "QEMU", "a")) == "a"

    # Image outside image directory we need to copy it
    open(str(tmpdir / "b"), "w+").close()
    assert ApplianceToTemplate()._relative_image_path("QEMU", str(tmpdir / "b")) == "b"
