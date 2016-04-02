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

import re

from gns3.qt import QtWidgets
from gns3.ui.new_server_dialog_ui import Ui_NewServerDialog
from gns3.servers import Servers


class NewServerDialog(QtWidgets.QDialog, Ui_NewServerDialog):

    """
    New server dialog.

    :param parent: parent widget.
    has been opened automatically when GNS3 started.
    """

    def __init__(self, parent):

        super().__init__(parent)
        self.setupUi(self)
        self.uiEnableAuthenticationCheckBox.stateChanged.connect(self._enableAuthenticationSlot)

    def _enableAuthenticationSlot(self, state):
        """
        Slot to enable or not the authentication.
        """

        if state:
            self.uiServerUserLineEdit.setEnabled(True)
            self.uiServerPasswordLineEdit.setEnabled(True)
        else:
            self.uiServerUserLineEdit.setEnabled(False)
            self.uiServerPasswordLineEdit.setEnabled(False)

    def accept(self):
        """
        Adds a new remote server.
        """

        protocol = self.uiServerProtocolComboBox.currentText().lower()
        host = self.uiServerHostLineEdit.text().strip()
        port = self.uiServerPortSpinBox.value()
        if self.uiEnableAuthenticationCheckBox.isChecked():
            user = self.uiServerUserLineEdit.text().strip()
            password = self.uiServerPasswordLineEdit.text().strip()
        else:
            user = password = ""

        if not re.match(r"^[a-zA-Z0-9\.{}-]+$".format("\u0370-\u1CDF\u2C00-\u30FF\u4E00-\u9FBF"), host):
            QtWidgets.QMessageBox.critical(self, "Remote server", "Invalid remote server hostname {}".format(host))
            return
        if port is None or port < 1:
            QtWidgets.QMessageBox.critical(self, "Remote server", "Invalid remote server port {}".format(port))
            return

        servers = Servers.instance()
        remote_servers = servers.remoteServers()

        # check if the remote server is already defined
        for server in remote_servers.values():
            if server.protocol() == protocol and server.host() == host and server.port() == port and server.user() == user:
                QtWidgets.QMessageBox.critical(self, "Remote server", "Remote server is already defined.")
                return

        servers.getRemoteServer(protocol, host, port, user, settings={"password": password})
        servers.save()
        super().accept()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    dialog = NewServerDialog(main)
    dialog.show()
    exit_code = app.exec_()
