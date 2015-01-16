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
from .qt import QtCore, QtGui, QtSvg
from .modules import MODULES


class NodesView(QtGui.QTreeWidget):
    """
    Nodes view to list the nodes.

    :param parent: parent widget
    """

    def __init__(self, parent=None):

        QtGui.QTreeWidget.__init__(self, parent)

        # enables the possibility to drag items.
        self.setDragEnabled(True)

    def populateNodesView(self, category, project_type):
        """
        Populates the nodes view with the device list of the specified
        category (None = all devices).

        :param category: category of device to list
        :param project_type: Filter devices for this type of project (cloud|local)
        """

        for module in MODULES:
            for node in module.instance().nodes():
                if category is not None and category not in node["categories"]:
                    continue
                server_type = node.get("server", None)
                if server_type is not None and server_type == "cloud" and server_type != project_type:
                    continue
                item = QtGui.QTreeWidgetItem(self)
                item.setText(0, node["name"])
                item.setData(0, QtCore.Qt.UserRole, node)
                svg_renderer = QtSvg.QSvgRenderer(node["default_symbol"])
                image = QtGui.QImage(32, 32, QtGui.QImage.Format_ARGB32)
                # Set the ARGB to 0 to prevent rendering artifacts
                image.fill(0x00000000)
                svg_renderer.render(QtGui.QPainter(image))
                icon = QtGui.QIcon(QtGui.QPixmap.fromImage(image))
                item.setIcon(0, icon)

        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def mouseMoveEvent(self, event):
        """
        Handles all mouse move events.
        This is the starting point to drag & drop a node on the scene.

        :param: QMouseEvent instance
        """

        # check the left button isn't used and that an item has been selected.
        if event.buttons() != QtCore.Qt.LeftButton or self.currentItem() == None:
            return

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
