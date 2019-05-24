# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 GNS3 Technologies Inc.
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
Custom adapters configuration.
"""

import textwrap
import re

from ..qt import QtCore, QtWidgets
from ..ui.custom_adapters_configuration_dialog_ui import Ui_CustomAdaptersConfigurationDialog


class NoEditDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        QtWidgets.QStyledItemDelegate.__init__(self, parent=parent)

    def createEditor(self, parent, option, index):
        return None


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):

    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        key1 = self.text(column)
        key2 = other.text(column)
        return self.natural_sort_key(key1) < self.natural_sort_key(key2)

    @staticmethod
    def natural_sort_key(key):
        regex = r'(\d*\.\d+|\d+)'
        parts = re.split(regex, key)
        return tuple((e if i % 2 == 0 else float(e)) for i, e in enumerate(parts))


class CustomAdaptersConfigurationDialog(QtWidgets.QDialog, Ui_CustomAdaptersConfigurationDialog):
    """
    Custom adapters configuration dialog.

    :param parent: parent widget
    """

    def __init__(self, ports, custom_adapters, default_adapter_type=None, adapter_types=None, base_mac_address=None, parent=None):

        super().__init__(parent)
        self.setupUi(self)
        self._ports = ports
        self._default_adapter_type = default_adapter_type
        self._adapter_types = adapter_types
        self._custom_adapters = custom_adapters
        self._base_mac_address = base_mac_address

        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Reset).clicked.connect(self._resetSlot)

        if self._default_adapter_type and self._adapter_types:
            self.uiAdaptersTreeWidget.setColumnCount(3)
            self.uiAdaptersTreeWidget.headerItem().setText(2, "Adapter type")

        if self._base_mac_address:
            self.uiAdaptersTreeWidget.setColumnCount(4)
            self.uiAdaptersTreeWidget.headerItem().setText(3, "MAC address")

        self._populateWidgets()

        # resize to fit the tree widget
        width = 0
        for column in range(self.uiAdaptersTreeWidget.columnCount()):
            width += 20 + self.uiAdaptersTreeWidget.columnWidth(column)
        self.resize(QtCore.QSize(width, self.height()))

    def _getCustomAdapterSettings(self, adapter_number):

        for custom_adapter in self._custom_adapters:
            if custom_adapter["adapter_number"] == adapter_number:
                return custom_adapter
        return {}

    def _MacToInteger(self, mac_address):
        """
        Convert a macaddress with the format 00:0c:29:11:b0:0a to a int

        :param mac_address: The mac address

        :returns: Integer
        """

        return int(mac_address.replace(":", ""), 16)

    def _IntegerToMac(self, integer):
        """
        Convert an integer to a mac address
        """

        return ":".join(textwrap.wrap("%012x" % (integer), width=2))

    def _populateWidgets(self):

        adapter_number = 0
        for port_name in self._ports:
            item = TreeWidgetItem(self.uiAdaptersTreeWidget)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            item.setText(0, "Adapter {}".format(adapter_number))
            item.setData(0, QtCore.Qt.UserRole, adapter_number)
            item.setData(1, QtCore.Qt.UserRole, port_name)
            custom_adapter = self._getCustomAdapterSettings(adapter_number)
            item.setText(1, custom_adapter.get("port_name", port_name))

            if self._default_adapter_type and self._adapter_types:
                combobox = QtWidgets.QComboBox(self)
                if type(self._adapter_types) == list:
                    for adapter_type in self._adapter_types:
                        combobox.addItem("{}".format(adapter_type))
                else:
                    index = 0
                    for adapter_type, adapter_description in self._adapter_types.items():
                        combobox.addItem("{}".format(adapter_type))
                        combobox.setItemData(index, adapter_description, QtCore.Qt.ToolTipRole)
                        index += 1
                adapter_type_index = combobox.findText(custom_adapter.get("adapter_type", self._default_adapter_type))
                combobox.setCurrentIndex(adapter_type_index)
                self.uiAdaptersTreeWidget.setItemWidget(item, 2, combobox)

            if self._base_mac_address:
                self.uiAdaptersTreeWidget.addTopLevelItem(item)
                line_edit = QtWidgets.QLineEdit(self)
                line_edit.setInputMask("HH:HH:HH:HH:HH:HH;_")
                mac_address = self._IntegerToMac(self._MacToInteger(self._base_mac_address) + adapter_number)
                line_edit.setText(custom_adapter.get("mac_address", mac_address))
                self.uiAdaptersTreeWidget.setItemWidget(item, 3, line_edit)
            adapter_number += 1

        self.uiAdaptersTreeWidget.setItemDelegateForColumn(0, NoEditDelegate(self))
        self.uiAdaptersTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.uiAdaptersTreeWidget.setSortingEnabled(True)

        for column in range(self.uiAdaptersTreeWidget.columnCount()):
            self.uiAdaptersTreeWidget.resizeColumnToContents(column)

    def _resetSlot(self):

        self.uiAdaptersTreeWidget.clear()
        self._custom_adapters.clear()
        self._populateWidgets()

    def _updateCustomAdapters(self):

        self._custom_adapters.clear()
        for row in range(self.uiAdaptersTreeWidget.topLevelItemCount()):
            custom_adapter_settings = {}
            item = self.uiAdaptersTreeWidget.topLevelItem(row)
            port_name = item.text(1)
            adapter_number = item.data(0, QtCore.Qt.UserRole)
            custom_adapter_settings["adapter_number"] = adapter_number
            original_port_name = item.data(1, QtCore.Qt.UserRole)
            if original_port_name != port_name:
                custom_adapter_settings["port_name"] = port_name
            if self._default_adapter_type and self._adapter_types:
                adapter_type = self.uiAdaptersTreeWidget.itemWidget(item, 2).currentText()
                if self._default_adapter_type != adapter_type:
                    custom_adapter_settings["adapter_type"] = adapter_type
            if self._base_mac_address:
                mac_address = self.uiAdaptersTreeWidget.itemWidget(item, 3).text()
                if mac_address and mac_address != ":::::":
                    if not re.search(r"""^([0-9a-fA-F]{2}[:]){5}[0-9a-fA-F]{2}$""", mac_address):
                        QtWidgets.QMessageBox.critical(self, "MAC address", "Invalid MAC address (format required: hh:hh:hh:hh:hh:hh)")
                        return
                    default_mac_address = self._IntegerToMac(self._MacToInteger(self._base_mac_address) + adapter_number)
                    if mac_address != default_mac_address:
                        custom_adapter_settings["mac_address"] = mac_address
            if len(custom_adapter_settings) > 1:
                # only save if there is more than the adapter_number key
                self._custom_adapters.append(custom_adapter_settings.copy())

    def done(self, result):
        """
        Called when the dialog is closed.

        :param result: boolean (accepted or rejected)
        """

        if result:
            self._updateCustomAdapters()
        super().done(result)
