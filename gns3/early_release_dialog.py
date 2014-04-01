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
from .qt import QtGui
from .ui.early_release_dialog_ui import Ui_EarlyReleaseDialog


class EarlyReleaseDialog(QtGui.QDialog, Ui_EarlyReleaseDialog):
    """
    Early release dialog.
    """

    def __init__(self, parent):

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def isEmail(self, email):

        if re.match("([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)", email):
            return True
        else:
            return False

    def done(self, result):

        if not result:  # cancelled
            QtGui.QApplication.quit()
        else:
            username = self.uiUsernameLineEdit.text()
            if not username:
                QtGui.QMessageBox.critical(self, "Username", "Please provide an username")
                return
            email = self.uiEmailLineEdit.text()
            if not email:
                QtGui.QMessageBox.critical(self, "Email", "Please provide an email address")
                return
            if not re.search(r"""^GNS[34]{1}[0-9]{4}$""", username) or not self.isEmail(email):
                QtGui.QMessageBox.critical(self, "Invalid membership", "Sorry this is an invalid membership")
                return
            if not self.uiDisclaimerCheckBox.isChecked():
                QtGui.QMessageBox.critical(self, "Disclaimer", "Please read the disclaimer!")
                return
            # Congratulations, you have found where we check for a GNS3 membership! and yes, it is very simple ;)
            # Since you were smart enough to get here, you deserve to use GNS3 without a membership...
        QtGui.QDialog.done(self, result)
