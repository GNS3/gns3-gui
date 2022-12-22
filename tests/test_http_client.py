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

from gns3.qt import QtCore, QtNetwork, FakeQtSignal, QtWebSockets
from gns3.http_client import HTTPClient
from gns3.http_client_error import HttpClientError, HttpClientBadRequestError
from gns3.version import __version__, __version_info__


@pytest.fixture
def network_manager(response):

    mock = unittest.mock.MagicMock()
    mock.sendCustomRequest.return_value = response
    return mock


@pytest.fixture
def response():
    response = unittest.mock.MagicMock()
    type(response).finished = unittest.mock.PropertyMock(return_value=FakeQtSignal())
    response.error.return_value = QtNetwork.QNetworkReply.NoError
    response.attribute.return_value = 200
    response.header.return_value = "application/json"
    return response


@pytest.fixture
def http_client(http_request, network_manager):

    http_client = HTTPClient({"protocol": "http", "host": "127.0.0.1", "port": "3080"})
    http_client._network_manager = network_manager
    return http_client


@pytest.fixture(autouse=True)
def http_request():

    mock = unittest.mock.Mock()

    def call_request(url):
        mock(url)
        return mock
    with unittest.mock.patch("gns3.http_client.HTTPClient._request", side_effect=call_request):
        yield mock


def test_get_connected(http_client, http_request, network_manager, response):

    http_client._connected = True
    callback = unittest.mock.MagicMock()

    http_client.sendRequest("GET", "/test", callback)
    http_request.assert_called_with(QtCore.QUrl("http://127.0.0.1:3080/v3/test"))
    http_request.setHeader.assert_any_call(QtNetwork.QNetworkRequest.UserAgentHeader, f"GNS3 QT Client v{__version__}")
    assert network_manager.sendCustomRequest.called
    args, kwargs = network_manager.sendCustomRequest.call_args
    assert args[0] == http_request
    assert args[1] == b"GET"

    # Trigger the completion
    response.finished.emit()

    assert callback.called


def test_paramsToQueryString(http_client):
    assert http_client._paramsToQueryString({}) == ""
    res = http_client._paramsToQueryString({"a": 1, "b": 2})
    assert res == "?a=1&b=2" or res == "?b=2&a=1"
    res = http_client._paramsToQueryString({"a": 1, "b": 2, "c": None})
    assert res == "?a=1&b=2" or res == "?b=2&a=1"


def test_get_connected_auth(http_client, http_request, network_manager, response):

    http_client._connected = True
    http_client._jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYzOTAzMjE1MH0.OWPhF8Fc1Wva-WyNoHfzBk2nraYUqTOdTed0q5QwTaI"
    callback = unittest.mock.MagicMock()

    http_client.sendRequest("GET", "/test", callback)
    http_request.assert_called_with(QtCore.QUrl("http://127.0.0.1:3080/v3/test"))
    http_request.setRawHeader.assert_any_call(b"Authorization", "Bearer {}".format(http_client._jwt_token).encode())
    http_request.setHeader.assert_any_call(QtNetwork.QNetworkRequest.UserAgentHeader, f"GNS3 QT Client v{__version__}")
    assert network_manager.sendCustomRequest.called
    args, kwargs = network_manager.sendCustomRequest.call_args
    assert args[0] == http_request
    assert args[1] == b"GET"

    # Trigger the completion
    response.finished.emit()

    assert callback.called


def test_dataReadySlot(http_client):

    callback = unittest.mock.MagicMock()
    response = unittest.mock.MagicMock()
    response.header.return_value = "application/json"
    response.error.return_value = QtNetwork.QNetworkReply.NoError
    response.attribute.return_value = 200
    response.readAll.return_value = b'{"action": "ping"}'
    http_client._dataReadySlot(response, callback, {"query_id": "bla"})

    assert callback.called
    args, kwargs = callback.call_args
    assert args[0] == {"action": "ping"}


