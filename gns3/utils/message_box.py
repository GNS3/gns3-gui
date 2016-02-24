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
To show a advanced message box.
"""

from gns3.qt import QtWidgets


def MessageBox(parent, title, message, details="", icon=QtWidgets.QMessageBox.Critical):

    msgbox = QtWidgets.QMessageBox(parent)
    msgbox.setWindowTitle(title)
    msgbox.setText(message)
    msgbox.setIcon(icon)
    if details:
        msgbox.setDetailedText(details)
    msgbox.exec_()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    dialog = MessageBox(main, "Test", "Hello world", details="A lot of details")
    dialog.show()
    exit_code = app.exec_()
