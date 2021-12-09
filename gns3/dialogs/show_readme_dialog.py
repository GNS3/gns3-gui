# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 GNS3 Technologies Inc.
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

from gns3.qt import QtCore, QtGui, QtWidgets
from gns3.ui.show_readme_dialog_ui import Ui_ShowReadmeDialog
from gns3.utils import parse_version

import logging
log = logging.getLogger(__name__)


class ShowReadmeDialog(QtWidgets.QDialog, Ui_ShowReadmeDialog):

    def __init__(self, project, path, content=None, parent=None):

        if parent is None:
            from gns3.main_window import MainWindow
            parent = MainWindow.instance()

        super().__init__(parent)
        self.setupUi(self)

        self._project = project
        self._path = path
        self.setWindowTitle(project.name() + " " + os.path.basename(path))
        self.uiRefreshButton.pressed.connect(self._refreshSlot)

        # QTextDocument before Qt version 5.14 doesn't support Markdown
        if parse_version(QtCore.QT_VERSION_STR) < parse_version("5.14.0") or parse_version(QtCore.PYQT_VERSION_STR) < parse_version("5.14.0"):
            self._markdown = False
        else:
            self._markdown = True

        self._document = QtGui.QTextDocument()
        self.uiTextBrowser.setDocument(self._document)

        if content:
            if self._markdown:
                self._document.setMarkdown(content)
            else:
                self._document.setPlainText(content)
        else:
            self._refreshSlot()

    def _refreshSlot(self):
        self._project.get("/files/" + self._path, self._getCallback, raw=True)

    def _getCallback(self, result, error=False, **kwargs):

        if not error:
            content = result.decode("utf-8", errors="ignore")
            if self._markdown:
                self._document.setMarkdown(content)
            else:
                self._document.setPlainText(content)
