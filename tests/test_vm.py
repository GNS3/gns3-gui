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

import uuid


from unittest.mock import patch, Mock, MagicMock
from gns3.modules.vpcs.vpcs_device import VPCSDevice
from gns3.node import Node
from gns3.ports.port import Port
from gns3.nios.nio_udp import NIOUDP


def test_create(vpcs_device, local_server):
    with patch('gns3.node.Node.controllerHttpPost') as mock:
        vpcs_device._create({"name": "PC 1", "startup_script": "echo TEST"})
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vms"
        assert kwargs["body"] == {
            "name": "PC 1",
            "compute_id": local_server.server_id(),
            "console_type": "telnet",
            "vm_type": "vpcs",
            "properties": {
                "startup_script": "echo TEST"
            }
        }


def test_setupVMCallback(vpcs_device):
    vm_id = str(uuid.uuid4())
    vpcs_device._setupCallback = MagicMock()
    vpcs_device._setupVMCallback({
        "name": "PC 1",
        "vm_id": vm_id,
        "properties": {
            "startup_script": "echo TEST"
        }
    })
    assert vpcs_device._vm_id == vm_id
    assert vpcs_device._settings["startup_script"] == "echo TEST"
    vpcs_device._setupCallback.assert_called_with({
            "name": "PC 1",
            "vm_id": vm_id,
            "startup_script": "echo TEST"
        },
        error=False
    )


def test_vpcs_device_start(vpcs_device):

    with patch('gns3.node.Node.controllerHttpPost') as mock:
        vpcs_device.start()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vms/{vm_id}/start".format(vm_id=vpcs_device.vm_id())


def test_vpcs_dump(vpcs_device):

    dump = vpcs_device.dump()
    assert dump["id"] == vpcs_device.id()
    assert dump["type"] == "VPCSDevice"
    assert dump["description"] == "VPCS device"
    assert dump["properties"] == {"name": vpcs_device.name()}
    assert dump["server_id"] == vpcs_device._server.id()


def test_vpcs_load(vpcs_device):

    dump = vpcs_device.dump()
    vpcs_device.load(dump)


def test_vpcs_device_stop(vpcs_device):

    with patch('gns3.node.Node.controllerHttpPost') as mock:
        vpcs_device.setStatus(Node.started)
        vpcs_device.stop()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vms/{vm_id}/stop".format(vm_id=vpcs_device.vm_id())


def test_vpcs_device_reload(vpcs_device):

    with patch('gns3.node.Node.controllerHttpPost') as mock:
        vpcs_device.reload()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vms/{vm_id}/reload".format(vm_id=vpcs_device.vm_id())


def test_readBaseConfig(vpcs_device, tmpdir):
    assert vpcs_device._readBaseConfig("") is None
    with open(str(tmpdir / "test.cfg"), "w+") as f:
        f.write("42")
    assert vpcs_device._readBaseConfig(str(tmpdir / "test.cfg")) == "42"


def test_readBaseConfigRelative(vpcs_device, tmpdir):
    with open(str(tmpdir / "test.cfg"), "w+") as f:
        f.write("42")
    with patch('gns3.servers.Servers.localServerSettings', return_value={'configs_path': str(tmpdir)}):
        assert vpcs_device._readBaseConfig(str("test.cfg")) == "42"

