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

    with patch("gns3.qt.QtWidgets.QInputDialog.getItem") as mock:
        with pytest.raises(ValueError):
            server = server_select(main_window, allow_local_server=False)

            assert not mock.called


def test_server_select_local_server_and_remote_select_local(main_window, remote_server, local_server):

    with patch("gns3.qt.QtWidgets.QInputDialog.getItem", return_value=("Local server (http://127.0.0.1:3080)", True)) as mock:
        server = server_select(main_window)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[3] == ["Local server (http://127.0.0.1:3080)", remote_server.url()]
        assert server.url() == local_server.url()


def test_server_select_local_server_and_remote_select_remote(main_window, remote_server, local_server):

    with patch("gns3.qt.QtWidgets.QInputDialog.getItem", return_value=(remote_server.url(), True)) as mock:
        server = server_select(main_window)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[3] == ["Local server (http://127.0.0.1:3080)", remote_server.url()]
        assert server == remote_server


def test_server_select_local_server_and_remote_local_disallowed(main_window, remote_server, local_server):

    with patch("gns3.qt.QtWidgets.QInputDialog.getItem", return_value=(remote_server.url(), True)) as mock:
        server = server_select(main_window, allow_local_server=False)

        assert not mock.called
        assert server == remote_server


def test_server_select_local_server_and_gns3_vm_select_vm(main_window, gns3vm_server, local_server):

    with patch("gns3.qt.QtWidgets.QInputDialog.getItem", return_value=("GNS3 VM", True)) as mock:
        server = server_select(main_window)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[3] == ["Local server (http://127.0.0.1:3080)", "GNS3 VM (http://unset:3080)"]
        assert server == gns3vm_server


def test_server_select_local_server_and_remote_user_cancel(main_window, remote_server, local_server):

    with patch("gns3.qt.QtWidgets.QInputDialog.getItem", return_value=("Local server (http://127.0.0.1:3080)", False)) as mock:
        server = server_select(main_window)

        assert mock.called
        args, kwargs = mock.call_args
        assert server is None
