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
Dialog to change node symbols.
"""

import os

from ..qt import QtSvg, QtCore, QtGui, QtWidgets
from ..ui.symbol_selection_dialog_ui import Ui_SymbolSelectionDialog


class SymbolSelectionDialog(QtWidgets.QDialog, Ui_SymbolSelectionDialog):

    """
    Symbol selection dialog.

    :param parent: parent widget
    :param items: list of items
    """

    def __init__(self, parent, items=None, symbol=None):

        super().__init__(parent)
        self.setupUi(self)

        self._items = items
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self._applyPreferencesSlot)
        self.uiSymbolToolButton.clicked.connect(self._symbolBrowserSlot)

        selected_symbol = symbol
        if not self._items:
            self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).hide()
        else:
            custom_symbol = items[0].renderer().objectName()
            if not custom_symbol:
                symbol_name = items[0].node().defaultSymbol()
            else:
                symbol_name = custom_symbol
            selected_symbol = symbol_name

        self.uiSymbolListWidget.setIconSize(QtCore.QSize(64, 64))
        symbol_resources = QtCore.QResource(":/symbols")
        for symbol in symbol_resources.children():
            if symbol.endswith(".svg"):
                name = os.path.splitext(symbol)[0]
                item = QtWidgets.QListWidgetItem(self.uiSymbolListWidget)
                item.setText(name)
                resource_path = ":/symbols/" + symbol
                svg_renderer = QtSvg.QSvgRenderer(resource_path)
                if resource_path == selected_symbol:
                    self.uiSymbolListWidget.setCurrentItem(item)
                image = QtGui.QImage(64, 64, QtGui.QImage.Format_ARGB32)
                # Set the ARGB to 0 to prevent rendering artifacts
                image.fill(0x00000000)
                svg_renderer.render(QtGui.QPainter(image))
                icon = QtGui.QIcon(QtGui.QPixmap.fromImage(image))
                item.setIcon(icon)

    def _applyPreferencesSlot(self):
        """
        Applies the selected symbol to the items.
        """

        current = self.uiSymbolListWidget.currentItem()
        if current:
            name = current.text()
            path = ":/symbols/{}.svg".format(name)
            renderer = QtSvg.QSvgRenderer(path)
            renderer.setObjectName(path)
            for item in self._items:
                item.setSharedRenderer(renderer)

    def getSymbol(self):

        if self.uiSymbolListWidget.isEnabled():
            current = self.uiSymbolListWidget.currentItem()
            name = current.text()
            normal_symbol = ":/symbols/{}.svg".format(name)
        else:
            normal_symbol = self.uiSymbolLineEdit.text()
        return normal_symbol

    def _symbolBrowserSlot(self):

        # supported image file formats
        file_formats = "PNG File (*.png);;JPG File (*.jpeg *.jpg);;BMP File (*.bmp);;XPM File (*.xpm *.xbm);;PPM File (*.ppm);;TIFF File (*.tiff);;All files (*.*)"
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Image", ".", file_formats)  # TODO: handle default dir
        if not path:
            return

        self.uiSymbolListWidget.setEnabled(False)
        self.uiSymbolLineEdit.clear()
        self.uiSymbolLineEdit.setText(path)

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        if result and self._items:
            self._applyPreferencesSlot()
        super().done(result)
