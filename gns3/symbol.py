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

import urllib.parse


class Symbol:
    def __init__(self, symbol_id=None, builtin=False, filename=None):
        self._id = symbol_id
        self._builtin = builtin
        self._filename = filename

    def id(self):
        return self._id

    def filename(self):
        return self._filename

    def builtin(self):
        return self._builtin

    def url(self):
        return urllib.parse.quote("/symbols/" + self._id + "/raw")

