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
from .nios.nio_udp import NIOUDP

import logging
log = logging.getLogger(__name__)


class Link(QtCore.QObject):

    """
    Link implementation.

    :param source_node: source Node instance
    :param source_port: source Port instance
    :param destination_node: destination Node instance
    :param destination_port: destination Port instance
    :param stub: indicates if the link is connected to a stub device like a Cloud
    """

    # signals used to let the GUI view know about link
    # additions and deletions.
    add_link_signal = QtCore.Signal(int)
    delete_link_signal = QtCore.Signal(int)

    _instance_count = 1

    def __init__(self, source_node, source_port, destination_node, destination_port):

        super(Link, self).__init__()

        log.info("adding link from {} {} to {} {}".format(source_node.name(),
                                                          source_port.name(),
                                                          destination_node.name(),
                                                          destination_port.name()))

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

        # we must request UDP information if the NIO is a NIO UDP and before
        # it can be created.
        if not self._stub:

            # connect signals used when a NIO has been created by a node
            # and this NIO need to be attached to a port connected to this link
            source_node.nio_signal.connect(self.newNIOSlot)
            destination_node.nio_signal.connect(self.newNIOSlot)

            # currently, we support only NIO_UDP for normal connections (non-stub).
            if not source_port.defaultNio() == NIOUDP:
                raise NotImplementedError()

            self._source_udp = None
            self._destination_udp = None

            # connect signals used to receive a UDP port and host allocated by a node
            source_node.allocate_udp_nio_signal.connect(self.UDPPortAllocatedSlot)
            destination_node.allocate_udp_nio_signal.connect(self.UDPPortAllocatedSlot)

            # request the UDP info for each node
            source_node.allocateUDPPort(self._source_port.id())
            destination_node.allocateUDPPort(self._destination_port.id())
        else:
            # handle stub connections (to a cloud for instance).
            if not source_port.isStub() and destination_port.isStub():
                source_node.nio_signal.connect(self.newNIOSlot)
                self._source_nio = self._destination_port.defaultNio()
                self._source_node.nio_cancel_signal.connect(self.cancelNIOSlot)
                self._source_node.addNIO(self._source_port, self._source_nio)
            elif not destination_port.isStub() and source_port.isStub():
                destination_node.nio_signal.connect(self.newNIOSlot)
                self._destination_nio = self._source_port.defaultNio()
                self._destination_node.nio_cancel_signal.connect(self.cancelNIOSlot)
                self._destination_node.addNIO(self._destination_port, self._destination_nio)
            else:
                log.error("both ports are stub!")

    @classmethod
    def reset(cls):
        """
        Reset the instance count.
        """

        cls._instance_count = 1

    def __str__(self):

        return "Link from {} port {} to {} port {}".format(self._source_node.name(),
                                                           self._source_port.name(),
                                                           self._destination_node.name(),
                                                           self._destination_port.name())

    def deleteLink(self):
        """
        Deletes this link.
        """

        log.info("deleting link from {} {} to {} {}".format(self._source_node.name(),
                                                            self._source_port.name(),
                                                            self._destination_node.name(),
                                                            self._destination_port.name()))

        # delete the NIOs on both source and destination nodes
        self._source_node.deleteNIO(self._source_port)
        self._source_port.setFree()
        self._source_node.updated_signal.emit()
        self._destination_node.deleteNIO(self._destination_port)
        self._destination_port.setFree()
        self._destination_node.updated_signal.emit()

        # let the GUI know about this link has been deleted
        self.delete_link_signal.emit(self._id)

    def id(self):
        """
        Returns this link identifier.

        :returns: link identifier (integer)
        """

        return self._id

    def sourceNode(self):
        """
        Returns the source node for this link.

        :returns: Node instance
        """

        return self._source_node

    def destinationNode(self):
        """
        Returns the destination node for this link.

        :returns: Node instance
        """

        return self._destination_node

    def sourcePort(self):
        """
        Returns the source port for this link.

        :returns: Port instance
        """

        return self._source_port

    def destinationPort(self):
        """
        Returns the destination port for this link.

        :returns: Port instance
        """

        return self._destination_port

    def UDPPortAllocatedSlot(self, node_id, port_id, lport):
        """
        Slot to receive events from Node instances
        when a UDP port has been allocated in order to create a NIO UDP.

        :param node_id: node identifier
        :param port_id: port identifier
        :param lport: local UDP port
        """

        # check that the node is connected to this link as a source
        if node_id == self._source_node.id() and port_id == self._source_port.id():
            laddr = self._source_node.server().host
            self._source_udp = (lport, laddr)
            # disconnect the signal has we don't expect new source UDP info for this link.
            self._source_node.allocate_udp_nio_signal.disconnect(self.UDPPortAllocatedSlot)

            log.debug("{} has allocated UDP port {} for host {}".format(self._source_node.name(),
                                                                        lport,
                                                                        laddr))

        # check that the node is connected to this link as a destination
        elif node_id == self._destination_node.id() and port_id == self._destination_port.id():
            laddr = self._destination_node.server().host
            self._destination_udp = (lport, laddr)
            # disconnect the signal has we don't expect new source UDP info for this link.
            self._destination_node.allocate_udp_nio_signal.disconnect(self.UDPPortAllocatedSlot)

            log.debug("{} has allocated UDP port {} for host {}".format(self._destination_node.name(),
                                                                        lport,
                                                                        laddr))

        if self._source_udp and self._destination_udp:

            # we got UDP info from both source and destination nodes
            # meaning we can proceed with the creation of UDP NIOs
            lport, laddr = self._source_udp
            rport, raddr = self._destination_udp

            self._source_nio = NIOUDP(lport, raddr, rport)
            self._destination_nio = NIOUDP(rport, laddr, lport)

            self._source_udp = None
            self._destination_udp = None

            log.debug("creating UDP tunnel from {}:{} to {}:{} ".format(laddr, lport, raddr, rport))

            # add the UDP NIOs to the nodes
            self._source_node.nio_cancel_signal.connect(self.cancelNIOSlot)
            self._source_node.addNIO(self._source_port, self._source_nio)
            self._destination_node.nio_cancel_signal.connect(self.cancelNIOSlot)
            self._destination_node.addNIO(self._destination_port, self._destination_nio)

    def newNIOSlot(self, node_id, port_id):
        """
        Slot to receive events from Node instances
        when a NIO has been created on the server
        and are active.

        :param node_id: node identifier
        :param port_id: port identifier
        """

        # check that the node is connected to this link as a source
        if node_id == self._source_node.id() and port_id == self._source_port.id():
            self._source_nio_active = True
            # disconnect the signal has we don't expect new source NIO for this link.
            self._source_node.nio_signal.disconnect(self.newNIOSlot)

        # check that the node is connected to this link as a destination
        elif node_id == self._destination_node.id() and port_id == self._destination_port.id():
            self._destination_nio_active = True
            # disconnect the signal has we don't expect new destination NIO for this link.
            self._destination_node.nio_signal.disconnect(self.newNIOSlot)

        if not self._stub and self._source_nio_active and self._destination_nio_active:
            # both NIOs are active now.
            self._addToSourcePort(self._source_nio)
            self._addToDestinationPort(self._destination_nio)

            self._source_node.nio_cancel_signal.disconnect(self.cancelNIOSlot)
            self._destination_node.nio_cancel_signal.disconnect(self.cancelNIOSlot)
            self._source_nio_active = False
            self._destination_nio_active = False

            # let the GUI know about this link has been created
            self.add_link_signal.emit(self._id)
        elif self._stub and self._source_nio_active:
            self._addToSourcePort(self._source_nio)
            # add the NIO to destination to show the port is not free.
            self._addToDestinationPort(self._source_nio)
            self._source_nio_active = False
            self._source_node.nio_cancel_signal.disconnect(self.cancelNIOSlot)
            self.add_link_signal.emit(self._id)
        elif self._stub and self._destination_nio_active:
            # add the NIO to source to show the port is not free.
            self._addToSourcePort(self._destination_nio)
            self._addToDestinationPort(self._destination_nio)
            self._destination_nio_active = False
            self._destination_node.nio_cancel_signal.disconnect(self.cancelNIOSlot)
            self.add_link_signal.emit(self._id)

    def _addToSourcePort(self, nio):
        """
        Adds a NIO, a link id and a description to the source port.

        :param nio: NIO instance
        """

        self._source_port.setNio(nio)
        self._source_port.setLinkId(self._id)
        self._source_port.setDestinationNode(self._destination_node)
        self._source_port.setDestinationPort(self._destination_port)

        log.debug("{} attached to {} on port {}".format(nio,
                                                        self._source_node.name(),
                                                        self._source_port.name()))

    def _addToDestinationPort(self, nio):
        """
        Adds a NIO, a link id and a description to the destination port.

        :param nio: NIO instance
        """

        self._destination_port.setNio(nio)
        self._destination_port.setLinkId(self._id)
        self._destination_port.setDestinationNode(self._source_node)
        self._destination_port.setDestinationPort(self._source_port)

        log.debug("{} attached to {} on port {}".format(nio,
                                                        self._destination_node.name(),
                                                        self._destination_port.name()))

    def cancelNIOSlot(self, node_id):
        """
        Slot to receive events from Node instances
        when a NIO has been canceled because of an
        error returned by the server.

        :param node_id: node identifier
        """

        if not self._stub:
            if self._source_node.id() != node_id:
                try:
                    # the destination node has canceled its NIO allocation
                    self._destination_node.nio_signal.disconnect(self.newNIOSlot)
                except TypeError:
                    # ignore TypeError: 'method' object is not connected
                    pass

                self._source_node.deleteNIO(self._source_port)
                self._source_port.setFree()
                self._source_node.updated_signal.emit()

            elif self._destination_node.id() != node_id:
                try:
                    # the source node has canceled its NIO allocation
                    self._source_node.nio_signal.disconnect(self.newNIOSlot)
                except TypeError:
                    # ignore TypeError: 'method' object is not connected
                    pass

                self._destination_node.deleteNIO(self._destination_port)
                self._destination_port.setFree()
                self._destination_node.updated_signal.emit()

            self._source_node.nio_cancel_signal.disconnect(self.cancelNIOSlot)
            self._destination_node.nio_cancel_signal.disconnect(self.cancelNIOSlot)
        else:
            if self._source_node.id() == node_id:
                self._source_node.nio_signal.disconnect(self.newNIOSlot)
                self._source_node.nio_cancel_signal.disconnect(self.cancelNIOSlot)
            else:
                self._destination_node.nio_signal.disconnect(self.newNIOSlot)
                self._destination_node.nio_cancel_signal.disconnect(self.cancelNIOSlot)

        self._source_nio_active = False
        self._destination_nio_active = False

    def dump(self):
        """
        Returns a representation of this link.

        :returns: dictionary
        """

        return {"id": self.id(),
                "description": str(self),
                "source_node_id": self._source_node.id(),
                "source_port_id": self._source_port.id(),
                "destination_node_id": self._destination_node.id(),
                "destination_port_id": self._destination_port.id(),
                }
