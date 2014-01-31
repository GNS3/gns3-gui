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
Manages and stores everything needed for a connection between 2 devices.
"""


from .qt import QtCore
from .nios.nio_udp import NIO_UDP

import logging
log = logging.getLogger(__name__)


class Link(QtCore.QObject):
    """
    Link implementation.

    :param source_node: source Node object
    :param source_port: source Port object
    :param destination_node: destination Node object
    :param destination_port: destination Port object
    :param stub: indicates if the link is connected to
    a stub device like a Cloud
    """

    # signals used to let the GUI view know about link
    # additions and deletions.
    add_link_signal = QtCore.Signal(int)
    delete_link_signal = QtCore.Signal(int)

    _instance_count = 1

    def __init__(self, source_node, source_port, destination_node, destination_port):

        super(Link, self).__init__()

        # create an unique ID
        self._id = Link._instance_count
        Link._instance_count += 1

        self._source_node = source_node
        self._source_port = source_port
        self._destination_node = destination_node
        self._destination_port = destination_port
        self._source_nio = None
        self._destination_nio = None
        self._source_nio_active = False
        self._destination_nio_active = False

        if source_port.isStub() or destination_port.isStub():
            self._stub = True
        else:
            self._stub = False

        #FIXME: polish this
        # we must request UDP information if the NIO is a NIO UDP and before
        # it can be created.
        if not self._stub:

            # connect signals used when a NIO has been created by a node
            # and this NIO need to be attached to a port connected to this link
            source_node.nio_signal.connect(self.newNIOSlot)
            destination_node.nio_signal.connect(self.newNIOSlot)

            # currently, we support only NIO_UDP for normal connections (non-stub).
            if not source_port.default_nio == NIO_UDP:
                raise NotImplementedError()

            self._source_udp = None
            self._destination_udp = None

            # connect signals used to receive a UDP port and host allocated by a node
            source_node.allocate_udp_nio_signal.connect(self.UDPPortAllocatedSlot)
            destination_node.allocate_udp_nio_signal.connect(self.UDPPortAllocatedSlot)

            # request the UDP info for each node
            source_node.allocateUDPPort()
            destination_node.allocateUDPPort()
        else:
            # handle stub connections (to a cloud for instance).
            if not source_port.isStub() and destination_port.isStub():
                source_node.nio_signal.connect(self.newNIOSlot)
                self._source_nio = self._destination_port.default_nio
                self._source_node.addNIO(self._source_port, self._source_nio)
            elif not destination_port.isStub() and source_port.isStub():
                destination_node.nio_signal.connect(self.newNIOSlot)
                self._destination_nio = self._source_port.default_nio
                self._destination_node.addNIO(self._destination_port, self._destination_nio)
            else:
                log.error("both ports are stub!")

    def deleteLink(self):
        """
        Deletes this link.
        """

        # delete the NIOs on both source and destination nodes
        self._source_node.deleteNIO(self._source_port)
        self._destination_node.deleteNIO(self._destination_port)

        # let the GUI know about this link has been deleted
        self.delete_link_signal.emit(self._id)

    @property
    def id(self):
        """
        Returns this link identifier.

        :returns: link identifier (integer)
        """

        return self._id

    def UDPPortAllocatedSlot(self, node_id, lport, laddr):
        """
        Slot to receive events from Node instances
        when a UDP port has been allocated in order to create a NIO UDP.

        :param node_id: node identifier
        :param lport: local UDP port
        :param laddr: local host/address
        """

        # check that the node is connected to this link as a source
        if node_id == self._source_node.id:
            self._source_udp = (lport, laddr)
            # disconnect the signal has we don't expect new source UDP info for this link.
            self._source_node.allocate_udp_nio_signal.disconnect()

        # check that the node is connected to this link as a destination
        elif node_id == self._destination_node.id:
            self._destination_udp = (lport, laddr)
            # disconnect the signal has we don't expect new source UDP info for this link.
            self._destination_node.allocate_udp_nio_signal.disconnect()

        if self._source_udp and self._destination_udp:
            # we got UDP info from both source and destination nodes
            # meaning we can proceed with the creation of UDP NIOs
            lport, laddr = self._source_udp
            rport, raddr = self._destination_udp

            #TODO: check address compatibility? for instance 127.0.0.1 <-> 83.15.12.2 isn't likely gonna work.
            self._source_nio = NIO_UDP(lport, raddr, rport)
            self._destination_nio = NIO_UDP(rport, laddr, lport)

            # add the UDP NIOs to the nodes
            self._source_node.addNIO(self._source_port, self._source_nio)
            self._destination_node.addNIO(self._destination_port, self._destination_nio)

    def newNIOSlot(self, node_id):
        """
        Slot to receive events from Node instances
        when a NIO has been created on the server
        and are active.

        :param node_id: node identifier
        """

        # check that the node is connected to this link as a source
        if node_id == self._source_node.id:
            self._source_nio_active = True
            # disconnect the signal has we don't expect new source NIO for this link.
            self._source_node.nio_signal.disconnect()

        # check that the node is connected to this link as a destination
        elif node_id == self._destination_node.id:
            self._destination_nio_active = True
            # disconnect the signal has we don't expect new destination NIO for this link.
            self._destination_node.nio_signal.disconnect()

        if not self._stub and self._source_nio_active and self._destination_nio_active:
            # both NIOs are active now.
            self._source_port.nio = self._source_nio
            self._destination_port.nio = self._destination_nio

            # let the GUI know about this link has been created
            self.add_link_signal.emit(self._id)
        elif self._stub and self._source_nio_active:
            self._source_port.nio = self._source_nio
            # add the NIO to destination to show the port is not free.
            self._destination_port.nio = self._source_nio
            self.add_link_signal.emit(self._id)
        elif self._stub and self._destination_nio_active:
            # add the NIO to source to show the port is not free.
            self._source_port.nio = self._destination_nio
            self._destination_port.nio = self._destination_nio
            self.add_link_signal.emit(self._id)
