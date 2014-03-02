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

from ..nios.nio_udp import NIOUDP


class Port(object):
    """
    Base port.

    :param name: port name (string)
    :param default_nio: NIO object to use by default
    :param stub: indicates a stub port
    """

    _instance_count = 1

    # port statuses
    stopped = 0
    started = 1
    suspended = 2

    def __init__(self, name, default_nio=None, stub=False):

        # create an unique ID
        self._id = Port._instance_count
        Port._instance_count += 1

        self._name = name
        self._port_number = None
        self._slot_number = None
        self._stub = stub
        self._link_id = None
        self._description = ""
        self._status = Port.stopped
        self._data = {}
        if default_nio == None:
            self._default_nio = NIOUDP
        else:
            self._default_nio = default_nio
        self._nio = None

    def id(self):
        """
        Returns an unique identifier for this port.

        :returns: port identifier (integer)
        """

        return self._id

    def setId(self, new_id):
        """
        Sets an identifier for this port.

        :param new_id: node identifier (integer)
        """

        self._id = new_id

    @classmethod
    def reset(cls):
        """
        Reset the instance count.
        """

        cls._instance_count = 1

    def name(self):
        """
        Returns the name of this port.

        :returns: current port name (string)
        """

        return self._name

    def setName(self, new_name):
        """
        Sets a new name for this port.

        :param new_name: new port name (string)
        """

        self._name = new_name

    def status(self):
        """
        Returns the status of this port.
        0 = stopped, 1 = started, 2 = suspended.

        :returns: port status (integer)
        """

        return self._status

    def setStatus(self, status):
        """
        Sets a status for this port.
        0 = stopped, 1 = started, 2 = suspended.

        :param status: port status (integer)
        """

        self._status = status

    def slotNumber(self):
        """
        Returns the slot number for this port.

        :returns: current slot number (integer)
        """

        return self._slot_number

    def setSlotNumber(self, slot_number):
        """
        Sets the slot number for this port.

        :param slot_number: new slot number (integer)
        """

        self._slot_number = slot_number

    def portNumber(self):
        """
        Returns the port number for this port.

        :returns: current port number (integer)
        """

        return self._port_number

    def setPortNumber(self, port_number):
        """
        Sets the port number for this port.

        :param port: new port number (integer)
        """

        self._port_number = port_number

    def defaultNio(self):
        """
        Returns the default NIO for this port.

        :returns: NIO object
        """

        return self._default_nio

    def nio(self):
        """
        Returns the NIO attached to this port.

        :returns: NIO instance
        """

        return self._nio

    def setNio(self, nio):
        """
        Attach a NIO to this port.

        :param nio: NIO instance
        """

        self._nio = nio

    def linkId(self):
        """
        Returns the link id connected to this port.

        :returns: link id (integer)
        """

        return self._link_id

    def setLinkId(self, link_id):
        """
        Adds the link id connected to this port.

        :param link_id: link id (integer)
        """

        self._link_id = link_id

    def description(self):
        """
        Returns the text description of this port.

        :returns: description
        """

        return self._description

    def setDescription(self, description):
        """
        Adds a text description to this port.

        :param description: description
        """

        self._description = description

    def setFree(self):
        """
        Frees this port.
        """

        self._nio = None
        self._link_id = None
        self._description = ""

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

    def data(self):
        """
        Returns the data associated with this port.

        :returns: current port data (dictionary)
        """

        return self._data

    def setData(self, new_data):
        """
        Sets data to be associated with this port.

        :param new_data: new port data (dictionary)
        """

        self._data = new_data

    def dump(self):
        """
        Returns a representation of this port.

        :returns: dictionary
        """

        port = {"name": self._name,
                "id": self._id}

        if self._nio:
            port["nio"] = str(self._nio)
        if self._port_number != None:
            port["port_number"] = self._port_number
        if self._slot_number != None:
            port["slot_number"] = self._slot_number
        if self._stub:
            port["stub"] = self._stub
        if self._description:
            port["description"] = self._description
        if self._link_id != None:
            port["link_id"] = self._link_id

        return port

    def __str__(self):

        return self._name
