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

from ..qt import QtCore, QtGui, QtWidgets, qpartial, sip_is_deleted
from ..qt.qimage_svg_renderer import QImageSvgRenderer
from ..ui.symbol_selection_dialog_ui import Ui_SymbolSelectionDialog
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
        if not SymbolSelectionDialog._symbols_dir:
            SymbolSelectionDialog._symbols_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.PicturesLocation)

        if not self._items:
            self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).hide()

        self.uiBuiltInSymbolRadioButton.setChecked(True)
        self.uiSymbolTreeWidget.setFocus()
        self.uiSymbolTreeWidget.setIconSize(QtCore.QSize(64, 64))
        self._symbol_items = []
        self._parents = {}

        Controller.instance().clearStaticCache()  # TODO: use etag to know when to refresh the cache
        Controller.instance().get("/symbols", self._listSymbolsCallback)

    def _listSymbolsCallback(self, result, error=False, **kwargs):
        if error:
            log.error("Error while listing symbols: {}".format(result["message"]))
            return

        self._symbol_items = []
        for symbol in result:
            symbol = Symbol(**symbol)
            theme = symbol.theme()
            if theme not in self._parents:
                parent = QtWidgets.QTreeWidgetItem(self.uiSymbolTreeWidget)
                parent.setText(0, theme)
                font = parent.font(0)
                font.setBold(True)
                parent.setFont(0, font)
                parent.setFlags(parent.flags() & ~QtCore.Qt.ItemIsSelectable)
                self._parents[theme] = parent
            else:
                parent = self._parents[theme]

            name = os.path.splitext(symbol.filename())[0]
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, QtCore.Qt.UserRole, symbol)
            item.setToolTip(0, symbol.id())
            self._symbol_items.append(item)
            item.setText(0, name)

            def render(item, path):
                if sip_is_deleted(item):
                    return
                svg_renderer = QImageSvgRenderer(path)
                image = QtGui.QImage(64, 64, QtGui.QImage.Format_ARGB32)
                # Set the ARGB to 0 to prevent rendering artifacts
                image.fill(0x00000000)
                svg_renderer.render(QtGui.QPainter(image))
                icon = QtGui.QIcon(QtGui.QPixmap.fromImage(image))
                item.setIcon(0, icon)

            Controller.instance().getStatic(symbol.url(), qpartial(render, item))

        for parent in self._parents.values():
            parent.sortChildren(0, QtCore.Qt.AscendingOrder)
        self.adjustSize()

    def _searchTextChangedSlot(self, text):
        self._filter()

    def _filter(self):
        """
        Hide element not matching the search
        """
        text = self.uiSearchLineEdit.text()
        for item in self._symbol_items:
            # if not item.data(0, QtCore.Qt.UserRole).builtin():
            #     item.setHidden(True)
            # else:
            if not text.strip() or text.strip().lower() in item.text(0).lower():
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
        if not symbol_path:
            return False
        for item in self._items:
            item.setSymbol(symbol_path)
        return True

    def getSymbol(self):

        if self.uiSymbolTreeWidget.isEnabled():
            current = self.uiSymbolTreeWidget.currentItem()
            if current and current.parent():
                return current.data(0, QtCore.Qt.UserRole).id()
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
            log.error("Error while uploading symbol: {}: {}".format(path, result.get("message", "unknown")))
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



