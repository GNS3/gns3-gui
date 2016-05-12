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


from gns3.utils import parse_version


def test_parse_version():
    assert parse_version('1') == ('000001', '00000', '000000', 'final')
    assert parse_version('1.3') == ('000001', '000003', '000000', 'final')
    assert parse_version('1.3.dev3') == ('000001', '000003', '000000', 'dev', '000003')
    assert parse_version('1.3a1') == ('000001', '000003', '000000', 'a', '000001')
    assert parse_version('1.3rc1') == ('000001', '000003', '000000', 'c', '000001')

    assert parse_version('1.2.3') > parse_version('1.2.2')
    assert parse_version('1.3') > parse_version('1.2.2')
    assert parse_version('1.3') > parse_version('1.3alpha1')
    assert parse_version('1.3') > parse_version('1.3rc1')
    assert parse_version('1.3rc1') > parse_version('1.3alpha3')
    assert parse_version('1.3dev1') > parse_version('1.3rc1')
    assert parse_version('1.2.3') > parse_version('1.2')
