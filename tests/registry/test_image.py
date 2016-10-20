#!/usr/bin/env python
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
import pytest
import tarfile
import io

from gns3.registry.image import Image


def test_filename(linux_microcore_img):
    image = Image("qemu", linux_microcore_img)
    assert image.filename == "linux-microcore-3.4.1.img"


def test_md5sum(linux_microcore_img):
    image = Image("qemu", linux_microcore_img)
    assert image.md5sum == "5d41402abc4b2a76b9719d911017c592"
    assert image._cache[linux_microcore_img] == "5d41402abc4b2a76b9719d911017c592"


def test_md5sum_ova(tmpdir):
    """
    An OVA can't have a md5sum computed. We can only use the disk cache.
    """
    path = str(tmpdir / "test.ova")
    os.makedirs(path)

    image = Image("qemu", path)
    assert image.md5sum is None

    with open(path + ".md5sum", "w+", encoding="utf-8") as f:
        f.write("56f46611dfa80d0eead602cbb3f6dcee")

    image = Image("qemu", path)
    assert image.md5sum == "56f46611dfa80d0eead602cbb3f6dcee"


def test_filesize(linux_microcore_img):
    image = Image("qemu", linux_microcore_img)
    assert image.filesize == 5


def test_md5sum_from_memory_cache(linux_microcore_img):
    Image._cache[linux_microcore_img] = "4d41402abc4b2a76b9719d911017c591"
    image = Image("qemu", linux_microcore_img)
    assert image.md5sum == "4d41402abc4b2a76b9719d911017c591"


def test_md5sum_from_file_cache(tmpdir):
    path = str(tmpdir / "test.img")
    open(path, "w+").close()

    with open(path + ".md5sum", "w+", encoding="utf-8") as f:
        f.write("56f46611dfa80d0eead602cbb3f6dcee")

    image = Image("qemu", path)
    assert image.md5sum == "56f46611dfa80d0eead602cbb3f6dcee"
