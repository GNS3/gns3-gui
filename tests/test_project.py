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

from unittest.mock import patch, MagicMock
from uuid import uuid4

from gns3.project import Project


def test_project_create(tmpdir, controller):
    """
    Test a post on a local servers. The project
    is not created on the server and should be created automatically.
    And after make the call
    """

    uuid = str(uuid4())
    project = Project()
    project.setFilesDir(str(tmpdir))
    project.setName("test")

    project.create()

    mock = controller._http_client.createHTTPQuery
    assert mock.called
    args, kwargs = mock.call_args
    assert args[0] == "POST"
    assert args[1] == "/projects"
    assert kwargs["body"] == {"name": "test",
                              "path": str(tmpdir),
                              "grid_size": 75,
                              "drawing_grid_size": 25,
                              "show_grid": False,
                              "snap_to_grid": False,
                              "show_interface_labels": False}

    args[2]({"project_id": uuid, "name": "test"})

    assert project._closed is False


def test_project_post_on_created_project(controller):
    """
    Test a post on a remote servers.
    The project is already created on the server
    """

    uuid = uuid4()
    project = Project()
    project._created = True
    project.setId(uuid)

    project.post("/test", lambda: 0, body={"test": "test"})

    mock = controller._http_client.createHTTPQuery
    args, kwargs = mock.call_args
    assert args[0] == "POST"
    assert args[1] == "/projects/{uuid}/test".format(uuid=uuid)
    assert kwargs["body"] == {"test": "test"}


def test_project_get_on_created_project(controller):
    """
    Test a get on a remote servers.
    The project is already created on the server
    """

    uuid = uuid4()
    project = Project()
    project._created = True
    project.setId(uuid)

    project.get("/test", lambda: 0)
    mock = controller._http_client.createHTTPQuery

    args, kwargs = mock.call_args
    assert args[0] == "GET"
    assert args[1] == "/projects/{uuid}/test".format(uuid=uuid)


def test_project_put_on_created_project(controller):
    """
    Test a put on a remote servers.
    The project is already created on the server
    """

    uuid = uuid4()
    project = Project()
    project._created = True
    project.setId(uuid)

    project.put("/test", lambda: 0, body={"test": "test"})
    mock = controller._http_client.createHTTPQuery

    args, kwargs = mock.call_args
    assert args[0] == "PUT"
    assert args[1] == "/projects/{uuid}/test".format(uuid=uuid)
    assert kwargs["body"] == {"test": "test"}


def test_project_delete_on_created_project(controller):
    """
    Test a delete on a remote servers.
    The project is already created on the server
    """

    uuid = uuid4()
    project = Project()
    project._created = True
    project.setId(uuid)

    project.delete("/test", lambda: 0)
    mock = controller._http_client.createHTTPQuery

    args, kwargs = mock.call_args
    assert args[0] == "DELETE"
    assert args[1] == "/projects/{uuid}/test".format(uuid=uuid)


def test_project_destroy(controller):
    project = Project()
    project.setId(str(uuid4()))
    project.destroy()

    mock = controller._http_client.createHTTPQuery
    assert mock.called
    args, kwargs = mock.call_args

    assert args[0] == "DELETE"
    assert args[1] == "/projects/{project_id}".format(project_id=project.id())


def test_project_variables():
    project = Project()
    project.setVariables([{'name': 'TEST'}])

    variables = project.variables()
    assert variables == [{'name': 'TEST'}]


def test_project_supplier():
    project = Project()
    project.setSupplier({'logo': 'test.png', 'url':  'http://domain'})

    supplier = project.supplier()
    assert supplier == {'logo': 'test.png', 'url':  'http://domain'}


def test_project_parse_response():
    result = {
        'project_id': 'projectid',
        'name': 'projectname',
        'filename': 'filename.gns3',
        'variables': [{'name': 'TEST'}],
        'supplier': {'logo': 'test.png', 'url':  'http://domain'}
    }
    project = Project()
    project._parseResponse(result)
    assert project.id() == 'projectid'
    assert project.name() == 'projectname'
    assert project.filename() == 'filename.gns3'
    assert project.variables() == [{'name': 'TEST'}]
    assert project.supplier() == {'logo': 'test.png', 'url':  'http://domain'}


def test_project_update(controller):
    project = Project()
    project.setVariables([{'name': 'TEST'}])
    project.setSupplier({'logo': 'test.png', 'url':  'http://domain'})
    project.update()
    mock = controller._http_client.createHTTPQuery
    args, kwargs = mock.call_args
    body = kwargs['body']
    assert body['variables'] == [{'name': 'TEST'}]
    assert body['supplier'] == {'logo': 'test.png', 'url':  'http://domain'}

