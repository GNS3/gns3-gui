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
from ..items.rectangle_item import RectangleItem


class StyleEditorDialog(QtWidgets.QDialog, Ui_StyleEditorDialog):

    """
    Style editor dialog.

    :param parent: parent widget
    :param items: list of items
    """

    def __init__(self, parent, items):

        super().__init__(parent)
        self.setupUi(self)
        self.uiWidthSpinBox.setMaximum(1000000)
        self.uiHeightSpinBox.setMaximum(1000000)
        self.uiBorderWidthSpinBox.setMinimum(0)
        for field in (self.uiWidthSpinBox, self.uiHeightSpinBox, self.uiBorderWidthSpinBox):
            field.setStyleSheet('QSpinBox, QSpinBox QLineEdit { background-color: white; color: black; selection-background-color: #3484c6; selection-color: white; }')

        self._items = items
        self.uiColorPushButton.clicked.connect(self._setColorSlot)
        self.uiBorderColorPushButton.clicked.connect(self._setBorderColorSlot)
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Apply).clicked.connect(self._applyPreferencesSlot)

        self.uiBorderStyleComboBox.addItem("Solid", QtCore.Qt.PenStyle.SolidLine)
        self.uiBorderStyleComboBox.addItem("Dash", QtCore.Qt.PenStyle.DashLine)
        self.uiBorderStyleComboBox.addItem("Dot", QtCore.Qt.PenStyle.DotLine)
        self.uiBorderStyleComboBox.addItem("Dash Dot", QtCore.Qt.PenStyle.DashDotLine)
        self.uiBorderStyleComboBox.addItem("Dash Dot Dot", QtCore.Qt.PenStyle.DashDotDotLine)
        self.uiBorderStyleComboBox.addItem("No border", QtCore.Qt.PenStyle.NoPen)

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
        if isinstance(first_item, RectangleItem):
            # use the horizontal corner radius first and then the vertical one if it's not set
            # maybe we allow configuring them separately in the future
            corner_radius = first_item.horizontalCornerRadius()
            if not corner_radius:
                corner_radius = first_item.verticalCornerRadius()
            self.uiCornerRadiusSpinBox.setValue(corner_radius)
        else:
            self.uiCornerRadiusLabel.hide()
            self.uiCornerRadiusSpinBox.hide()
        self.uiRotationSpinBox.setValue(int(first_item.rotation()))
        self.uiBorderWidthSpinBox.setValue(pen.width())
        if isinstance(first_item, ShapeItem):
            rect = first_item.rect()
            self.uiWidthSpinBox.setValue(int(rect.width()))
            self.uiHeightSpinBox.setValue(int(rect.height()))
        else:
            self.uiWidthSpinBox.hide()
            self.uiWidthLabel.hide()
            self.uiHeightSpinBox.hide()
            self.uiHeightLabel.hide()
        index = self.uiBorderStyleComboBox.findData(pen.style())
        if index != -1:
            self.uiBorderStyleComboBox.setCurrentIndex(index)

    def _setColorSlot(self):
        """
        Slot to select the filling color.
        """

        color = QtWidgets.QColorDialog.getColor(self._color, self, "Select Color", QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel)
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

        color = QtWidgets.QColorDialog.getColor(self._border_color, self, "Select Color", QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel)
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
        if self.uiBorderWidthSpinBox.value() == 0:
            border_style = QtCore.Qt.PenStyle.NoPen
        pen = QtGui.QPen(self._border_color, self.uiBorderWidthSpinBox.value(), border_style, QtCore.Qt.PenCapStyle.RoundCap, QtCore.Qt.PenJoinStyle.RoundJoin)
        if self._color:
            brush = QtGui.QBrush(self._color)
        else:
            brush = None

        for item in self._items:
            item.setPen(pen)
            # on multi-selection it's possible to select many type of items
            # but brush can be applied only on ShapeItem,
            if brush and isinstance(item, ShapeItem):
                item.setBrush(brush)
            if isinstance(item, RectangleItem):
                corner_radius = self.uiCornerRadiusSpinBox.value()
                # use the corner radius for both horizontal (rx) and vertical (ry)
                # maybe we support setting them separately in the future
                item.setHorizontalCornerRadius(corner_radius)
                item.setVerticalCornerRadius(corner_radius)
            if isinstance(item, ShapeItem):
                item.setWidthAndHeight(item.rect().width() if int(item.rect().width()) == self.uiWidthSpinBox.value() else self.uiWidthSpinBox.value(),
                                       item.rect().height() if int(item.rect().height()) == self.uiHeightSpinBox.value() else self.uiHeightSpinBox.value())
            item.setRotation(self.uiRotationSpinBox.value())

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        if result:
            self._applyPreferencesSlot()
        super().done(result)
