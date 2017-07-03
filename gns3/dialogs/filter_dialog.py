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

    def _listAvailableFiltersCallback(self, result, error=False, *args, **kwargs):
        if error:
            QtWidgets.QMessageBox.warning(None, "Link", "Error while list informations about the link: {}".format(result["message"]))
            return
        self._filters = result
        self._initialized = True
        self._updateUiSlot()

    @qslot
    def _updateUiSlot(self, *args):
        # self.uiFiltersTextEdit.setPlainText(json.dumps(self._link.filters()))

        # Empty the main layout
        while True:
            item = self.uiVerticalLayout.takeAt(0)
            if item is None:
                break
            elif item.widget():
                item.widget().deleteLater()

        if len(self._filters):
            self.uiNotSupportedLabel.hide()
        else:
            self.uiNotSupportedLabel.show()

        for filter in self._filters:
            groupBox = QtWidgets.QGroupBox(self)
            groupBox.setTitle(filter["name"])

            vlayout = QtWidgets.QVBoxLayout(groupBox)
            description = QtWidgets.QLabel(groupBox)
            description.setText(filter["description"])
            description.setWordWrap(True)
            vlayout.addWidget(description)

            gridLayout = QtWidgets.QGridLayout()
            line = 0
            filter["spinBoxes"] = []
            nb_spin = 0
            for param in filter["parameters"]:
                label = QtWidgets.QLabel()
                label.setText(param["name"] + ":")
                gridLayout.addWidget(label, line, 0, 1, 1)

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
                    spinBox.setValue(self._link.filters()[filter["type"]][nb_spin])
                except(KeyError, IndexError):
                    pass
                nb_spin += 1

                gridLayout.addWidget(spinBox, line, 1, 1, 1)

                unit = QtWidgets.QLabel()
                unit.setText(param["unit"])
                gridLayout.addWidget(unit, line, 2, 1, 1)

                line += 1

            vlayout.addLayout(gridLayout)
            self.uiVerticalLayout.addWidget(groupBox)

    @qslot
    def _applyPreferencesSlot(self, *args):
        new_filters = {}
        for filter in self._filters:
            new_filters[filter["type"]] = []
            for spinBox in filter["spinBoxes"]:
                new_filters[filter["type"]].append(spinBox.value())
        self._link.setFilters(new_filters)
        self._link.update()

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """
        if result and self._initialized:
            self._applyPreferencesSlot()
        super().done(result)
