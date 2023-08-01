# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Pekka Helenius
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
Style editor to edit Link items.
"""

from ..qt import QtCore, QtWidgets, QtGui
from ..ui.style_editor_dialog_ui import Ui_StyleEditorDialog


class StyleEditorDialogLink(QtWidgets.QDialog, Ui_StyleEditorDialog):

    """
    Style editor dialog.

    :param parent: parent widget
    :param link: selected link
    """

    def __init__(self, link, parent):

        super().__init__(parent)
        self.setupUi(self)

        self._link = link
        self._link_style = {}

        self.uiBorderColorPushButton.clicked.connect(self._setBorderColorSlot)
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self._applyPreferencesSlot)

        self.uiBorderStyleComboBox.addItem("Solid", QtCore.Qt.SolidLine)
        self.uiBorderStyleComboBox.addItem("Dash", QtCore.Qt.DashLine)
        self.uiBorderStyleComboBox.addItem("Dot", QtCore.Qt.DotLine)
        self.uiBorderStyleComboBox.addItem("Dash Dot", QtCore.Qt.DashDotLine)
        self.uiBorderStyleComboBox.addItem("Dash Dot Dot", QtCore.Qt.DashDotDotLine)
        self.uiBorderStyleComboBox.addItem("Invisible", QtCore.Qt.NoPen)

        self.uiColorLabel.hide()
        self.uiColorPushButton.hide()
        self._color = None

        self.uiCornerRadiusLabel.hide()
        self.uiCornerRadiusSpinBox.hide()
        self.uiRotationLabel.hide()
        self.uiRotationSpinBox.hide()

        link.setHovered(False)  # make sure we use the right style
        pen = link.pen()
        link.setHovered(True)

        self._border_color = pen.color()
        self.uiBorderColorPushButton.setStyleSheet("background-color: rgba({}, {}, {}, {});".format(self._border_color.red(),
                                                                                                    self._border_color.green(),
                                                                                                    self._border_color.blue(),
                                                                                                    self._border_color.alpha()))
        self.uiBorderWidthSpinBox.setValue(pen.width())
        index = self.uiBorderStyleComboBox.findData(pen.style())
        if index != -1:
            self.uiBorderStyleComboBox.setCurrentIndex(index)

        self.adjustSize()

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

        self._link.setPen(pen)

        new_link_style = {}
        new_link_style["color"] = self._border_color.name()
        new_link_style["width"] = self.uiBorderWidthSpinBox.value()
        new_link_style["type"]  = border_style
        
        # Store values
        self._link.setLinkStyle(new_link_style)
        self._link.setHovered(False)  # allow to see the new style

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        if result:
            self._applyPreferencesSlot()
        super().done(result)
