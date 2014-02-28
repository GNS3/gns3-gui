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
NIO (Network Input/Output) for UDP tunnel connections (port is chosen automatically in a defined range)
"""

from .nio import NIO


#TODO: finish this.
class NIOUDPAuto(NIO):
    """
    NIO UDP Auto.

    :param laddr: local address
    :param lport_start: start local port range
    :param lport_end: end local port range
    """

    def __init__(self, laddr, lport_start, lport_end):

        NIO.__init__(self)

        self._laddr = laddr
        self._lport_start = lport_start
        self._lport_end = lport_end

    def __str__(self):

        return "NIO_UDP_Auto"

    def laddr(self):
        """
        Returns the local address

        :returns: local address
        """

        return self._laddr

    def lport(self):
        """
        Returns the local port

        :returns: local port number
        """

        return self._lport

    def raddr(self):
        """
        Returns the remote address

        :returns: remote address
        """

        return self._raddr

    def rport(self):
        """
        Returns the remote port

        :returns: remote port number
        """

        return self._rport
