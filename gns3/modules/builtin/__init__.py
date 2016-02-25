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
Built-in module implementation.
"""

from gns3.qt import QtWidgets
from ..module import Module
from .cloud import Cloud
from .host import Host


import logging
log = logging.getLogger(__name__)


class Builtin(Module):

    """
    Built-in module.
    """

    def __init__(self):
        super().__init__()

        self._nodes = []

    def configChangedSlot(self):
        pass

    def addNode(self, node):
        """
        Adds a node to this module.

        :param node: Node instance
        """

        self._nodes.append(node)

    def removeNode(self, node):
        """
        Removes a node from this module.

        :param node: Node instance
        """

        if node in self._nodes:
            self._nodes.remove(node)

    def reset(self):
        """
        Resets the module.
        """

        log.info("Built-in module reset")
        self._nodes.clear()

    def createNode(self, node_class, server, project):
        """
        Creates a new node.

        :param node_class: Node object
        :param server: HTTPClient instance
        :param project: Project instance
        """

        log.info("creating node {}".format(node_class))

        # create an instance of the node class
        return node_class(self, server, project)

    def setupNode(self, node, node_name):
        """
        Setups a node.

        :param node: Node instance
        :param node_name: Node name
        """

        log.info("configuring node {}".format(node))
        node.setup()

    @staticmethod
    def findAlternativeInterface(node, missing_interface):

        from gns3.main_window import MainWindow
        mainwindow = MainWindow.instance()

        available_interfaces = []
        for interface in node.settings()["interfaces"]:
            available_interfaces.append(interface["name"])

        if available_interfaces:
            selection, ok = QtWidgets.QInputDialog.getItem(mainwindow,
                                                           "Cloud interfaces", "Interface {} could not be found\nPlease select an alternative from your existing interfaces:".format(missing_interface),
                                                           available_interfaces, 0, False)
            if ok:
                return selection
            QtWidgets.QMessageBox.warning(mainwindow, "Cloud interface", "No alternative interface chosen to replace {} on this host, this may lead to issues".format(missing_interface))
            return None
        else:
            QtWidgets.QMessageBox.critical(mainwindow, "Cloud interface", "Could not find interface {} on this host".format(missing_interface))
            return missing_interface

    @staticmethod
    def getNodeClass(name):
        """
        Returns the object with the corresponding name.

        :param name: object name
        """

        if name in globals():
            return globals()[name]
        return None

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [Cloud, Host]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        nodes = []
        for node_class in Builtin.classes():
            nodes.append(
                {"class": node_class.__name__,
                 "name": node_class.symbolName(),
                 "categories": node_class.categories(),
                 "symbol": node_class.defaultSymbol(),
                 "builtin": True}
            )
        return nodes

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        return []

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of built-in module.

        :returns: instance of Builtin
        """

        if not hasattr(Builtin, "_instance"):
            Builtin._instance = Builtin()
        return Builtin._instance
