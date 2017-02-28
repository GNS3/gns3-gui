#!/usr/bin/env python
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

import os

import logging
log = logging.getLogger(__name__)

from .image import Image
from ..controller import Controller
from ..qt import QtCore


class RegistryError(Exception):
    pass


class Registry(QtCore.QObject):
    image_list_changed_signal = QtCore.pyqtSignal()

    def __init__(self, images_dirs):
        """
        :param images_dirs: Local image image dir
        """
        super().__init__()
        self._images_dirs = images_dirs
        self._remote_images = []

    def appendImageDirectory(self, image_directory):
        """
        Add a folder to the list of we need to scan

        :param image_directory: Folder we need to add
        """
        self._images_dirs.append(image_directory)

    def getRemoteImageList(self, emulator, compute_id):
        self._emulator = emulator
        Controller.instance().getCompute("/{}/images".format(emulator), compute_id, self._getRemoteListCallback, progressText="Listing remote images...")

    def _getRemoteListCallback(self, result, error=False, **kwargs):
        if error:
            if "message" in result:
                log.error("Error while getting the list of remote images: {}".format(result["message"]))
            return
        self._remote_images = []
        for res in result:
            image = Image(self._emulator, res["path"])
            image.location = "remote"
            image.md5sum = res.get("md5sum")
            image.filesize = res.get("filesize")
            self._remote_images.append(image)
        self.image_list_changed_signal.emit()

    def search_image_file(self, emulator, filename, md5sum, size):
        """
        Search an image based on its MD5 checksum

        :param emulator: Emulator type
        :param filename: Image filename (used for ova in order to return the correct file in the archive)
        :param md5sum: Hash of the image
        :param size: File size
        :returns: Image object or None
        """

        for remote_image in list(self._remote_images):
            if remote_image.md5sum == md5sum:
                return remote_image
            elif md5sum is None:  # We create a new version
                if filename == remote_image.filename:
                    return remote_image

        for directory in self._images_dirs:
            log.debug("Search images %s (%s) in %s", filename, md5sum, directory)
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    if not file.endswith(".md5sum") and not file.startswith("."):
                        path = os.path.join(directory, file)
                        try:
                            if os.path.isfile(path):
                                if md5sum is None:
                                    if filename == os.path.basename(path):
                                        return Image(emulator, path)
                                else:
                                    # We take all the file with almost the size of the image
                                    # Almost to avoid round issue with system.
                                    file_size = os.stat(path).st_size
                                    if size is None or (file_size - 10 < size and file_size + 10 > size):
                                        image = Image(emulator, path)
                                        if image.md5sum == md5sum:
                                            log.debug("Found images %s (%s) in %s", filename, md5sum, image.path)
                                            return image
                        except (OSError, PermissionError) as e:
                            log.error("Can't scan {}: {}".format(path, str(e)))

        return None
