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

from ..qt import QtGui


def ConnectToServer(server, parent=None):

    progress_dialog = ConnectToServerProgressDialog(server, parent=parent)
    progress_dialog.show()
    success = progress_dialog.exec_()
    if not success:
        return False
    return True


class ConnectToServerProgressDialog(QtGui.QProgressDialog):

    """
    Progress dialog to wait for a server connection.

    :param server: HTTPClient instance
    :param parent: parent widget
    """

    def __init__(self, server, parent=None):

        self._server = server
        host = self._server.host
        port = self._server.port

        QtGui.QProgressDialog.__init__(self, "Connecting to server {}:{}".format(host, port), "Cancel", 0, 0, parent)
        self.setModal(True)
        self.setWindowTitle("Server connection")
        self.canceled.connect(self.cancel)
        self._server.connected_signal.connect(self._connectCallback)
        self._server.connection_error_signal.connect(self._connectionErrorCallback)

    def _connectCallback(self):
        """
        Slot to close this dialog when the connection is successful.
        """

        QtGui.QProgressDialog.accept(self)

    def _connectionErrorCallback(self, message):
        """
        Slot to show an error message.

        :param message: error message
        """

        QtGui.QMessageBox.critical(self, "Server connection error", "{}".format(message))
        QtGui.QProgressDialog.reject(self)

    def exec_(self):

        self._server.connect()
        return QtGui.QProgressDialog.exec_(self)

    def cancel(self):
        """
        Slot to stop trying to connect to the server and close this dialog.
        """

        self._server.connected_signal.disconnect(self._connectCallback)
        self._server.connection_error_signal.disconnect(self._connectionErrorCallback)
        QtGui.QProgressDialog.cancel(self)
