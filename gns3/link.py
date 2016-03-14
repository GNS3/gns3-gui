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
from .servers import Servers


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

        super().__init__()

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
        self._link_id = None

        body = {
            "vms": [
                {"vm_id": source_node.vm_id(), "adapter_number": source_port.adapterNumber(), "port_number": source_port.portNumber()},
                {"vm_id": destination_node.vm_id(), "adapter_number": destination_port.adapterNumber(), "port_number": destination_port.portNumber()}
            ]
        }

        Servers.instance().controllerServer().post("/projects/{project_id}/links".format(project_id=source_node.project().id()), self._linkCreatedCallback, body=body)

    def _linkCreatedCallback(self, result, error=False, **kwargs):
        if error:
            log.error("error while creating link: {}".format(result["message"]))
            return

        # let the GUI know about this link has been deleted
        self.add_link_signal.emit(self._id)
        self._source_port.setLinkId(self._id)
        self._source_port.setDestinationNode(self._destination_node)
        self._source_port.setDestinationPort(self._destination_port)
        self._destination_port.setLinkId(self._id)
        self._destination_port.setDestinationNode(self._source_node)
        self._destination_port.setDestinationPort(self._source_port)

        self._link_id = result["link_id"]

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

        Servers.instance().controllerServer().delete("/projects/{project_id}/links/{link_id}".format(project_id=self._source_node.project().id(),
                                                                                                     link_id=self._link_id), self._linkDeletedCallback)

    def _linkDeletedCallback(self, result, error=False, **kwargs):
        """
        Called after the link is remove from the topology
        """
        if error:
            log.error("error while deleting link: {}".format(result["message"]))
            return

        self._source_port.setFree()
        self._source_node.updated_signal.emit()
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
                "destination_port_id": self._destination_port.id()}
