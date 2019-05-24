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

import os
import pytest
import unittest.mock
import pathlib
import tempfile

from gns3.registry.image import Image
from gns3.image_upload_manager import ImageUploadManager


@pytest.fixture
def image():
    (fd, path) = tempfile.mkstemp(suffix=".img")
    return Image('QEMU', path)


@pytest.fixture
def controller():
    return unittest.mock.MagicMock()

@pytest.fixture
def callback():
    return unittest.mock.MagicMock()


def test_direct_file_upload(image, controller, callback):


    manager = ImageUploadManager(image, controller, 'compute_id', callback, directFileUpload=True)
    manager.upload()
    controller.getEndpoint.assert_called_with(
        '/QEMU/images/{}'.format(image.filename),
        'compute_id',
        manager._onLoadEndpointCallback,
        showProgress=False
    )

    with unittest.mock.patch('gns3.image_upload_manager.HTTPClient') as client:
        manager._onLoadEndpointCallback(dict(endpoint='/endpoint'))
        client.fromUrl.return_value.createHTTPQuery.assert_called_with(
            'POST', '/endpoint', manager._checkIfSuccessfulCallback, body=pathlib.Path(image.path),
            prefix="", context={'image_path': image.path}, progressText='Uploading {}'.format(image.filename), timeout=None
        )

    manager._checkIfSuccessfulCallback({})
    callback.assert_called_with({}, False)


def test_direct_file_upload_fallback_to_controller(image, controller, callback):
    manager = ImageUploadManager(image, controller, callback, directFileUpload=True)
    manager._checkIfSuccessfulCallback({}, error=True, connection_error=True)
    controller.postCompute.assert_called_with(
        '/QEMU/images/{}'.format(image.filename),
        callback,
        None,
        body=pathlib.Path(image.path),
        context={'image_path': image.path},
        progressText='Uploading {}'.format(image.filename),
        timeout=None
    )


def test_upload_via_controller(image, controller, callback):
    manager = ImageUploadManager(image, controller, callback, directFileUpload=False)
    manager.upload()
    controller.postCompute.assert_called_with(
        '/QEMU/images/{}'.format(image.filename),
        callback,
        None,
        body=pathlib.Path(image.path),
        context={'image_path': image.path},
        progressText='Uploading {}'.format(image.filename),
        timeout=None
    )

