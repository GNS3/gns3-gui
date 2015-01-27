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

from gns3.servers import Servers


class Project:
    """Current project"""

    def __init__(self, temporary=False):

        self._temporary = temporary
        self._servers = Servers.instance()
        self._create()

    @property
    def temporary(self):
        """
        :returns: True if the project is temporary
        """

        return self._temporary

    @temporary.setter
    def temporary(self, temporary):
        """
        Set the temporary flag for a project. And update
        it on the server.

        :param temporary: Temporary flag
        """

        self._temporary = temporary

    @property
    def uuid(self):
        """
        Get project UUID
        """

        return self._uuid

    def _create(self):
        """
        Create project on all servers
        """

        def project_created(status, params):
            self._uuid = params["uuid"]
            #TODO: call all server when we got uuid
        self._servers.localServer().post("/project", {"temporary": self.temporary}, project_created)
