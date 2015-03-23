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

import os
import sys

from ..qt import QtCore, QtGui, QtWebKit
from ..ui.getting_started_dialog_ui import Ui_GettingStartedDialog
from ..utils.get_resource import get_resource
from ..local_config import LocalConfig


class GettingStartedDialog(QtGui.QDialog, Ui_GettingStartedDialog):

    """
    GettingStarted dialog.
    """

    def __init__(self, parent):

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.uiWebView.page().mainFrame().setScrollBarPolicy(QtCore.Qt.Horizontal, QtCore.Qt.ScrollBarAlwaysOff)
        self.uiWebView.page().mainFrame().setScrollBarPolicy(QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff)
        self.adjustSize()
        self.uiWebView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.uiWebView.linkClicked.connect(self._urlClickedSlot)
        self._local_config = LocalConfig.instance()
        gui_settings = self._local_config.loadSectionSettings("GUI", {"hide_getting_started_dialog": False})
        self.uiCheckBox.setChecked(gui_settings["hide_getting_started_dialog"])
        getting_started = get_resource(os.path.join("static", "getting_started.html"))
        if getting_started and not (sys.platform.startswith("win") and not sys.maxsize > 2 ** 32):
            # do not show the page on Windows 32-bit (crash when no Internet connection)
            self.uiWebView.load(QtCore.QUrl.fromLocalFile(getting_started))
        else:
            self.uiCheckBox.setChecked(True)
            self.accept()

    def showit(self):
        """
        Either this dialog should be automatically showed at startup.

        :returns: boolean
        """

        return not self.uiCheckBox.isChecked()

    def done(self, result):
        """
        This dialog is closed.

        :param result: ignored
        """

        self._local_config.saveSectionSettings("GUI", {"hide_getting_started_dialog": self.uiCheckBox.isChecked()})
        QtGui.QDialog.done(self, result)

    def _urlClickedSlot(self, url):
        """
        Opens a clicked URL using user's default browser.

        :param url: URL to open
        """

        if QtGui.QDesktopServices.openUrl(url) is False:
            QtGui.QMessageBox.critical(self, "Getting started", "Failed to open the URL: {}".format(url))
