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


import pytest
import json
import os


from gns3.registry.registry import Registry, RegistryError


def test_search_image_file(tmpdir):

    os.makedirs(str(tmpdir / "QEMU"))
    with open(str(tmpdir / "QEMU" / "a"), "w+", encoding="utf-8") as f:
        f.write("ALPHA")
    with open(str(tmpdir / "QEMU" / "b"), "w+", encoding="utf-8") as f:
        f.write("BETA")
    with open(str(tmpdir / "QEMU" / "c"), "w+", encoding="utf-8") as f:
        f.write("CHARLIE")
    with open(str(tmpdir / "QEMU" / "c.md5sum"), "w+", encoding="utf-8") as f:
        f.write("42b84f8e3fba5bf993e3ba352d62d146")

    registry = Registry(set([str(tmpdir / "QEMU")]))
    image = registry.search_image_file("qemu", "b", "36b84f8e3fba5bf993e3ba352d62d146", 5)
    assert image.path == str(tmpdir / "QEMU" / "b")

    # Search by name
    image = registry.search_image_file("qemu", "b", None, None)
    assert image.path == str(tmpdir / "QEMU" / "b")

    # Test using md5sum cache file
    image = registry.search_image_file("qemu", "c", "42b84f8e3fba5bf993e3ba352d62d146", 5)
    assert image.path == str(tmpdir / "QEMU" / "c")

    # If size doesn't match ignore the file
    registry = Registry(set([str(tmpdir / "QEMU")]))
    image = registry.search_image_file("qemu", "b", "36b84f8e3fba5bf993e3ba352d62d146", 1000)
    assert image is None

    # md5sum doesn't exists
    assert registry.search_image_file("qemu", "x", "00000000000000000000000000000000", 5) is None
