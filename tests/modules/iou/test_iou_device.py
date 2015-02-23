# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GNS3 Technologies Inc.
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
import os
from uuid import uuid4
from unittest.mock import patch, Mock

from gns3.modules.iou.iou_device import IOUDevice
from gns3.ports.port import Port
from gns3.nios.nio_udp import NIOUDP
from gns3.node import Node
from gns3.utils.normalize_filename import normalize_filename
from gns3.modules.iou import IOU


@pytest.fixture
def fake_bin(tmpdir):
    path = str(tmpdir / "test.bin")
    with open(path, "w+") as f:
        f.write("1")
    return path


def test_iou_device_init(local_server, project):

    iou_device = IOUDevice(None, local_server, project)


def test_iou_device_setup(iou_device, project):

    with patch('gns3.node.Node.httpPost') as mock:
        iou_device.setup("/tmp/iou.bin", name="PC 1")
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms"
        assert kwargs["body"] == {
            "name": "PC 1",
            "path": "/tmp/iou.bin"
        }

        # Callback
        params = {
            "console": 2000,
            "name": "PC1",
            "project_id": "f91bd115-3b5c-402e-b411-e5919723cf4b",
            "vm_id": "aec7a00c-e71c-45a6-8c04-29e40732883c"
        }
        args[1](params)

        assert iou_device.vm_id() == "aec7a00c-e71c-45a6-8c04-29e40732883c"


def test_iou_device_setup_with_uuid(iou_device, project):
    """
    If we have an ID that mean the VM already exits and we should not send startup_script
    """

    with patch('gns3.node.Node.httpPost') as mock:
        iou_device.setup("/tmp/iou.bin", name="PC 1", vm_id="aec7a00c-e71c-45a6-8c04-29e40732883c")
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms"
        assert kwargs["body"] == {
            "vm_id": "aec7a00c-e71c-45a6-8c04-29e40732883c",
            "name": "PC 1",
            "path": "/tmp/iou.bin"
        }

        # Callback
        params = {
            "console": 2000,
            "name": "PC1",
            "project_id": "f91bd115-3b5c-402e-b411-e5919723cf4b",
            "vm_id": "aec7a00c-e71c-45a6-8c04-29e40732883c"
        }
        args[1](params)

        assert iou_device.vm_id() == "aec7a00c-e71c-45a6-8c04-29e40732883c"


def test_iou_device_setup_with_initial_config(iou_device, project, tmpdir):
    """
    If we have an ID that mean the VM already exits and we should not send startup_script
    """

    initial_config = str(tmpdir / "config.cfg")
    with open(initial_config, "w+") as f:
        f.write("hostname %h")

    with patch('gns3.node.Node.httpPost') as mock:
        iou_device.setup("/tmp/iou.bin", name="PC 1", vm_id="aec7a00c-e71c-45a6-8c04-29e40732883c", initial_config=initial_config)
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms"
        assert kwargs["body"] == {
            "vm_id": "aec7a00c-e71c-45a6-8c04-29e40732883c",
            "name": "PC 1",
            "path": "/tmp/iou.bin",
            "initial_config_content": "!\nhostname %h"
        }


def test_update(iou_device):

    new_settings = {
        "name": "Unreal IOU",
    }

    with patch('gns3.node.Node.httpPut') as mock:
        iou_device.update(new_settings)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms/{vm_id}".format(vm_id=iou_device.vm_id())
        assert kwargs["body"] == new_settings

        # Callback
        args[1]({})


def test_update_initial_config(iou_device, tmpdir):

    initial_config = str(tmpdir / "config.cfg")
    with open(initial_config, "w+") as f:
        f.write("hostname %h")

    new_settings = {
        "name": "Unreal IOU",
        "initial_config": initial_config
    }

    with patch('gns3.node.Node.httpPut') as mock:
        iou_device.update(new_settings)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms/{vm_id}".format(vm_id=iou_device.vm_id())
        assert kwargs["body"]["name"] == "Unreal IOU"
        assert kwargs["body"]["initial_config_content"] == "!\nhostname %h"

        # Callback
        args[1]({})


def test_dump(local_server, project):

    iou_device = IOUDevice(IOU(), local_server, project)
    iou_device._settings["name"] = "IOU 1"
    iou_device._settings["path"] = "test.bin"
    iou_device._settings["initial_config"] = "/tmp"
    assert iou_device.dump() == {
        "description": "IOU device",
        "id": iou_device.id(),
        "ports": [
            {"adapter_number": 0,
             "id": 1,
             "name": "Ethernet0/0",
             "port_number": 0},
            {"adapter_number": 0,
             "id": 2,
             "name": "Ethernet0/1",
             "port_number": 1},
            {"adapter_number": 0,
             "id": 3,
             "name": "Ethernet0/2",
             "port_number": 2},
            {"adapter_number": 0,
             "id": 4,
             "name": "Ethernet0/3",
             "port_number": 3},
            {"adapter_number": 1,
             "id": 5,
             "name": "Ethernet1/0",
             "port_number": 0},
            {"adapter_number": 1,
             "id": 6,
             "name": "Ethernet1/1",
             "port_number": 1},
            {"adapter_number": 1,
             "id": 7,
             "name": "Ethernet1/2",
             "port_number": 2},
            {"adapter_number": 1,
             "id": 8,
             "name": "Ethernet1/3",
             "port_number": 3},
            {"adapter_number": 2,
             "id": 9,
             "name": "Serial2/0",
             "port_number": 0},
            {"adapter_number": 2,
             "id": 10,
             "name": "Serial2/1",
             "port_number": 1},
            {"adapter_number": 2,
             "id": 11,
             "name": "Serial2/2",
             "port_number": 2},
            {"adapter_number": 2,
             "id": 12,
             "name": "Serial2/3",
             "port_number": 3},
            {"adapter_number": 3,
             "id": 13,
             "name": "Serial3/0",
             "port_number": 0},
            {"adapter_number": 3,
             "id": 14,
             "name": "Serial3/1",
             "port_number": 1},
            {"adapter_number": 3,
             "id": 15,
             "name": "Serial3/2",
             "port_number": 2},
            {"adapter_number": 3,
             "id": 16,
             "name": "Serial3/3",
             "port_number": 3}
        ],
        "properties": {
            "name": "IOU 1",
            "path": "test.bin",
            "initial_config": "/tmp"
        },
        "server_id": local_server.id(),
        "type": "IOUDevice",
        "vm_id": None
    }


