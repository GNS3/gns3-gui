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

import re
import os
import hashlib
import shutil
import tarfile

import logging
log = logging.getLogger(__name__)


class Image:
    """
    An appliance image file.
    """

    # Cache md5sum in order to improve performances
    _cache = {}

    def __init__(self, path):
        """
        :params: path of the image
        """

        self.path = path
        self._md5sum = None
        self._version = None

    @property
    def filename(self):
        """
        :returns: Image filename
        """
        return os.path.basename(self.path)

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
            from_cache = Image._cache.get(self.path)
            if from_cache:
                self._md5sum = from_cache
                return self._md5sum

            if os.path.exists(self.path + ".md5sum"):
                with open(self.path + ".md5sum", encoding="utf-8") as f:
                    self._md5sum = f.read()
                    return self._md5sum

            if not os.path.isfile(self.path):
                return None
            m = hashlib.md5()
            with open(self.path, "rb") as f:
                while True:
                    buf = f.read(4096)
                    if not buf:
                        break
                    m.update(buf)
            self._md5sum = m.hexdigest()
        Image._cache[self.path] = self._md5sum
        return self._md5sum

    @property
    def filesize(self):
        """
        Return image file size
        """
        try:
            return os.path.getsize(self.path)
        except OSError:
            return 0

    def copy(self, directory, filename):
        """
        Copy the image to a directory. Extract the image if it's an OVA.

        The destination directory is created if not exists

        :param directory: Destination directory
        """
        log.debug("Copy %s to %s", directory, filename)

        is_tar = False
        if tarfile.is_tarfile(self.path):
            if '/' in filename or '\\' in filename:
                # In case of OVA we want to update the OVA name
                base_file = re.split(r'[/\\]', filename)[0]
            else:
                base_file = filename
            dst = os.path.join(directory, base_file)

            # is_tarfile can have false positive if file start with 00000 like ISO
            # we check if we have file in the tar
            tar = tarfile.open(self.path)
            if len(tar.getnames()) > 0:
                is_tar = True
                os.makedirs(dst, exist_ok=True)
                tar.extractall(path=dst)
            tar.close()

        if not is_tar:
            dst = os.path.join(directory, filename)
            os.makedirs(directory, exist_ok=True)
            shutil.copy(self.path, dst)
        with open(dst + ".md5sum", "w+", encoding="utf-8") as f:
            f.write(self.md5sum)
