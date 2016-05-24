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
    with patch('gns3.base_node.BaseNode.controllerHttpPost') as mock:
        vpcs_device._create(name="PC 1", params={"startup_script": "echo TEST"})
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes"
        assert kwargs["body"] == {
            "name": "PC 1",
            "compute_id": local_server.id(),
            "node_type": "vpcs",
            "properties": {
                "startup_script": "echo TEST"
            }
        }


def test_setupVMCallback(vpcs_device):
    node_id = str(uuid.uuid4())
    vpcs_device._createCallback = MagicMock()
    vpcs_device.createNodeCallback({
        "name": "PC 1",
        "node_id": node_id,
        "properties": {
            "startup_script": "echo TEST"
        }
    })
    assert vpcs_device._node_id == node_id
    assert vpcs_device._settings["startup_script"] == "echo TEST"
    vpcs_device._createCallback.assert_called_with({
            "name": "PC 1",
            "node_id": node_id,
            "startup_script": "echo TEST"
        }
    )


def test_vpcs_device_start(vpcs_device):

    with patch('gns3.base_node.BaseNode.controllerHttpPost') as mock:
        vpcs_device.start()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes/{node_id}/start".format(node_id=vpcs_device.node_id())


def test_vpcs_dump(vpcs_device):

    dump = vpcs_device.dump()
    assert dump["id"] == vpcs_device.id()
    assert dump["type"] == "VPCSDevice"
    assert dump["description"] == "VPCS device"
    assert dump["properties"] == {"name": vpcs_device.name()}
    assert dump["server_id"] == vpcs_device._compute.id()


def test_vpcs_load(vpcs_device):

    dump = vpcs_device.dump()
    vpcs_device.load(dump)


def test_vpcs_device_stop(vpcs_device):

    with patch('gns3.base_node.BaseNode.controllerHttpPost') as mock:
        vpcs_device.setStatus(Node.started)
        vpcs_device.stop()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes/{node_id}/stop".format(node_id=vpcs_device.node_id())


def test_vpcs_device_reload(vpcs_device):

    with patch('gns3.base_node.BaseNode.controllerHttpPost') as mock:
        vpcs_device.reload()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes/{node_id}/reload".format(node_id=vpcs_device.node_id())


def test_readBaseConfig(vpcs_device, tmpdir):
    assert vpcs_device._readBaseConfig("") is None
    with open(str(tmpdir / "test.cfg"), "w+") as f:
        f.write("42")
    assert vpcs_device._readBaseConfig(str(tmpdir / "test.cfg")) == "42"


def test_readBaseConfigRelative(vpcs_device, tmpdir):
    with open(str(tmpdir / "test.cfg"), "w+") as f:
        f.write("42")
    with patch('gns3.local_server.LocalServer.localServerSettings', return_value={'configs_path': str(tmpdir)}):
        assert vpcs_device._readBaseConfig(str("test.cfg")) == "42"

