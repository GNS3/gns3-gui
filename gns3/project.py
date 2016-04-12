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

import os
import sys
import traceback
from .qt import QtCore, qpartial

from gns3.servers import Servers
from gns3.topology import Topology
from gns3.node import Node

import logging
log = logging.getLogger(__name__)


class Project(QtCore.QObject):

    """Current project"""

    # Called before project closing
    project_about_to_close_signal = QtCore.Signal()

    # Called when the project is closed on all servers
    project_closed_signal = QtCore.Signal()

    # List of non closed project instance
    _project_instances = set()

    def __init__(self):

        self._servers = Servers.instance()
        self._id = None
        self._temporary = False
        self._closed = True
        self._created = False
        self._files_dir = None
        self._images_dir = None
        self._name = "untitled"
        self._project_instances.add(self)

        # We queue query in order to ensure the project is only created once on remote server
        self._callback_finish_creating_on_server = None

        self._notification_stream = None

        super().__init__()

    def name(self):
        """
        :returns: Project name (string)
        """

        return self._name

    def setName(self, name):
        """
        Set project name

        :param name: Project name (string)
        """

        assert name is not None
        self._name = name

    def closed(self):
        """
        :returns: True if project is closed
        """

        return self._closed

    def temporary(self):
        """
        :returns: True if the project is temporary
        """

        return self._temporary

    def setTemporary(self, temporary):
        """
        Set the temporary flag for a project. And update
        it on the server.

        :param temporary: Temporary flag
        """

        self._temporary = temporary

    def servers(self):
        """
        :returns: List of server where GNS3 is running
        """
        return self._created_servers

    def id(self):
        """
        Get project identifier
        """

        return self._id

    def setId(self, project_id):
        """
        Set project identifier
        """

        self._id = project_id

    def filesDir(self):
        """
        Project directory on the local server
        """

        return self._files_dir

    def setFilesDir(self, files_dir):

        self._files_dir = files_dir

    def readmePathFile(self):
        return os.path.join(self._files_dir, "README.txt")

    def topologyFile(self):
        """
        Path to the topology file
        """

        try:
            assert self._files_dir is not None
            assert self._name is not None
        except AssertionError:
            exc_type, exc_value, exc_tb = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_tb)
            tb = "".join(lines)
            log.debug("Assertion detected: {}".format(tb))
            raise
        return os.path.join(self._files_dir, self._name + ".gns3")

    def setTopologyFile(self, topology_file):
        """
        Set path to the topology file and by extension the project directory.

        :params topology_file: Path to a .gns3 file
        """

        self.setFilesDir(os.path.dirname(topology_file))
        self._name = os.path.basename(topology_file).replace('.gns3', '')

    def commit(self):
        """Save project on remote servers"""

        # If current project doesn't exist on remote server
        if self._id is None:
            return

        Servers.instance().controllerServer().post("/projects/{project_id}/commit".format(project_id=self._id), None, body={})

    def get(self, server, path, callback, **kwargs):
        """
        HTTP GET on the remote server

        :param server: Server instance
        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """
        self._projectHTTPQuery(server, "GET", path, callback, **kwargs)

    def post(self, server, path, callback, body={}, **kwargs):
        """
        HTTP POST on the remote server

        :param server: Server instance
        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """
        self._projectHTTPQuery(server, "POST", path, callback, body=body, **kwargs)

    def put(self, server, path, callback, body={}, **kwargs):
        """
        HTTP PUT on the remote server

        :param server: Server instance
        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """
        self._projectHTTPQuery(server, "PUT", path, callback, body=body, **kwargs)

    def delete(self, server, path, callback, body={}, **kwargs):
        """
        HTTP DELETE on the remote server

        :param server: Server instance
        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """
        self._projectHTTPQuery(server, "DELETE", path, callback, body=body, **kwargs)

    def _projectHTTPQuery(self, server, method, path, callback, body={}, **kwargs):
        """
        HTTP query on the remote server

        :param server: Server instance
        :param method: HTTP method (string)
        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """

        if not self._created:
            func = qpartial(self._projectOnServerCreated, method, path, callback, body, hypervisor_server=server, **kwargs)

            if self._callback_finish_creating_on_server is None:
                self._callback_finish_creating_on_server = []
                body = {
                    "name": self._name,
                    "temporary": self._temporary,
                    "project_id": self._id,
                    "path": self.filesDir()
                }
                Servers.instance().controllerServer().post("/projects", func, body=body)
            else:
                # We bufferize the query for when the project is created on the remote server
                self._callback_finish_creating_on_server.append(func)
        else:
            self._projectOnServerCreated(method, path, callback, body, params={}, hypervisor_server=server, **kwargs)

    def _projectOnServerCreated(self, method, path, callback, body, params={}, error=False, hypervisor_server=None, server=None, **kwargs):
        """
        The project is created on the server continue
        the query

        :param method: HTTP Method type (string)
        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)
        :param params: Answer from the creation on server
        :param server: Server instance
        :param error: HTTP error

        Full arg list in createHTTPQuery
        """

        if error:
            print("Error while creating project: {}".format(params["message"]))
            return

        if not self._created:
            self._closed = False
            self._created = True

        if not self._id:
            self._id = params["project_id"]

            self._startListenNotifications()

        path = "/projects/{project_id}{path}".format(project_id=self._id, path=path)
        hypervisor_server.createHTTPQuery(method, path, callback, body=body, **kwargs)

        # Call all operations waiting for project creation:
        if self._callback_finish_creating_on_server:
            calls = self._callback_finish_creating_on_server
            self._callback_finish_creating_on_server = []
            for call in calls:
                call()

    def close(self, local_server_shutdown=False):
        """Close project"""

        if self._id:
            self.project_about_to_close_signal.emit()

            if self._servers.localServerProcessIsRunning() and local_server_shutdown:
                Servers.instance().controllerServer().post("/hypervisors/shutdown", self._projectClosedCallback)
            else:
                Servers.instance().controllerServer().post("/projects/{project_id}/close".format(project_id=self._id), self._projectClosedCallback, body={}, progressText="Close the project")
        else:
            if self._servers.localServerProcessIsRunning() and local_server_shutdown:
                log.info("Local server running shutdown the server")
                local_server = self._servers.localServer()
                local_server.post("/hypervisors/shutdown", self._projectClosedCallback, progressText="Shutdown the server")
            else:
                # The project is not initialized when we close it
                self._closed = True
                self.project_about_to_close_signal.emit()
                self.project_closed_signal.emit()

    def _projectClosedCallback(self, result, error=False, server=None, **kwargs):

        if error:
            log.error("Error while closing project {}: {}".format(self._id, result["message"]))
        else:
            if self._notification_stream:
                self._notification_stream.abort()
        log.info("Project {} closed".format(self._id))

        self._closed = True
        self.project_closed_signal.emit()
        try:
            self._project_instances.remove(self)
        except KeyError:
            return

    def moveFromTemporaryToPath(self, new_path):
        """
        Inform the server that a project is no longer
        temporary and as a new location.

        :param path: New path of the project
        """

        self._files_dir = new_path
        self._temporary = False
        for server in list(self._created_servers):
            params = {"name": self._name, "temporary": False}
            if server.isLocal():
                params["path"] = new_path
            server.put("/projects/{project_id}".format(project_id=self._id),
                       None,
                       body=params)

    def _startListenNotifications(self):

        path = "/projects/{project_id}/notifications".format(project_id=self._id)
        self._notification_stream = Servers.instance().controllerServer().createHTTPQuery("GET", path, None, downloadProgressCallback=self._event_received, showProgress=False, ignoreErrors=True)

    def _event_received(self, result, server=None, **kwargs):

        log.debug("Event received: %s", result)
        if result["action"] in ["vm.started", "vm.stopped"]:
            vm = Topology.instance().getVM(result["event"]["vm_id"])
            if vm is not None:
                if result["action"] == "vm.started":
                    vm.setStatus(Node.started)
                    vm.started_signal.emit()
                elif result["action"] == "vm.stopped":
                    vm.setStatus(Node.stopped)
                    vm.stopped_signal.emit()
        elif result["action"] == "log.error":
            log.error(result["event"]["message"])
            print("Error: " + result["event"]["message"])
        elif result["action"] == "log.warning":
            log.warning(result["event"]["message"])
            print("Warning: " + result["event"]["message"])
        elif result["action"] == "log.info":
            log.info(result["event"]["message"])
            print("Info: " + result["event"]["message"])
        elif result["action"] == "ping":
            if "hypervisor_id" in result:
                hypervisor = Servers.instance().getServerFromString(result["hypervisor_id"])
                hypervisor.setSystemUsage(result["event"])
