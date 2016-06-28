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
import pathlib

from ..qt import QtCore, QtGui, QtWidgets, qpartial
from ..qt.qimage_svg_renderer import QImageSvgRenderer
from ..ui.symbol_selection_dialog_ui import Ui_SymbolSelectionDialog
from ..local_server import LocalServer
from ..controller import Controller
from ..symbol import Symbol


import logging
log = logging.getLogger(__name__)


class SymbolSelectionDialog(QtWidgets.QDialog, Ui_SymbolSelectionDialog):

    """
    Symbol selection dialog.

    :param parent: parent widget
    :param items: list of items
    """

    _symbols_dir = None

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
        if not SymbolSelectionDialog._symbols_dir:
            SymbolSelectionDialog._symbols_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.PicturesLocation)

        if not self._items:
            self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).hide()

        self.uiBuiltInSymbolRadioButton.setChecked(True)
        self.uiSymbolListWidget.setFocus()
        self.uiSymbolListWidget.setIconSize(QtCore.QSize(64, 64))
        self._symbol_items = []

        Controller.instance().get("/symbols", self._listSymbolsCallback)

    def _listSymbolsCallback(self, result, error=False, **kwargs):
        if error:
            log.error("Error while listing symbols: {}".format(result["message"]))
            return

        self._symbol_items = []
        for symbol in result:
            symbol = Symbol(**symbol)
            name = os.path.splitext(symbol.filename())[0]
            item = QtWidgets.QListWidgetItem(self.uiSymbolListWidget)
            item.setData(QtCore.Qt.UserRole, symbol)
            self._symbol_items.append(item)
            item.setText(name)

            image = QtGui.QImage(64, 64, QtGui.QImage.Format_ARGB32)
            # Set the ARGB to 0 to prevent rendering artifacts
            image.fill(0x00000000)
            icon = QtGui.QIcon(QtGui.QPixmap.fromImage(image))
            item.setIcon(icon)

            def render(item, path):
                svg_renderer = QImageSvgRenderer(path)
                image = QtGui.QImage(64, 64, QtGui.QImage.Format_ARGB32)
                # Set the ARGB to 0 to prevent rendering artifacts
                image.fill(0x00000000)
                svg_renderer.render(QtGui.QPainter(image))
                icon = QtGui.QIcon(QtGui.QPixmap.fromImage(image))
                item.setIcon(icon)

            Controller.instance().getStatic(symbol.url(), qpartial(render, item))
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
            if self.uiBuiltinSymbolOnlyCheckBox.isChecked() and not item.data(QtCore.Qt.UserRole).builtin():
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
        for item in self._items:
            item.setSymbol(symbol_path)
        return True

    def getSymbol(self):

        if self.uiSymbolListWidget.isEnabled():
            current = self.uiSymbolListWidget.currentItem()
            if current:
                return current.data(QtCore.Qt.UserRole).id()
        else:
            return os.path.basename(self.uiSymbolLineEdit.text())
        return None

    def _symbolBrowserSlot(self):

        # supported image file formats
        file_formats = "Image files (*.svg *.bmp *.jpeg *.jpg *.pbm *.pgm *.png *.ppm *.xbm *.xpm *.gif);;All files (*.*)"
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Image", SymbolSelectionDialog._symbols_dir, file_formats)
        if not path:
            return
        SymbolSelectionDialog._symbols_dir = os.path.dirname(path)

        symbol_id = os.path.basename(path)
        Controller.instance().post("/symbols/" + symbol_id + "/raw", qpartial(self._finishSymbolUpload, path), body=pathlib.Path(path), progressText="Uploading {}".format(symbol_id), timeout=None)

    def _finishSymbolUpload(self, path, result, error=False, **kwargs):
        if error:
            log.error("Error while uploading symbol: {}".format(path))
            return
        self.uiSymbolLineEdit.clear()
        self.uiSymbolLineEdit.setText(path)
        self.uiSymbolLineEdit.setToolTip('<img src="{}"/>'.format(path))

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        if result and self._items and not self._applyPreferencesSlot():
            result = 0
        super().done(result)



