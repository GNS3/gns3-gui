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
Dialog to load module and built-in preference pages.
"""

from .qt import QtCore, QtGui
from .ui.preferences_dialog_ui import Ui_PreferencesDialog
from .pages.server_preferences_page import ServerPreferencesPage
from .pages.general_preferences_page import GeneralPreferencesPage
from .pages.cloud_preferences_page import CloudPreferencesPage
from .modules import MODULES


class PreferencesDialog(QtGui.QDialog, Ui_PreferencesDialog):
    """
    Preferences dialog implementation.

    :param parent: parent widget
    """

    def __init__(self, parent):

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.uiListWidget.currentItemChanged.connect(self._showPreferencesPageSlot)
        self.uiButtonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self._applyPreferences)
        self._items = []
        self._loadPreferencePages()

        # select the first available page
        self._items[0].setSelected(True)

    def _loadPreferencePages(self):
        """
        Loads all preference pages (built-ins and from modules).
        """

        # load general settings pages
        general_page = GeneralPreferencesPage()
        general_page.loadPreferences()
        name = general_page.windowTitle()
        item = QtGui.QListWidgetItem(name, self.uiListWidget)
        item.setData(QtCore.Qt.UserRole, general_page)
        self.uiStackedWidget.addWidget(general_page)
        self._items.append(item)

        # load server settings page
        servers_page = ServerPreferencesPage()
        servers_page.loadPreferences()
        name = servers_page.windowTitle()
        item = QtGui.QListWidgetItem(name, self.uiListWidget)
        item.setData(QtCore.Qt.UserRole, servers_page)
        self.uiStackedWidget.addWidget(servers_page)
        self._items.append(item)

        # load cloud settings page
        cloud_page = CloudPreferencesPage()
        # TODO load settings
        name = cloud_page.windowTitle()
        item = QtGui.QListWidgetItem(name, self.uiListWidget)
        item.setData(QtCore.Qt.UserRole, cloud_page)
        self.uiStackedWidget.addWidget(cloud_page)
        self._items.append(item)

        # load module preference pages
        for module in MODULES:
            for cls in module.preferencePages():
                preferences_page = cls()
                preferences_page.loadPreferences()
                name = preferences_page.windowTitle()
                item = QtGui.QListWidgetItem(name, self.uiListWidget)
                item.setData(QtCore.Qt.UserRole, preferences_page)
                self.uiStackedWidget.addWidget(preferences_page)
                self._items.append(item)

    def _showPreferencesPageSlot(self, current, previous):
        """
        Shows a preference page in the current dialog.

        :param current: current preference page widget
        :param previous: ignored
        """

        if current == None:
            current = previous

        preferences_page = current.data(QtCore.Qt.UserRole)
        name = preferences_page.windowTitle()
        self.uiTitleLabel.setText("{} preferences".format(name))
        index = self.uiStackedWidget.indexOf(preferences_page)
        widget = self.uiStackedWidget.widget(index)
        self.uiStackedWidget.setMinimumSize(widget.size())
        self.uiStackedWidget.resize(widget.size())
        self.uiStackedWidget.setCurrentIndex(index)

    def _applyPreferences(self):
        """
        Saves all the preferences.
        """

        for item in self._items:
            preferences_page = item.data(QtCore.Qt.UserRole)
            preferences_page.savePreferences()
        return True

    def reject(self):
        """
        Closes this dialog.
        """

        #TODO: refresh the devices list when closing the window
        QtGui.QDialog.reject(self)

    def accept(self):
        """
        Saves the preferences and closes this dialog.
        """

        #TODO: refresh the devices list when closing the window
        #globals.GApp.mainWindow.nodesDock.populateNodeDock(globals.GApp.workspace.dockWidget_NodeTypes.windowTitle())
        if self._applyPreferences():
            QtGui.QDialog.accept(self)
