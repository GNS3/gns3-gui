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

"""
Text editor to edit Note items.
"""

from ..qt import QtCore, QtWidgets
from ..ui.text_editor_dialog_ui import Ui_TextEditorDialog


class TextEditorDialog(QtWidgets.QDialog, Ui_TextEditorDialog):
    """
    Text editor dialog.

    :param parent: parent widget
    :param items: list of items
    """

    def __init__(self, parent, items):

        super().__init__(parent)
        self.setupUi(self)

        self._items = items
        self.uiFontPushButton.clicked.connect(self._setFontSlot)
        self.uiColorPushButton.clicked.connect(self._setColorSlot)
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self._applyPreferencesSlot)

        # use the first item in the list as the model
        first_item = items[0]
        self._setColor(first_item.defaultTextColor())
        self.uiRotationSpinBox.setValue(first_item.rotation())
        self.uiPlainTextEdit.setPlainText(first_item.toPlainText())
        self.uiPlainTextEdit.setFont(first_item.font())

        if not first_item.editable():
            self.uiPlainTextEdit.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)

        if len(self._items) == 1:
            self.uiApplyColorToAllItemsCheckBox.setChecked(True)
            self.uiApplyColorToAllItemsCheckBox.hide()
            self.uiApplyRotationToAllItemsCheckBox.setChecked(True)
            self.uiApplyRotationToAllItemsCheckBox.hide()
            self.uiApplyTextToAllItemsCheckBox.setChecked(True)
            self.uiApplyTextToAllItemsCheckBox.hide()

    def _setColor(self, color):
        self._color = color
        self.uiColorPushButton.setStyleSheet("background-color: rgba({}, {}, {}, {});".format(color.red(),
                                                                                              color.green(),
                                                                                              color.blue(),
                                                                                              color.alpha()))
        self.uiPlainTextEdit.setStyleSheet("color: rgba({}, {}, {}, {});".format(color.red(),
                                                                                 color.green(),
                                                                                 color.blue(),
                                                                                 color.alpha()))

    def _setFontSlot(self):
        """
        Slot to select the font.
        """

        selected_font, ok = QtWidgets.QFontDialog.getFont(self.uiPlainTextEdit.font(), self)
        if ok:
            self.uiPlainTextEdit.setFont(selected_font)

    def _setColorSlot(self):
        """
        Slot to select the color.
        """

        color = QtWidgets.QColorDialog.getColor(self._color, self, None, QtWidgets.QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self._setColor(color)

    def _applyPreferencesSlot(self):
        """
        Applies the new text settings.
        """

        for item in self._items:
            item.setFont(self.uiPlainTextEdit.font())
            if self.uiApplyColorToAllItemsCheckBox.isChecked():
                item.setDefaultTextColor(self._color)
            if self.uiApplyRotationToAllItemsCheckBox.isChecked():
                item.setRotation(self.uiRotationSpinBox.value())
            if item.editable() and self.uiApplyTextToAllItemsCheckBox.isChecked():
                item.setPlainText(self.uiPlainTextEdit.toPlainText())

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        if result:
            self._applyPreferencesSlot()
        super().done(result)
