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
GigabitEthernet port for Ethernet link end points.
"""

from .port import Port


class GigabitEthernetPort(Port):

    """
    GigabitEthernet port.

    :param name: port name (string)
    :param nio: NIO instance to attach to this port
    """

    def __init__(self, name, nio=None):

        Port.__init__(self, name, nio)

    @staticmethod
    def longNameType():
        """
        Returns the long name type for this port.

        :returns: string
        """

        return "GigabitEthernet"

    @staticmethod
    def shortNameType():
        """
        Returns the short name type for this port.

        :returns: string
        """

        return "g"
