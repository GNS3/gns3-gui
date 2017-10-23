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
from .settings import NODES_VIEW_SETTINGS
from .local_config import LocalConfig


class NodesDockWidget(QtWidgets.QDockWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._settings = LocalConfig.instance().loadSectionSettings("NodesView", NODES_VIEW_SETTINGS)

    def _filterTextChangedSlot(self, text):
        self.window().uiNodesView.setCurrentSearch(text)
        self.window().uiNodesView.refresh()

    def _filterIndexChangedSlot(self, index):
        self._settings["nodes_view_filter"] = index
        LocalConfig.instance().saveSectionSettings("NodesView", self._settings)

        if index == 0:
            self.window().uiNodesView.setShowInstalledAppliances(True)
            self.window().uiNodesView.setShowBuiltinAvailableAppliances(True)
            self.window().uiNodesView.setShowMyAvailableAppliances(True)
        elif index == 1:
            self.window().uiNodesView.setShowInstalledAppliances(True)
            self.window().uiNodesView.setShowBuiltinAvailableAppliances(False)
            self.window().uiNodesView.setShowMyAvailableAppliances(False)
        elif index == 2:
            self.window().uiNodesView.setShowInstalledAppliances(False)
            self.window().uiNodesView.setShowBuiltinAvailableAppliances(True)
            self.window().uiNodesView.setShowMyAvailableAppliances(True)
        else:
            self.window().uiNodesView.setShowInstalledAppliances(False)
            self.window().uiNodesView.setShowBuiltinAvailableAppliances(False)
            self.window().uiNodesView.setShowMyAvailableAppliances(True)
        self.window().uiNodesView.refresh()

    def populateNodesView(self, category):
        # it's common race condition that uiNodesFilterComboBox that doesn't exist
        # ref. https://github.com/GNS3/gns3-gui/issues/2304
        if hasattr(self.window(), 'uiNodesFilterComboBox'):
            if self.window().uiNodesFilterComboBox.currentIndex() != self._settings["nodes_view_filter"]:
                self.window().uiNodesFilterComboBox.setCurrentIndex(self._settings["nodes_view_filter"])
                self._filterIndexChangedSlot(self._settings["nodes_view_filter"])
            self.window().uiNodesFilterComboBox.activated.connect(self._filterIndexChangedSlot)
            self.window().uiNodesFilterLineEdit.textChanged.connect(self._filterTextChangedSlot)
            self.window().uiNodesView.clear()
            text = self.window().uiNodesFilterLineEdit.text().strip().lower()
            self.window().uiNodesView.populateNodesView(category, text)
