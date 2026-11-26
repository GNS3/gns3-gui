"""Hand and Selection navigation, driven with real viewport mouse events."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtTest import QTest

import gns3.graphics_view as graphics_view
from gns3.graphics_view import GraphicsView
from gns3.items.node_item import NodeItem
from gns3.qt import QtCore, QtGui, QtWidgets

LEFT = QtCore.Qt.MouseButton.LeftButton
RIGHT = QtCore.Qt.MouseButton.RightButton
EMPTY = QtCore.QPoint(700, 500)


@pytest.fixture
def canvas(main_window):
    main_window.uiSnapToGridAction.isChecked.return_value = False
    window = QtWidgets.QMainWindow()
    central = QtWidgets.QWidget(window)
    window.setCentralWidget(central)
    view = GraphicsView(central)
    view._main_window = main_window
    view.toggleUiDeviceMenu = MagicMock()
    view._showDeviceContextualMenu = MagicMock()
    main_window.uiGraphicsView = view
    view._topology = MagicMock()
    view._topology.project.return_value = None
    view._topology.links.return_value = []
    view.resize(800, 600)
    view.show()
    yield view
    window.close()


def device(view, x=0, y=0):
    node = MagicMock()
    node.x.return_value, node.y.return_value = x, y
    node.z.return_value = 1
    node.locked.return_value = False
    node.initialized.return_value = False
    node.node_id.return_value = str(uuid.uuid4())
    node.name.return_value = "Device-" + node.node_id.return_value
    item = NodeItem(node)
    view.scene().addItem(item)
    return item


def scrollable(view):
    device(view, -2000, -2000)
    device(view, 2000, 2000)


def drag(view, button, start, end):
    QTest.mousePress(view.viewport(), button, pos=start)
    QTest.mouseMove(view.viewport(), end)
    QTest.mouseRelease(view.viewport(), button, pos=end)


def right_click(view, pos):
    # On X11 and Wayland the platform sends the context menu request after the press.
    QTest.mousePress(view.viewport(), RIGHT, pos=pos)
    request = QtGui.QContextMenuEvent(QtGui.QContextMenuEvent.Reason.Mouse, pos, view.viewport().mapToGlobal(pos))
    QtWidgets.QApplication.sendEvent(view.viewport(), request)
    QTest.mouseRelease(view.viewport(), RIGHT, pos=pos)


class FakeLink(QtWidgets.QGraphicsRectItem):

    def __init__(self):
        super().__init__(0, 0, 200, 6)
        self.menus = 0

    def setHovered(self, value):
        pass

    def contextMenuEvent(self, event):
        self.menus += 1
        event.accept()


def test_hand_is_default_and_pans_empty_canvas(canvas):
    scrollable(canvas)
    assert canvas.navigationMode() == "hand"
    assert canvas.cursor().shape() == QtCore.Qt.CursorShape.OpenHandCursor
    start = canvas.mapToScene(QtCore.QPoint(40, 40))
    QTest.mousePress(canvas.viewport(), LEFT, pos=QtCore.QPoint(40, 40))
    assert canvas.cursor().shape() == QtCore.Qt.CursorShape.ClosedHandCursor
    QTest.mouseMove(canvas.viewport(), QtCore.QPoint(140, 100))
    QTest.mouseRelease(canvas.viewport(), LEFT, pos=QtCore.QPoint(140, 100))
    assert canvas.mapToScene(QtCore.QPoint(40, 40)) != start
    assert canvas.cursor().shape() == QtCore.Qt.CursorShape.OpenHandCursor


def test_selection_mode_keeps_left_rubber_band(canvas):
    scrollable(canvas)
    node = device(canvas, 0, 0)
    canvas.setNavigationMode("selection")
    rect = canvas.mapFromScene(node.sceneBoundingRect()).boundingRect().adjusted(-10, -10, 10, 10)
    start = canvas.mapToScene(QtCore.QPoint(10, 10))
    drag(canvas, LEFT, rect.topLeft(), rect.bottomRight())
    assert canvas.mapToScene(QtCore.QPoint(10, 10)) == start
    assert node.isSelected()


def test_gestures_do_not_change_the_mode(canvas):
    right_click(canvas, EMPTY)
    drag(canvas, RIGHT, QtCore.QPoint(10, 10), QtCore.QPoint(200, 200))
    assert canvas.navigationMode() == "hand"
    canvas.setNavigationMode("selection")
    QTest.mouseClick(canvas.viewport(), LEFT, pos=EMPTY)
    assert canvas.navigationMode() == "selection"


def test_left_click_on_empty_canvas_clears_selection(canvas):
    node = device(canvas)
    node.setSelected(True)
    QTest.mouseClick(canvas.viewport(), LEFT, pos=EMPTY)
    assert canvas.scene().selectedItems() == []


def test_pan_keeps_selection(canvas):
    scrollable(canvas)
    node = device(canvas)
    node.setSelected(True)
    drag(canvas, LEFT, EMPTY, QtCore.QPoint(600, 400))
    assert node.isSelected()


def test_right_drag_selects_and_opens_menu(canvas):
    node = device(canvas, 0, 0)
    rect = canvas.mapFromScene(node.sceneBoundingRect()).boundingRect().adjusted(-10, -10, 10, 10)
    QTest.mousePress(canvas.viewport(), RIGHT, pos=rect.topLeft())
    QTest.mouseMove(canvas.viewport(), rect.bottomRight())
    assert not canvas._selection_band.isHidden()
    QTest.mouseRelease(canvas.viewport(), RIGHT, pos=rect.bottomRight())
    assert node.isSelected()
    assert canvas._selection_band is None
    canvas._showDeviceContextualMenu.assert_called_once()


def test_ctrl_right_drag_adds_to_selection(canvas):
    first, second = device(canvas, 0, 0), device(canvas, 300, 0)
    first.setSelected(True)
    rect = canvas.mapFromScene(second.sceneBoundingRect()).boundingRect().adjusted(-10, -10, 10, 10)
    QTest.mousePress(canvas.viewport(), RIGHT, QtCore.Qt.KeyboardModifier.ControlModifier, rect.topLeft())
    QTest.mouseMove(canvas.viewport(), rect.bottomRight())
    QTest.mouseRelease(canvas.viewport(), RIGHT, QtCore.Qt.KeyboardModifier.ControlModifier, rect.bottomRight())
    assert first.isSelected() and second.isSelected()


def test_right_click_on_device_opens_its_menu(canvas):
    node = device(canvas)
    right_click(canvas, canvas.mapFromScene(node.sceneBoundingRect().center()))
    assert node.isSelected()
    canvas._showDeviceContextualMenu.assert_called_once()


def test_right_click_on_selected_device_keeps_multi_selection(canvas):
    first, second = device(canvas, 0, 0), device(canvas, 300, 0)
    first.setSelected(True)
    second.setSelected(True)
    right_click(canvas, canvas.mapFromScene(first.sceneBoundingRect().center()))
    assert first.isSelected() and second.isSelected()
    canvas._showDeviceContextualMenu.assert_called_once()


def test_right_click_on_empty_canvas_keeps_multi_selection_menu(canvas):
    first, second = device(canvas, 0, 0), device(canvas, 300, 0)
    first.setSelected(True)
    second.setSelected(True)
    right_click(canvas, EMPTY)
    canvas._showDeviceContextualMenu.assert_called_once()


def test_right_click_on_link_opens_link_menu(canvas):
    link = FakeLink()
    canvas.scene().addItem(link)
    with patch.object(graphics_view, "LinkItem", FakeLink):
        right_click(canvas, canvas.mapFromScene(QtCore.QPointF(100, 3)))
    assert link.menus == 1
    canvas._showDeviceContextualMenu.assert_not_called()


def test_escape_cancels_right_drag_and_restores_selection(canvas):
    node = device(canvas, 0, 0)
    node.setSelected(True)
    QTest.mousePress(canvas.viewport(), RIGHT, pos=QtCore.QPoint(600, 400))
    QTest.mouseMove(canvas.viewport(), QtCore.QPoint(700, 500))
    assert not node.isSelected()
    QTest.keyClick(canvas, QtCore.Qt.Key.Key_Escape)
    assert canvas._selection_band is None
    assert node.isSelected()
    canvas._showDeviceContextualMenu.assert_not_called()


def test_focus_loss_cleans_up_gestures(canvas):
    QTest.mousePress(canvas.viewport(), LEFT, pos=EMPTY)
    assert canvas._dragging
    canvas.focusOutEvent(QtGui.QFocusEvent(QtCore.QEvent.Type.FocusOut))
    assert not canvas._dragging
    assert canvas.cursor().shape() == QtCore.Qt.CursorShape.OpenHandCursor


def test_adding_note_restores_navigation_cursor(canvas):
    canvas.addNote(True)
    assert canvas.cursor().shape() != QtCore.Qt.CursorShape.OpenHandCursor
    canvas.addNote(False)
    assert canvas.cursor().shape() == QtCore.Qt.CursorShape.OpenHandCursor
