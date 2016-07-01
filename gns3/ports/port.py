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

import os
import sys
import tempfile
import shutil
import subprocess
import shlex
import logging

log = logging.getLogger(__name__)

from gns3.utils.normalize_filename import normalize_filename
from ..local_config import LocalConfig
from ..settings import PACKET_CAPTURE_SETTINGS


class Port:

    """
    Base port.

    :param name: port name (string)
    """

    _instance_count = 1
    _settings = {}

    # port statuses
    stopped = 0
    started = 1
    suspended = 2

    def __init__(self, name):

        # create an unique ID
        self._id = Port._instance_count
        Port._instance_count += 1

        # In 1.3.3 and 1.3.4 we have issue with port name not a string
        # see: https://github.com/gns3/gns3-gui/issues/393
        assert isinstance(name, str)

        self._name = name
        self._short_name = None
        self._port_number = None
        self._adapter_number = None
        self._link_id = None
        self._link = None
        self._port_label = None
        self._status = Port.stopped
        self._data = {}
        self._destination_node = None
        self._destination_port = None
        self._hot_pluggable = True

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

        # update the instance count to avoid conflicts
        if new_id >= Port._instance_count:
            Port._instance_count = new_id + 1

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

    def shortName(self):
        """
        Returns the short name of this port.

        :returns: current short port name (string)
        """

        if not self._short_name:
            return self._name
        return self._short_name

    def setShortName(self, short_name):
        """
        Sets a new short name for this port.

        :param short_name: short port name (string)
        """

        self._short_name = short_name

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

    def adapterNumber(self):
        """
        Returns the slot number for this port.

        :returns: current slot number (integer)
        """

        return self._adapter_number

    def setAdapterNumber(self, adapter_number):
        """
        Sets the adapter number for this port.

        :param adapter_number: new slot number (integer)
        """

        self._adapter_number = adapter_number

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

    def destinationNode(self):
        """
        Returns the destination node

        :returns: destination Node instance
        """

        return self._destination_node

    def setDestinationNode(self, node):
        """
        Sets a new destination Node instance for this port.

        :param node: new destination Node instance
        """

        self._destination_node = node

    def destinationPort(self):
        """
        Returns the destination Port instance

        :returns: destination Port instance
        """

        return self._destination_port

    def setDestinationPort(self, port):
        """
        Sets a new destination Port instance for this port.

        :param port: new destination Port instance
        """

        self._destination_port = port

    def setLink(self, link):
        """
        Adds the link connected to this port.

        :param link: Link object
        """

        self._link = link
        if self._link and self._port_label:
            self._link.addPortLabel(self, self._port_label)

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

    def description(self, short=False):
        """
        Returns the text description of this port.

        :param short: returns a shorter description.

        :returns: description
        """

        if self._destination_node and self._destination_port:
            if short:
                return "<-> {port} {name}".format(port=self._destination_port.shortName(),
                                                  name=self._destination_node.name())
            return "connected to {name} on port {port}".format(name=self._destination_node.name(),
                                                               port=self._destination_port.name())
        return ""

    def setFree(self):
        """
        Frees this port.
        """

        self._link_id = None
        self._link = None
        self._destination_node = None
        self._destination_port = None
        self._port_label = None

    def isFree(self):
        """
        Checks if this port is free to use (no NIO attached).

        :returns: boolean
        """

        if self._link_id:
            return False
        return True

    def setHotPluggable(self, hot_pluggable):
        """
        :param hot_pluggable: either the port is hot pluggable.
        """

        self._hot_pluggable = hot_pluggable

    def isHotPluggable(self):
        """
        Checks if this port is hot pluggable.

        :returns: boolean
        """

        return self._hot_pluggable

    @staticmethod
    def linkType():
        """
        Default link type to be used.

        :returns: string
        """

        return "Ethernet"

    @staticmethod
    def dataLinkTypes():
        """
        Returns the supported PCAP DLTs.

        :return: dictionary
        """

        return {"Ethernet": "DLT_EN10MB"}

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

    def label(self):
        """
        Returns the port label.

        :return: NoteItem instance.
        """

        return self._port_label

    def setLabel(self, label):
        """
        Sets a port label.

        :param label: NoteItem instance.
        """
        self._port_label = label
        if self._link and self._port_label:
            self._link.addPortLabel(self, self._port_label)

    def deleteLabel(self):
        """
        Deletes a port label.
        """

        if self._port_label is not None:
            self._port_label.delete()
            self._port_label = None

    def __str__(self):

        return self._name
