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
        self.uiEnableAuthenticationCheckBox.toggled.connect(self._enableAuthenticationSlot)
        self._compute = compute
        if self._compute:
            self.uiServerNameLineEdit.setText(self._compute.name())
            self.uiServerHostLineEdit.setText(self._compute.host())
            self.uiServerPortSpinBox.setValue(self._compute.port())

            index = self.uiServerProtocolComboBox.findText(self._compute.protocol().upper())
            self.uiServerProtocolComboBox.setCurrentIndex(index)

            if self._compute.user():
                self.uiEnableAuthenticationCheckBox.setChecked(True)
                self.uiServerUserLineEdit.setText(self._compute.user())
            else:
                self.uiEnableAuthenticationCheckBox.setChecked(False)
                self.uiWarningLabel.setVisible(False)
        else:
            self.uiEnableAuthenticationCheckBox.setChecked(False)
            self.uiWarningLabel.setVisible(False)
        self._enableAuthenticationSlot(self.uiEnableAuthenticationCheckBox.isChecked())

    def _enableAuthenticationSlot(self, state):
        """
        Slot to enable or not the authentication.
        """

        if self.uiEnableAuthenticationCheckBox.isChecked():
            self.uiServerUserLineEdit.setVisible(True)
            self.uiServerPasswordLineEdit.setVisible(True)
            self.uiServerUserLabel.setVisible(True)
            self.uiServerPasswordLabel.setVisible(True)
        else:
            self.uiServerUserLineEdit.setVisible(False)
            self.uiServerPasswordLineEdit.setVisible(False)
            self.uiServerUserLabel.setVisible(False)
            self.uiServerPasswordLabel.setVisible(False)

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
            QtWidgets.QMessageBox.critical(self, "Remote compute", "Invalid remote server hostname {}".format(host))
            return
        if name == "gns3vm":
            QtWidgets.QMessageBox.critical(self, "Remote compute", "{} is a reserved name".format(name))
            return
        if len(name) == 0:
            QtWidgets.QMessageBox.critical(self, "Remote compute", "Invalid remote server name {}".format(name))
            return
        if port is None or port < 1:
            QtWidgets.QMessageBox.critical(self, "Remote compute", "Invalid remote server port {}".format(port))
            return

        if not self._compute:
            self._compute = Compute()
        self._compute.setName(name)
        self._compute.setProtocol(protocol)
        self._compute.setHost(host)
        self._compute.setPort(port)
        if self.uiEnableAuthenticationCheckBox.isChecked():
            self._compute.setUser(user)
            self._compute.setPassword(password)
        else:
            self._compute.setUser(None)
            self._compute.setPassword(None)

        super().accept()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    dialog = EditComputeDialog(main)
    dialog.show()
    exit_code = app.exec_()
