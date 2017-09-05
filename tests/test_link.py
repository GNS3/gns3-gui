#!/usr/bin/env python
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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
import uuid
from unittest.mock import MagicMock


from gns3.link import Link
from gns3.ports.ethernet_port import EthernetPort
from gns3.modules.vpcs.vpcs_node import VPCSNode
from gns3.modules.vpcs import VPCS
from gns3.controller import Controller


@pytest.fixture
def devices(local_server, project):
    """
    Create two VPCS for test
    """
    device1 = VPCSNode(VPCS(), local_server, project)
    device1._vpcs_id = str(uuid.uuid4())
    device1._settings = {"name": "VPCS 1", "script_file": "", "console": None, "startup_script": None}
    device1.setInitialized(True)

    port = EthernetPort("E1")
    port.setAdapterNumber(0)
    port.setPortNumber(0)
    device1._ports.append(port)

    device2 = VPCSNode(VPCS(), local_server, project)
    device2._vpcs_id = str(uuid.uuid4())
    device2._settings = {"name": "VPCS 2", "script_file": "", "console": None, "startup_script": None}
    device2.setInitialized(True)

    port = EthernetPort("E2")
    port.setAdapterNumber(0)
    port.setPortNumber(0)
    device2._ports.append(port)

    return (device1, device2)


@pytest.fixture
def link(devices, controller, project):
    link = Link(devices[0], devices[0].ports()[0], devices[1], devices[1].ports()[0])

    data = {
        "suspend": False,
        "nodes": [
            {"node_id": devices[0].node_id(), "adapter_number": 0, "port_number": 0},
            {"node_id": devices[1].node_id(), "adapter_number": 0, "port_number": 0}
        ],
        "filters": {},
    }

    controller.post.assert_called_with("/projects/{}/links".format(project.id()), link._linkCreatedCallback, body=data)

    link._linkCreatedCallback({"link_id": str(uuid.uuid4())})
    return link


@pytest.fixture
def controller():
    Controller._instance = MagicMock()
    return Controller._instance


def test_create_link(devices, project, controller):
    link = Link(devices[0], devices[0].ports()[0], devices[1], devices[1].ports()[0])

    data = {
        "suspend": False,
        "nodes": [
            {"node_id": devices[0].node_id(), "adapter_number": 0, "port_number": 0},
            {"node_id": devices[1].node_id(), "adapter_number": 0, "port_number": 0},
        ],
        "filters": {},
    }

    controller.post.assert_called_with("/projects/{}/links".format(project.id()), link._linkCreatedCallback, body=data)

    mock_signal = MagicMock()
    link.add_link_signal.connect(mock_signal)
    link._linkCreatedCallback({"link_id": str(uuid.uuid4())})
    mock_signal.assert_called_with(link._id)

    assert link._link_id is not None
    assert not devices[0].ports()[0].isFree()

    assert link in devices[0].links()
    assert link in devices[1].links()

    assert link.getNodePort(devices[0]) == devices[0].ports()[0]
    assert link.getNodePort(devices[1]) == devices[1].ports()[0]


def test_delete_link(devices, project, controller):
    link = Link(devices[0], devices[0].ports()[0], devices[1], devices[1].ports()[0])
    link._link_id = str(uuid.uuid4())
    link.deleteLink()

    controller.delete.assert_called_with("/projects/{}/links/{}".format(project.id(), link._link_id), link._linkDeletedCallback)

    mock_signal = MagicMock()
    link.delete_link_signal.connect(mock_signal)
    link._linkDeletedCallback({})
    mock_signal.assert_called_with(link._id)

    assert devices[0].ports()[0].isFree()
    assert link not in devices[0].links()
    assert link not in devices[1].links()


def test_start_capture_link(link, controller, project):
    link.startCapture("DLT_EN10MB", "test.pcap")
    controller.post.assert_called_with("/projects/{}/links/{}/start_capture".format(project.id(), link._link_id), link._startCaptureCallback, body={'capture_file_name': 'test.pcap', 'data_link_type': 'DLT_EN10MB'})


def test_stop_capture_link(link, controller, project):
    link.stopCapture()
    controller.post.assert_called_with("/projects/{}/links/{}/stop_capture".format(project.id(), link._link_id), link._stopCaptureCallback)
