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
Base class for node classes.
"""

from .qt import QtCore


class Node(QtCore.QObject):
    """
    Node implementation.
    """

    # signals used to let the GUI view know about some events.
    newname_signal = QtCore.Signal(str)
    started_signal = QtCore.Signal()
    stopped_signal = QtCore.Signal()
    suspended_signal = QtCore.Signal()
    delete_links_signal = QtCore.Signal()
    delete_signal = QtCore.Signal()
    error_signal = QtCore.Signal(str, int, str)
    nio_signal = QtCore.Signal(int)
    allocate_udp_nio_signal = QtCore.Signal(int, int, str)

    _instance_count = 1

    def __init__(self):

        super(Node, self).__init__()

        # create an unique ID
        self._id = Node._instance_count
        Node._instance_count += 1

    @property
    def id(self):
        """
        Returns this node identifier.

        :returns: node identifier (integer)
        """

        return self._id

    def name(self):
        """
        Returns the name of this node.
        Must be overloaded.

        :returns: name (string)
        """

        raise NotImplementedError()

    def update(self, new_settings):
        """
        Updates the settings for this node.
        Must be overloaded.

        :param new_settings: settings dictionary
        """

        raise NotImplementedError()

    def ports(self):
        """
        Returns all the ports for this node.
        Must be overloaded.

        :returns: list of Port objects
        """

        raise NotImplementedError()

    def configPage(self):
        """
        Returns the configuration page widget to be used by the node configurator.
        Must be overloaded.

        :returns: QWidget object.
        """

        raise NotImplementedError()

    def settings(self):
        """
        Returns all the node settings.
        Must be overloaded.

        :returns: settings dictionary
        """

        raise NotImplementedError()

    @staticmethod
    def defaultSymbol():
        """
        Returns the default symbol path for this node.
        Must be overloaded.

        :returns: symbol path (or resource).
        """

        raise NotImplementedError()

    @staticmethod
    def hoverSymbol():
        """
        Returns the symbol to use when the node is hovered.
        Must be overloaded.

        :returns: symbol path (or resource).
        """

        raise NotImplementedError()

    @staticmethod
    def symbolName():
        """
        Returns the symbol name (for the nodes view).

        :returns: name (string)
        """

        raise NotImplementedError()

    def __str__(self):
        """
        Must be overloaded.
        """

        raise NotImplementedError()
