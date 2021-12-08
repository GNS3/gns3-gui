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
from unittest.mock import MagicMock

from gns3.controller import Controller


@pytest.fixture
def controller():
    c = Controller()
    c._http_client = MagicMock()
    return c


def test_http_query_forwarded_to_http_client(controller):
    """
    The HTTP query should be forwarded to the HTTP client
    """
    controller.get("/get")
    controller._http_client.sendRequest.assert_called_with("GET", "/get")
    controller.post("/post")
    controller._http_client.sendRequest.assert_called_with("POST", "/post")
    controller.put("/put")
    controller._http_client.sendRequest.assert_called_with("PUT", "/put")
    controller.delete("/delete")
    controller._http_client.sendRequest.assert_called_with("DELETE", "/delete")


def test_connected(controller):
    callback = MagicMock()
    controller.connected_signal.connect(callback)
    assert controller.connected() is False
    controller._httpClientConnectedSlot()
    assert controller.connected() is True
    assert callback.called
