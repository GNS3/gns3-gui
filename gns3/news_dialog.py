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

from .qt import QtCore, QtGui

# QtWebKit is not installed by default on FreeBSD, Solaris and possibly other systems.
try:
    from .ui.news_dialog_ui import Ui_NewsDialog
    from .qt import QtWebKit
except ImportError:
    pass


class NewsDialog(QtGui.QDialog, Ui_NewsDialog):
    """
    News dialog.
    """

    def __init__(self, parent):

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.webpage = QtCore.QUrl('http://ads.gns3.net/er_ads.php')
        self.uiWebView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.connect(self.uiWebView, QtCore.SIGNAL('linkClicked(const QUrl &)'), self._urlClickedSlot)
        self.connect(self.uiWebView, QtCore.SIGNAL('loadFinished(bool)'), self._loadFinishedSlot)
        self.adjustSize()
        self._timer = QtCore.QTimer()
        self.connect(self._timer, QtCore.SIGNAL('timeout()'), self._refreshSlot)
        self._timer.start(10000)  # refresh every 10 seconds
        self.loadWebPage()

    def done(self, result):

        self._timer.stop()
        QtGui.QDialog.done(self, result)

    def _refreshSlot(self):

        self.uiWebView.reload()

    def loadWebPage(self):

        self.uiWebView.load(self.webpage)

    def _urlClickedSlot(self, url):

        if QtGui.QDesktopServices.openUrl(url) == False:
            print("Failed to open the URL: {}".format(url))

    def _loadFinishedSlot(self, result):

        self.disconnect(self.uiWebView, QtCore.SIGNAL('loadFinished(bool)'), self._loadFinishedSlot)
        if result == False:
            QtGui.QMessageBox.information(self, "News", "Cannot load the online page, trying with your default browser ...")
            if QtGui.QDesktopServices.openUrl(self.webpage) == False:
                print("Failed to open the URL: {}".format(self.webpage.toString()))
            self.close()
