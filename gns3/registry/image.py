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
import hashlib

import logging
log = logging.getLogger(__name__)


class Image:
    """
    An appliance image file.
    """

    # Cache md5sum in order to improve performances
    _cache = {}

    def __init__(self, emulator, path, filename=None):
        """
        :params: Emulator type
        :params: path of the image
        """

        self._location = "local"
        self._emulator = emulator
        self._path = path
        if filename is None:
            self._filename = os.path.basename(self.path)
        else:
            self._filename = filename
        self._md5sum = None
        self._version = None
        self._filesize = None

    @property
    def location(self):
        """
        :returns: remote or local. Where the file is store.
        If local we will need to upload it at the end of the process
        """
        return self._location

    @location.setter
    def location(self, val):
        self._location = val

    @property
    def filename(self):
        """
        :returns: Image filename
        """
        return self._filename

    @property
    def path(self):
        """
        :returns: Image path
        """
        return self._path

    @property
    def version(self):
        """
        :returns: Get the file version / release
        """
        return self._version

    @version.setter
    def version(self, version):
        """
        :returns: Set the file version / release
        """
        self._version = version

    @property
    def md5sum(self):
        """
        Compute a md5 hash for file

        :params cache: Cache sum on disk
        :returns: hexadecimal md5
        """

        if self._md5sum is None:
            from_cache = Image._cache.get(self._path)
            if from_cache:
                self._md5sum = from_cache
                return self._md5sum

            md5_file = self._path + ".md5sum"
            if os.path.exists(md5_file):
                try:
                    with open(md5_file) as f:
                        self._md5sum = f.read().strip()
                        return self._md5sum
                except (OSError, UnicodeDecodeError) as e:
                    log.debug("Could not read '{}': {}".format(md5_file, e))

            try:
                if not os.path.isfile(self._path):
                    return None
            except (OSError, PermissionError) as e:
                log.debug("Cannot access '{}': {}".format(self._path, e))
                return None
            m = hashlib.md5()
            with open(self._path, "rb") as f:
                while True:
                    buf = f.read(4096)
                    if not buf:
                        break
                    m.update(buf)
            self._md5sum = m.hexdigest()
        Image._cache[self._path] = self._md5sum
        return self._md5sum

    @md5sum.setter
    def md5sum(self, val):
        self._md5sum = val

    @property
    def filesize(self):
        """
        Return image file size
        """
        if self._filesize is not None:
            return self._filesize
        try:
            self._filesize = os.path.getsize(self._path)
            return self._filesize
        except OSError:
            return 0

    @filesize.setter
    def filesize(self, val):
        self._filesize = val

    @property
    def emulator(self):
        return self._emulator
