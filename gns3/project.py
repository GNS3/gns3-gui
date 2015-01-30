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

    def __init__(self):

        super().__init__()
        self._uuid = None
        self._servers = Servers.instance()
        self._temporary = False
        self._closed = False

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

    def uuid(self):
        """
        Get project UUID
        """

        return self._uuid

    def setUuid(self, uuid):
        """
        Set project UUID
        """

        self._uuid = uuid

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of Project.

        :returns: instance of Project
        """

        if not hasattr(Project, "_instance"):
            Project._instance = Project()
        return Project._instance

    def create(self):
        """
        Create project on all servers
        """

        self._servers.localServer().post("/project", self._project_created, body={"temporary": self._temporary})

    def close(self):
        """Close project"""

        # TODO: call all server
        if self._uuid:
            self.project_about_to_close_signal.emit()
            self._servers.localServer().post("/project/{uuid}/close".format(uuid=self._uuid), self._project_closed, body={})
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
        self._uuid = params["uuid"]
        log.info("Project {} created".format(self._uuid))
        # TODO: call all server when we got uuid
        self._closed = False

        self.project_created_signal.emit()

    def _project_closed(self, params, error=False):
        if error:
            print(params)
            return
        # TODO: Manage errors
        log.info("Project {} closed".format(self._uuid))
        self._closed = True
        self.project_closed_signal.emit()
