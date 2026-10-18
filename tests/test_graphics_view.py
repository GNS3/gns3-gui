#!/usr/bin/env python
#
# Copyright (C) 2017 GNS3 Technologies Inc.
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

from unittest.mock import MagicMock, patch
from gns3.graphics_view import GraphicsView
from gns3.node import Node


def test_console_to_node_vncviewer_and_ipv6():
    node = MagicMock(
        initialized=MagicMock(return_value=True),
        status=MagicMock(return_value=Node.started),
        consoleCommand=MagicMock(return_value="vncviewer"),
        consoleHost=MagicMock(return_value="::1")
    )
    view = GraphicsView.__new__(GraphicsView)
    with patch('gns3.qt.QtWidgets.QMessageBox.warning') as warning_mock:
        view.consoleToNode(node)
        assert warning_mock.called
        assert warning_mock.call_args[0][1] == 'TightVNC'
