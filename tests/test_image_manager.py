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

import pathlib
import pytest
import os
from unittest.mock import patch

from gns3.image_manager import ImageManager

@pytest.yield_fixture
def image_manager(tmpdir):
    ImageManager._instance = None
    with patch('gns3.servers.Servers.localServerSettings', return_value={'images_path': str(tmpdir)}):
        yield ImageManager.instance()


@pytest.fixture
def qemu_img(tmpdir):
    """
    Return a fake qemu IMG
    """
    path = str(tmpdir / 'QEMU' /'test.img')
    os.makedirs(str(tmpdir / 'QEMU'))
    open(path, 'w+').close()
    return path


def test_askCopyUploadImage_remote(image_manager, remote_server):
    with patch('gns3.image_manager.ImageManager._uploadImageToRemoteServer') as mock:
        image_manager.askCopyUploadImage(None, '/tmp/test', remote_server, 'QEMU')
        assert mock.called


def test_uploadImageToRemoteServer(image_manager, remote_server):
    with patch('gns3.http_client.HTTPClient.post') as mock:
        filename = image_manager._uploadImageToRemoteServer('/tmp/test', remote_server, 'QEMU')
        assert filename == 'test'
        args, kwargs = mock.call_args
        assert args[0] == '/qemu/vms/test'
        assert kwargs['body'] == pathlib.Path('/tmp/test')


def test_getDirectory(image_manager, tmpdir):
    assert image_manager.getDirectory() == str(tmpdir)


def test_directoryType(image_manager, tmpdir):
    assert image_manager.getDirectoryForType('DYNAMIPS') == str(tmpdir / 'IOS')
    assert image_manager.getDirectoryForType('QEMU') == str(tmpdir / 'QEMU')
    assert image_manager.getDirectoryForType('IOU') == str(tmpdir / 'IOU')


def test_addMissingImage(image_manager, remote_server, qemu_img):
    with patch('gns3.image_manager.ImageManager._uploadImageToRemoteServer') as mock:
        with patch('gns3.image_manager.ImageManager._askForUploadMissingImage', return_value=True):
            image_manager.addMissingImage('test.img', remote_server, 'QEMU')
            assert mock.called
            args, kwargs = mock.call_args
            assert args[0] == qemu_img
            assert args[1] == remote_server
            assert args[2] == 'QEMU'


def test_addMissingImage_ask_once(image_manager, remote_server, qemu_img):
    with patch('gns3.image_manager.ImageManager._askForUploadMissingImage', return_value=False) as mock:
        image_manager.addMissingImage('test.img', remote_server, 'QEMU')
        image_manager.addMissingImage('test.img', remote_server, 'QEMU')
        assert mock.call_count == 1


def test_addMissingImageLocalServer(image_manager, local_server, qemu_img):
    with patch('gns3.image_manager.ImageManager._uploadImageToRemoteServer') as mock:
        image_manager.addMissingImage('test.img', local_server, 'QEMU')
        assert not mock.called
