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

from .qt import QtCore
from gns3.servers import Servers

import logging
log = logging.getLogger(__name__)


class Project(QtCore.QObject):

    """Current project"""

    project_created_signal = QtCore.Signal()

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
        self._closed = False
        self._files_dir = None
        self._path = None
        self._type = None
        self._name = None
        self._project_instances.add(self)

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

    def type(self):
        """
        :returns: Project type (string)
        """

        return self._type

    def setType(self, type):
        """
        Set project type

        :param type: Project type (string)
        """

        self._type = type

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

        return self._files_dir

    def setFilesDir(self, files_dir):

        self._files_dir = files_dir

    def path(self):

        return self._path

    def setPath(self, path):

        self._path = path

    def create(self):
        """
        Create project on all servers
        """

        self._servers.localServer().post("/projects", self._project_created, body={
            "temporary": self._temporary,
            "project_id": self._id
        })

    def commit(self):
        """Save projet on remote servers"""

        # TODO: call all server
        if self._id is not None:
            self._servers.localServer().post("/projects/{project_id}/commit".format(project_id=self._id), None, body={})

    def close(self):
        """Close project"""

        # TODO: call all server
        if self._id:
            self.project_about_to_close_signal.emit()
            self._servers.localServer().post("/projects/{project_id}/close".format(project_id=self._id), self._project_closed, body={})
        else:
            # The project is not initialized when can close it
            self.project_about_to_close_signal.emit()
            self.project_closed_signal.emit()
            self._closed = True

    def _project_created(self, params, error=False):
        if error:
            print(params)
            return
        # TODO: Manage errors
        self._id = params["project_id"]
        log.info("Project {} created".format(self._id))
        # Only for local server
        self._files_dir = params["path"]
        self._closed = False

        self.project_created_signal.emit()

    def _project_closed(self, params, error=False):
        if error:
            print(params)
        else:
            if self._id:
                log.info("Project {} closed".format(self._id))
        self._closed = True
        self.project_closed_signal.emit()
        self._project_instances.remove(self)

    def moveFromTemporaryToPath(self, path):
        """
        Inform the server that a project is no longer
        temporary and as a new location.

        :params path: New path of the project
        """

        self._files_dir = path
        self._temporary = False
        self._servers.localServer().put("/projects/{project_id}".format(project_id=self._id), None, body={"path": path, "temporary": False})