def test_load(local_server, project, fake_bin):

    uuid = uuid4()
    iou_device = IOUDevice(IOU(), local_server, project)
    nio_node = {
        "description": "IOU device",
        "id": 1,
        "ports": [
            {
                "adapter_number": 0,
                "id": 1,
                "name": "Hyper Ethernet0/0",
                "port_number": 0},
        ],
        "properties": {
            "name": "IOU 1",
            "path": fake_bin,
            "initial_config": "/tmp"
        },
        "server_id": 1,
        "type": "IOUDevice",
        "vm_id": uuid
    }
    with patch("gns3.modules.iou.iou_device.IOUDevice.setup") as mock:
        iou_device.load(nio_node)

        assert mock.called
        (path, name, console, vm_id, settings), kwargs = mock.call_args
        assert path == fake_bin
        assert name == "IOU 1"
        assert console is None
        assert settings == {"initial_config": "/tmp"}
        assert vm_id == uuid

    iou_device.updated_signal.emit()
    assert iou_device._ports[0].name() == "Hyper Ethernet0/0"


def test_load_1_2(local_server, project, fake_bin):

    uuid = uuid4()
    iou_device = IOUDevice(IOU(), local_server, project)
    nio_node = {
        "description": "IOU device",
        "id": 1,
        "ports": [
            {
                "slot_number": 0,
                "id": 1,
                "name": "Hyper Ethernet0/0",
                "port_number": 0},
        ],
        "properties": {
            "name": "IOU 1",
            "path": fake_bin,
            "initial_config": "/tmp"
        },
        "server_id": 1,
        "type": "IOUDevice",
        "vm_id": uuid
    }
    with patch("gns3.modules.iou.iou_device.IOUDevice.setup") as mock:
        iou_device.load(nio_node)

        assert mock.called
        (path, name, console, vm_id, settings), kwargs = mock.call_args
        assert path == fake_bin
        assert name == "IOU 1"
        assert console is None
        assert settings == {"initial_config": "/tmp"}
        assert vm_id == uuid

    iou_device.updated_signal.emit()
    assert iou_device._ports[0].name() == "Hyper Ethernet0/0"


def test_startPacketCapture(iou_device):

    port = Port("test")
    port.setAdapterNumber(2)
    port.setPortNumber(1)

    with patch("gns3.node.Node.httpPost") as mock:
        iou_device.startPacketCapture(port, "test.pcap", "DLT_EN10MB")
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms/{vm_id}/adapters/2/ports/1/start_capture".format(vm_id=iou_device.vm_id())
        assert kwargs["body"] == {
            "data_link_type": "DLT_EN10MB",
            "capture_file_name": "test.pcap"
        }

        with patch("gns3.ports.port.Port.startPacketCapture") as port_mock:

            # Callback
            args[1]({"pcap_file_path": "/tmp/test.pcap"}, context=kwargs["context"])

            assert port_mock.called_with("/tmp/test.pcap")


def test_stopPacketCapture(iou_device):

    port = Port("test")
    port.setAdapterNumber(2)
    port.setPortNumber(1)

    with patch("gns3.node.Node.httpPost") as mock:
        iou_device.stopPacketCapture(port)
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms/{vm_id}/adapters/2/ports/1/stop_capture".format(vm_id=iou_device.vm_id())

        with patch("gns3.ports.port.Port.stopPacketCapture") as port_mock:

            # Callback
            args[1]({}, context=kwargs["context"])

            assert port_mock.called


def test_exportConfig(iou_device, tmpdir):

    path = str(tmpdir / "test.cfg")

    with patch("gns3.node.Node.httpGet") as mock:
        iou_device.exportConfig(path)
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms/{vm_id}/initial_config".format(vm_id=iou_device.vm_id())

        # Callback
        args[1]({"content": "TEST"}, context=kwargs["context"])

        with open(path) as f:
            assert f.read() == "TEST"


def test_exportConfigToDirectory(iou_device, tmpdir):

    path = str(tmpdir)

    with patch("gns3.node.Node.httpGet") as mock:
        iou_device.exportConfigToDirectory(path)
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms/{vm_id}/initial_config".format(vm_id=iou_device.vm_id())

        # Callback
        args[1]({"content": "TEST"}, context=kwargs["context"])

        with open(os.path.join(path, normalize_filename(iou_device.name()) + "_initial-config.cfg"
                               )) as f:
            assert f.read() == "TEST"
