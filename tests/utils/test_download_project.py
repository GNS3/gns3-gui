# -*- coding: utf-8 -*-
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

import pytest
import os
from unittest.mock import MagicMock


from gns3.project import Project
from gns3.servers import Servers
from gns3.utils.download_project import DownloadProjectWorker


@pytest.fixture(scope="function")
def servers():

    Servers._instance = None
    servers = Servers.instance()
    servers._remote_servers = {}  #  Erase server from settings
    return servers


@pytest.fixture(scope="function")
def project(tmpdir):

    p = MagicMock()
    p.filesDir.return_value = str(tmpdir)
    return p


@pytest.fixture(scope="function")
def download_project(project, servers):

    return DownloadProjectWorker(None, project, servers)


def test_download_project_without_server(download_project):

    download_project.run()


def test_download_project_with_one_server(download_project, servers, tmpdir, project):

    one = servers.getRemoteServer("http", "127.0.0.1", 8000, None)
    download_project.run()
    project.get.assert_called_with(one, "/files", download_project._fileListReceived)
    assert download_project._get_file_lists == 1


def test_fileListReceived(download_project, servers):

    download_project._get_file_lists = 3
    one = servers.getRemoteServer("http", "127.0.0.1", 8000, None)
    two = servers.getRemoteServer("http", "127.0.0.1", 8001, None)

    download_project._fileListReceived([{"path": "a", "md5sum": "d8e8fca2dc0f896fd7cb4cb0031ba249"}], server=one)
    download_project._fileListReceived([{"path": "b", "md5sum": "126a8a51b9d1bbd07fddc65819a542c3"}], server=two)
    assert download_project._get_file_lists == 1

    assert download_project._files_to_download == [
        {"path": "a", "md5sum": "d8e8fca2dc0f896fd7cb4cb0031ba249", "server": one},
        {"path": "b", "md5sum": "126a8a51b9d1bbd07fddc65819a542c3", "server": two}
    ]
    assert download_project._total_files_to_download == 2


def test_downloadNextFile_empty_list(download_project):

    mark_finished = MagicMock()
    download_project.finished.connect(mark_finished)
    download_project._is_running = True
    download_project._downloadNextFile()
    download_project._is_running = False
    assert mark_finished.called


def test_downloadNextFile_non_empty_list(download_project, servers, project):

    one = servers.getRemoteServer("http", "127.0.0.1", 8000, None)

    download_project._files_to_download = [
        {"path": "a", "md5sum": "d8e8fca2dc0f896fd7cb4cb0031ba249", "server": one}
    ]
    download_project._total_files_to_download = 1
    download_project._is_running = True

    mark_finished = MagicMock()
    download_project.finished.connect(mark_finished)
    download_project._downloadNextFile()
    assert not mark_finished.called

    assert os.path.exists(os.path.join(project.filesDir(), "a"))
    assert project.get.called
    args, kwargs = project.get.call_args
    assert args[0] == one
    assert args[1] == "/files/a"
    assert args[2] == download_project._downloadFileReceived
    assert kwargs["context"] is not None
    assert kwargs["downloadProgressCallback"] == download_project._downloadFileProgress


def test_downloadNextFile_file_exist_but_different(download_project, servers, project):

    one = servers.getRemoteServer("http", "127.0.0.1", 8000, None)

    download_project._files_to_download = [
        {"path": "a", "md5sum": "d8e8fca2dc0f896fd7cb4cb0031ba249", "server": one}
    ]
    download_project._total_files_to_download = 1
    download_project._is_running = True

    with open(os.path.join(project.filesDir(), "a"), "w+") as f:
        f.write("hello")

    download_project._downloadNextFile()

    assert project.get.called
    args, kwargs = project.get.call_args
    assert args[0] == one
    assert args[1] == "/files/a"
    assert args[2] == download_project._downloadFileReceived
    assert kwargs["context"] is not None
    assert kwargs["downloadProgressCallback"] == download_project._downloadFileProgress


def test_downloadNextFile_file_exist_and_the_same(download_project, servers, project):

    one = servers.getRemoteServer("http", "127.0.0.1", 8000, None)

    download_project._files_to_download = [
        {"path": "a", "md5sum": "5d41402abc4b2a76b9719d911017c592", "server": one}
    ]
    download_project._total_files_to_download = 1

    with open(os.path.join(project.filesDir(), "a"), "w+") as f:
        f.write("hello")

    download_project._downloadNextFile()

    assert not project.get.called


def test_downloadNextFile_subdirectory(download_project, servers, project):

    one = servers.getRemoteServer("http", "127.0.0.1", 8000, None)

    download_project._files_to_download = [
        {"path": "a/b/c", "md5sum": "d8e8fca2dc0f896fd7cb4cb0031ba249", "server": one}
    ]
    download_project._total_files_to_download = 4
    download_project._is_running = True

    mark_finished = MagicMock()
    download_project.finished.connect(mark_finished)

    progress = MagicMock()
    download_project.updated.connect(progress)

    download_project._downloadNextFile()
    assert not mark_finished.called
    progress.assert_called_once_with(75)

    assert os.path.exists(os.path.join(project.filesDir(), "a", "b", "c"))
    assert project.get.called
    args, kwargs = project.get.call_args
    assert args[0] == one
    assert args[1] == "/files/a/b/c"
    assert args[2] == download_project._downloadFileReceived
    assert kwargs["context"] is not None
    assert kwargs["downloadProgressCallback"] == download_project._downloadFileProgress


def test_downloadFileReceived(download_project, tmpdir):

    f = open(str(tmpdir / "a"), "w+")
    download_project._downloadFileReceived(None, context={"fd": f})
    assert f.closed


# TODO: Test progress
# TODO: MD5 sum

def test_downloadFileReceived(download_project, tmpdir):

    f = open(str(tmpdir / "a"), "w+")
    download_project._downloadFileProgress("hello", context={"fd": f})
    f.close()
    with open(str(tmpdir / "a")) as f:
        assert f.read() == "hello"
