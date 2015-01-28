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
Interface for TAP NIOs (UNIX based OSes only).
"""

from .nio import NIO


class NIOTAP(NIO):

    """
    TAP NIO.

    :param tap_device: TAP device name (e.g. tap0)
    """

    def __init__(self, tap_device):

        NIO.__init__(self)
        self._tap_device = tap_device

    def __str__(self):

        return "NIO_TAP"

    def tapDevice(self):
        """
        Returns the TAP device used by this NIO.

        :returns: the TAP device name
        """

        return self._tap_device
