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
from gns3.modules.vpcs.vpcs_node import VPCSNode
from gns3.node import Node
from gns3.ports.port import Port
from gns3.ports.ethernet_port import EthernetPort
from gns3.ports.serial_port import SerialPort


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


def test_updatePorts(vpcs_device):
    vpcs_device._updatePorts([
        {
            "name": "Ethernet0/0",
            "short_name": "e0/0",
            "data_link_types": {"Ethernet": "DLT_EN10MB"},
            "port_number": 0,
            "adapter_number": 0,
            "link_type": "ethernet"
        }
    ])
    assert len(vpcs_device._ports) == 1
    port = vpcs_device._ports[0]
    assert port.name() == "Ethernet0/0"
    assert port.shortName() == "e0/0"
    assert port.portNumber() == 0
    assert port.adapterNumber() == 0
    assert port.dataLinkTypes() == {"Ethernet": "DLT_EN10MB"}
    assert port.status() == Port.stopped
    assert isinstance(port, EthernetPort)

    vpcs_device.setStatus(Node.started)
    vpcs_device._updatePorts([
        {
            "name": "Serial0/0",
            "short_name": "s0/0",
            "data_link_types": {},
            "port_number": 0,
            "adapter_number": 0,
            "link_type": "serial"
        }
    ])
    assert len(vpcs_device._ports) == 1
    port = vpcs_device._ports[0]
    assert port.status() == Port.started
    assert isinstance(port, EthernetPort)


def test_updatePorts_PortChange(vpcs_device):
    """
    If the same port we do not recreate it but just update his informations
    """
    vpcs_device._updatePorts([
        {
            "name": "Ethernet0/0",
            "short_name": "e0/0",
            "data_link_types": {"Ethernet": "DLT_EN10MB"},
            "port_number": 0,
            "adapter_number": 0,
            "link_type": "ethernet"
        }
    ])
    port = vpcs_device._ports[0]

    vpcs_device.setStatus(Node.started)
    vpcs_device._updatePorts([
        {
            "name": "Ethernet0/0",
            "short_name": "e0/0",
            "data_link_types": {"Ethernet": "DLT_EN10MB"},
            "port_number": 0,
            "adapter_number": 0,
            "link_type": "ethernet"
        }
    ])
    assert port == vpcs_device._ports[0]
    assert port.status() == Port.started


def test_node_setGraphics(vpcs_device):
    node = MagicMock(
        pos=MagicMock(
            return_value=MagicMock(
                x=MagicMock(
                    return_value=10
                ),
                y=MagicMock(
                    return_value=20
                )
            )
        ),
        zValue=MagicMock(
            return_value=2
        ),
        locked=MagicMock(
            return_value=False
        ),
        symbol=MagicMock(
            return_value="symbol.svg"
        )
    )
    with patch('gns3.base_node.BaseNode.controllerHttpPut') as mock:
        vpcs_device.setGraphics(node)
        assert mock.call_count == 1
        args, kwargs = mock.call_args
        assert args[0] == "/nodes/{node_id}".format(node_id=vpcs_device.node_id())

        # second call should not make an update
        vpcs_device.setSettingValue('x', 10)
        vpcs_device.setSettingValue('y', 20)
        vpcs_device.setSettingValue('z', 2)
        vpcs_device.setSettingValue('locked', False)
        vpcs_device.setSettingValue('symbol', "symbol.svg")
        vpcs_device.setSettingValue('label', node.label().dump())

        vpcs_device.setGraphics(node)
        assert mock.call_count == 1