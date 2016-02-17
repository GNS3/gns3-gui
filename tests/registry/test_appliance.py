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

from gns3.registry.appliance import Appliance, ApplianceError
from gns3.registry.registry import Registry


@pytest.fixture
def registry(images_dir):
    return Registry([os.path.join(images_dir, "QEMU")])


@pytest.fixture
def microcore_appliance(registry):
    """
    An instance of microcore Appliance object
    """
    return Appliance(registry, "tests/registry/appliances/microcore-linux.json")


def test_check_config(tmpdir, registry):

    test_path = str(tmpdir / "test.json")

    with open(test_path, "w+", encoding="utf-8") as f:
        f.write("")

    with pytest.raises(ApplianceError):
        Appliance(registry, "jkhj")

    with pytest.raises(ApplianceError):
        Appliance(registry, test_path)

    with open(test_path, "w+", encoding="utf-8") as f:
        f.write("{}")

    with pytest.raises(ApplianceError):
        Appliance(registry, test_path)

    with pytest.raises(ApplianceError):
        with open(test_path, "w+", encoding="utf-8") as f:
            f.write('{"registry_version": 42}')
        Appliance(registry, test_path)

    Appliance(registry, "tests/registry/appliances/microcore-linux.json")


def test_resolve_version(tmpdir):

    with open("tests/registry/appliances/microcore-linux.json", encoding="utf-8") as f:
        config = json.load(f)

    hda = config["images"][0]

    new_config = Appliance(registry, "tests/registry/appliances/microcore-linux.json")
    assert new_config["versions"][0]["images"] == {"hda_disk_image": hda}


def test_resolve_docker(tmpdir):

    with open("tests/registry/appliances/openvswitch.gns3a", encoding="utf-8") as f:
        config = json.load(f)

    new_config = Appliance(registry, "tests/registry/appliances/openvswitch.gns3a")


def test_resolve_version_dynamips(tmpdir):

    with open("tests/registry/appliances/cisco-3745.gns3a", encoding="utf-8") as f:
        config = json.load(f)

    hda = config["images"][0]
    hda["idlepc"] = "0x60aa1da0"

    new_config = Appliance(registry, "tests/registry/appliances/cisco-3745.gns3a")
    assert new_config["versions"][0]["images"] == {"image": hda}


def test_resolve_version_invalid_file(tmpdir):

    with pytest.raises(ApplianceError):
        Appliance(registry, "tests/registry/appliances/broken-microcore-linux.json")


def test_resolve_version_ova(tmpdir):

    with open("tests/registry/appliances/juniper-vsrx.gns3a", encoding="utf-8") as f:
        config = json.load(f)

    hda = config["images"][0]
    hda["filename"] = os.path.join("junos-vsrx-12.1X47-D10.4-domestic.ova", "junos-vsrx-12.1X47-D10.4-domestic-disk1.vmdk")

    new_config = Appliance(registry, "tests/registry/appliances/juniper-vsrx.gns3a")

    assert new_config["versions"][0]["images"] == {
        "hda_disk_image": hda
    }


def test_search_images_for_version(linux_microcore_img, microcore_appliance):

    detected = microcore_appliance.search_images_for_version("3.4.1")
    assert detected["name"] == "Micro Core Linux 3.4.1"
    assert detected["images"][0]["type"] == "hda_disk_image"
    assert detected["images"][0]["path"] == linux_microcore_img
    assert detected["images"][0]["md5sum"] == "5d41402abc4b2a76b9719d911017c592"
    assert detected["images"][0]["filesize"] == 5


def test_search_images_for_version_no_md5(linux_microcore_img, microcore_appliance):

    microcore_appliance._appliance['versions'][0]['images']['hda_disk_image'].pop('filesize')
    microcore_appliance._appliance['versions'][0]['images']['hda_disk_image'].pop('md5sum')
    detected = microcore_appliance.search_images_for_version("3.4.1")
    assert detected["name"] == "Micro Core Linux 3.4.1"
    assert detected["images"][0]["type"] == "hda_disk_image"
    assert detected["images"][0]["path"] == linux_microcore_img
    assert detected["images"][0]["md5sum"] == "5d41402abc4b2a76b9719d911017c592"
    assert detected["images"][0]["filesize"] == 5


def test_search_images_for_version_unknow_version(microcore_appliance):

    with pytest.raises(ApplianceError):
        detected = microcore_appliance.search_images_for_version("42")


def test_search_images_for_version_missing_file(microcore_appliance):

    with pytest.raises(ApplianceError):
        detected = microcore_appliance.search_images_for_version("4.0.2")


def test_is_version_installable(linux_microcore_img, microcore_appliance):

    assert microcore_appliance.is_version_installable("3.4.1")
    assert not microcore_appliance.is_version_installable("4.0.2")


def test_image_dir_name(microcore_appliance):

    assert Appliance(registry, "tests/registry/appliances/microcore-linux.json").image_dir_name() == "QEMU"
    assert Appliance(registry, "tests/registry/appliances/cisco-iou-l3.gns3a").image_dir_name() == "IOU"


def test_create_new_version(microcore_appliance):

    a = Appliance(registry, "tests/registry/appliances/microcore-linux.json")
    a.create_new_version("42.0")
    v = a['versions'][-1:][0]
    assert v == {
        'images':
        {
            'hda_disk_image':
                {
                    'filename': 'linux-microcore-42.0.img',
                    'version': '42.0'
                }
        },
        'name': '42.0'
    }

