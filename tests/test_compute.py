#!/usr/bin/env python
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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

from gns3.compute import Compute


def test_init():
    compute = Compute("local")
    assert compute.id() == "local"


def test_init_without_id():
    compute = Compute()
    assert compute.id() is not None


def test_json():
    compute = Compute("test")
    compute.setHost("example.org")
    compute.setName("Test")
    compute.setProtocol("https")
    compute.setUser("hello")
    compute.setPassword("world")
    compute.setPort(4242)
    assert compute.__json__() == {
        'compute_id': 'test',
        'host': 'example.org',
        'name': 'Test',
        'password': 'world',
        'port': 4242,
        'protocol': 'https',
        'user': 'hello'
    }