def test_dataReadySlotHTTPError(http_client):

    callback = unittest.mock.MagicMock()
    response = unittest.mock.MagicMock()
    response.header.return_value = "application/json"
    response.error.return_value = QtNetwork.QNetworkReply.NoError
    response.attribute.return_value = 404
    http_client._dataReadySlot(response, callback, {"query_id": "bla"})
    assert not callback.called


def test_dataReadySlotConnectionRefusedError(http_client):

    callback = unittest.mock.MagicMock()
    response = unittest.mock.MagicMock()
    response.header.return_value = "application/json"
    response.error.return_value = QtNetwork.QNetworkReply.ConnectionRefusedError
    response.attribute.return_value = 200
    http_client._dataReadySlot(response, callback, {"query_id": "bla"})
    assert not callback.called


def test_dataReadySlotPartialJSON(http_client):
    """
    We can read an incomplete JSON on the network and we need
    to wait for the next part"""
    callback = unittest.mock.MagicMock()
    response = unittest.mock.MagicMock()
    response.header.return_value = "application/json"
    response.readAll.return_value = b'{"action": "ping"'
    response.error.return_value = QtNetwork.QNetworkReply.NoError
    response.attribute.return_value = 200
    http_client._dataReadySlot(response, callback, {"query_id": "bla"})
    assert not callback.called
    response.readAll.return_value = b'}\n{"a": "b"'
    http_client._dataReadySlot(response, callback, {"query_id": "bla"})
    assert callback.call_count == 1
    args, kwargs = callback.call_args
    assert args[0] == {"action": "ping"}


def test_dataReadySlotPartialBytes(http_client):

    callback = unittest.mock.MagicMock()
    response = unittest.mock.MagicMock()
    response.header.return_value = "application/octet-stream"
    response.readAll.return_value = b'hello'
    response.error.return_value = QtNetwork.QNetworkReply.NoError
    response.attribute.return_value = 200

    http_client._dataReadySlot(response, callback, {"query_id": "bla"})

    assert callback.call_count == 1
    args, kwargs = callback.call_args
    assert args[0] == b'hello'


def test_validateServerVersion_version_ok(http_client):

    params = {
        "local": True,
        "version": __version__
    }
    http_client._validateServerVersion(params)


def test_validateServerVersion_major_version_invalid(http_client):

    params = {
        "local": True,
        "version": "1.2.3"
    }
    mock = unittest.mock.MagicMock()
    http_client._query_waiting_connections.append((None, mock))
    with pytest.raises(HttpClientError):
        http_client._validateServerVersion(params)


def test_validateServerVersion_minor_version_invalid(http_client):

    new_version = "{}.{}.{}".format(__version_info__[0], __version_info__[1], __version_info__[2] + 1)
    params = {
        "local": True,
        "version": new_version
    }
    mock = unittest.mock.MagicMock()

    http_client._query_waiting_connections.append((None, mock))
    # Stable release
    if __version_info__[3] == 0:
        http_client._validateServerVersion(params)
        mock.assert_called_with({"message": "Client version {} is not the same as server (controller) version {}".format(__version__, new_version)}, error=True, server=None)
    else:
        http_client._validateServerVersion(params)


def test_non_gns3_server(http_client):

    params = {
        "virus": True,
    }
    mock = unittest.mock.MagicMock()
    http_client._query_waiting_connections.append((None, mock))
    with pytest.raises(HttpClientBadRequestError):
        http_client._validateServerVersion(params)
    assert http_client._connected is False


def test_connectWebSocket(http_client):

    http_client._jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYzOTAzMjE1MH0.OWPhF8Fc1Wva-WyNoHfzBk2nraYUqTOdTed0q5QwTaI"
    with unittest.mock.patch('gns3.qt.QtWebSockets.QWebSocket.open') as open_mock:
        test = QtWebSockets.QWebSocket()
        http_client.connectWebSocket(test, '/test')
    assert open_mock.called
    request = open_mock.call_args[0][0]
    assert request.url().toString() == "ws://127.0.0.1:3080/v3/test?token={}".format(http_client._jwt_token)
