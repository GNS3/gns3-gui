# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 GNS3 Technologies Inc.
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
import pathlib

from gns3.http_client_error import HttpClientError, HttpClientCancelledRequestError
from gns3.qt import QtWidgets
from gns3.registry.image import Image
from gns3.controller import Controller

import logging
log = logging.getLogger(__name__)


class ImageUploadManager(object):
    """
    Manager over the image upload
    """

    def __init__(self, image: Image, controller: Controller, parent: QtWidgets.QWidget):

        self._image = image
        self._controller = controller
        self._parent = parent

    def upload(self) -> bool:

        if not os.path.exists(self._image.path):
            log.error("Image '{}' could not be found".format(self._image.path))
            return False
        return self._fileUploadToController()

    def _fileUploadToController(self) -> bool:

        log.debug("Uploading image '{}' to controller".format(self._image.path))
        try:
            self._controller.post(
                f"/images/upload/{self._image.filename}",
                callback=None,
                body=pathlib.Path(self._image.path),
                context={"image_path": self._image.path},
                progress_text="Uploading {}".format(self._image.filename),
                timeout=None,
                wait=True
            )
        except HttpClientCancelledRequestError:
            return False
        except HttpClientError as e:
            QtWidgets.QMessageBox.critical(
                self._parent,
                "Image upload",
                f"Could not upload image {self._image.filename}: {e}"
            )
            return False
        return True
