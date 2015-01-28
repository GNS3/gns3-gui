# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GNS3 Technologies Inc.
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

"""
Interface for dummy NIOs (mostly for tests or fake connections).
"""

from .nio import NIO


class NIONull(NIO):

    """
    NULL NIO.
    """

    def __init__(self, identifier):

        NIO.__init__(self)
        self._identifier = identifier

    def __str__(self):

        return "NIO_Null"

    def identifier(self):
        """
        Returns the identifier used by this NIO.

        :returns: the identifier
        """

        return self._identifier
