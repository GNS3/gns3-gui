# -*- coding: utf-8 -*-
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

import uuid
from unittest.mock import patch, MagicMock

from gns3.topology import Topology
from gns3.version import __version__


def test_topology_init():
    Topology()


def test_topology_node(vpcs_device):
    topology = Topology()
    topology.addNode(vpcs_device)
    assert len(topology.nodes()) == 1
    assert topology.getNode(vpcs_device.id()) == vpcs_device
    topology.removeNode(vpcs_device)
    assert len(topology.nodes()) == 0


def test_dump(vpcs_device, project):
    topology = Topology()
    topology.project = project
    topology.addNode(vpcs_device)

    dump = topology.dump(include_gui_data=False)
    assert dict(dump) == {
        "auto_start": False,
        "name": project.name(),
        "resources_type": "local",
        "version": __version__,
        "topology": {
            "nodes": [
                {
                    "description": "VPCS device",
                    "id": vpcs_device.id(),
                    "ports": [
                        {
                            "id": vpcs_device.ports()[0].id(),
                            "name": "Ethernet0",
                            "port_number": 0
                        }
                    ],
                    "properties": {
                        "name": vpcs_device.name()
                    },
                    "server_id": 1,
                    "type": "VPCSDevice",
                    "uuid": None
                }
            ],
            "servers": [
                {
                    "cloud": False,
                    "host": "127.0.0.1",
                    "id": 1,
                    "local": True,
                    "port": 8000,
                }
            ]
        },
        "type": "topology"
    }


def test_load(project, monkeypatch, main_window):

    topo = {
        "auto_start": False,
        "name": "twovpcs",
        "resources_type": "local",
        "topology": {
            "links": [
                {
                    "description": "Link from VPCS 1 port Ethernet0 to VPCS 2 port Ethernet0",
                    "destination_node_id": 2,
                    "destination_port_id": 2,
                    "id": 1,
                    "source_node_id": 1,
                    "source_port_id": 1
                }
            ],
            "nodes": [
                {
                    "description": "VPCS device",
                    "id": 1,
                    "label": {
                        "color": "#000000",
                        "font": "TypeWriter,10,-1,5,75,0,0,0,0,0",
                        "text": "VPCS 1",
                        "x": 10.75,
                        "y": -25.0
                    },
                    "ports": [
                        {
                            "description": "connected to VPCS 2 on port Ethernet0",
                            "id": 1,
                            "link_id": 1,
                            "name": "Ethernet0",
                            "nio": "NIO_UDP",
                            "port_number": 0
                        }
                    ],
                    "properties": {
                        "console": 4501,
                        "name": "VPCS 1",
                        "script_file": "startup.vpc"
                    },
                    "server_id": 1,
                    "type": "VPCSDevice",
                    "vpcs_id": 1,
                    "x": -349.5,
                    "y": -206.5
                },
                {
                    "description": "VPCS device",
                    "id": 2,
                    "label": {
                        "color": "#000000",
                        "font": "TypeWriter,10,-1,5,75,0,0,0,0,0",
                        "text": "VPCS 2",
                        "x": 10.75,
                        "y": -25.0
                    },
                    "ports": [
                        {
                            "description": "connected to VPCS 1 on port Ethernet0",
                            "id": 2,
                            "link_id": 1,
                            "name": "Ethernet0",
                            "nio": "NIO_UDP",
                            "port_number": 0
                        }
                    ],
                    "properties": {
                        "console": 4502,
                        "name": "VPCS 2",
                        "script_file": "startup.vpc"
                    },
                    "server_id": 1,
                    "type": "VPCSDevice",
                    "vpcs_id": 2,
                    "x": 69.5,
                    "y": -190.5
                }
            ],
            "servers": [
                {
                    "cloud": False,
                    "host": "127.0.0.1",
                    "id": 1,
                    "local": True,
                    "port": 8000
                }
            ]
        },
        "type": "topology",
        "version": "1.2.3"
    }

    monkeypatch.setattr('gns3.main_window.MainWindow.instance', lambda: main_window)

    # We return an uuid for each HTTP post
    def http_loader(self, method, path, callback, body={}, connecting=False):
        callback({"uuid": uuid.uuid4()})
    monkeypatch.setattr("gns3.http_client.HTTPClient._createHTTPQuery", http_loader)

    monkeypatch.setattr("gns3.http_client.HTTPClient.connected", lambda self: True)

    topology = Topology()
    topology.project = project
    topology.load(topo)

    assert topology._project.name() == "twovpcs"
    assert len(topology.nodes()) == 2
    assert len(topology._node_to_links_mapping) == 2
    assert topology.getNode(1).initialized()
    assert topology.getNode(2).initialized()
    assert main_window.uiGraphicsView.addLink.called
