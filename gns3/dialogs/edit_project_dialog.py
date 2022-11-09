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

from gns3.utils import parse_version

from ..qt import QtGui, QtWidgets, QtCore, qslot, qpartial
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
        self.uiNodeGridSizeSpinBox.setValue(self._project.nodeGridSize())
        self.uiDrawingGridSizeSpinBox.setValue(self._project.drawingGridSize())

        self.uiGlobalVariablesGrid.setAlignment(QtCore.Qt.AlignTop)

        self.uiNewVarButton = QtWidgets.QPushButton('Add new variable', self)
        self.uiNewVarButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.uiNewVarButton.clicked.connect(self.onAddNewVariable)
        self.uiGlobalVariablesGrid.addWidget(self.uiNewVarButton, 0, 3, QtCore.Qt.AlignRight)

        self._readme_filename = "README.txt"
        self.uiTabWidget.currentChanged.connect(self._previewMarkdownSlot)
        self._loadReadme()
        self._variables = self._project.variables()
        if not self._variables:
            self._variables = [{"name": "", "value": ""}]
        self.updateGlobalVariables()

    def _loadReadme(self):

        self._project.get("/files/{}".format(self._readme_filename), self._loadedReadme, raw=True)

    def _loadedReadme(self, result, error=False, context={}, **kwargs):

        if not error:
            content = result.decode("utf-8", errors="replace")
            self.uiReadmeTextEdit.setPlainText(content)

    def _previewMarkdownSlot(self, index):

        # index 1 is preview tab
        if index == 1:

            # QTextDocument before Qt version 5.14 doesn't support Markdown
            if parse_version(QtCore.QT_VERSION_STR) < parse_version("5.14.0") or parse_version(QtCore.PYQT_VERSION_STR) < parse_version("5.14.0"):
                QtWidgets.QMessageBox.critical(self, "Markdown preview", "Markdown preview is only support with Qt version 5.14.0 or above")
                return

            # show Markdown preview
            document = QtGui.QTextDocument()
            self.uiReadmePreview.setDocument(document)
            document.setMarkdown(self.uiReadmeTextEdit.toPlainText())

    def updateGlobalVariables(self):
        while True:
            item = self.uiGlobalVariablesGrid.takeAt(1)
            if item is None:
                break
            elif item.widget():
                item.widget().deleteLater()

        for i, variable in enumerate(self._variables, start=1):
            nameLabel = QtWidgets.QLabel()
            nameLabel.setText("Name:")
            self.uiGlobalVariablesGrid.addWidget(nameLabel, i, 0)

            nameEdit = QtWidgets.QLineEdit()
            nameEdit.setText(variable.get("name", ""))
            nameEdit.textChanged.connect(qpartial(self.onNameChange, variable))
            self.uiGlobalVariablesGrid.addWidget(nameEdit, i, 1)

            valueLabel = QtWidgets.QLabel()
            valueLabel.setText("Value:")
            self.uiGlobalVariablesGrid.addWidget(valueLabel, i, 2)

            valueEdit = QtWidgets.QLineEdit()
            valueEdit.setText(variable.get("value", ""))
            valueEdit.textChanged.connect(qpartial(self.onValueChange, variable))
            self.uiGlobalVariablesGrid.addWidget(valueEdit, i, 3)

    @qslot
    def onAddNewVariable(self, event):
        self._variables += [{"name": "", "value": ""}]
        self.updateGlobalVariables()

    def onNameChange(self, variable, text):
        variable["name"] = text

    def onValueChange(self, variable, text):
        variable["value"] = text

    def _cleanVariables(self):
        return [v for v in self._variables if v.get("name").strip() != ""]

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        if result:
            node_grid_size = self.uiNodeGridSizeSpinBox.value()
            drawing_grid_size = self.uiDrawingGridSizeSpinBox.value()
            if node_grid_size % drawing_grid_size != 0:
                QtWidgets.QMessageBox.critical(self, "Grid sizes", "Invalid grid sizes which will create overlapping lines")
            else:
                self._project.setNodeGridSize(node_grid_size)
                self._project.setDrawingGridSize(drawing_grid_size)
                self._project.setName(self.uiProjectNameLineEdit.text())
                self._project.setAutoOpen(self.uiProjectAutoOpenCheckBox.isChecked())
                self._project.setAutoClose(not self.uiProjectAutoCloseCheckBox.isChecked())
                self._project.setAutoStart(self.uiProjectAutoStartCheckBox.isChecked())
                self._project.setSceneHeight(self.uiSceneHeightSpinBox.value())
                self._project.setSceneWidth(self.uiSceneWidthSpinBox.value())
                self._project.setVariables(self._cleanVariables())
                self._project.update()
                content = self.uiReadmeTextEdit.toPlainText()
                if content:
                    self._project.post("/files/{}".format(self._readme_filename), self._saveReadmeCallback, body=content)
        super().done(result)

    def _saveReadmeCallback(self, result, error=False, **kwargs):

        if error:
            QtWidgets.QMessageBox.critical(self, "Edit project", "Could not created readme file")
