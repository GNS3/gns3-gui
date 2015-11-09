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
Dialog to configure and update node settings using widget pages.
"""

from ..qt import QtCore, QtGui, QtWidgets
from ..ui.node_properties_dialog_ui import Ui_NodePropertiesDialog


class NodePropertiesDialog(QtWidgets.QDialog, Ui_NodePropertiesDialog):

    """
    Node properties implementation.

    :param node_items: list of NodeItem instances
    :param parent: parent widget
    """

    def __init__(self, node_items, parent):

        super().__init__(parent)
        self.setupUi(self)

        self._node_items = node_items
        self._parent_items = {}

        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).setEnabled(False)
        self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Reset).setEnabled(False)

        self.previousItem = None
        self.previousPage = None

        # load the empty page widget by default
        self.uiEmptyPageWidget = self.uiConfigStackedWidget.findChildren(QtWidgets.QWidget, "uiEmptyPageWidget")[0]
        self.uiConfigStackedWidget.setCurrentWidget(self.uiEmptyPageWidget)

        self.splitter.setSizes([250, 600])
        self._loadNodeItems()

        self.uiNodesTreeWidget.itemClicked.connect(self.showConfigurationPageSlot)

    def _loadNodeItems(self):
        """
        Loads the nodes into the Node properties QTreeWidget
        """

        # create the parent (group) items
        for node_item in self._node_items:
            if not node_item.node().initialized():
                continue

            # If something of one of the displayed nodes we reload everything
            node_item.node().updated_signal.connect(self.resetSettings)

            group_name = " {} group".format(str(node_item.node()))
            parent = group_name
            if parent not in self._parent_items:
                item = QtWidgets.QTreeWidgetItem(self.uiNodesTreeWidget, [group_name])
                item.setIcon(0, QtGui.QIcon(node_item.node().defaultSymbol()))
                item.setExpanded(True)
                self._parent_items[parent] = item

        # create the children items (configuration page items)
        for node_item in self._node_items:
            if not node_item.node().initialized():
                continue
            parent = " {} group".format(str(node_item.node()))
            ConfigurationPageItem(self._parent_items[parent], node_item)

        # sort the tree
        self.uiNodesTreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)

        if len(self._node_items) == 1:
            parent = " {} group".format(str(node_item.node()))
            item = self._parent_items[parent].child(0)
            item.setSelected(True)
            self.uiNodesTreeWidget.setCurrentItem(item)
            self.showConfigurationPageSlot(item, 0)
            self.splitter.setSizes([0, 600])

    def showConfigurationPageSlot(self, item, column):
        """
        Shows a configuration page widget.

        :param item: reference to the selected item in the QTreeWidget
        :param column: ignored
        """

        # save the previous item temporary settings from the
        # previous page before showing another one
        if self.previousItem:
            try:
                self.previousPage.saveSettings(self.previousItem.settings(), self.previousItem.node())
            except ConfigurationError:
                pass

        if not item.parent():
            # this is a group item, let load
            # the page of its first child.
            self.uiTitleLabel.setText("{} configuration".format(item.text(0)))
            item = item.child(0)
            page = item.page()
            # load the item temporary settings onto the page
            page.loadSettings(item.settings(), item.node(), group=True)
        else:
            self.uiTitleLabel.setText("{} configuration".format(item.node().name()))
            page = item.page()
            self.previousItem = item
            self.previousPage = page
            # load the item temporary settings onto the page
            page.loadSettings(item.settings(), item.node())

        self.uiConfigStackedWidget.addWidget(page)
        self.uiConfigStackedWidget.setCurrentWidget(page)

        if page != self.uiEmptyPageWidget:
            self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).setEnabled(True)
            self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Reset).setEnabled(True)
        else:
            self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply).setEnabled(False)
            self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Reset).setEnabled(False)

    def on_uiButtonBox_clicked(self, button):
        """
        Slot called when a button of the uiButtonBox is clicked.

        :param button: button that was clicked (QAbstractButton)
        """

        try:
            if button == self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Apply):
                self.applySettings()
            elif button == self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Reset):
                self.resetSettings()
            elif button == self.uiButtonBox.button(QtWidgets.QDialogButtonBox.Cancel):
                QtWidgets.QDialog.reject(self)
            else:
                self.applySettings()
                QtWidgets.QDialog.accept(self)
        except ConfigurationError:
            pass

    def applySettings(self):
        """
        Applies the temporary settings to the nodes.
        """

        if self.uiConfigStackedWidget.currentWidget() != self.uiEmptyPageWidget:
            page = self.uiConfigStackedWidget.currentWidget()
            item = self.uiNodesTreeWidget.currentItem()
            if item and item.parent():
                # save the temporary setting for the current page
                page.saveSettings(item.settings(), item.node())
            elif item:
                # save the temporary settings for the current group
                # by applying the first child temporary settings to
                # all children for that group
                self.previousItem = None
                self.previousNode = None
                settings = item.child(0).settings().copy()
                node = item.child(0).node()
                page.saveSettings(settings, node, group=True)
                for index in range(0, item.childCount()):
                    child = item.child(index)
                    # child.node().update(settings)  #TODO: delete
                    child.settings().update(settings)

        # update the nodes with the settings
        for item in self._parent_items.values():
            for index in range(0, item.childCount()):
                child = item.child(index)
                child.node().update(child.settings())

    def resetSettings(self):
        """
        Resets the temporary settings by reloading the settings from the nodes.
        """

        if self.uiConfigStackedWidget.currentWidget() != self.uiEmptyPageWidget:
            page = self.uiConfigStackedWidget.currentWidget()
            item = self.uiNodesTreeWidget.currentItem()
            if item and item.parent():
                # reload the settings on the current page.
                item.setSettings(item.node().settings().copy())
                page.loadSettings(item.settings(), item.node())
            else:
                # this is a group item (no parent), reload the settings
                # on the current page by taking the settings of the first child.
                self.previousItem = None
                self.previousNode = None
                page.loadSettings(item.child(0).settings().copy(), item.child(0).node(), group=True)

        # reset the settings
        for item in self._parent_items.values():
            for index in range(0, item.childCount()):
                child = item.child(index)
                child.setSettings(child.node().settings().copy())


class ConfigurationPageItem(QtWidgets.QTreeWidgetItem):

    """
    Item for the QTreeWidget instance.
    Store temporary node settings configured in a page widget.

    :param parent: parent widget
    :param node_item: NodeItem instance
    """

    def __init__(self, parent, node_item):

        self._node = node_item.node()
        super().__init__(parent, [self._node.name()])

        # return the configuration page widget used to configure the node.
        self._page = self._node.configPage()

        # make a copy of the node settings
        self.setSettings(self._node.settings().copy())

        # we want to know about updated settings
        self._node.updated_signal.connect(self._updatedSlot)

    def _updatedSlot(self):
        """
        Slot called when the node settings have been updated.
        """

        # update the name of the widget item
        self.setText(0, self._node.name())

    def page(self):
        """
        Returns the page widget to be displayed by the node properties dialog.

        :returns: QWidget instance
        """

        return self._page()

    def node(self):
        """
        Returns node associated with this item.

        :returns: Node instance
        """

        return self._node

    def settings(self):
        """
        Returns all the temporary settings.

        :returns: dictionary
        """

        return self._settings

    def setSettings(self, settings):
        """
        Sets new temporary settings.

        :param settings: dictionary
        """

        self._settings = settings


class ConfigurationError(Exception):

    """
    Exception to be raised when a configuration error occurs.
    """

    def __init__(self):

        super().__init__()
