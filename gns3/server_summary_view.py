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
Server summary view that list all the server, their status.
"""

import sip

from .qt import QtGui, QtCore, QtWidgets
from .servers import Servers

import logging
log = logging.getLogger(__name__)


class ServerItem(QtWidgets.QTreeWidgetItem):

    """
    Custom item for the QTreeWidget instance
    (topology summary view).

    :param parent: parent widget
    :param server: Server instance
    """

    def __init__(self, parent, server):

        super().__init__(parent)
        self._server = server
        self._parent = parent
        self._status = "unknown"

        self._server.connection_connected_signal.connect(self._refreshStatusSlot)
        self._server.connection_closed_signal.connect(self._refreshStatusSlot)
        self._server.system_usage_updated_signal.connect(self._refreshStatusSlot)
        self._refreshStatusSlot()

    def _refreshStatusSlot(self):
        """
        Changes the icon to show the node status (started, stopped etc.)
        """

        usage = self._server.systemUsage()

        if self._server.isLocal():
            text = "Local"
        elif self._server.isGNS3VM():
            text = "GNS3 VM"
        else:
            text = self._server.url()

        if usage is not None:
            text = "{} CPU {}%, RAM {}%".format(text, usage["cpu_usage_percent"], usage["memory_usage_percent"])

        self.setText(0, text)
        if self._server.connected():
            self._status = "connected"
            if usage is None or (usage["cpu_usage_percent"] < 90 and usage["memory_usage_percent"] < 90):
                self.setIcon(0, QtGui.QIcon(':/icons/led_green.svg'))
            else:
                self.setIcon(0, QtGui.QIcon(':/icons/led_yellow.svg'))
        else:
            if self._status == "unknown":
                self.setIcon(0, QtGui.QIcon(':/icons/led_gray.svg'))
            else:
                self._status = "stopped"
                self.setIcon(0, QtGui.QIcon(':/icons/led_red.svg'))


class ServerSummaryView(QtWidgets.QTreeWidget):

    """
    Server summary view implementation.

    :param parent: parent widget
    """

    def __init__(self, parent):

        super().__init__(parent)

        self._servers = {}

        Servers.instance().server_added_signal.connect(self._serverAddedSlot)
        Servers.instance().server_removed_signal.connect(self._serverRemovedSlot)
        for server in Servers.instance().servers():
            self._serverAddedSlot(server.url())

    def _serverAddedSlot(self, url):
        """
        Called when a server is added to the list of servers

        :params url: URL of the server
        """

        server = Servers.instance().getServerFromString(url)
        url = server.url()
        # We can get twice an url in case of GNS3 VM remote server
        # to avoid duplicate desynchronized informations we removed one
        # version
        if url in self._servers:
            if not server.isGNS3VM():
                return
            else:
                self.takeTopLevelItem(self.indexOfTopLevelItem(self._servers[url]))
        self._servers[url] = ServerItem(self, server)

    def _serverRemovedSlot(self, url):
        """
        Called when a server is removed to the list of servers

        :params url: URL of the server
        """

        if url in self._servers:
            self.takeTopLevelItem(self.indexOfTopLevelItem(self._servers[url]))
            del self._servers[url]
