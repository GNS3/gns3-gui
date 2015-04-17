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
Interface for VDE (Virtual Distributed Ethernet) NIOs (Unix based OSes only).
"""

from .nio import NIO


class NIOVDE(NIO):

    """
    VDE NIO.

    :param control_file: VDE control filename
    :param local_file: VDE local filename
    """

    def __init__(self, control_file, local_file):

        super().__init__()
        self._control_file = control_file
        self._local_file = local_file

    def __str__(self):

        return "NIO_VDE"

    def controlFile(self):
        """
        Returns the VDE control file.

        :returns: VDE control filename
        """

        return self._control_file

    def localFile(self):
        """
        Returns the VDE local file.

        :returns: VDE local filename
        """

        return self._local_file
