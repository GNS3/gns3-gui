# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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

from gns3.qt import QtGui, QtCore, QtWidgets


class EthernetInterfacesListWidget(QtWidgets.QListWidget):

    """
    Lists Ethernet interfaces and allows to filter them.

    :param parent: parent widget
    """

    def __init__(self, parent):

        super().__init__(parent)
        self._show_virtualization_interfaces = True

    def refresh(self):

        if self._show_virtualization_interfaces:
            self._showVirtInterfacesSlot()
        else:
            self._hideVirtInterfacesSlot()

    def _isVirtualizationInterface(self, interface):

        for virtualization_interface in ("vmnet", "vboxnet", "docker", "lxcbr", "virbr", "ovs-system"):
            if interface.lower().startswith(virtualization_interface):
                return True
        return False

    def _showContextualMenu(self):

        menu = QtWidgets.QMenu()

        if self._show_virtualization_interfaces:
            hide_virt_interfaces = QtWidgets.QAction("Hide virtualization interfaces", menu)
            hide_virt_interfaces.setIcon(QtGui.QIcon(":/icons/minus.svg"))
            hide_virt_interfaces.triggered.connect(self._hideVirtInterfacesSlot)
            menu.addAction(hide_virt_interfaces)
        else:
            show_virt_interfaces = QtWidgets.QAction("Show virtualization interfaces", menu)
            show_virt_interfaces.setIcon(QtGui.QIcon(":/icons/plus.svg"))
            show_virt_interfaces.triggered.connect(self._showVirtInterfacesSlot)
            menu.addAction(show_virt_interfaces)

        menu.exec_(QtGui.QCursor.pos())

    def _showVirtInterfacesSlot(self):

        self._show_virtualization_interfaces = True
        for index in range(0, self.count()):
            item = self.item(index)
            interface = item.text()
            if self._isVirtualizationInterface(interface):
                self.setRowHidden(index, False)

    def _hideVirtInterfacesSlot(self):

        self._show_virtualization_interfaces = False
        for index in range(0, self.count()):
            item = self.item(index)
            interface = item.text()
            if self._isVirtualizationInterface(interface):
                self.setRowHidden(index, True)

    def mousePressEvent(self, event):
        """
        Handles all mouse press events.

        :param event: QMouseEvent instance
        """

        if event.button() == QtCore.Qt.RightButton:
            self._showContextualMenu()
        else:
            super().mousePressEvent(event)
