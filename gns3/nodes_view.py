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
Nodes view that list all the available nodes to be dragged and dropped on the QGraphics scene.
"""

import pickle
import sip

from .qt import QtCore, QtGui, QtWidgets, qpartial
from .modules import MODULES
from .node import Node
from .controller import Controller
from .dialogs.configuration_dialog import ConfigurationDialog
from .local_config import LocalConfig


class NodesView(QtWidgets.QTreeWidget):

    """
    Nodes view to list the nodes.

    :param parent: parent widget
    """

    def __init__(self, parent=None):

        super().__init__(parent)
        self._current_category = None

        # enables the possibility to drag items.
        self.setDragEnabled(True)

        Controller.instance().connected_signal.connect(self.refresh)

    def refresh(self):
        self.clear()
        self.populateNodesView(self._current_category)

    def populateNodesView(self, category):
        """
        Populates the nodes view with the device list of the specified
        category (None = all devices).

        :param category: category of device to list
        """

        if not Controller.instance().connected():
            return
        self.setIconSize(QtCore.QSize(32, 32))
        self._current_category = category
        for module in MODULES:
            for node in module.instance().nodes():
                if category is not None and category not in node["categories"]:
                    continue
                item = QtWidgets.QTreeWidgetItem(self)
                item.setText(0, node["name"])
                item.setData(0, QtCore.Qt.UserRole, node)
                item.setSizeHint(0, QtCore.QSize(32, 32))
                Controller.instance().getSymbolIcon(node["symbol"], qpartial(self._setItemIcon, item))

        if not self.topLevelItemCount() and category == Node.routers:
            QtWidgets.QMessageBox.warning(self, 'Routers', 'No routers have been configured.<br>You must provide your own router images in order to use GNS3.<br><br><a href="https://gns3.com/support/docs">Show documentation</a>')

        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def _setItemIcon(self, item, icon):
        if not sip.isdeleted(item):
            item.setIcon(0, icon)

    def mousePressEvent(self, event):
        """
        Handles all mouse press events.

        :param: QMouseEvent instance
        """

        # Check that an item has been selected and right click
        if self.currentItem() is not None and event.button() == QtCore.Qt.RightButton:
            self._showContextualMenu()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Handles all mouse move events.
        This is the starting point to drag & drop a node on the scene.

        :param: QMouseEvent instance
        """

        # Check that an item has been selected and left button clicked
        if self.currentItem() is not None and event.buttons() == QtCore.Qt.LeftButton:
            item = self.currentItem()
            icon = item.icon(0)

            # retrieve the node class from the item data
            node = item.data(0, QtCore.Qt.UserRole)
            mimedata = QtCore.QMimeData()

            # pickle the node class, set the Mime type and data
            # and start dragging the item.
            data = pickle.dumps(node)
            mimedata.setData("application/x-gns3-node", data)
            drag = QtGui.QDrag(self)
            drag.setMimeData(mimedata)
            drag.setPixmap(icon.pixmap(self.iconSize()))
            drag.setHotSpot(QtCore.QPoint(drag.pixmap().width(), drag.pixmap().height()))
            drag.exec_(QtCore.Qt.CopyAction)
            event.accept()

    def _showContextualMenu(self):
        item = self.currentItem()
        node = item.data(0, QtCore.Qt.UserRole)
        for module in MODULES:
            node_class = module.getNodeClass(node["class"])
            if node_class:
                break

        # We can not edit stuff like EthernetSwitch
        # or without config template like VPCS
        if "builtin" not in node and hasattr(module, "vmConfigurationPage"):
            for vm_key, vm in module.instance().VMs().items():
                if vm["name"] == node["name"]:
                    break
            if vm is None:
                return
            menu = QtWidgets.QMenu()
            configuration = QtWidgets.QAction("Configure Template", menu)
            configuration.setIcon(QtGui.QIcon(":/icons/configuration.svg"))
            configuration.triggered.connect(qpartial(self._configurationSlot, vm, module))
            menu.addAction(configuration)

            configuration = QtWidgets.QAction("Delete Template", menu)
            configuration.setIcon(QtGui.QIcon(":/icons/delete.svg"))
            configuration.triggered.connect(qpartial(self._deleteSlot, vm_key, vm, module))
            menu.addAction(configuration)

            menu.exec_(QtGui.QCursor.pos())

    def _configurationSlot(self, vm, module, source):

        dialog = ConfigurationDialog(vm["name"], vm, module.vmConfigurationPage()(), parent=self)
        dialog.show()
        if dialog.exec_():
            module.instance().setVMs(module.instance().VMs())
            LocalConfig.instance().writeConfig()
            self.refresh()

    def _deleteSlot(self, vm_key, vm, module, source):

        reply = QtWidgets.QMessageBox.question(self, "Template", "Delete {} template?".format(vm["name"]),
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            vms = module.instance().VMs()
            vms.pop(vm_key)
            module.instance().setVMs(vms)
            LocalConfig.instance().writeConfig()
            self.refresh()
