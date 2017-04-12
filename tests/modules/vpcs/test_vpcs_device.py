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


def test_update(vpcs_device):

    new_settings = {
        "name": "Unreal VPCS",
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
        args[1]({"name": "Unreal VPCS"})
