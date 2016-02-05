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

import sys

from gns3.qt import QtWidgets
from gns3.ui.console_command_dialog_ui import Ui_uiConsoleCommandDialog
from gns3.settings import PRECONFIGURED_TELNET_CONSOLE_COMMANDS, \
        PRECONFIGURED_SERIAL_CONSOLE_COMMANDS, \
        PRECONFIGURED_VNC_CONSOLE_COMMANDS


import logging
log = logging.getLogger(__name__)


class ConsoleCommandDialog(QtWidgets.QDialog, Ui_uiConsoleCommandDialog):
    """
    This dialog allow user to select the command used to start a
    console.
    """

    def __init__(self, parent, console_type="telnet", current=None):
        """
        :params console_type: telnet, serial or vnc
        :params current: Current console command
        """
        super().__init__(parent)
        self.setupUi(self)

        if console_type == "telnet":
            consoles = PRECONFIGURED_TELNET_CONSOLE_COMMANDS
        elif console_type == "vnc":
            consoles = PRECONFIGURED_VNC_CONSOLE_COMMANDS
        else:
            consoles = PRECONFIGURED_SERIAL_CONSOLE_COMMANDS

        self.uiCommandComboBox.addItem("Custom", "")
        for name, cmd in sorted(consoles.items(), key=(lambda item: item[0].lower())):
            self.uiCommandComboBox.addItem(name, cmd)

        self.uiCommandComboBox.currentIndexChanged.connect(self.commandComboBoxCurrentIndexChangedSlot)
        self.uiCommandPlainTextEdit.textChanged.connect(self.textChangedSlot)

        if current:
            self.uiCommandPlainTextEdit.setPlainText(current)

    def textChangedSlot(self):
        index = self.uiCommandComboBox.findData(self.uiCommandPlainTextEdit.toPlainText())
        if index == -1:
            index = 0
        self.uiCommandComboBox.setCurrentIndex(index)

    def commandComboBoxCurrentIndexChangedSlot(self, index):
        # Ignore custom command
        if index != 0:
            self.uiCommandPlainTextEdit.setPlainText(self.uiCommandComboBox.currentData())

    @staticmethod
    def getCommand(parent, console_type="telnet", current=None):
        dialog = ConsoleCommandDialog(parent, console_type=console_type, current=current)
        dialog.show()
        if dialog.exec_():
            return (True, dialog.uiCommandPlainTextEdit.toPlainText().replace("\n", " "))
        return (False, None)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    (ok, command) = ConsoleCommandDialog.getCommand(main, console_type="telnet", current=list(PRECONFIGURED_TELNET_CONSOLE_COMMANDS.items())[0][1])
    print(ok)
    print(command)

