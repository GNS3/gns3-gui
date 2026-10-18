# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
"""Name and fixed canvas dimensions, shared by group creation and editing."""

from ..qt import QtWidgets
from .container_style_widget import ContainerStyleWidget


class GroupPropertiesDialog(QtWidgets.QDialog):
    def __init__(self, parent, name, width, height, style=None, preview=None):
        super().__init__(parent)
        self.setWindowTitle("Container properties")
        outer = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget(self)
        general = QtWidgets.QWidget(self)
        layout = QtWidgets.QFormLayout(general)
        self.tabs.addTab(general, 'General')
        self.styleEditor = ContainerStyleWidget(style, self)
        self.tabs.addTab(self.styleEditor, 'Style')
        outer.addWidget(self.tabs)
        self.nameEdit = QtWidgets.QLineEdit(name, self)
        self.nameEdit.setObjectName("groupName")
        self.widthEdit = QtWidgets.QDoubleSpinBox(self)
        self.heightEdit = QtWidgets.QDoubleSpinBox(self)
        for field, value, label in ((self.widthEdit, width, "Width:"),
                                    (self.heightEdit, height, "Height:")):
            field.setRange(1, 1000000)
            field.setDecimals(2)
            field.setValue(value)
            field.setSuffix(" units")
            # Scope this override to these inputs, including their line edits;
            # global dark themes must not obscure the numeric values.
            field.setStyleSheet(
                "QDoubleSpinBox, QDoubleSpinBox QLineEdit { background-color: white; color: black; "
                "selection-background-color: #3484c6; selection-color: white; }")
        layout.addRow("Name:", self.nameEdit)
        layout.addRow("Width:", self.widthEdit)
        layout.addRow("Height:", self.heightEdit)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Apply, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)
        apply = buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Apply)
        apply.setVisible(preview is not None)
        if preview is not None:
            apply.clicked.connect(lambda: preview(self.properties()))
        self.applyButton = apply
        ok = buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.nameEdit.textChanged.connect(lambda text: ok.setEnabled(bool(text.strip())))
        ok.setEnabled(bool(name.strip()))
        self.nameEdit.textChanged.connect(lambda text: apply.setEnabled(bool(text.strip())))
        self.nameEdit.selectAll()
        self.nameEdit.setFocus()

    def properties(self):
        return self.nameEdit.text().strip(), self.widthEdit.value(), self.heightEdit.value(), self.styleEditor.styleData()

    @classmethod
    def getProperties(cls, parent, name, width, height, style=None, preview=None):
        dialog = cls(parent, name, width, height, style, preview)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return None
        return dialog.properties()
