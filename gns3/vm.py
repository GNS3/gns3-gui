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
Base class for VM classes.
"""

from .node import Node
from .ports.port import Port

import logging
log = logging.getLogger(__name__)


class VM(Node):

    def __init__(self, module, server, project):

        super().__init__(module, server, project)

        self._vm_id = None

    def vm_id(self):
        """
        Return the ID of this device

        :returns: identifier (string)
        """

        return self._vm_id

    def delete(self):
        """
        Deletes this VM instance.
        """

        log.debug("{} is being deleted".format(self.name()))
        # first delete all the links attached to this node
        self.delete_links_signal.emit()
        if self._vm_id and self._server.connected():
            self.httpDelete("/{prefix}/vms/{vm_id}".format(prefix=self.URL_PREFIX, vm_id=self._vm_id), self._deleteCallback)
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

    def start(self):
        """
        Starts this VM instance.
        """

        if self.status() == Node.started:
            log.debug("{} is already running".format(self.name()))
            return

        log.debug("{} is starting".format(self.name()))
        self.httpPost("/{prefix}/vms/{vm_id}/start".format(prefix=self.URL_PREFIX, vm_id=self._vm_id), self._startCallback)

    def _startCallback(self, result, error=False, **kwargs):
        """
        Callback for start.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while starting {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{} has started".format(self.name()))
            self.setStatus(Node.started)
            for port in self._ports:
                # set ports as started
                port.setStatus(Port.started)
            self.started_signal.emit()

    def stop(self):
        """
        Stops this VM instance.
        """

        if self.status() == Node.stopped:
            log.debug("{} is already stopped".format(self.name()))
            return

        log.debug("{} is stopping".format(self.name()))
        self.httpPost("/{prefix}/vms/{vm_id}/stop".format(prefix=self.URL_PREFIX, vm_id=self._vm_id), self._stopCallback)

    def _stopCallback(self, result, error=False, **kwargs):
        """
        Callback for stop.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while stopping {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{} has stopped".format(self.name()))
            self.setStatus(Node.stopped)
            for port in self._ports:
                # set ports as stopped
                port.setStatus(Port.stopped)
            self.stopped_signal.emit()

    def reload(self):
        """
        Reloads this VM instance.
        """

        log.debug("{} is being reloaded".format(self.name()))
        self.httpPost("/{prefix}/vms/{vm_id}/reload".format(prefix=self.URL_PREFIX, vm_id=self._vm_id), self._reloadCallback)

    def _reloadCallback(self, result, error=False, **kwargs):
        """
        Callback for reload.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while suspending {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
        else:
            log.info("{} has reloaded".format(self.name()))

    def addNIO(self, port, nio):
        """
        Adds a new NIO on the specified port for this VM instance.

        :param port: Port instance
        :param nio: NIO instance
        """

        params = self.getNIOInfo(nio)
        log.debug("{} is adding an {}: {}".format(self.name(), nio, params))
        self.httpPost("/{prefix}/vms/{vm_id}/adapters/{adapter}/ports/{port}/nio".format(
            adapter=port.adapterNumber(),
            port=port.portNumber(),
            prefix=self.URL_PREFIX,
            vm_id=self._vm_id),
            self._addNIOCallback,
            context={"port_id": port.id()},
            body=params)

    def _addNIOCallback(self, result, error=False, context={}, **kwargs):
        """
        Callback for addNIO.

        :param result: server response (dict)
        :param error: indicates an error (boolean)
        """

        if error:
            log.error("error while adding an UDP NIO for {}: {}".format(self.name(), result["message"]))
            self.server_error_signal.emit(self.id(), result["message"])
            self.nio_cancel_signal.emit(self.id())
        else:
            self.nio_signal.emit(self.id(), context["port_id"])

    def deleteNIO(self, port):
        """
        Deletes an NIO from the specified port on this instance

        :param port: Port instance
        """

        log.debug("{} is deleting an NIO".format(self.name()))
        self.httpDelete("/{prefix}/vms/{vm_id}/adapters/{adapter}/ports/{port}/nio".format(
            adapter=port.adapterNumber(),
            prefix=self.URL_PREFIX,
            port=port.portNumber(),
            vm_id=self._vm_id),
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

    def _readBaseConfig(self, config_path):
        """
        Returns a base config content.

        :param config_path: path to the configuration file.

        :returns: config content
        """

        try:
            with open(config_path, "r", errors="replace") as f:
                log.info("Opening configuration file: {}".format(config_path))
                config = f.read()
                config = "!\n" + config.replace('\r', "")
                return config
        except OSError as e:
            log.warn("Could not read base configuration file {}: {}".format(config_path, e))
            return ""
