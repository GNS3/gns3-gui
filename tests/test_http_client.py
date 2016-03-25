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

from gns3.qt import QtCore, QtNetwork, FakeQtSignal
from gns3.http_client import HTTPClient
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

    return HTTPClient({"protocol": "http", "host": "127.0.0.1", "port": "3080"}, network_manager)


@pytest.yield_fixture(autouse=True)
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

    http_client.get("/test", callback)
    http_request.assert_called_with(QtCore.QUrl("http://127.0.0.1:3080/v1/test"))

    http_request.setRawHeader.assert_any_call(b"Content-Type", b"application/json")
    http_request.setRawHeader.assert_any_call(b"User-Agent", "GNS3 QT Client v{version}".format(version=__version__).encode())
    assert network_manager.sendCustomRequest.called
    args, kwargs = network_manager.sendCustomRequest.call_args
    assert args[0] == http_request
    assert args[1] == b"GET"

    # Trigger the completion
    response.finished.emit()

    assert callback.called


def test_get_connected_auth(http_client, http_request, network_manager, response):

    http_client._connected = True
    http_client._user = "gns3"
    http_client._password = "3sng"
    callback = unittest.mock.MagicMock()

    http_client.get("/test", callback)
    http_request.assert_called_with(QtCore.QUrl("http://gns3@127.0.0.1:3080/v1/test"))
    http_request.setRawHeader.assert_any_call(b"Content-Type", b"application/json")
    http_request.setRawHeader.assert_any_call(b"Authorization", b"Basic Z25zMzozc25n")
    http_request.setRawHeader.assert_any_call(b"User-Agent", "GNS3 QT Client v{version}".format(version=__version__).encode())
    assert network_manager.sendCustomRequest.called
    args, kwargs = network_manager.sendCustomRequest.call_args
    assert args[0] == http_request
    assert args[1] == b"GET"

    # Trigger the completion
    response.finished.emit()

    assert callback.called


def test_post_not_connected(http_client, http_request, network_manager, response):

    http_client._connected = False
    callback = unittest.mock.MagicMock()

    http_client.post("/test", callback, context={"toto": 42})

    args, kwargs = network_manager.sendCustomRequest.call_args
    assert args[0] == http_request
    assert args[1] == b"GET"

    response.header.return_value = "application/json"
    response.readAll.return_value = ("{\"version\": \"" + __version__ + "\", \"local\": true}").encode()

    # Trigger the completion of /version
    response.finished.emit()

    # Trigger the completion
    response.finished.emit()

    args, kwargs = network_manager.sendCustomRequest.call_args
    assert args[0] == http_request
    assert args[1] == b"POST"

    assert http_client._connected
    assert callback.called

    args, kwargs = callback.call_args
    assert kwargs["context"]["toto"] == 42


def test_post_not_connected_connection_failed(http_client, http_request, network_manager, response):

    http_client._connected = False
    callback = unittest.mock.MagicMock()

    response.error.return_value = QtNetwork.QNetworkReply.ConnectionRefusedError

    http_client.post("/test", callback)

    args, kwargs = network_manager.sendCustomRequest.call_args
    assert args[0] == http_request
    assert args[1] == b"GET"

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


def test_processDownloadProgress(http_client):

    callback = unittest.mock.MagicMock()
    response = unittest.mock.MagicMock()
    response.header.return_value = "application/json"
    response.error.return_value = QtNetwork.QNetworkReply.NoError
    response.attribute.return_value = 200

    response.readAll.return_value = b'{"action": "ping"}'

    http_client._processDownloadProgress(response, callback, {"query_id": "bla"}, 10, 100)

    assert callback.called
    args, kwargs = callback.call_args
    assert args[0] == {"action": "ping"}


def test_processDownloadProgressHTTPError(http_client):

    callback = unittest.mock.MagicMock()
    response = unittest.mock.MagicMock()
    response.header.return_value = "application/json"
    response.error.return_value = QtNetwork.QNetworkReply.NoError
    response.attribute.return_value = 404

    http_client._processDownloadProgress(response, callback, {"query_id": "bla"}, 10, 100)

    assert not callback.called


