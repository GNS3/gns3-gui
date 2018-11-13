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
Nodes view that list all the available nodes to be dragged and dropped
on the QGraphics scene.
"""

import tempfile
import json
import sip

from .qt import QtCore, QtGui, QtWidgets, qpartial
from .modules import MODULES
from .controller import Controller
from .appliance_manager import ApplianceManager
from .dialogs.configuration_dialog import ConfigurationDialog

import logging
log = logging.getLogger(__name__)


CATEGORY_TO_ID = {
    "firewall": 3,
    "guest": 2,
    "switch": 1,
    "multilayer_switch": 1,
    "router": 0
}


class NodesView(QtWidgets.QTreeWidget):

    """
    Nodes view to list the nodes.

    :param parent: parent widget
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self._current_category = None
        self._current_search = ""

        # enables the possibility to drag items.
        self.setDragEnabled(True)
        ApplianceManager.instance().appliances_changed_signal.connect(self.refresh)

    def setCurrentSearch(self, search):
        self._current_search = search

    def refresh(self):

        self.clear()
        self.populateNodesView(self._current_category, self._current_search)

    def populateNodesView(self, category, search):
        """
        Populates the nodes view with the device list of the specified
        category (None = all devices).

        :param category: category of device to list
        :param search: filter
        """

        if not Controller.instance().connected():
            log.debug("Could not retrieve templates because there is no connection to the controller")
            return

        self.setIconSize(QtCore.QSize(32, 32))
        self._current_category = category
        self._current_search = search

        display_appliances = set()
        for appliance in ApplianceManager.instance().appliances().values():
            if category is not None and category != appliance.category():
                continue
            if search != "" and search.lower() not in appliance.name().lower():
                continue

            display_appliances.add(appliance.name())
            item = QtWidgets.QTreeWidgetItem(self)
            item.setText(0, appliance.name())
            item.setData(0, QtCore.Qt.UserRole, appliance.id())
            item.setData(1, QtCore.Qt.UserRole, "appliance")
            item.setSizeHint(0, QtCore.QSize(32, 32))
            Controller.instance().getSymbolIcon(appliance.symbol(),
                                                qpartial(self._setItemIcon, item),
                                                fallback=":/symbols/{}.svg".format(appliance.category()))

        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def _setItemIcon(self, item, icon):
        if not sip.isdeleted(item):
            item.setIcon(0, icon)

    def _getMainWindow(self):
        from .main_window import MainWindow
        window = self.window()
        # when we're docked in main window
        if isinstance(window, MainWindow):
            return window
        # when we're in docked mode, outside main window
        return self.window().parent()

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

            # retrieve the node class from the item data
            if item.data(1, QtCore.Qt.UserRole) == "appliance_template":
                try:
                    with tempfile.NamedTemporaryFile(mode="w+", suffix=".builtin.gns3a", delete=False) as f:
                        json.dump(item.data(0, QtCore.Qt.UserRole), f)
                    self._getMainWindow().loadPath(f.name)
                except OSError as e:
                    QtWidgets.QMessageBox.critical(self, "Appliance", "Cannot install appliance: {}".format(e))
                return

            icon = item.icon(0)
            mimedata = QtCore.QMimeData()

            if item.data(1, QtCore.Qt.UserRole) == "appliance":
                appliance_id = item.data(0, QtCore.Qt.UserRole)
                mimedata.setData("application/x-gns3-appliance", appliance_id.encode())
            elif item.data(1, QtCore.Qt.UserRole) == "node":
                appliance_id = item.data(0, QtCore.Qt.UserRole)
                mimedata.setData("application/x-gns3-appliance", appliance_id.encode())

            drag = QtGui.QDrag(self)
            drag.setMimeData(mimedata)
            drag.setPixmap(icon.pixmap(self.iconSize()))
            drag.setHotSpot(QtCore.QPoint(drag.pixmap().width(), drag.pixmap().height()))
            drag.exec_(QtCore.Qt.CopyAction)
            event.accept()

    def _showContextualMenu(self):
        item = self.currentItem()
        appliance = ApplianceManager.instance().getAppliance(item.data(0, QtCore.Qt.UserRole))
        if not appliance:
            return

        for module in MODULES:
            if appliance.appliance_type() == "dynamips":
                node_class = module.getNodeClass(appliance.appliance_type(), appliance.settings()["platform"])
            else:
                node_class = module.getNodeClass(appliance.appliance_type())

            if node_class:
                break

        # We cannot edit devices like EthernetSwitch or device without config templates
        if not appliance.builtin() and hasattr(module, "configurationPage"):
            menu = QtWidgets.QMenu()
            configuration = QtWidgets.QAction("Configure Template", menu)
            configuration.setIcon(QtGui.QIcon(":/icons/configuration.svg"))
            configuration.triggered.connect(qpartial(self._configurationSlot, appliance, module))
            menu.addAction(configuration)

            configuration = QtWidgets.QAction("Delete Template", menu)
            configuration.setIcon(QtGui.QIcon(":/icons/delete.svg"))
            configuration.triggered.connect(qpartial(self._deleteSlot, appliance, module))
            menu.addAction(configuration)
            menu.exec_(QtGui.QCursor.pos())

    def _configurationSlot(self, appliance, module, source):

        dialog = ConfigurationDialog(appliance.name(), appliance.settings(), module.configurationPage()(), parent=self)
        dialog.show()
        if dialog.exec_():
            ApplianceManager.instance().updateAppliance(appliance)

    def _deleteSlot(self, appliance, module, source):

        reply = QtWidgets.QMessageBox.question(self, "Template", "Delete {} template?".format(appliance.name()),
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            ApplianceManager.instance().deleteAppliance(appliance.id())
