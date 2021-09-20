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

from .qt import sip

from .qt import QtCore, QtGui, QtWidgets, qpartial
from .controller import Controller
from .template_manager import TemplateManager
from .dialogs.configuration_dialog import ConfigurationDialog
from .utils.get_icon import get_icon

from gns3.modules.builtin import Builtin
from gns3.modules.dynamips import Dynamips
from gns3.modules.iou import IOU
from gns3.modules.vpcs import VPCS
from gns3.modules.traceng import TraceNG
from gns3.modules.virtualbox import VirtualBox
from gns3.modules.qemu import Qemu
from gns3.modules.vmware import VMware
from gns3.modules.docker import Docker


import logging
log = logging.getLogger(__name__)


CATEGORY_TO_ID = {
    "firewall": 3,
    "guest": 2,
    "switch": 1,
    "multilayer_switch": 1,
    "router": 0
}

TEMPLATE_TYPE_TO_CONFIGURATION_PAGE = {
    "ethernet_switch": Builtin.configurationPage("ethernet_switch"),
    "ethernet_hub": Builtin.configurationPage("ethernet_hub"),
    "cloud": Builtin.configurationPage("cloud"),
    "dynamips": Dynamips.configurationPage(),
    "iou": IOU.configurationPage(),
    "vpcs": VPCS.configurationPage(),
    "traceng": TraceNG.configurationPage(),
    "virtualbox": VirtualBox.configurationPage(),
    "qemu": Qemu.configurationPage(),
    "vmware": VMware.configurationPage(),
    "docker": Docker.configurationPage()
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
        TemplateManager.instance().templates_changed_signal.connect(self.refresh)

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

        display_templates = set()
        for template in TemplateManager.instance().templates().values():
            if category is not None and category != template.category():
                continue
            if search != "" and search.lower() not in template.name().lower():
                continue

            display_templates.add(template.name())
            item = QtWidgets.QTreeWidgetItem(self)
            item.setText(0, template.name())
            item.setData(0, QtCore.Qt.UserRole, template.id())
            item.setData(1, QtCore.Qt.UserRole, "template")
            item.setSizeHint(0, QtCore.QSize(32, 32))
            Controller.instance().getSymbolIcon(template.symbol(),
                                                qpartial(self._setItemIcon, item),
                                                fallback=":/symbols/{}.svg".format(template.category()))

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

    def contextMenuEvent(self, event):
        """
        Handles all context menu events.

        :param event: QContextMenuEvent instance
        """

        self._showContextualMenu(event.globalPos())

    def mouseDoubleClickEvent(self, event):
        """
        Handles all mouse double click events.

        :param event: QMouseEvent instance
        """

        item = self.itemAt(event.pos())
        if item:
            template = TemplateManager.instance().getTemplate(item.data(0, QtCore.Qt.UserRole))
            if template:
                configuration_page = TEMPLATE_TYPE_TO_CONFIGURATION_PAGE.get(template.template_type())
                if not template.builtin() and configuration_page:
                    self._configurationSlot(template, configuration_page)
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        """
        Handles all mouse move events.
        This is the starting point to drag & drop a template on the scene.

        :param: QMouseEvent instance
        """

        # Check that an item has been selected and left button clicked
        if self.currentItem() is not None and event.buttons() == QtCore.Qt.LeftButton:
            item = self.currentItem()
            icon = item.icon(0)
            mimedata = QtCore.QMimeData()

            assert item.data(1, QtCore.Qt.UserRole) == "template"
            template_id = item.data(0, QtCore.Qt.UserRole)

            mimedata.setData("application/x-gns3-template", template_id.encode())
            drag = QtGui.QDrag(self)
            drag.setMimeData(mimedata)
            drag.setPixmap(icon.pixmap(self.iconSize()))
            drag.setHotSpot(QtCore.QPoint(drag.pixmap().width(), drag.pixmap().height()))
            drag.exec_(QtCore.Qt.CopyAction)
            event.accept()

    def _showContextualMenu(self, pos):

        menu = QtWidgets.QMenu()
        refresh_action = QtWidgets.QAction("Refresh templates", menu)
        refresh_action.setIcon(get_icon("reload.svg"))
        refresh_action.triggered.connect(self.refresh)
        menu.addAction(refresh_action)

        item = self.currentItem()
        if item:
            template = TemplateManager.instance().getTemplate(item.data(0, QtCore.Qt.UserRole))
            if not template:
                return

            configuration_page = TEMPLATE_TYPE_TO_CONFIGURATION_PAGE.get(template.template_type())
            if not template.builtin() and configuration_page:
                configure_action = QtWidgets.QAction("Configure template", menu)
                configure_action.setIcon(get_icon("configuration.svg"))
                configure_action.triggered.connect(qpartial(self._configurationSlot, template, configuration_page))
                menu.addAction(configure_action)

                delete_action = QtWidgets.QAction("Delete template", menu)
                delete_action.setIcon(get_icon("delete.svg"))
                delete_action.triggered.connect(qpartial(self._deleteSlot, template))
                menu.addAction(delete_action)

        menu.exec_(pos)

    def _configurationSlot(self, template, configuration_page, source=None):

        dialog = ConfigurationDialog(template.name(), template.settings(), configuration_page(), parent=self)
        dialog.show()
        if dialog.exec_():
            TemplateManager.instance().updateTemplate(template)

    def _deleteSlot(self, template, source=None):

        reply = QtWidgets.QMessageBox.question(self, "Template", "Delete {} template?".format(template.name()),
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            TemplateManager.instance().deleteTemplate(template.id())
