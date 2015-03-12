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


def test_project_post_non_initialized_project_local_server(tmpdir, local_server):
    """
    Test a post on a local servers. The project
    is not created on the server and should be created automatically.
    And after make the call
    """

    uuid = str(uuid4())
    project = Project()
    project._created_servers = set()
    project.setFilesDir(str(tmpdir))

    with patch("gns3.http_client.HTTPClient.createHTTPQuery") as mock:
        project.post(local_server, "/test", lambda: 0, body={"test": "test"})

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "POST"
        assert args[1] == "/projects"
        assert kwargs["body"] == {"name": None,
                                  "temporary": False,
                                  "path": str(tmpdir),
                                  "project_id": None}

        args[2]({"project_id": uuid}, server=local_server)

        assert len(project._created_servers) == 1
        assert project._closed is False

        args, kwargs = mock.call_args
        assert args[0] == "POST"
        assert args[1] == "/projects/{uuid}/test".format(uuid=uuid)
        assert kwargs["body"] == {"test": "test"}


def test_project_post_non_created_project_local_server(tmpdir, local_server):
    """
    Test a post on a local servers. The project
    is not created on the server and should be created automaticaly.
    And after make the call
    """

    uuid = str(uuid4())
    project = Project()
    project.setId(uuid)
    project.setFilesDir(str(tmpdir))

    with patch("gns3.http_client.HTTPClient.createHTTPQuery") as mock:
        project.post(local_server, "/test", lambda: 0, body={"test": "test"})

        args, kwargs = mock.call_args
        assert args[0] == "POST"
        assert args[1] == "/projects"
        assert kwargs["body"] == {"name": None,
                                  "temporary": False,
                                  "project_id": uuid,
                                  "path": str(tmpdir)}

        args[2]({}, server=local_server)

        assert len(project._created_servers) == 1

        args, kwargs = mock.call_args
        assert args[0] == "POST"
        assert args[1] == "/projects/{uuid}/test".format(uuid=uuid)
        assert kwargs["body"] == {"test": "test"}


def test_project_post_non_created_project_remote_server(remote_server):
    """
    Test a post on a remote servers. The project
    is not created on the server and should be created automaticaly.
    And after make the call
    """

    uuid = uuid4()
    project = Project()
    project._created_servers = set()
    project.setId(uuid)

    with patch("gns3.http_client.HTTPClient.createHTTPQuery") as mock:
        project.post(remote_server, "/test", lambda: 0, body={"test": "test"})

        args, kwargs = mock.call_args
        assert args[0] == "POST"
        assert args[1] == "/projects"
        assert kwargs["body"] == {"name": None, "temporary": False, "project_id": uuid}

        args[2]({}, server=remote_server)

        assert len(project._created_servers) == 1

        args, kwargs = mock.call_args
        assert args[0] == "POST"
        assert args[1] == "/projects/{uuid}/test".format(uuid=uuid)
        assert kwargs["body"] == {"test": "test"}


def test_project_post_on_created_project(local_server):
    """
    Test a post on a remote servers.
    The project is already created on the server
    """

    uuid = uuid4()
    project = Project()
    project._created_servers = set((local_server, ))
    project.setId(uuid)

    with patch("gns3.http_client.HTTPClient.createHTTPQuery") as mock:
        project.post(local_server, "/test", lambda: 0, body={"test": "test"})

        args, kwargs = mock.call_args
        assert args[0] == "POST"
        assert args[1] == "/projects/{uuid}/test".format(uuid=uuid)
        assert kwargs["body"] == {"test": "test"}


def test_project_get_on_created_project(local_server):
    """
    Test a get on a remote servers.
    The project is already created on the server
    """

    uuid = uuid4()
    project = Project()
    project._created_servers = set((local_server, ))
    project.setId(uuid)

    with patch("gns3.http_client.HTTPClient.createHTTPQuery") as mock:
        project.get(local_server, "/test", lambda: 0)

        args, kwargs = mock.call_args
        assert args[0] == "GET"
        assert args[1] == "/projects/{uuid}/test".format(uuid=uuid)


def test_project_put_on_created_project(local_server):
    """
    Test a put on a remote servers.
    The project is already created on the server
    """

    uuid = uuid4()
    project = Project()
    project._created_servers = set((local_server, ))
    project.setId(uuid)

    with patch("gns3.http_client.HTTPClient.createHTTPQuery") as mock:
        project.put(local_server, "/test", lambda: 0, body={"test": "test"})

        args, kwargs = mock.call_args
        assert args[0] == "PUT"
        assert args[1] == "/projects/{uuid}/test".format(uuid=uuid)
        assert kwargs["body"] == {"test": "test"}


