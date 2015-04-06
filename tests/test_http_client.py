# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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
import unittest.mock

from gns3.qt import QtNetwork, FakeQtSignal
from gns3.http_client import HTTPClient
from gns3.version import __version__


@pytest.fixture
def network_manager(response):

    mock = unittest.mock.MagicMock()
    mock.get.return_value = response
    mock.post.return_value = response
    mock.put.return_value = response
    mock.delete.return_value = response
    return mock


@pytest.fixture
def response():
    response = unittest.mock.MagicMock()
    type(response).finished = unittest.mock.PropertyMock(return_value=FakeQtSignal())
    response.error.return_value = QtNetwork.QNetworkReply.NoError
    response.attribute.return_value = 200
    return response


@pytest.fixture
def http_client(request, network_manager):

    return HTTPClient("http://127.0.0.1:8000", network_manager)


@pytest.yield_fixture(autouse=True)
def request():

    mock = unittest.mock.Mock()
    with unittest.mock.patch("gns3.http_client.HTTPClient._request", return_value=mock):
        yield mock


def test_get_connected(http_client, request, network_manager, response):

    http_client._connected = True
    callback = unittest.mock.MagicMock()

    http_client.get("/test", callback)
    request.assert_call_with("/test")
    request.setRawHeader.assert_any_call("Content-Type", "application/json")
    request.setRawHeader.assert_any_call("User-Agent", "GNS3 QT Client v{version}".format(version=__version__))
    network_manager.get.assert_call_with(request)

    # Trigger the completion
    response.finished.emit()

    assert callback.called


def test_post_not_connected(http_client, request, network_manager, response):

    http_client._connected = False
    callback = unittest.mock.MagicMock()

    http_client.post("/test", callback, context={"toto": 42})

    assert network_manager.get.called

    response.header.return_value = "application/json"
    response.readAll.return_value = ("{\"version\": \"" + __version__ + "\", \"local\": true}").encode()

    # Trigger the completion of /version
    response.finished.emit()

    # Trigger the completion
    response.finished.emit()

    assert network_manager.post.called

    assert http_client._connected
    assert callback.called

    args, kwargs = callback.call_args
    assert kwargs["context"]["toto"] == 42


def test_post_not_connected_connection_failed(http_client, request, network_manager, response):

    http_client._connected = False
    callback = unittest.mock.MagicMock()

    response.error.return_value = QtNetwork.QNetworkReply.ConnectionRefusedError

    http_client.post("/test", callback)

    assert network_manager.get.called

    # Trigger the completion of /version
    response.finished.emit()

    assert callback.called


def test_progress_callback(http_client, response):

    http_client._connected = True
    callback = unittest.mock.MagicMock()
    progress = unittest.mock.MagicMock()

    http_client.setProgressCallback(progress)
    http_client.post("/test", callback)

    # Trigger the completion
    response.finished.emit()

    assert progress.add_query_signal.emit.called
    assert progress.remove_query_signal.emit.called
