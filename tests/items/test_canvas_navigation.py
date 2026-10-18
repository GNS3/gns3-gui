"""Real viewport gestures: navigation never steals element movement."""
from unittest.mock import MagicMock
from PyQt6.QtTest import QTest
from gns3.qt import QtCore, QtWidgets
from test_group_item import canvas, device


def test_hand_default_pans_empty_canvas(canvas):
    assert canvas._navigation_mode == 'hand'
    assert canvas.cursor().shape() == QtCore.Qt.CursorShape.OpenHandCursor
    start = canvas.mapToScene(QtCore.QPoint(40, 40))
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=QtCore.QPoint(40, 40))
    assert canvas.cursor().shape() == QtCore.Qt.CursorShape.ClosedHandCursor
    QTest.mouseMove(canvas.viewport(), QtCore.QPoint(140, 100))
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=QtCore.QPoint(140, 100))
    assert canvas.mapToScene(QtCore.QPoint(40, 40)) != start
    assert canvas.cursor().shape() == QtCore.Qt.CursorShape.OpenHandCursor


def test_right_rectangle_selects_and_opens_menu(canvas):
    node = device(canvas, 0, 0)
    canvas._showDeviceContextualMenu = MagicMock()
    rect = canvas.mapFromScene(node.sceneBoundingRect()).boundingRect().adjusted(-10, -10, 10, 10)
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.RightButton, pos=rect.topLeft())
    QTest.mouseMove(canvas.viewport(), rect.bottomRight())
    assert not canvas._selection_band.isHidden()
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.RightButton, pos=rect.bottomRight())
    assert node.isSelected()
    assert canvas._navigation_mode == 'selection'
    assert canvas._selection_band is None
    canvas._showDeviceContextualMenu.assert_called_once()
    menu = QtWidgets.QMenu()
    canvas.populateDeviceContextualMenu(menu)
    assert 'Create container' in [a.text() for a in menu.actions()]


def test_right_click_does_not_select_single_item(canvas):
    node = device(canvas)
    canvas._showDeviceContextualMenu = MagicMock()
    pos = canvas.mapFromScene(node.sceneBoundingRect().center())
    QTest.mouseClick(canvas.viewport(), QtCore.Qt.MouseButton.RightButton, pos=pos)
    assert not node.isSelected()
    canvas._showDeviceContextualMenu.assert_not_called()
