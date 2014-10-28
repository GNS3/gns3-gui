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
Dialog to change the topology symbol of NodeItems
"""

from ..qt import QtSvg, QtCore, QtGui
from ..ui.symbol_selection_dialog_ui import Ui_SymbolSelectionDialog
from ..node import Node


class SymbolSelectionDialog(QtGui.QDialog, Ui_SymbolSelectionDialog):
    """
    Symbol selection dialog.

    :param parent: parent widget
    :param items: list of items
    """

    def __init__(self, parent, items=None):

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self._items = items
        self.uiButtonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self._applyPreferencesSlot)

        if not self._items:
            self.uiButtonBox.button(QtGui.QDialogButtonBox.Apply).hide()

            # current categories
            categories = {"Routers": Node.routers,
                          "Switches": Node.switches,
                          "End devices": Node.end_devices,
                          "Security devices": Node.security_devices
                          }

            for name, category in categories.items():
                self.uiCategoryComboBox.addItem(name, category)
        else:
            self.uiCategoryLabel.hide()
            self.uiCategoryComboBox.hide()

        self.uiSymbolListWidget.setIconSize(QtCore.QSize(64, 64))
        symbol_resources = QtCore.QResource(":/symbols")
        for symbol in symbol_resources.children():
            if symbol.endswith('.normal.svg'):
                name = symbol[:-11]
                item = QtGui.QListWidgetItem(self.uiSymbolListWidget)
                item.setText(name)
                item.setIcon(QtGui.QIcon(':/symbols/' + symbol))

    def _applyPreferencesSlot(self):
        """
        Applies the selected symbol to the items.
        """

        current = self.uiSymbolListWidget.currentItem()
        if current:
            name = current.text()
            path = ":/symbols/{}.normal.svg".format(name)
            default_renderer = QtSvg.QSvgRenderer(path)
            default_renderer.setObjectName(path)
            path = ":/symbols/{}.selected.svg".format(name)
            hover_renderer = QtSvg.QSvgRenderer(path)
            hover_renderer.setObjectName(path)
            for item in self._items:
                item.setDefaultRenderer(default_renderer)
                item.setHoverRenderer(hover_renderer)

    def getSymbols(self):

        current = self.uiSymbolListWidget.currentItem()
        if current:
            name = current.text()
            normal_symbol = ":/symbols/{}.normal.svg".format(name)
            selected_symbol = ":/symbols/{}.selected.svg".format(name)
        return normal_symbol, selected_symbol

    def getCategory(self):

        return self.uiCategoryComboBox.itemData(self.uiCategoryComboBox.currentIndex())

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        if result and self._items:
            self._applyPreferencesSlot()
        QtGui.QDialog.done(self, result)
