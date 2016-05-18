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


class RegistryError(Exception):
    pass


class Registry:

    def __init__(self, images_dirs):
        self._images_dirs = images_dirs

    def appendImageDirectory(self, image_directory):
        """
        Add a folder to the list of we need to scan

        :param image_directory: Folder we need to add
        """
        self._images_dirs.append(image_directory)

    def search_image_file(self, filename, md5sum, size):
        """
        Search an image based on its MD5 checksum

        :param filename: Image filename (used for ova in order to return the correct file in the archive)
        :param md5sum: Hash of the image
        :param size: File size
        :returns: Image object or None
        """

        for directory in self._images_dirs:
            log.debug("Search images %s (%s) in %s", filename, md5sum, directory)
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    if not file.endswith(".md5sum") and not file.startswith("."):
                        path = os.path.join(directory, file)
                        if os.path.isfile(path):
                            if md5sum is None:
                                if filename == os.path.basename(path):
                                    return Image(path)
                            else:
                                # We take all the file with almost the size of the image
                                # Almost to avoid round issue with system.
                                file_size = os.stat(path).st_size
                                if size is None or (file_size - 10 < size and file_size + 10 > size):
                                    image = Image(path)
                                    if image.md5sum == md5sum:
                                        log.debug("Found images %s (%s) in %s", filename, md5sum, image.path)
                                        return image
                        elif path.endswith(".ova"):
                            if md5sum is None:
                                # File searched in OVA use the notation x.ova/a.vmdk
                                if os.path.dirname(filename) == os.path.basename(path):

                                    path = os.path.join(path, os.path.basename(filename))
                                    log.debug("Found images  %s (%s) from ova in %s", filename, md5sum, path)
                                    return Image(path)
                            else:
                                image = Image(path)
                                if image.md5sum == md5sum:
                                    # File searched in OVA use the notation x.ova/a.vmdk
                                    path = os.path.join(image.path, os.path.basename(filename))
                                    log.debug("Found images  %s (%s) from ova in %s", filename, md5sum, path)
                                    return Image(path)

        return None
