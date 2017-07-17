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

from ..qt import QtWidgets, qslot
from ..ui.filter_dialog_ui import Ui_FilterDialog


class FilterDialog(QtWidgets.QDialog, Ui_FilterDialog):

    """
    Filter dialog.
    """

    def __init__(self, parent, link):

        super().__init__(parent)
        self.setupUi(self)
        self._link = link
        self._link.updated_link_signal.connect(self._updateUiSlot)
        self._link.listAvailableFilters(self._listAvailableFiltersCallback)
        self._initialized = False
        self._filter_items = {}
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self._applyPreferencesSlot)
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Help).clicked.connect(self._helpSlot)

    def _listAvailableFiltersCallback(self, result, error=False, *args, **kwargs):
        if error:
            QtWidgets.QMessageBox.warning(None, "Link", "Error while listing information about the link: {}".format(result["message"]))
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
        self._tabWidget.setMinimumWidth(550)

        for i, filter in enumerate(self._filters):
            tab = QtWidgets.QWidget()
            self._tabWidget.addTab(tab, filter['name'])
            self._tabWidget.setTabToolTip(i, filter['description'])
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

                    spinBox.valueChanged[str].connect(self._onAnyChange)

                    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                    sizePolicy.setHorizontalStretch(0)
                    sizePolicy.setVerticalStretch(0)
                    sizePolicy.setHeightForWidth(spinBox.sizePolicy().hasHeightForWidth())
                    spinBox.setSizePolicy(sizePolicy)
                    try:
                        spinBox.setValue(self._link.filters()[filter["type"]][nb_spin])
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
                    textEdit.textChanged.connect(self._onAnyChange)
                    try:
                        textEdit.setPlainText(self._link.filters()[filter["type"]][0])
                    except(KeyError, IndexError):
                        pass
                    gridLayout.addWidget(textEdit, line, 1, 1, 1)

                line += 1

            vlayout.addLayout(gridLayout)
            tab.setLayout(vlayout)

        self.uiVerticalLayout.addWidget(self._tabWidget)
        self.adjustSize()

    def _onAnyChange(self):
        # when filter's value is not empty we add "+" to name of the tab
        for i, filter in enumerate(self._filters):
            not_empty = []
            if 'spinBoxes' in filter.keys():
                not_empty.extend([b for b in filter['spinBoxes'] if b.value() != 0])

            if 'textEdits' in filter.keys():
                not_empty.extend([e for e in filter['textEdits'] if e.toPlainText() != ''])

            if len(not_empty) > 0:
                text = "{} +".format(filter['name'])
            else:
                text = filter['name']

            self._tabWidget.setTabText(i, text)

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

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """
        if result and self._initialized:
            self._applyPreferencesSlot()
        super().done(result)
