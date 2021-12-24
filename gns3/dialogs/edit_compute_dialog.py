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
from gns3.compute import Compute
from gns3.ui.edit_compute_dialog_ui import Ui_EditComputeDialog


class EditComputeDialog(QtWidgets.QDialog, Ui_EditComputeDialog):

    """
    New compute dialog.

    :param parent: parent widget.
    """

    def __init__(self, parent, compute=None):

        super().__init__(parent)
        self.setupUi(self)
        self._compute = compute

        if self._compute:
            self.uiServerNameLineEdit.setText(self._compute.name())
            self.uiServerHostLineEdit.setText(self._compute.host())
            self.uiServerPortSpinBox.setValue(self._compute.port())
            index = self.uiServerProtocolComboBox.findText(self._compute.protocol().upper())
            self.uiServerProtocolComboBox.setCurrentIndex(index)
            self.uiServerUserLineEdit.setText(self._compute.user())

    def compute(self):
        return self._compute

    def accept(self):
        """
        Adds a new remote compute.
        """

        host = self.uiServerHostLineEdit.text().strip()
        name = self.uiServerNameLineEdit.text().strip()
        protocol = self.uiServerProtocolComboBox.currentText().lower()
        port = self.uiServerPortSpinBox.value()
        user = self.uiServerUserLineEdit.text().strip()
        password = self.uiServerPasswordLineEdit.text().strip()

        if not re.match(r"^[a-zA-Z0-9\.{}-]+$".format("\u0370-\u1CDF\u2C00-\u30FF\u4E00-\u9FBF"), host):
            QtWidgets.QMessageBox.critical(self, "Remote compute", "Invalid compute hostname {}".format(host))
            return
        if name == "gns3vm":
            QtWidgets.QMessageBox.critical(self, "Remote compute", "{} is a reserved name".format(name))
            return
        if len(name) == 0:
            QtWidgets.QMessageBox.critical(self, "Remote compute", "Invalid compute name {}".format(name))
            return
        if port is None or port < 1:
            QtWidgets.QMessageBox.critical(self, "Remote compute", "Invalid compute port {}".format(port))
            return

        if not self._compute:
            self._compute = Compute()
        self._compute.setName(name)
        self._compute.setProtocol(protocol)
        self._compute.setHost(host)
        self._compute.setPort(port)
        self._compute.setUser(user)
        self._compute.setPassword(password)

        super().accept()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    dialog = EditComputeDialog(main)
    dialog.show()
    exit_code = app.exec_()
