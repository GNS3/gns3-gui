#!/usr/bin/env python
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

from unittest.mock import MagicMock, patch
import pytest

from gns3.utils.server_select import server_select


def test_server_select_local_server(main_window, local_server):
    """
    With only local server we don't show the list of server
    """

    with patch("gns3.qt.QtWidgets.QInputDialog.getItem") as mock:
        server = server_select(main_window)

        assert not mock.called
        assert server == local_server


def test_server_select_local_server_local_disallow(main_window, local_server):
    """
    With only local server we don't show the list of server
    """

    with patch("gns3.qt.QtWidgets.QMessageBox.critical"):
        with patch("gns3.qt.QtWidgets.QInputDialog.getItem") as mock:
            server = server_select(main_window, allow_local_server=False)
            assert not mock.called
            assert server is None


def test_server_select_local_server_and_remote_select_local(main_window, remote_server, local_server):

    with patch("gns3.qt.QtWidgets.QInputDialog.getItem", return_value=(local_server.name(), True)) as mock:
        server = server_select(main_window)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[3] == [local_server.name(), remote_server.name()]
        assert server.id() == local_server.id()


def test_server_select_local_server_and_remote_select_remote(main_window, remote_server, local_server):

    with patch("gns3.qt.QtWidgets.QInputDialog.getItem", return_value=(remote_server.name(), True)) as mock:
        server = server_select(main_window)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[3] == [local_server.name(), remote_server.name()]

        assert server == remote_server


def test_server_select_local_server_and_remote_local_disallowed(main_window, remote_server, local_server):

    with patch("gns3.qt.QtWidgets.QInputDialog.getItem", return_value=(remote_server.name(), True)) as mock:
        server = server_select(main_window, allow_local_server=False)

        assert not mock.called
        assert server == remote_server


def test_server_select_local_server_and_remote_user_cancel(main_window, remote_server, local_server):

    with patch("gns3.qt.QtWidgets.QInputDialog.getItem", return_value=(local_server.name(), False)) as mock:
        server = server_select(main_window)

        assert mock.called
        args, kwargs = mock.call_args
        assert server is None



def test_server_select_node_type(main_window, remote_server, local_server):
    """
    If only one server support this node type select it by default
    """

    remote_server.setCapabilities({"node_types": ["dynamips", "nat"]})
    local_server.setCapabilities({"node_types": ["dynamips", "cloud"]})
    with patch("gns3.qt.QtWidgets.QInputDialog.getItem", return_value=(local_server.name(), True)) as mock:
        server = server_select(main_window, node_type="nat")

        assert not mock.called
        assert server == remote_server

