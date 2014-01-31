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
Main window for the GUI.
"""

import socket
from .servers import Servers
from .qt import QtGui, QtCore
from .ui.main_window_ui import Ui_MainWindow
from .preferences_dialog import PreferencesDialog


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    """
    Main window implementation.

    :param parent: parent widget
    """

    # signal to tell the view if the user is adding a link or not
    adding_link_signal = QtCore.Signal(bool)

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # restore the geometry and state of the main window.
        settings = QtCore.QSettings()
        self.restoreGeometry(settings.value("GUI/geometry", QtCore.QByteArray()))
        self.restoreState(settings.value("GUI/state", QtCore.QByteArray()))

        # flag to know if there are any unsaved changes
        self.unsaved_changes = False

        # load initial stuff once the event loop isn't busy
        QtCore.QTimer.singleShot(0, self.startupLoading)

        # connect the signal to the view
        self.adding_link_signal.connect(self.uiGraphicsView.addingLinkSlot)

        # connect actions
        self.uiAddLinkAction.triggered.connect(self._addLinkActionSlot)

        self.uiPreferencesAction.triggered.connect(self._preferencesActionSlot)

    def _addLinkActionSlot(self):
        """
        Slot to receive events from the add a link action.
        """

        if not self.uiAddLinkAction.isChecked():
            self.uiAddLinkAction.setText("Add a link")
            link_icon = QtGui.QIcon()
            link_icon.addPixmap(QtGui.QPixmap(":/icons/connection-new.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            link_icon.addPixmap(QtGui.QPixmap(":/icons/connection-new-hover.svg"), QtGui.QIcon.Active, QtGui.QIcon.On)
            self.uiAddLinkAction.setIcon(link_icon)
            self.adding_link_signal.emit(False)
        else:
#TODO: handle automatic linking based on the link type
#             modifiers = QtGui.QApplication.keyboardModifiers()
#             if not globals.GApp.systconf['general'].manual_connection or modifiers == QtCore.Qt.ShiftModifier:
#                 menu = QtGui.QMenu()
#                 for linktype in globals.linkTypes.keys():
#                     menu.addAction(linktype)
#                 menu.connect(menu, QtCore.SIGNAL("triggered(QAction *)"), self.__setLinkType)
#                 menu.exec_(QtGui.QCursor.pos())
#             else:
#                 globals.currentLinkType = globals.Enum.LinkType.Manual
            self.uiAddLinkAction.setText("Cancel")
            self.uiAddLinkAction.setIcon(QtGui.QIcon(':/icons/cancel-connection.svg'))
            self.adding_link_signal.emit(True)

    def _preferencesActionSlot(self):
        """
        Slot to show the preferences dialog.
        """

        dialog = PreferencesDialog(self)
        dialog.show()
        dialog.exec_()

    def keyPressEvent(self, event):
        """
        Handles all key press events for the main window.

        :param event: QKeyEvent
        """

        key = event.key()
        # if the user is adding a link and press Escape, then cancel the link addition.
        if self.uiAddLinkAction.isChecked() and key == QtCore.Qt.Key_Escape:
            self.uiAddLinkAction.setChecked(False)
            self._addLinkActionSlot()
        else:
            QtGui.QMainWindow.keyPressEvent(self, event)

    def closeEvent(self, event):
        """
        Handles the event when the main window is closed.

        :param event: QCloseEvent
        """

        if self.checkForUnsavedChanges():
            # save the geometry and state of the main window.
            settings = QtCore.QSettings()
            settings.setValue("GUI/geometry", self.saveGeometry())
            settings.setValue("GUI/state", self.saveState())
        else:
            event.ignore()

    def checkForUnsavedChanges(self):
        """
        Checks if there are any unsaved changes.

        :returns: boolean
        """

        if self.unsaved_changes:
            return True
        return True

    def startupLoading(self):
        """
        Called by QTimer.singleShot to load everything needed at startup.
        """

        # connect to the local server
        servers = Servers.instance()
        server = servers.localServer()
        if not server.connected:
            try:
                server.connect()
            except socket.error as e:
                QtGui.QMessageBox.critical(self, "Local server", "Could not connect to the local server {host} on port {port}: {error}".format(host=server.host,
                                                                                                                                               port=server.port,
                                                                                                                                               error=e))
                return

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of MainWindow.

        :returns: instance of MainWindow
        """

        if not hasattr(MainWindow, "_instance"):
            MainWindow._instance = MainWindow()
        return MainWindow._instance