def test_processDownloadProgressConnectionRefusedError(http_client):

    callback = unittest.mock.MagicMock()
    response = unittest.mock.MagicMock()
    response.header.return_value = "application/json"
    response.error.return_value = QtNetwork.QNetworkReply.ConnectionRefusedError
    response.attribute.return_value = 200

    http_client._processDownloadProgress(response, callback, {"query_id": "bla"}, 10, 100)

    assert not callback.called


def test_processDownloadProgressPartialJSON(http_client):
    """
    We can read an incomplete JSON on the network and we need
    to wait for the next part"""
    callback = unittest.mock.MagicMock()
    response = unittest.mock.MagicMock()
    response.header.return_value = "application/json"
    response.readAll.return_value = b'{"action": "ping"'
    response.error.return_value = QtNetwork.QNetworkReply.NoError
    response.attribute.return_value = 200

    http_client._processDownloadProgress(response, callback, {"query_id": "bla"}, 10, 100)

    assert not callback.called

    response.readAll.return_value = b'}\n{"a": "b"'
    http_client._processDownloadProgress(response, callback, {"query_id": "bla"}, 10, 100)

    assert callback.call_count == 1
    args, kwargs = callback.call_args
    assert args[0] == {"action": "ping"}


def test_processDownloadProgressPartialBytes(http_client):
    callback = unittest.mock.MagicMock()
    response = unittest.mock.MagicMock()
    response.header.return_value = "application/octet-stream"
    response.readAll.return_value = b'hello'
    response.error.return_value = QtNetwork.QNetworkReply.NoError
    response.attribute.return_value = 200

    http_client._processDownloadProgress(response, callback, {"query_id": "bla"}, 10, 100)

    assert callback.call_count == 1
    args, kwargs = callback.call_args
    assert args[0] == b'hello'


def test_dump(http_client):

    assert http_client.dump() == {
        'host': '127.0.0.1',
        'id': 0,
        'local': True,
        'port': 3080,
        'protocol': 'http',
        'vm': False}


def test_callbackConnect_version_ok(http_client):

    params = {
        "local": True,
        "version": __version__
    }
    http_client._callbackConnect("GET", "/version", None, {}, {}, params)
    assert http_client._connected


def test_callbackConnect_version_non_local(http_client):

    params = {
        "local": False,
        "version": __version__
    }
    mock = unittest.mock.MagicMock()
    http_client._callbackConnect("GET", "/version", mock, {}, {}, params)
    assert http_client._connected is False
    mock.assert_called_with({"message": "Running server is not a GNS3 local server (not started with --local)"}, error=True, server=http_client)


def test_callbackConnect_version_non_local_remote_server(http_client):

    params = {
        "local": False,
        "version": __version__
    }
    mock = unittest.mock.MagicMock()
    http_client._local = False
    http_client._callbackConnect("GET", "/version", mock, {}, {}, params)
    assert http_client._connected is True


def test_callbackConnect_major_version_invalid(http_client):

    params = {
        "local": True,
        "version": "1.2.3"
    }
    mock = unittest.mock.MagicMock()
    http_client._callbackConnect("GET", "/version", mock, {}, {}, params)
    assert http_client._connected is False
    mock.assert_called_with({"message": "Client version {} differs with server version 1.2.3".format(__version__)}, error=True, server=http_client)


def test_callbackConnect_minor_version_invalid(http_client):

    new_version = "{}.{}.{}".format(__version_info__[0], __version_info__[1], __version_info__[2] + 1)
    params = {
        "local": True,
        "version": new_version
    }
    mock = unittest.mock.MagicMock()

    # Stable release
    if __version_info__[3] == 0:
        http_client._callbackConnect("GET", "/version", mock, {}, {}, params)
        assert http_client._connected is False
        mock.assert_called_with({"message": "Client version {} differs with server version {}".format(__version__, new_version)}, error=True, server=http_client)
    else:
        http_client._callbackConnect("GET", "/version", mock, {}, {}, params)
        assert http_client._connected is True


def test_callbackConnect_non_gns3_server(http_client):

    params = {
        "virus": True,
    }
    mock = unittest.mock.MagicMock()
    http_client._callbackConnect("GET", "/version", mock, {}, {}, params)
    assert http_client._connected is False
    mock.assert_called_with({"message": "The remote server http://127.0.0.1:3080 is not a GNS3 server"}, error=True, server=http_client)
