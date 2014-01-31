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
Base class for port objects.
"""

from ..nios.nio_udp import NIO_UDP


class Port(object):
    """
    Base port.

    :param name: port name (string)
    :param nio: NIO object to attach to this port
    """

    def __init__(self, name, default_nio=None, stub=False):

        self._name = name
        self._slot = None
        self._port = None
        self._stub = stub
        if default_nio == None:
            self._default_nio = NIO_UDP
        else:
            self._default_nio = default_nio
        self._nio = None

    @property
    def name(self):
        """
        Returns the name of this port.

        :returns: current port name (string)
        """

        return self._name

    @name.setter
    def name(self, new_name):
        """
        Sets a new name for this port.

        :param new_name: new port name (string)
        """

        self._name = new_name

    @property
    def slot(self):
        """
        Returns the slot number for this port.

        :returns: current slot number (integer)
        """

        return self._slot

    @slot.setter
    def slot(self, slot):
        """
        Sets the slot number for this port.

        :param slot: new slot number (integer)
        """

        self._slot = slot

    @property
    def port(self):
        """
        Returns the port number for this port.

        :returns: current port number (integer)
        """

        return self._port

    @port.setter
    def port(self, port):
        """
        Sets the port number for this port.

        :param port: new port number (integer)
        """

        self._port = port

    @property
    def default_nio(self):

        return self._default_nio

    @property
    def nio(self):
        """
        Returns the NIO attached to this port.

        :returns: NIO object
        """

        return self._nio

    @nio.setter
    def nio(self, nio):
        """
        Attach a NIO to this port.

        :param nio: NIO object
        """

        self._nio = nio

    def isFree(self):
        """
        Checks if this port is free to use (no NIO attached).

        :returns: boolean
        """

        if self._nio:
            return False
        return True

    def isStub(self):
        """
        Checks if this is a stub port.

        :returns: boolean
        """

        return self._stub

    @staticmethod
    def linkType():
        """
        Default link type to be used.

        :returns: string
        """

        return "Ethernet"

    def __str__(self):

        return self._name
