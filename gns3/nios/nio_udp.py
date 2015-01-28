# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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
NIO (Network Input/Output) for UDP tunnel connections.
"""

from .nio import NIO


class NIOUDP(NIO):

    """
    NIO UDP.

    :param lport: local port number
    :param rhost: remote address/host
    :param rport: remote port number
    """

    def __init__(self, lport, rhost, rport):

        NIO.__init__(self)

        self._lport = lport
        self._rhost = rhost
        self._rport = rport

    def __str__(self):

        return "NIO_UDP"

    def lport(self):
        """
        Returns the local port

        :returns: local port number
        """

        return self._lport

    def rhost(self):
        """
        Returns the remote host

        :returns: remote address/host
        """

        return self._rhost

    def rport(self):
        """
        Returns the remote port

        :returns: remote port number
        """

        return self._rport
