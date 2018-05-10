# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 GNS3 Technologies Inc.
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

import copy

from gns3.qt import QtWidgets, QtCore, qpartial
from gns3.ui.project_welcome_dialog_ui import Ui_ProjectWelcomeDialog

import logging
log = logging.getLogger(__name__)


class ProjectWelcomeDialog(QtWidgets.QDialog, Ui_ProjectWelcomeDialog):
    """
    This dialog shows when project is imported and global variables assigned to the project are missing.
    """

    def __init__(self, parent, project):

        super().__init__(parent)
        self._project = project
        self.setupUi(self)
        self.uiOkButton.clicked.connect(self._okButtonClickedSlot)
        self.gridLayout.setAlignment(QtCore.Qt.AlignTop)
        self.label.setOpenExternalLinks(True)

        self._variables = self._getVariables(project)

        self._loadReadme()
        self._addMisingVariablesEdits()

    def _getVariables(self, project):
        variables = copy.copy(self._project.variables())
        if variables is None:
            variables = []
        return variables

    def _addMisingVariablesEdits(self):
        missing = [v for v in self._variables if v.get("value", "").strip() == ""]
        for i, variable in enumerate(missing, start=0):
            nameLabel = QtWidgets.QLabel()
            nameLabel.setText(variable.get("name", ""))
            self.gridLayout.addWidget(nameLabel, i, 0)

            valueEdit = QtWidgets.QLineEdit()
            valueEdit.setText(variable.get("value", ""))
            valueEdit.textChanged.connect(qpartial(self.onValueChange, variable))
            self.gridLayout.addWidget(valueEdit, i, 1)

    def _loadReadme(self):
        self._project.get("/files/README.txt", self._loadedReadme)

    def _loadedReadme(self, result, error=False, raw_body=None, context={}, **kwargs):
        if not error:
            self.label.setText(raw_body.decode("utf-8"))

    def onValueChange(self, variable, text):
        variable["value"] = text

    def _okButtonClickedSlot(self):
        missing = [v for v in self._variables if v.get("value", "").strip() == ""]
        if len(missing) > 0:
            reply = QtWidgets.QMessageBox.warning(
                self, 'Missing values',
                'Are you sure you want to continue without providing missing values?',
                QtWidgets.QMessageBox.Yes,
                QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                return

        self._project.setVariables(self._variables)
        self._project.update()
        self.accept()

