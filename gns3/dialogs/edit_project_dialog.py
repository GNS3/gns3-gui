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

from ..qt import QtWidgets
from ..topology import Topology
from ..ui.edit_project_dialog_ui import Ui_EditProjectDialog


class EditProjectDialog(QtWidgets.QDialog, Ui_EditProjectDialog):
    """
    Edit current project settings
    """

    def __init__(self, parent):

        super().__init__(parent)
        self.setupUi(self)
        self._project = Topology.instance().project()
        self.uiProjectNameLineEdit.setText(self._project.name())
        self.uiProjectAutoOpenCheckBox.setChecked(self._project.autoOpen())
        self.uiProjectAutoCloseCheckBox.setChecked(not self._project.autoClose())
        self.uiProjectAutoStartCheckBox.setChecked(self._project.autoStart())
        self.uiSceneWidthSpinBox.setValue(self._project.sceneWidth())
        self.uiSceneHeightSpinBox.setValue(self._project.sceneHeight())

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        if result:
            self._project.setName(self.uiProjectNameLineEdit.text())
            self._project.setAutoOpen(self.uiProjectAutoOpenCheckBox.isChecked())
            self._project.setAutoClose(not self.uiProjectAutoCloseCheckBox.isChecked())
            self._project.setAutoStart(self.uiProjectAutoStartCheckBox.isChecked())
            self._project.setSceneHeight(self.uiSceneHeightSpinBox.value())
            self._project.setSceneWidth(self.uiSceneWidthSpinBox.value())
            self._project.update()
        super().done(result)
