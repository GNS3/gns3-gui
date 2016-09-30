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

import copy
from unittest.mock import MagicMock

from gns3.compute_manager import ComputeManager
from gns3.compute import Compute


def test_getCompute():
    cm = ComputeManager()
    compute = cm.getCompute("local")
    assert cm.getCompute("local") == compute


def test_getComputeRemote1X():
    """
    It should convert old server id
    """
    cm = ComputeManager()
    cm.computeDataReceivedCallback({
        "compute_id": "aaecb19d-5a32-4c18-ac61-f54f92a0f594",
        "name": "Test Compute",
        "connected": True,
        "protocol": "http",
        "host": "test.org",
        "port": 3080,
        "user": None,
        "cpu_usage_percent": None,
        "memory_usage_percent": None,
        "capabilities": {"test": "a"}
    })

    compute = cm.getCompute("aaecb19d-5a32-4c18-ac61-f54f92a0f594")
    assert cm.getCompute("http://test.org:3080") == compute


def test_deleteCompute(controller):
    callback_delete = MagicMock()
    cm = ComputeManager()
    cm.deleted_signal.connect(callback_delete)
    compute = cm.getCompute("test")
    assert cm.getCompute("test") == compute
    cm.deleteCompute("test")
    assert "test" not in cm._computes
    assert callback_delete.called
    controller._http_client.createHTTPQuery.assert_called_with("DELETE", "/computes/test", None)


def test_listComputesCallback():
    callback = MagicMock()
    cm = ComputeManager()
    cm.created_signal.connect(callback)
    cm._listComputesCallback([
        {
            "compute_id": "local",
            "name": "Local server",
            "connected": False,
            "protocol": "http",
            "host": "localhost",
            "port": 3080,
            "user": None,
            "cpu_usage_percent": None,
            "memory_usage_percent": None,
            "capabilities": {"test": "a"}
        }
    ])
    assert cm._computes["local"].name() == "Local server"
    assert callback.called


def test_computeDataReceivedCallback():
    callback_create = MagicMock()
    callback_update = MagicMock()
    cm = ComputeManager()
    cm.created_signal.connect(callback_create)
    cm.updated_signal.connect(callback_update)
    cm.computeDataReceivedCallback({
        "compute_id": "test",
        "name": "Test server",
        "connected": False,
        "protocol": "http",
        "host": "test.org",
        "port": 3080,
        "user": None,
        "cpu_usage_percent": None,
        "memory_usage_percent": None,
        "capabilities": {"test": "a"}
    })
    assert cm._computes["test"].name() == "Test server"
    assert cm._computes["test"].protocol() == "http"
    assert cm._computes["test"].host() == "test.org"
    assert cm._computes["test"].port() == 3080
    assert cm._computes["test"].user() is None
    assert cm._computes["test"].capabilities() == {"test": "a"}
    assert cm._computes["test"].connected() is False
    assert callback_create.called
    assert not callback_update.called

    # Data should be update
    cm.computeDataReceivedCallback({
        "compute_id": "test",
        "name": "Test Compute",
        "connected": True,
        "protocol": "http",
        "host": "test.org",
        "port": 3080,
        "user": None,
        "cpu_usage_percent": None,
        "memory_usage_percent": None,
        "capabilities": {"test": "a"}
    })
    assert cm._computes["test"].name() == "Test Compute"
    assert cm._computes["test"].connected()
    assert callback_update.called


def test_updateList_deleted(controller):
    cm = ComputeManager()
    computes = []
    computes.append(cm.getCompute("test1"))
    computes.append(cm.getCompute("test2"))
    # This server new to be deleted because exist in compute manager
    # but not in setting list
    cm.getCompute("test3")
    cm.updateList(computes)
    assert "test1" in cm._computes
    assert "test2" in cm._computes
    assert "test3" not in cm._computes


def test_updateList_updated(controller):
    cm = ComputeManager()
    computes = []
    compute = copy.copy(cm.getCompute("test1"))
    computes.append(compute)
    compute.setName("TEST2")
    cm.updateList(computes)
    assert cm._computes["test1"].name() == "TEST2"
    controller._http_client.createHTTPQuery.assert_called_with("PUT", "/computes/test1", None, body=compute.__json__())


def test_updateList_added(controller):
    cm = ComputeManager()
    computes = []
    compute = Compute()
    computes.append(compute)
    controller._http_client = MagicMock()
    cm.updateList(computes)
    assert compute.id() in cm._computes
    controller._http_client.createHTTPQuery.assert_called_with("POST", "/computes", None, body=compute.__json__())


def test_updateList_no_change(controller):
    cm = ComputeManager()
    computes = []
    compute = copy.copy(cm.getCompute("test1"))
    computes.append(compute)
    controller._http_client = MagicMock()
    cm.updateList(computes)
    assert not controller._http_client.createHTTPQuery.called
