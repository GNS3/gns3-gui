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

from unittest.mock import patch, Mock
from gns3.modules.vpcs.vpcs_node import VPCSNode
from gns3.ports.port import Port
from gns3.base_node import BaseNode
from gns3.utils.normalize_filename import normalize_filename


def test_vpcs_device_init(local_server, project):

    vpcs_device = VPCSNode(None, local_server, project)


def test_vpcs_device_create(vpcs_device, project, local_server):

    with patch('gns3.base_node.BaseNode.controllerHttpPost') as mock:
        vpcs_device.create(name="PC 1", additional_settings={"startup_script": "echo TEST"})
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes"
        assert kwargs["body"] == {
            "node_id": vpcs_device._node_id,
            "name": "PC 1",
            "compute_id": local_server.id(),
            "node_type": "vpcs",
            "properties": {
                "startup_script": "echo TEST"
            }
        }

        # Callback
        params = {
            "console": 2000,
            "name": "PC1",
            "node_id": "aec7a00c-e71c-45a6-8c04-29e40732883c",
            "project_id": "f91bd115-3b5c-402e-b411-e5919723cf4b",
            "properties": {
                "script_file": None,
                "startup_script": None,
            }
        }
        vpcs_device.createNodeCallback(params)

        assert vpcs_device.node_id() == "aec7a00c-e71c-45a6-8c04-29e40732883c"


def test_vpcs_device_setup_with_uuid(vpcs_device, project, local_server):
    """
    If we have an ID that mean the VM already exits and we should not send startup_script
    """

    with patch('gns3.base_node.BaseNode.controllerHttpPost') as mock:
        vpcs_device.create(name="PC 1", node_id="aec7a00c-e71c-45a6-8c04-29e40732883c", additional_settings={"startup_script": "echo TEST"})
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes"
        assert kwargs["body"] == {
            "node_id": "aec7a00c-e71c-45a6-8c04-29e40732883c",
            "name": "PC 1",
            "compute_id": local_server.id(),
            "node_type": "vpcs",
            "properties": {}
        }

        # Callback
        params = {
            "console": 2000,
            "name": "PC1",
            "project_id": "f91bd115-3b5c-402e-b411-e5919723cf4b",
            "node_id": "aec7a00c-e71c-45a6-8c04-29e40732883c",
            "properties": {
                "script_file": None,
                "startup_script": None,
            }
        }
        vpcs_device.createNodeCallback(params)

        assert vpcs_device.node_id() == "aec7a00c-e71c-45a6-8c04-29e40732883c"


def test_vpcs_device_setup_script_file(vpcs_device, project, tmpdir, local_server):
    """
    Script file is converted to a text version in order to work
    on remote servers.
    """

    path = str(tmpdir / "test.vpc")
    with open(path, 'w+') as f:
        f.write("echo TEST")

    with patch('gns3.base_node.BaseNode.controllerHttpPost') as mock:
        vpcs_device.create(name="PC 1", node_id="aec7a00c-e71c-45a6-8c04-29e40732883c", additional_settings={"base_script_file": path})
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes"
        assert kwargs["body"] == {
            "node_id": "aec7a00c-e71c-45a6-8c04-29e40732883c",
            "name": "PC 1",
            "compute_id": local_server.id(),
            "node_type": "vpcs",
            "properties": {}
        }

        # Callback
        params = {
            "console": 2000,
            "name": "PC1",
            "project_id": "f91bd115-3b5c-402e-b411-e5919723cf4b",
            "node_id": "aec7a00c-e71c-45a6-8c04-29e40732883c",
            "properties": {
                "script_file": None,
                "startup_script": "echo TEST",
            }
        }
        vpcs_device.createNodeCallback(params)

        assert vpcs_device.node_id() == "aec7a00c-e71c-45a6-8c04-29e40732883c"


@pytest.mark.skip(reason="Need refactor for controller support")
def test_exportConfigToDirectory(tmpdir, vpcs_device):

    path = tmpdir / normalize_filename(vpcs_device.name()) + '_startup.vpc'

    with patch('gns3.base_node.BaseNode.httpGet') as mock:
        vpcs_device.exportConfigToDirectory(str(tmpdir))

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/nodes/{node_id}".format(node_id=vpcs_device.node_id())

        # Callback
        args[1]({"startup_script": "echo TEST"}, context={"directory": str(tmpdir)})

        assert path.exists()

        with open(str(path)) as f:
            assert f.read() == "echo TEST"


def test_update(vpcs_device):

    new_settings = {
        "name": "Unreal VPCS",
        "script_file": "echo TEST"
    }

    with patch('gns3.base_node.BaseNode.controllerHttpPut') as mock:
        vpcs_device.update(new_settings)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes/{node_id}".format(node_id=vpcs_device.node_id())
        assert kwargs["body"] == {
            'node_id': vpcs_device._node_id,
            'name': 'Unreal VPCS', 'compute_id': 'local', 'node_type': 'vpcs', 'properties': {}}

        # Callback
        args[1]({"startup_script": "echo TEST", "name": "Unreal VPCS"})


def test_importConfig(vpcs_device, tmpdir):

    path = str(tmpdir / 'startup.vpcs')
    content = "echo TEST"

    with open(path, 'w+') as f:
        f.write(content)

    with patch('gns3.base_node.BaseNode.controllerHttpPut') as mock:
        vpcs_device.importConfig(path)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes/{node_id}".format(node_id=vpcs_device.node_id())
        assert kwargs["body"] == {'compute_id': 'local',
                                  'node_type': 'vpcs',
                                  'node_id': vpcs_device._node_id,
                                  'properties': {'startup_script': 'echo TEST'}}
