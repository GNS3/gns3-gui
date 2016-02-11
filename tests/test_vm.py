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
from gns3.ports.port import Port
from gns3.nios.nio_udp import NIOUDP


def test_vpcs_device_start(vpcs_device):

    with patch('gns3.node.Node.httpPost') as mock:
        vpcs_device.start()
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/vms/{vm_id}/start".format(vm_id=vpcs_device.vm_id())


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


def test_addNIO(vpcs_device):

    with patch('gns3.node.Node.httpPost') as mock:
        port = Port("Port 1")
        port.setPortNumber(0)
        port.setAdapterNumber(0)
        nio = NIOUDP(4242, "127.0.0.1", 4243)
        vpcs_device.addNIO(port, nio)
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/vpcs/vms/{vm_id}/adapters/0/ports/0/nio".format(vm_id=vpcs_device.vm_id())

        # Connect the signal
        signal_mock = Mock()
        vpcs_device.nio_signal.connect(signal_mock)

        # Callback
        args[1]({}, context=kwargs["context"])

        # Check the signal
        assert signal_mock.called
        args, kwargs = signal_mock.call_args
        assert args[0] == vpcs_device.id()
        assert args[1] == port.id()


def test_deleteNIO(vpcs_device):

    with patch('gns3.node.Node.httpPost') as mock_post:
        with patch('gns3.node.Node.httpDelete') as mock_delete:
            port = Port("Port 1")
            port.setPortNumber(0)
            port.setAdapterNumber(0)
            nio = NIOUDP(4242, "127.0.0.1", 4243)
            vpcs_device.addNIO(port, nio)

            vpcs_device.deleteNIO(port)
            assert mock_delete.called

            args, kwargs = mock_delete.call_args
            assert args[0] == "/vpcs/vms/{vm_id}/adapters/0/ports/0/nio".format(vm_id=vpcs_device.vm_id())


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

