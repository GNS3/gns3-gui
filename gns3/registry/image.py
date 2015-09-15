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



class Image:
    """
    An appliance image file.
    """

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

        if os.path.exists(self.path + ".md5sum"):
            with open(self.path + ".md5sum", encoding="utf-8") as f:
                self._md5sum = f.read()
                return self._md5sum

        if self._md5sum is None:
            m = hashlib.md5()
            with open(self.path, "rb") as f:
                while True:
                    buf = f.read(4096)
                    if not buf:
                        break
                    m.update(buf)
            self._md5sum = m.hexdigest()
        return self._md5sum

    @property
    def filesize(self):
        """
        Return image file size
        """
        return os.path.getsize(self.path)
