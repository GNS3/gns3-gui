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
import pkg_resources

from .qt import QtGui, QtCore, QtWebKit
from .ui.news_dock_widget_ui import Ui_NewsDockWidget

import logging
log = logging.getLogger(__name__)


class NewsDockWidget(QtGui.QDockWidget, Ui_NewsDockWidget):
    """
    :param parent: parent widget
    """

    def __init__(self, parent):

        QtGui.QDockWidget.__init__(self, parent)
        self.setupUi(self)

        self.uiWebView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.uiWebView.linkClicked.connect(self._urlClickedSlot)
        self.uiWebView.loadFinished.connect(self._loadFinishedSlot)
        self._refresh_timer = QtCore.QTimer(self)
        self._refresh_timer.timeout.connect(self._refreshSlot)
        self._refresh_timer.start(60000)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._loadFinishedSlot)
        self._timer.setSingleShot(True)
        self._timer.start(5000)
        if parent.settings()["default_local_news"]:
            self._loadFinishedSlot()
        else:
            self.uiWebView.load(QtCore.QUrl("http://as.gns3.com/software/docked_200x200.html"))

    def closeEvent(self, event):
        """
        You really cannot close that dock (using ATL+F4...)

        :param event: closeEvent instance.
        """

        event.ignore()

    def _refreshSlot(self):
        """
        Refeshes the page.
        """

        self.uiWebView.reload()

    def _urlClickedSlot(self, url):
        """
        Opens a clicked URL using user's default browser.

        :param url: URL to open
        """

        if QtGui.QDesktopServices.openUrl(url) is False:
            QtGui.QMessageBox.critical(self, "Getting started", "Failed to open the URL: {}".format(url))

    def _loadFinishedSlot(self, result=False):
        """
        Slot called when the web page has been loaded.

        :param result: boolean
        """

        self.uiWebView.loadFinished.disconnect(self._loadFinishedSlot)
        self._timer.stop()
        self._timer.timeout.disconnect()
        if result is False:
            self._refresh_timer.stop()
            # load a local resource if the page is not available
            resource_name = os.path.join("static", "gns3_jungle.html")
            gns3_jungle = None
            if hasattr(sys, "frozen") and os.path.isfile(resource_name):
                gns3_jungle = os.path.normpath(resource_name)
            elif pkg_resources.resource_exists("gns3", resource_name):
                gns3_jungle_page = pkg_resources.resource_filename("gns3", resource_name)
                gns3_jungle = os.path.normpath(gns3_jungle_page)
            if gns3_jungle and not (sys.platform.startswith("win") and not sys.maxsize > 2 ** 32):
                # do not show the page on Windows 32-bit (crash when no Internet connection)
                self.uiWebView.load(QtCore.QUrl("file://{}".format(gns3_jungle)))
            else:
                self.hide()
