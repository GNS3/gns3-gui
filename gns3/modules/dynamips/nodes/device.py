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
Base class for Device classes.
"""


from gns3.base_node import BaseNode

import logging
log = logging.getLogger(__name__)


class Device(BaseNode):

    URL_PREFIX = "dynamips"

    def __init__(self, module, server, project):

        super().__init__(module, server, project)
        self._device_id = None

    def device_id(self):
        """
        Return the ID of this device

        :returns: identifier (string)
        """

        return self._device_id

    def _setupCallback(self, result, error=False, **kwargs):
        """
        Callback for setup.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while setting up {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            return

        self._device_id = result["device_id"]
        self._settings["name"] = result["name"]
        log.info("{} has been created".format(self.name()))
        self.setInitialized(True)
        self.created_signal.emit(self.id())
        self._module.addNode(self)

    def delete(self):
        """
        Deletes this Device instance.
        """

        log.debug("{} is being deleted".format(self.name()))
        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        if self._device_id and self._server.connected():
            self.httpDelete("/{prefix}/devices/{device_id}".format(prefix=self.URL_PREFIX, device_id=self._device_id),
                            self._deleteCallback)
        else:
            self.deleted_signal.emit()
            self._module.removeNode(self)

    def _deleteCallback(self, result, error=False, **kwargs):
        """
        Callback for delete.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while deleting {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        log.info("{} has been deleted".format(self.name()))
        self.deleted_signal.emit()
        self._module.removeNode(self)

    def _addNIOCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for addNIO.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while adding a NIO for {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            self.nio_cancel_signal.emit(self.id())
        else:
            self.nio_signal.emit(self.id(), context["port_id"])

    def deleteNIO(self, port):
        """
        Deletes an NIO from the specified port on this Device instance

        :param port: Port instance
        """

        log.debug("{} is deleting an NIO".format(self.name()))
        self.httpDelete("/{prefix}/devices/{device_id}/ports/{port}/nio".format(prefix=self.URL_PREFIX,
                                                                                port=port.portNumber(),
                                                                                device_id=self._device_id),
                        self._deleteNIOCallback)

    def _deleteNIOCallback(self, result, error=False, **kwargs):
        """
        Callback for deleteNIO.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("Error while deleting NIO {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            return

        log.debug("{} has deleted a NIO: {}".format(self.name(), result))

