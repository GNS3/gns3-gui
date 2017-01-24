#!/usr/bin/env python
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

from .qt import QtWidgets


class NodesDockWidget(QtWidgets.QDockWidget):

    def _filterTextChangedSlot(self, text):
        self.window().uiNodesView.setCurrentSearch(text)
        self.window().uiNodesView.refresh()

    def _filterIndexChangedSlot(self, index):
        if index == 0:
            self.window().uiNodesView.setShowInstalledAppliances(True)
            self.window().uiNodesView.setShowAvailableAppliances(True)
        elif index == 1:
            self.window().uiNodesView.setShowInstalledAppliances(True)
            self.window().uiNodesView.setShowAvailableAppliances(False)
        else:
            self.window().uiNodesView.setShowInstalledAppliances(False)
            self.window().uiNodesView.setShowAvailableAppliances(True)
        self.window().uiNodesView.refresh()

    def populateNodesView(self, category):
        self.window().uiNodesFilterComboBox.activated.connect(self._filterIndexChangedSlot)
        self.window().uiNodesFilterLineEdit.textChanged.connect(self._filterTextChangedSlot)
        self.window().uiNodesView.clear()
        text = self.window().uiNodesFilterLineEdit.text().strip().lower()
        self.window().uiNodesView.populateNodesView(category, text)
