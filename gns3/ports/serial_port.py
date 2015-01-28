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
Serial port for serial link end points.
"""

from .port import Port


class SerialPort(Port):

    """
    Serial port.

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

        return "Serial"

    @staticmethod
    def shortNameType():
        """
        Returns the short name type for this port.

        :returns: string
        """

        return "s"

    @staticmethod
    def linkType():
        """
        Returns the link type to be used to connect this port.

        :returns: string
        """

        return "Serial"

    @staticmethod
    def dataLinkTypes():
        """
        Returns the supported PCAP DLTs.

        :return: dictionary
        """

        return {"Frame Relay": "DLT_FRELAY",
                "Cisco HDLC": "DLT_C_HDLC",
                "Cisco PPP": "DLT_PPP_SERIAL"}
