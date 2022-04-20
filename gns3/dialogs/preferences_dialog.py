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

from ..qt import QtCore, QtWidgets
from ..ui.preferences_dialog_ui import Ui_PreferencesDialog
from ..pages.server_preferences_page import ServerPreferencesPage
from ..pages.general_preferences_page import GeneralPreferencesPage
from ..pages.packet_capture_preferences_page import PacketCapturePreferencesPage
from ..pages.gns3_vm_preferences_page import GNS3VMPreferencesPage
from ..modules import MODULES

import logging
log = logging.getLogger(__name__)


class PreferencesDialog(QtWidgets.QDialog, Ui_PreferencesDialog):

    """
    Preferences dialog implementation.

    :param parent: parent widget
    """

    def __init__(self, parent):

        super().__init__(parent)

        self.setupUi(self)
        self._modified_pages = set()

        # We adapt the max size to the screen resolution
        # We need to manually do that otherwise on small screen the windows
        # could be bigger than the screen instead of displaying scrollbars
        height = QtWidgets.QDesktopWidget().screenGeometry().height() - 100
        width = QtWidgets.QDesktopWidget().screenGeometry().width() - 100

        # 980 is the default width
        if self.width() > width:
            self.resize(width, self.height())
        # 680 is the default height
        if self.height() > height:
            self.resize(self.width(), height)

        self.uiTreeWidget.currentItemChanged.connect(self._showPreferencesPageSlot)
        self._applyButton = self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply)
        self._applyButton.clicked.connect(self._applyPreferences)
        self._applyButton.setEnabled(False)
        self._applyButton.setStyleSheet("QPushButton:disabled {color: gray}")
        self._items = []
        self._loadPreferencePages()

        # select the first available page
        self.uiTreeWidget.setCurrentItem(self._items[0])

        # set the maximum width based on the content of column 0
        self.uiTreeWidget.setMaximumWidth(self.uiTreeWidget.sizeHintForColumn(0) + 10)

        # Something has change?
        self._modified_pages = set()

    def _loadPreferencePages(self):
        """
        Loads all preference pages (built-ins and from modules).
        """

        # load built-in preference pages
        pages = [
            GeneralPreferencesPage,
            ServerPreferencesPage,
            GNS3VMPreferencesPage,
            PacketCapturePreferencesPage,
        ]

        for page in pages:
            preferences_page = page(self)
            preferences_page.loadPreferences()
            name = preferences_page.windowTitle()
            item = QtWidgets.QTreeWidgetItem(self.uiTreeWidget)
            item.setText(0, name)
            item.setData(0, QtCore.Qt.UserRole, preferences_page)
            self.uiStackedWidget.addWidget(preferences_page)
            self._items.append(item)
            self._watchForChanges(preferences_page)

        # load module preference pages
        for module in MODULES:
            preference_pages = module.preferencePages()
            parent = self.uiTreeWidget
            for cls in preference_pages:
                preferences_page = cls()
                preferences_page.setParent(self)
                preferences_page.loadPreferences()
                name = preferences_page.windowTitle()
                item = QtWidgets.QTreeWidgetItem(parent)
                item.setText(0, name)
                item.setData(0, QtCore.Qt.UserRole, preferences_page)
                self.uiStackedWidget.addWidget(preferences_page)
                self._items.append(item)
                if cls is preference_pages[0]:
                    parent = item
                self._watchForChanges(preferences_page)

        # expand all items by default
        self.uiTreeWidget.expandAll()

    def _watchForChanges(self, preferences_page):
        """
        Connect all the widget of a page to check if something has change
        """

        # Class name, changed signal
        widget_to_watch = {
            QtWidgets.QLineEdit: "textChanged",
            QtWidgets.QPlainTextEdit: "textChanged",
            # QtWidgets.QTreeWidget: "itemChanged",
            QtWidgets.QTreeWidget: "itemDoubleClicked",
            QtWidgets.QComboBox: "currentIndexChanged",
            QtWidgets.QSpinBox: "valueChanged",
            QtWidgets.QAbstractButton: "pressed"
        }

        for widget, signal in widget_to_watch.items():
            for children in preferences_page.findChildren(widget):
                getattr(children, signal).connect(self._preferenceChangeSlot)

    def _preferenceChangeSlot(self, *args):
        """
        Called when something change in the preference dialog
        """

        # Found the page with the change
        widget = sender = self.sender()
        while widget.parent() != self.uiStackedWidget:
            widget = widget.parent()

        if self.addModifiedPage(widget):
            log.debug("%s value has changed", sender.objectName())

    def addModifiedPage(self, widget):
        """
        :returns: True is the page is initialized and element added
        """
        # The widget can trigger signal before the end of init due to async api call
        if not hasattr(widget, 'pageInitialized') or widget.pageInitialized():
            self._applyButton.setEnabled(True)
            self._modified_pages.add(widget)
            return True
        return False

    def _showPreferencesPageSlot(self, current, previous):
        """
        Shows a preference page in the current dialog.

        :param current: current preference page widget
        :param previous: ignored
        """

        if current is None:
            current = previous

        preferences_page = current.data(0, QtCore.Qt.UserRole)
        accessible_name = preferences_page.accessibleName()
        if accessible_name:
            self.uiTitleLabel.setText(accessible_name)
        else:
            name = preferences_page.windowTitle()
            self.uiTitleLabel.setText("{} preferences".format(name))
        index = self.uiStackedWidget.indexOf(preferences_page)
        widget = self.uiStackedWidget.widget(index)
        #self.uiStackedWidget.setMinimumSize(widget.size())  # FIXME: this seems to not work on Windows and OSX
        #self.uiStackedWidget.resize(widget.size())
        self.uiStackedWidget.setCurrentIndex(index)

        for index in range(0, self.uiStackedWidget.count()):
            page = self.uiStackedWidget.widget(index)
            if self.uiStackedWidget.currentIndex() == index:
                page.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            else:
                page.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

    def _applyPreferences(self):
        """
        Saves all the preferences.
        """

        success = True
        for preferences_page in list(self._modified_pages):
            ok = preferences_page.savePreferences()
            # if page.savePreferences() returns None, assume success
            if ok is not None and not ok:
                success = False
        if success:
            self._applyButton.setEnabled(False)
            self._modified_pages = set()
        return success

    def reject(self):
        """
        Closes this dialog.
        """

        if len(self._modified_pages) > 0:
            # Get the title of pages with modifications
            pages_title = ', '.join([page.windowTitle() for page in self._modified_pages])
            reply = QtWidgets.QMessageBox.warning(self,
                                                  "Preferences",
                                                  "You have unsaved preferences in {}.\n\nContinue without saving?".format(pages_title),
                                                  QtWidgets.QMessageBox.Yes,
                                                  QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                return
        QtWidgets.QDialog.reject(self)

    def accept(self):
        """
        Saves the preferences and closes this dialog.
        """

        if self._applyPreferences():
            QtWidgets.QDialog.accept(self)
