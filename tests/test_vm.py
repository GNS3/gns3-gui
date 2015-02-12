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


from unittest.mock import patch, Mock
from gns3.modules.vpcs.vpcs_device import VPCSDevice
from gns3.node import Node
from gns3.utils.normalize_filename import normalize_filename


def test_vpcs_device_start(vpcs_device):

    with patch('gns3.node.Node.httpPost') as mock:
        vpcs_device.start()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/vms/{vm_id}/start".format(vm_id=vpcs_device.vm_id())


def test_vpcs_device_stop(vpcs_device):

    with patch('gns3.node.Node.httpPost') as mock:
        vpcs_device.setStatus(Node.started)
        vpcs_device.stop()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/vms/{vm_id}/stop".format(vm_id=vpcs_device.vm_id())


def test_vpcs_device_reload(vpcs_device):

    with patch('gns3.node.Node.httpPost') as mock:
        vpcs_device.reload()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/vms/{vm_id}/reload".format(vm_id=vpcs_device.vm_id())
