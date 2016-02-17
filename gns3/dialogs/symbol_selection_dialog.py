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

from ..qt import QtCore, QtGui, QtWidgets
from ..qt.qimage_svg_renderer import QImageSvgRenderer
from ..ui.symbol_selection_dialog_ui import Ui_SymbolSelectionDialog
from ..servers import Servers

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
        self.uiSearchLineEdit.textChanged.connect(self._searchTextChangedSlot)
        self.uiBuiltinSymbolOnlyCheckBox.toggled.connect(self._builtinSymbolOnlyToggledSlot)
        self._symbols_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.PicturesLocation)
        self._symbols_path = Servers.instance().localServerSettings()["symbols_path"]

        if not self._items:
            self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).hide()

        self.uiBuiltInSymbolRadioButton.setChecked(True)
        self.uiSymbolListWidget.setFocus()
        self.uiSymbolListWidget.setIconSize(QtCore.QSize(64, 64))
        symbol_resources = QtCore.QResource(":/symbols")
        self._symbol_items = []
        symbols = symbol_resources.children()

        try:
            for file in os.listdir(self._symbols_path):
                symbols.append(file)
        except OSError:
            pass

        symbols.sort()
        for symbol in symbols:
            if symbol.endswith(".svg") or symbol.endswith(".png"):
                name = os.path.splitext(symbol)[0]
                item = QtWidgets.QListWidgetItem(self.uiSymbolListWidget)
                self._symbol_items.append(item)
                item.setText(name)

                image = QtGui.QImage(64, 64, QtGui.QImage.Format_ARGB32)
                # Set the ARGB to 0 to prevent rendering artifacts
                image.fill(0x00000000)

                if os.path.exists(os.path.join(self._symbols_path, symbol)):
                    svg_renderer = QImageSvgRenderer(os.path.join(self._symbols_path, symbol))
                else:
                    resource_path = ":/symbols/" + symbol
                    svg_renderer = QImageSvgRenderer(resource_path)
                svg_renderer.render(QtGui.QPainter(image))

                icon = QtGui.QIcon(QtGui.QPixmap.fromImage(image))
                item.setIcon(icon)

        self.adjustSize()

    def _builtinSymbolOnlyToggledSlot(self, checked):
        self._filter()

    def _searchTextChangedSlot(self, text):
        self._filter()

    def _filter(self):
        """
        Hide element not matching the search
        """
        text = self.uiSearchLineEdit.text()
        for item in self._symbol_items:
            if self.uiBuiltinSymbolOnlyCheckBox.isChecked() and not QtCore.QResource(":/symbols/{}.svg".format(item.text())).isValid():
                item.setHidden(True)
            else:
                if len(text.strip()) == 0 or text.strip().lower() in item.text().lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)

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

        symbol_path = self.getSymbol()

        pixmap = QtGui.QPixmap(symbol_path)
        if not pixmap.isNull():
            for item in self._items:
                renderer = QImageSvgRenderer(symbol_path)
                renderer.setObjectName(symbol_path)
                if renderer.isValid():
                    item.setSharedRenderer(renderer)
                else:
                    QtWidgets.QMessageBox.critical(self, "Custom pixmap symbol", "Invalid image")
                    return False

        return True

    def getSymbol(self):

        if self.uiSymbolListWidget.isEnabled():
            current = self.uiSymbolListWidget.currentItem()
            if current:
                name = current.text()
                if QtCore.QResource(":/symbols/{}.svg".format(name)).isValid():
                    return ":/symbols/{}.svg".format(name)
                else:
                    symbol_path = os.path.join(self._symbols_path, "{}.svg".format(name))
                    if not os.path.exists(symbol_path):
                        symbol_path = os.path.join(self._symbols_path, "{}.png".format(name))
                    return symbol_path
        else:
            return self.uiSymbolLineEdit.text()
        return None

    def _symbolBrowserSlot(self):

        # supported image file formats
        file_formats = "Image files (*.svg *.bmp *.jpeg *.jpg *.pbm *.pgm *.png *.ppm *.xbm *.xpm *.gif);;All files (*.*)"
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
