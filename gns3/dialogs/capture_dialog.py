# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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

from gns3.qt import QtWidgets
from gns3.ui.capture_dialog_ui import Ui_CaptureDialog

import logging
log = logging.getLogger(__name__)


class CaptureDialog(QtWidgets.QDialog, Ui_CaptureDialog):
    """
    This dialog allow configure the packet capture
    """

    def __init__(self, parent, file_name, auto_start, ethernet_link=True):

        super().__init__(parent)
        self.setupUi(self)
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self._okButtonClickedSlot)
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.reject)

        if ethernet_link:
            self.uiDataLinkTypeComboBox.addItem("Ethernet", "DLT_EN10MB")
        else:
            self.uiDataLinkTypeComboBox.addItem("Cisco HDLC", "DLT_C_HDLC")
            self.uiDataLinkTypeComboBox.addItem("Cisco PPP", "DLT_PPP_SERIAL")
            self.uiDataLinkTypeComboBox.addItem("Frame Relay", "DLT_FRELAY")
            self.uiDataLinkTypeComboBox.addItem("ATM", "DLT_ATM_RFC1483")

        self.uiCaptureFileNameLineEdit.setText(file_name)
        self.uiStartCommandCheckBox.setChecked(auto_start)

    def _okButtonClickedSlot(self):
        if len(self.fileName()) == 0:
            QtWidgets.QMessageBox.warning(self.parent(), "Packet capture", "Please provide a file name for the capture")
            return
        self.accept()

    def fileName(self):
        return self.uiCaptureFileNameLineEdit.text()

    def dataLink(self):
        """
        Type of link for capture
        """
        return self.uiDataLinkTypeComboBox.currentData()

    def commandAutoStart(self):
        return self.uiStartCommandCheckBox.isChecked()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    dialog = CaptureDialog(main, "test.pcap")
    dialog.show()
    exit_code = app.exec_()
    print(dialog.dataLink())
    print(dialog.fileName())
