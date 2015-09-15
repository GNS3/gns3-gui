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
import copy

from .image import Image


class RegistryError(Exception):
    pass


class Registry:
    def __init__(self, images_dirs):
        self._images_dirs = images_dirs

    def list_images(self):
        """
        List image on user computer
        """
        images = []

        for directory in self._images_dirs:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    if not filename.endswith(".md5sum") and not filename.startswith("."):
                        path = os.path.join(directory, filename)
                        if os.path.isfile(path):
                            images.append(Image(path))
        return images

    def search_image_file(self, md5sum):
        """
        Search an image based on its MD5 checksum

        :param md5sum: Hash of the image
        :returns: Image object or None
        """

        for directory in self._images_dirs:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    if not filename.endswith(".md5sum") and not filename.startswith("."):
                        path = os.path.join(directory, filename)
                        if os.path.isfile(path):
                            image = Image(path)
                            if image.md5sum == md5sum:
                                return image.path
        return None
