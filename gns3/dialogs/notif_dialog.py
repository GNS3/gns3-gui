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

"""
Display error to the user in an overlay popup
"""

import time

from gns3.qt import QtWidgets, QtCore, qslot

import logging
log = logging.getLogger(__name__)


MAX_ELEMENTS = 3
DISPLAY_DURATION = {
    "CRITICAL": 120,
    "ERROR": 120,
    "WARNING": 20,
    "INFO": 5
}


class NotifDialogHandler(logging.StreamHandler):

    def __init__(self, dialog):
        super().__init__()
        self._dialog = dialog
        self.setLevel(logging.INFO)
        self._dialog.show()

    def emit(self, record):
        self._dialog.addNotif(record.levelname, record.getMessage())


class NotifDialog(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self._notifs = []

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowDoesNotAcceptFocus |
                            QtCore.Qt.SubWindow)
        # QtCore.Qt.Tool)
        # QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)  # | QtCore.Qt.WA_TranslucentBackground)

        self._layout = QtWidgets.QVBoxLayout()

        self._timer = QtCore.QTimer()
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._refreshSlot)
        self._timer.start()

        for i in range(0, MAX_ELEMENTS):
            l = QtWidgets.QLabel()
            l.setAlignment(QtCore.Qt.AlignTop)
            l.setWordWrap(True)
            l.hide()
            self._layout.addWidget(l)
        self.setLayout(self._layout)

    @qslot
    def addNotif(self, level, message):
        if not self.parent().settings().get("overlay_notifications", True):
            return

        # This unicode char prevent the wordwrap at /
        message = message.replace("/", "\u2060/\u2060")
        if len(self._notifs) == MAX_ELEMENTS:
            self._notifs.pop(0)
        self._notifs.append((level, message, time.time()))
        self.update()

    @qslot
    def _refreshSlot(self):
        """
        Hide the notifs after some delay
        """
        notifs = []
        for (i, (level, message, when)) in enumerate(self._notifs):
            if when + DISPLAY_DURATION[level] > time.time():
                notifs.append((level, message, when))
        if notifs != self._notifs:
            self._notifs = notifs
            self.update()
        elif len(notifs) > 0:
            self.resize()

    def update(self):
        if len(self._notifs) == 0:
            self.hide()
        else:
            for (i, (level, message, when)) in enumerate(self._notifs):
                w = self._layout.itemAt(i).widget()
                w.setText(message)
                if level == "ERROR" or level == "CRITICAL":
                    w.setStyleSheet("""
                        color: black;
                        padding-left: 12px;
                        background-color: rgb(247, 205, 198);
                        border-left: 10px solid red;
                    """)
                elif level == "WARNING":
                    w.setStyleSheet("""
                        color: black;
                        padding-left: 12px;
                        background-color: #f4f2b5;
                        border-left: 10px solid orange;
                    """)
                elif level == "INFO":
                    w.setStyleSheet("""
                        color: black;
                        padding-left: 12px;
                        background-color: #cfffc9;
                        border-left: 10px solid green;
                    """)

                w.show()
            for i in range(i + 1, MAX_ELEMENTS):
                w = self._layout.itemAt(i).widget()
                w.hide()

            self.resize()
            self.show()

    def resize(self):
        x = self.parent().width() - self.width() - 10
        y = 10
        self.setGeometry(x, y, self.sizeHint().width(), self.sizeHint().height())

    @qslot
    def mousePressEvent(self, event):
        self._notifs.clear()
        self.update()


if __name__ == '__main__':
    """
    A demo main for testing the features
    """
    import sys
    app = QtWidgets.QApplication(sys.argv)
    logging.basicConfig(level=logging.INFO)

    class MainWindow(QtWidgets.QWidget):

        def __init__(self):
            super().__init__()
            l1 = QtWidgets.QLabel()
            l1.setText("Hello World")

            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(l1)
            self.setLayout(vbox)
            self.setStyleSheet("background-color:blue;")
            self._dialog = NotifDialog(self)
            log.addHandler(NotifDialogHandler(self._dialog))
            log.info("test")

        def moveEvent(self, event):
            log.error("An error")
            log.info("An info with an url http://test")
            log.warning("A warning with a long long long longlong longlong longlong longlong longlong longlong longlong long message")
            self._dialog.update()

        def resizeEvent(self, event):
            self._dialog.update()

    main = MainWindow()
    main.setMinimumWidth(600)
    main.setMinimumHeight(600)
    main.show()
    exit_code = app.exec_()
