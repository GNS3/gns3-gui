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
from ..items.svg_node_item import SvgNodeItem
from ..items.pixmap_node_item import PixmapNodeItem
from ..ui.symbol_selection_dialog_ui import Ui_SymbolSelectionDialog

import logging
log = logging.getLogger(__name__)


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
        self.uiCustomSymbolRadioButton.toggled.connect(self._customSymbolToggledSlot)
        self.uiBuiltInSymbolRadioButton.toggled.connect(self._builtInSymbolToggledSlot)
        self._symbols_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.PicturesLocation)

        selected_symbol = symbol
        if not self._items:
            self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).hide()
        else:
            first_item = items[0]
            if isinstance(first_item, SvgNodeItem):
                custom_symbol = first_item.renderer().objectName()
                if not custom_symbol:
                    symbol_name = first_item.node().defaultSymbol()
                else:
                    symbol_name = custom_symbol
                selected_symbol = symbol_name
            elif isinstance(first_item, PixmapNodeItem):
                selected_symbol = first_item.pixmapSymbolPath()

        custom_symbol = True
        self.uiBuiltInSymbolRadioButton.setChecked(True)
        self.uiSymbolListWidget.setFocus()
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
                    # this is a built-in symbol
                    custom_symbol = False
                    self.uiSymbolListWidget.setCurrentItem(item)
                image = QtGui.QImage(64, 64, QtGui.QImage.Format_ARGB32)
                # Set the ARGB to 0 to prevent rendering artifacts
                image.fill(0x00000000)
                svg_renderer.render(QtGui.QPainter(image))
                icon = QtGui.QIcon(QtGui.QPixmap.fromImage(image))
                item.setIcon(icon)

        if custom_symbol:
            # this is a custom symbol
            self.uiCustomSymbolRadioButton.setChecked(True)
            self.uiSymbolLineEdit.setText(selected_symbol)
            self.uiSymbolLineEdit.setToolTip('<img src="{}"/>'.format(selected_symbol))
            self.uiBuiltInGroupBox.setEnabled(False)
            self.uiBuiltInGroupBox.hide()

        self.adjustSize()

    def _customSymbolToggledSlot(self, checked):
        """
        Slot for when the custom symbol radio button is toggled.

        :param checked: either the button is checked or not
        """

        if checked:
            self.uiCustomSymbolGroupBox.setEnabled(True)
            self.uiCustomSymbolGroupBox.show()
            self.uiBuiltInGroupBox.setEnabled(False)
            self.uiBuiltInGroupBox.hide()
            self.adjustSize()

    def _builtInSymbolToggledSlot(self, checked):
        """
        Slot for when the built-in symbol radio button is toggled.

        :param checked: either the button is checked or not
        """

        if checked:
            self.uiCustomSymbolGroupBox.setEnabled(False)
            self.uiCustomSymbolGroupBox.hide()
            self.uiBuiltInGroupBox.setEnabled(True)
            self.uiBuiltInGroupBox.show()
            self.adjustSize()

    def _applyPreferencesSlot(self):
        """
        Applies the selected symbol to the items.
        """

        if self.uiSymbolListWidget.isEnabled():
            current = self.uiSymbolListWidget.currentItem()
            if current:
                name = current.text()
                path = ":/symbols/{}.svg".format(name)
                renderer = QtSvg.QSvgRenderer(path)
                renderer.setObjectName(path)
                for item in self._items:
                    if isinstance(item, SvgNodeItem):
                        item.setSharedRenderer(renderer)
                    else:
                        pixmap = QtGui.QPixmap(path)
                        if not pixmap.isNull():
                            item.setPixmap(pixmap)
                            item.setPixmapSymbolPath(path)
                        else:
                            QtWidgets.QMessageBox.critical(self, "Built-in SVG symbol", "Built-in SVG symbol cannot be applied on Pixmap node item")
                            return False
        else:
            symbol_path = self.uiSymbolLineEdit.text()
            pixmap = QtGui.QPixmap(symbol_path)
            if not pixmap.isNull():
                for item in self._items:
                    if isinstance(item, PixmapNodeItem):
                        item.setPixmap(pixmap)
                        item.setPixmapSymbolPath(symbol_path)
                    else:
                        renderer = QtSvg.QSvgRenderer(symbol_path)
                        renderer.setObjectName(symbol_path)
                        if renderer.isValid():
                            item.setSharedRenderer(renderer)
                        else:
                            QtWidgets.QMessageBox.critical(self, "Custom pixmap symbol", "Custom pixmap symbol which is not SVG format cannot be applied on SVG node item")
                            return False
        return True

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
        file_formats = "Image files (*.svg *.bmp *.jpeg *.jpg *.pbm *.pgm *.png *.ppm *.xbm *.xpm);;All files (*.*)"
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Image", self._symbols_dir, file_formats)
        if not path:
            return

        self._symbols_dir = os.path.dirname(path)
        self.uiSymbolLineEdit.clear()
        self.uiSymbolLineEdit.setText(path)
        self.uiSymbolLineEdit.setToolTip('<img src="{}"/>'.format(path))

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        if result:
            if not self.uiSymbolListWidget.isEnabled() and not os.path.exists(self.uiSymbolLineEdit.text()):
                QtWidgets.QMessageBox.critical(self, "Custom symbol", "Invalid path to custom symbol: {}".format(self.uiSymbolLineEdit.text()))
                result = 0
            elif result and self._items and not self._applyPreferencesSlot():
                result = 0
        super().done(result)
