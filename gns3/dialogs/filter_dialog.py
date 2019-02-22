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

from ..qt import QtGui, QtWidgets, qslot
from ..ui.filter_dialog_ui import Ui_FilterDialog

import logging
log = logging.getLogger(__name__)


class FilterDialog(QtWidgets.QDialog, Ui_FilterDialog):

    """
    Filter dialog.
    """

    def __init__(self, parent, link):

        super().__init__(parent)
        self.setupUi(self)
        self._link = link
        self._filters = {}
        self._link.updated_link_signal.connect(self._updateUiSlot)
        self._link.listAvailableFilters(self._listAvailableFiltersCallback)
        self._initialized = False
        self._filter_items = {}
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self._applyPreferencesSlot)
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Help).clicked.connect(self._helpSlot)
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Reset).clicked.connect(self._resetSlot)

    def _listAvailableFiltersCallback(self, result, error=False, *args, **kwargs):
        if error:
            log.warning("Error while listing information about the link: {}".format(result["message"]))
            return
        self._filters = result
        self._initialized = True
        self._updateUiSlot()

    @qslot
    def _updateUiSlot(self, *args):

        # Empty the main layout
        while True:
            item = self.uiVerticalLayout.takeAt(0)
            if item is None:
                break
            elif item.widget():
                item.widget().deleteLater()

        if len(self._filters) == 0:
            QtWidgets.QMessageBox.critical(self, "Link", "No filter available for this link. Try with a different node type.")
            self.reject()

        self._tabWidget = QtWidgets.QTabWidget(self)
        for i, filter in enumerate(self._filters):
            tab = QtWidgets.QWidget()
            self._tabWidget.addTab(tab, filter['name'])
            self._tabWidget.setTabToolTip(i, filter['description'])
            self._tabWidget.setTabIcon(i, QtGui.QIcon(':/icons/led_red.svg'))
            vlayout = QtWidgets.QVBoxLayout()

            gridLayout = QtWidgets.QGridLayout()
            line = 0
            filter["spinBoxes"] = []
            filter["textEdits"] = []

            nb_spin = 0

            for param in filter["parameters"]:
                label = QtWidgets.QLabel()
                label.setText(param["name"] + ":")
                gridLayout.addWidget(label, line, 0, 1, 1)

                if param["type"] == "int":
                    spinBox = QtWidgets.QSpinBox()
                    filter["spinBoxes"].append(spinBox)
                    spinBox.setMinimum(param["minimum"])
                    spinBox.setMaximum(param["maximum"])

                    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                    sizePolicy.setHorizontalStretch(0)
                    sizePolicy.setVerticalStretch(0)
                    sizePolicy.setHeightForWidth(spinBox.sizePolicy().hasHeightForWidth())
                    spinBox.setSizePolicy(sizePolicy)
                    try:
                        value = self._link.filters()[filter["type"]][nb_spin]
                        spinBox.setValue(value)
                        if value != 0:
                            self._tabWidget.setTabIcon(i, QtGui.QIcon(':/icons/led_green.svg'))
                    except(KeyError, IndexError):
                        pass
                    nb_spin += 1
                    gridLayout.addWidget(spinBox, line, 1, 1, 1)
                    unit = QtWidgets.QLabel()
                    unit.setText(param["unit"])
                    gridLayout.addWidget(unit, line, 2, 1, 1)
                elif param["type"] == "text":
                    textEdit = QtWidgets.QTextEdit()
                    textEdit.setAcceptRichText(False)
                    filter["textEdits"].append(textEdit)
                    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                    sizePolicy.setHorizontalStretch(0)
                    sizePolicy.setVerticalStretch(0)
                    textEdit.setMinimumWidth(300)
                    textEdit.setSizePolicy(sizePolicy)
                    try:
                        text = self._link.filters()[filter["type"]][0]
                        textEdit.setPlainText(text)
                        if text:
                            self._tabWidget.setTabIcon(i, QtGui.QIcon(':/icons/led_green.svg'))
                    except(KeyError, IndexError):
                        pass
                    gridLayout.addWidget(textEdit, line, 1, 1, 1)

                line += 1

            spacerItem = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            gridLayout.addItem(spacerItem, line, 0, 1, 1)
            vlayout.addLayout(gridLayout)
            tab.setLayout(vlayout)

        self.uiVerticalLayout.addWidget(self._tabWidget)

    @qslot
    def _applyPreferencesSlot(self, *args):
        new_filters = {}
        for filter in self._filters:
            new_filters[filter["type"]] = []
            for spinBox in filter["spinBoxes"]:
                new_filters[filter["type"]].append(spinBox.value())
            for spinBox in filter["textEdits"]:
                new_filters[filter["type"]].append(spinBox.toPlainText())
        self._link.setFilters(new_filters)
        self._link.update()

    @qslot
    def _helpSlot(self, *args):
        help_text = "Filters are applied to packets in both direction.\n\n"

        filter_nb = 0
        for filter in self._filters:
            help_text += "{}: {}".format(filter["name"], filter["description"])
            filter_nb += 1
            if len(self._filters) != filter_nb:
                help_text += "\n\n"

        QtWidgets.QMessageBox.information(self, "Help for filters", help_text)

    @qslot
    def _resetSlot(self, *args):

        filters = {}
        self._link.setFilters(filters)
        self._link.update()

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """
        if result and self._initialized:
            self._applyPreferencesSlot()
        super().done(result)
