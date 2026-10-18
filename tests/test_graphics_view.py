#!/usr/bin/env python
#
# Copyright (C) 2017 GNS3 Technologies Inc.
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

from unittest.mock import MagicMock, patch
from gns3.graphics_view import GraphicsView
from gns3.node import Node


def test_console_to_node_vncviewer_and_ipv6():
    node = MagicMock(
        initialized=MagicMock(return_value=True),
        status=MagicMock(return_value=Node.started),
        consoleCommand=MagicMock(return_value="vncviewer"),
        consoleHost=MagicMock(return_value="::1")
    )
    view = GraphicsView.__new__(GraphicsView)
    with patch('gns3.qt.QtWidgets.QMessageBox.warning') as warning_mock:
        view.consoleToNode(node)
        assert warning_mock.called
        assert warning_mock.call_args[0][1] == 'TightVNC'


def _grouping_view(main_window):
    from gns3.qt import QtWidgets
    main_window.uiSnapToGridAction.isChecked.return_value = False
    window = QtWidgets.QMainWindow()
    central = QtWidgets.QWidget(window)
    window.setCentralWidget(central)
    view = GraphicsView(central)
    view._main_window = main_window
    view.toggleUiDeviceMenu = MagicMock()
    view.resize(800, 600)
    view.show()
    return window, view


def _grouping_node(view, x):
    from gns3.items.node_item import NodeItem
    node = MagicMock()
    node.x.return_value = x
    node.y.return_value = 0
    node.z.return_value = 1
    node.locked.return_value = False
    node.initialized.return_value = False
    item = NodeItem(node)
    view.scene().addItem(item)
    return item


def test_group_merge_ungroup_and_deleted_members(main_window):
    from gns3.qt import sip
    window, view = _grouping_view(main_window)
    a, b, c = [_grouping_node(view, x) for x in (0, 100, 200)]
    a.setSelected(True)
    view.groupSelectedNodes()
    assert not view._node_groups
    b.setSelected(True)
    view.groupSelectedNodes()
    view.scene().clearSelection()
    a.setSelected(True)
    c.setSelected(True)
    view.groupSelectedNodes()
    assert view._node_groups == [{a, b, c}]
    assert all(item.parentItem() is None for item in (a, b, c))
    sip.delete(c)
    assert view._liveNodeGroups() == [{a, b}]
    view.ungroupSelectedNodes()
    assert not view._node_groups
    window.close()


def test_group_mouse_drag_and_locked_member(main_window):
    from PyQt6.QtTest import QTest
    from gns3.qt import QtCore, QtWidgets
    window, view = _grouping_view(main_window)
    a, b = [_grouping_node(view, x) for x in (0, 100)]
    a.setSelected(True)
    b.setSelected(True)
    view.groupSelectedNodes()
    view.scene().clearSelection()
    QtWidgets.QApplication.processEvents()
    start = view.mapFromScene(a.sceneBoundingRect().center())
    delta = QtCore.QPoint(40, 30)
    initial = [item.pos() for item in (a, b)]
    QTest.mousePress(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    assert a.isSelected() and b.isSelected()
    QTest.mouseMove(view.viewport(), start + delta)
    QTest.mouseRelease(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start + delta)
    assert a.pos() - initial[0] == b.pos() - initial[1] == QtCore.QPointF(delta)
    assert a.node().setGraphics.called and b.node().setGraphics.called
    b.setLocked(True)
    initial = [item.pos() for item in (a, b)]
    start = view.mapFromScene(a.sceneBoundingRect().center())
    QTest.mousePress(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(view.viewport(), start + delta)
    QTest.mouseRelease(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start + delta)
    assert [item.pos() for item in (a, b)] == initial
    window.close()
