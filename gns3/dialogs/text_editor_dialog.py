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

from ..qt import QtCore, QtGui, QtWidgets, qslot, sip_is_deleted
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
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Apply).clicked.connect(self._applyPreferencesSlot)

        # use the first item in the list as the model
        first_item = items[0]
        self._setColor(first_item.defaultTextColor())
        self.uiRotationSpinBox.setValue(int(first_item.rotation()))
        self.uiPlainTextEdit.setPlainText(first_item.toPlainText())
        self.uiPlainTextEdit.setFont(first_item.font())

        if not first_item.editable():
            self.uiPlainTextEdit.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.NoTextInteraction)

        if len(self._items) == 1:
            self.uiApplyColorToAllItemsCheckBox.setChecked(True)
            self.uiApplyColorToAllItemsCheckBox.hide()
            self.uiApplyRotationToAllItemsCheckBox.setChecked(True)
            self.uiApplyRotationToAllItemsCheckBox.hide()
            self.uiApplyTextToAllItemsCheckBox.setChecked(True)
            self.uiApplyTextToAllItemsCheckBox.hide()

        # Prefer fonts already used by this project, then common installed
        # families. Unavailable project families remain selectable: Qt supplies
        # a local substitute without changing the saved family name.
        self.fontFamily = QtWidgets.QComboBox(self)
        self.fontFamily.setEditable(True)
        used = {item.font().family() for item in first_item.scene().items()
                if isinstance(item, QtWidgets.QGraphicsTextItem)} if first_item.scene() else set()
        used.add(first_item.font().family())
        installed = sorted(QtGui.QFontDatabase.families())
        common = [name for name in ['Arial', 'Helvetica', 'Times New Roman', 'Courier New',
                                   'Liberation Sans', 'Liberation Serif', 'DejaVu Sans', 'Noto Sans'] if name in installed]
        self.fontFamily.addItems(list(dict.fromkeys(sorted(used) + common + installed)))
        self.fontSize = QtWidgets.QDoubleSpinBox(self)
        self.fontSize.setRange(1, 512)
        self.underline = QtWidgets.QCheckBox('Underline', self)
        self.bold = QtWidgets.QCheckBox('Bold', self)
        self.italic = QtWidgets.QCheckBox('Italic', self)
        typography = QtWidgets.QFormLayout()
        typography.addRow('Font:', self.fontFamily)
        typography.addRow('Size:', self.fontSize)
        row = QtWidgets.QHBoxLayout()
        for field in (self.bold, self.italic, self.underline):
            row.addWidget(field)
        typography.addRow(row)
        self.layout().insertLayout(0, typography)
        self.loadFontControls(first_item.font())
        self.fontFamily.currentTextChanged.connect(self.updateFontPreview)
        self.fontSize.valueChanged.connect(self.updateFontPreview)
        for field in (self.bold, self.italic, self.underline):
            field.toggled.connect(self.updateFontPreview)

    def loadFontControls(self, font):
        blockers = [QtCore.QSignalBlocker(field) for field in
                    (self.fontFamily, self.fontSize, self.bold, self.italic, self.underline)]
        self.fontFamily.setCurrentText(font.family())
        self.fontSize.setValue(font.pointSizeF() if font.pointSizeF() > 0 else 12)
        self.bold.setChecked(font.bold())
        self.italic.setChecked(font.italic())
        self.underline.setChecked(font.underline())
        del blockers

    def updateFontPreview(self, *args):
        font = QtGui.QFont(self.uiPlainTextEdit.font())
        font.setFamily(self.fontFamily.currentText())
        font.setPointSizeF(self.fontSize.value())
        font.setBold(self.bold.isChecked())
        font.setItalic(self.italic.isChecked())
        font.setUnderline(self.underline.isChecked())
        self.uiPlainTextEdit.setFont(font)

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

    @qslot
    def _setFontSlot(self, *args):
        """
        Slot to select the font.
        """

        selected_font, ok = QtWidgets.QFontDialog.getFont(self.uiPlainTextEdit.font(), self,
                                                          options=QtWidgets.QFontDialog.FontDialogOption.DontUseNativeDialog)
        if ok:
            self.uiPlainTextEdit.setFont(selected_font)
            self.loadFontControls(selected_font)

    @qslot
    def _setColorSlot(self, *args):
        """
        Slot to select the color.
        """

        color = QtWidgets.QColorDialog.getColor(self._color, self, None, QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            self._setColor(color)

    @qslot
    def _applyPreferencesSlot(self, *args):
        """
        Applies the new text settings.
        """

        for item in self._items:
            if sip_is_deleted(item):
                continue
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
