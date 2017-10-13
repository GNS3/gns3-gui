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
Style editor to edit Shape items.
"""

from ..qt import QtCore, QtWidgets, QtGui
from ..ui.style_editor_dialog_ui import Ui_StyleEditorDialog
from ..items.shape_item import ShapeItem


class StyleEditorDialog(QtWidgets.QDialog, Ui_StyleEditorDialog):

    """
    Style editor dialog.

    :param parent: parent widget
    :param items: list of items
    """

    def __init__(self, parent, items):

        super().__init__(parent)
        self.setupUi(self)

        self._items = items
        self.uiColorPushButton.clicked.connect(self._setColorSlot)
        self.uiBorderColorPushButton.clicked.connect(self._setBorderColorSlot)
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self._applyPreferencesSlot)

        self.uiBorderStyleComboBox.addItem("Solid", QtCore.Qt.SolidLine)
        self.uiBorderStyleComboBox.addItem("Dash", QtCore.Qt.DashLine)
        self.uiBorderStyleComboBox.addItem("Dot", QtCore.Qt.DotLine)
        self.uiBorderStyleComboBox.addItem("Dash Dot", QtCore.Qt.DashDotLine)
        self.uiBorderStyleComboBox.addItem("Dash Dot Dot", QtCore.Qt.DashDotDotLine)
        self.uiBorderStyleComboBox.addItem("No border", QtCore.Qt.NoPen)

        # use the first item in the list as the model
        first_item = items[0]
        pen = first_item.pen()
        if hasattr(first_item, "brush"):  # Line don't have brush
            brush = first_item.brush()
            self._color = brush.color()
            self.uiColorPushButton.setStyleSheet("background-color: rgba({}, {}, {}, {});".format(self._color.red(),
                                                                                                  self._color.green(),
                                                                                                  self._color.blue(),
                                                                                                  self._color.alpha()))
        else:
            self.uiColorLabel.hide()
            self.uiColorPushButton.hide()
            self._color = None

        self._border_color = pen.color()
        self.uiBorderColorPushButton.setStyleSheet("background-color: rgba({}, {}, {}, {});".format(self._border_color.red(),
                                                                                                    self._border_color.green(),
                                                                                                    self._border_color.blue(),
                                                                                                    self._border_color.alpha()))
        self.uiRotationSpinBox.setValue(first_item.rotation())
        self.uiBorderWidthSpinBox.setValue(pen.width())
        index = self.uiBorderStyleComboBox.findData(pen.style())
        if index != -1:
            self.uiBorderStyleComboBox.setCurrentIndex(index)

    def _setColorSlot(self):
        """
        Slot to select the filling color.
        """

        color = QtWidgets.QColorDialog.getColor(self._color, self, "Select Color", QtWidgets.QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self._color = color
            self.uiColorPushButton.setStyleSheet("background-color: rgba({}, {}, {}, {});".format(self._color.red(),
                                                                                                  self._color.green(),
                                                                                                  self._color.blue(),
                                                                                                  self._color.alpha()))

    def _setBorderColorSlot(self):
        """
        Slot to select the border color.
        """

        color = QtWidgets.QColorDialog.getColor(self._border_color, self, "Select Color", QtWidgets.QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self._border_color = color
            self.uiBorderColorPushButton.setStyleSheet("background-color: rgba({}, {}, {}, {});".format(self._border_color.red(),
                                                                                                        self._border_color.green(),
                                                                                                        self._border_color.blue(),
                                                                                                        self._border_color.alpha()))

    def _applyPreferencesSlot(self):
        """
        Applies the new style settings.
        """

        border_style = QtCore.Qt.PenStyle(self.uiBorderStyleComboBox.itemData(self.uiBorderStyleComboBox.currentIndex()))
        pen = QtGui.QPen(self._border_color, self.uiBorderWidthSpinBox.value(), border_style, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        if self._color:
            brush = QtGui.QBrush(self._color)
        else:
            brush = None

        for item in self._items:
            item.setPen(pen)
            # on multiselection it's possible to select many type of items
            # but brush can be applied only on ShapeItem,
            if brush and isinstance(item, ShapeItem):
                item.setBrush(brush)
            item.setRotation(self.uiRotationSpinBox.value())

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        if result:
            self._applyPreferencesSlot()
        super().done(result)
