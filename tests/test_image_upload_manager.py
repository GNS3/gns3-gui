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

def test_upload_controller(image, controller, callback):
    manager = ImageUploadManager(image, controller, None)
    manager.upload()
    controller.post(
        f"/images/upload/{image.filename}",
        callback=callback,
        params={"image_type": image.type},
        body=pathlib.Path(image.path),
        context={"image_path": image.path},
        progress_text="Uploading {}".format(image.filename),
        timeout=None,
        wait=False
    )
