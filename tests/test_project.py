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


def test_project_create():

    uuid = uuid4()
    mock = MagicMock
    with patch("gns3.http_client.HTTPClient.post") as mock:

        signal = MagicMock()

        project = Project()
        project.project_created_signal.connect(signal)
        project.create()

        args, kwargs = mock.call_args

        assert args[0] == "/projects"
        assert kwargs["body"] == {"temporary": False, "project_id": None}
        # Call the project creation callback
        args[1]({"project_id": uuid})
        assert project.uuid() == uuid

        assert signal.called


def test_project_close():

    uuid = uuid4()
    mock = MagicMock
    with patch("gns3.http_client.HTTPClient.post") as mock:

        signal = MagicMock()

        project = Project()
        project.setUuid(uuid)

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
        args[1]({"project_id": uuid})
        assert mock_signal_closed.called

        assert project.closed()


def test_project_close_error():

    uuid = uuid4()
    mock = MagicMock
    with patch("gns3.http_client.HTTPClient.post") as mock:

        signal = MagicMock()

        project = Project()
        project.setUuid(uuid)

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
        args[1]({"message": "Can't connect"}, error=True)
        assert mock_signal_closed.called

        assert project.closed()


def test_project_commit():

    with patch("gns3.http_client.HTTPClient.post") as mock:

        project = Project()
        project.setUuid(str(uuid4()))
        project.commit()

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/projects/{project_id}/commit".format(project_id=project.uuid())
