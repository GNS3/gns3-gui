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
from gns3.controller import Controller
from gns3.compute_manager import ComputeManager
from gns3.topology import Topology

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

        self._id = None
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

        # Don't do anything if the project doesn't exist on the server
        if self._id is None:
            return

        Controller.instance().post("/projects/{project_id}/commit".format(project_id=self._id), None, body={})

    def start_all_nodes(self):
        """Start all nodes belonging to this project"""

        # Don't do anything if the project doesn't exist on the server
        if self._id is None:
            return

        Controller.instance().post("/projects/{project_id}/nodes/start".format(project_id=self._id), None, body={})

    def stop_all_nodes(self):
        """Stop all nodes belonging to this project"""

        # Don't do anything if the project doesn't exist on the server
        if self._id is None:
            return

        Controller.instance().post("/projects/{project_id}/nodes/stop".format(project_id=self._id), None, body={})

    def suspend_all_nodes(self):
        """Suspend all nodes belonging to this project"""

        # Don't do anything if the project doesn't exist on the server
        if self._id is None:
            return

        Controller.instance().post("/projects/{project_id}/nodes/suspend".format(project_id=self._id), None, body={})

    def reload_all_nodes(self):
        """Reload all nodes belonging to this project"""

        # Don't do anything if the project doesn't exist on the server
        if self._id is None:
            return

        Controller.instance().post("/projects/{project_id}/nodes/reload".format(project_id=self._id), None, body={})

    def get(self, path, callback, **kwargs):
        """
        HTTP GET on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """
        self._projectHTTPQuery("GET", path, callback, **kwargs)

    def post(self, path, callback, body={}, **kwargs):
        """
        HTTP POST on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """
        self._projectHTTPQuery("POST", path, callback, body=body, **kwargs)

    def put(self, path, callback, body={}, **kwargs):
        """
        HTTP PUT on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """
        self._projectHTTPQuery("PUT", path, callback, body=body, **kwargs)

    def delete(self, path, callback, body={}, **kwargs):
        """
        HTTP DELETE on the remote server

        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """
        self._projectHTTPQuery("DELETE", path, callback, body=body, **kwargs)

    def _projectHTTPQuery(self, method, path, callback, body={}, **kwargs):
        """
        HTTP query on the remote server

        :param method: HTTP method (string)
        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)

        Full arg list in createHTTPQuery
        """

        if not self._created:
            func = qpartial(self._projectOnServerCreated, method, path, callback, body, **kwargs)

            if self._callback_finish_creating_on_server is None:
                self._callback_finish_creating_on_server = []
                body = {
                    "name": self._name,
                    "project_id": self._id,
                    "path": self.filesDir()
                }
                Controller.instance().post("/projects", func, body=body)
            else:
                # We bufferize the query for when the project is created on the remote server
                self._callback_finish_creating_on_server.append(func)
        else:
            self._projectOnServerCreated(method, path, callback, body, params={}, **kwargs)

    def _projectOnServerCreated(self, method, path, callback, body, params={}, error=False, **kwargs):
        """
        The project is created on the server continue
        the query

        :param method: HTTP Method type (string)
        :param path: Remote path
        :param callback: callback method to call when the server replies
        :param body: params to send (dictionary)
        :param params: Answer from the creation on server
        :param error: HTTP error

        Full arg list in createHTTPQuery
        """

        if error:
            log.error("Error while creating project: {}".format(params["message"]))
            return

        if not self._created:
            self._closed = False
            self._created = True

        if not self._id:
            self._id = params["project_id"]

            self._startListenNotifications()

        path = "/projects/{project_id}{path}".format(project_id=self._id, path=path)
        Controller.instance().createHTTPQuery(method, path, callback, body=body, **kwargs)

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
            Controller.instance().post("/projects/{project_id}/close".format(project_id=self._id), self._projectClosedCallback, body={}, progressText="Close the project")
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

    def _startListenNotifications(self):

        path = "/projects/{project_id}/notifications".format(project_id=self._id)
        self._notification_stream = Controller.instance().createHTTPQuery("GET", path, None, downloadProgressCallback=self._event_received, showProgress=False, ignoreErrors=True)

    def _event_received(self, result, server=None, **kwargs):

        log.debug("Event received: %s", result)
        if result["action"] == "node.updated":
            node = Topology.instance().getNodeFromUuid(result["event"]["node_id"])
            if node is not None:
                node.updateNodeCallback(result["event"])
        elif result["action"] == "log.error":
            log.error(result["event"]["message"])
        elif result["action"] == "log.warning":
            log.warning(result["event"]["message"])
        elif result["action"] == "log.info":
            log.info(result["event"]["message"], extra={"show": True})
        elif result["action"] == "compute.created" or result["action"] == "compute.updated":
            cm = ComputeManager.instance()
            print(result)
            cm.computeDataReceivedCallback(result["event"])
        elif result["action"] == "ping":
            if "compute_id" in result:
                compute = Servers.instance().getServerFromString(result["compute_id"])
                compute.setSystemUsage(result["event"])
