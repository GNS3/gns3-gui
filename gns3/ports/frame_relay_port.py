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
Frame relay port for serial link end points.
"""

from .serial_port import SerialPort


class FrameRelayPort(SerialPort):

    """
    Frame port.

    :param name: port name (string)
    :param nio: NIO instance to attach to this port
    """

    def __init__(self, name, nio=None):

        super().__init__(name, nio)

    @staticmethod
    def dataLinkTypes():
        """
        Returns the supported PCAP DLTs.

        :return: dictionary
        """

        return {"Frame Relay": "DLT_FRELAY"}
