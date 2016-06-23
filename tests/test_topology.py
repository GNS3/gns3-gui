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
from unittest.mock import MagicMock

from gns3.topology import Topology


def test_topology_init():
    Topology()


def test_topology_node(vpcs_device):
    topology = Topology()
    topology.addNode(vpcs_device)
    assert len(topology.nodes()) == 1
    assert topology.getNode(vpcs_device.id()) == vpcs_device
    topology.removeNode(vpcs_device)
    assert len(topology.nodes()) == 0


def test_createDrawing_ellipse():
    topology = Topology()
    shape_data = {
        "x": 42,
        "y": 12,
        "z": 0,
        "rotation": 0,
        "drawing_id": str(uuid.uuid4()),
        "svg": "<svg height=\"105.0\" width=\"158.0\"><ellipse cx=\"79\" cy=\"52\" rx=\"79\" ry=\"53\" style=\"stroke-width:2;stroke:#000000;fill:#ffffff;\" /></svg>",
    }
    topology._main_window = MagicMock()
    topology.createDrawing(shape_data)
    topology._main_window.uiGraphicsView.createDrawingItem.assert_called_with("ellipse", 42, 12, 0, rotation=0, svg=shape_data["svg"], drawing_id=shape_data["drawing_id"])


def test_createDrawing_rect():
    topology = Topology()
    shape_data = {
        "x": 42,
        "y": 12,
        "z": 0,
        "rotation": 0,
        "drawing_id": str(uuid.uuid4()),
        "svg": "<svg height=\"105.0\" width=\"158.0\"><rect/></svg>",
    }
    topology._main_window = MagicMock()
    topology.createDrawing(shape_data)
    topology._main_window.uiGraphicsView.createDrawingItem.assert_called_with("rect", 42, 12, 0, rotation=0, svg=shape_data["svg"], drawing_id=shape_data["drawing_id"])


def test_createDrawing_text():
    topology = Topology()
    shape_data = {
        "x": 42,
        "y": 12,
        "z": 0,
        "rotation": 0,
        "drawing_id": str(uuid.uuid4()),
        "svg": "<svg height=\"105.0\" width=\"158.0\"><text/></svg>",
    }
    topology._main_window = MagicMock()
    topology.createDrawing(shape_data)
    topology._main_window.uiGraphicsView.createDrawingItem.assert_called_with("text", 42, 12, 0, rotation=0, svg=shape_data["svg"], drawing_id=shape_data["drawing_id"])


def test_createDrawing_svg():
    """
    If SVG is more complex we consider it as an image
    """
    topology = Topology()
    shape_data = {
        "x": 42,
        "y": 12,
        "z": 0,
        "rotation": 0,
        "drawing_id": str(uuid.uuid4()),
        "svg": "<svg height=\"105.0\" width=\"158.0\"><rect><line/></rect></svg>",
    }
    topology._main_window = MagicMock()
    topology.createDrawing(shape_data)
    topology._main_window.uiGraphicsView.createDrawingItem.assert_called_with("image", 42, 12, 0, rotation=0, svg=shape_data["svg"], drawing_id=shape_data["drawing_id"])