def test_project_delete_on_created_project(local_server):
    """
    Test a delete on a remote servers.
    The project is already created on the server
    """

    uuid = uuid4()
    project = Project()
    project._created_servers = set((local_server, ))
    project.setId(uuid)

    with patch("gns3.http_client.HTTPClient.createHTTPQuery") as mock:
        project.delete(local_server, "/test", lambda: 0)

        args, kwargs = mock.call_args
        assert args[0] == "DELETE"
        assert args[1] == "/projects/{uuid}/test".format(uuid=uuid)


def test_project_close(local_server):

    uuid = uuid4()
    mock = MagicMock
    with patch("gns3.http_client.HTTPClient.post") as mock:

        signal = MagicMock()

        project = Project()
        project._created_servers = set((local_server, ))
        project.setId(uuid)

        mock_signal = MagicMock()
        mock_signal_closed = MagicMock()
        project.project_about_to_close_signal.connect(mock_signal)
        project.project_closed_signal.connect(mock_signal_closed)

        project.close()

        assert mock_signal.called
        assert not mock_signal_closed.called

        args, kwargs = mock.call_args

        assert args[0] == "/projects/{project_id}/close".format(project_id=uuid)
        assert kwargs["body"] == {}

        # Call the project close callback
        args[1]({"project_id": uuid}, server=local_server)

        assert mock_signal_closed.called

        assert project.closed()


def test_project_close_multiple_servers(local_server, remote_server):

    uuid = uuid4()
    mock = MagicMock
    with patch("gns3.http_client.HTTPClient.post") as mock:

        signal = MagicMock()

        project = Project()
        project._created_servers = set((local_server, ))
        project._created_servers.add(remote_server)
        project.setId(uuid)

        mock_signal = MagicMock()
        mock_signal_closed = MagicMock()
        project.project_about_to_close_signal.connect(mock_signal)
        project.project_closed_signal.connect(mock_signal_closed)

        project.close()

        assert mock_signal.call_count == 1
        assert not mock_signal_closed.called

        assert mock.call_count == 2

        args, kwargs = mock.call_args

        assert args[0] == "/projects/{project_id}/close".format(project_id=uuid)
        assert kwargs["body"] == {}

        # Call the project close callback
        args[1]({"project_id": uuid}, server=local_server)
        args[1]({"project_id": uuid}, server=remote_server)

        assert mock_signal_closed.call_count == 1
        assert project.closed()


def test_project_close_error(local_server):

    uuid = uuid4()
    mock = MagicMock
    with patch("gns3.http_client.HTTPClient.post") as mock:

        signal = MagicMock()

        project = Project()
        project.setId(uuid)
        project._created_servers = set((local_server, ))

        mock_signal = MagicMock()
        mock_signal_closed = MagicMock()
        project.project_about_to_close_signal.connect(mock_signal)
        project.project_closed_signal.connect(mock_signal_closed)

        project.close()

        assert mock_signal.called
        assert not mock_signal_closed.called

        args, kwargs = mock.call_args

        assert args[0] == "/projects/{project_id}/close".format(project_id=uuid)
        assert kwargs["body"] == {}

        # Call the project close callback
        args[1]({"message": "Can't connect"}, error=True, server=local_server)
        assert mock_signal_closed.called

        assert project.closed()


def test_project_commit(local_server):

    with patch("gns3.http_client.HTTPClient.post") as mock:

        project = Project()
        project.setId(str(uuid4()))
        project._created_servers = set((local_server, ))
        project.commit()

        assert mock.called
        args, kwargs = mock.call_args

        assert args[0] == "/projects/{project_id}/commit".format(project_id=project.id())


def test_project_moveFromTemporaryToPath(tmpdir, local_server):

    project = Project()
    project.setId(str(uuid4()))
    project._created_servers = set((local_server, ))
    project._temporary = True

    with patch("gns3.http_client.HTTPClient.put") as mock:
        project.moveFromTemporaryToPath(str(tmpdir))

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/projects/{project_id}".format(project_id=project.id())
        assert kwargs["body"] == {"name": None, "path": str(tmpdir), "temporary": False}

    assert project.temporary() is False
    assert project.filesDir() == str(tmpdir)


def test_topology_file(tmpdir):

    project = Project()
    project.setName("test")
    project.setFilesDir(str(tmpdir))
    assert project.topologyFile() == str(tmpdir / "test.gns3")


def test_set_topology_file(tmpdir):

    project = Project()
    project.setTopologyFile(str(tmpdir / "test.gns3"))
    assert project.filesDir() == str(tmpdir)
    assert project.name() == "test"
