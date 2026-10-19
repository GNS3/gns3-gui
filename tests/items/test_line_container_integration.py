"""Line/container integration runs on the complete canvas branch."""
from unittest.mock import patch
import pytest
from PyQt6.QtTest import QTest
from gns3.qt import QtCore, QtGui, QtWidgets

pytest.importorskip('gns3.items.group_item', reason='Container integration requires feature-container')
from gns3.items.group_item import read_group
from gns3.dialogs.line_properties_dialog import LinePropertiesDialog
from test_group_item import group, drawing
from test_line_workflow import line_canvas, make_line, move_pointer


@pytest.mark.parametrize('index', [0, 1])
def test_nested_rotated_line_endpoint_preserves_hierarchy_and_saves_once(line_canvas, index):
    view = line_canvas
    item = make_line(view)
    inner = group(view, [item])
    outer = group(view, [inner])
    outer.setPos(outer.pos() + QtCore.QPointF(20, 15))
    item.setRotation(-10)
    view.enterGroup(inner)
    item.setSelected(True)
    points = (item.line().p1(), item.line().p2())
    fixed = item.mapToScene(points[1 - index])
    start = view.mapFromScene(item.mapToScene(points[index]))
    end = start + QtCore.QPoint(24, 16)
    # Avoid the frame's own alphanumeric title/corner hit areas.
    assert view._groups.resizeHandleAt(view.mapToScene(start)) is None
    with patch.object(view._groups, 'save', wraps=view._groups.save) as save:
        QTest.mousePress(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
        assert view._lines._resize is not None
        QTest.mouseMove(view.viewport(), end)
        QTest.mouseRelease(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
        save.assert_called_once_with([item])
    assert item.parentItem() is inner and inner.parentItem() is outer
    stationary = item.line().p2() if index == 0 else item.line().p1()
    assert (item.mapToScene(stationary) - fixed).manhattanLength() < 1e-8
    assert read_group(inner.toSvg())['children'][0]['id'] == item.drawing_id()
    assert view._groups.editing is inner


def test_container_corner_keeps_priority_over_coincident_line_endpoint(line_canvas):
    view = line_canvas
    container = group(view, [drawing(view)])
    container.setDimensions(400, 300)
    item = make_line(view)
    corner = container.mapToScene(container.corners()['br'])
    item.setPos(corner)
    item.setLine(0, 0, 100, 30)
    container.setSelected(True)
    item.setSelected(True)
    point = view.mapFromScene(corner)
    original = QtCore.QLineF(item.line()), item.pos()
    QTest.mousePress(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=point)
    assert view._groups._resize is not None
    assert view._lines._resize is None and not view._dragging
    end = point + QtCore.QPoint(30, 20)
    QTest.mouseMove(view.viewport(), end)
    QTest.mouseRelease(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
    assert (container.rect().width(), container.rect().height()) == (430, 320)
    assert (item.line(), item.pos()) == original


def test_closed_or_clipped_container_prevents_hidden_endpoint_access(line_canvas):
    view = line_canvas
    item = make_line(view)
    container = group(view, [item])
    item.setSelected(True)
    position = item.mapToScene(item.line().p2())
    assert view._lines.endpointAt(position) is None  # Closed parent owns children.
    view.enterGroup(container)
    item.setSelected(True)
    assert view._lines.endpointAt(position) == (item, 1)
    container.setDimensions(30, 30)
    assert view._lines.endpointAt(position) is None  # Clipped handle is inaccessible.


def test_shape_draft_and_pending_container_request_cancel_when_line_tool_starts(line_canvas):
    view = line_canvas
    view.addRectangle(True)
    point = QtCore.QPoint(120, 100)
    QTest.mousePress(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=point)
    assert view._shape_preview is not None
    view._groups.selection_pending = True
    view.addLine(True)
    assert view._shape_preview is None
    assert not view._groups.selection_pending
    assert not view._adding_rectangle and view._adding_line
    QTest.mouseRelease(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=point)


@pytest.mark.parametrize('mode', ['hand', 'selection'])
def test_navigation_tool_cancels_pending_line(line_canvas, mode):
    view = line_canvas
    view.addLine(True)
    QTest.mouseClick(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=QtCore.QPoint(120, 100))
    assert view._lines.preview is not None
    view.setNavigationMode(mode)
    assert view._lines.preview is None and not view._adding_line
    assert view._navigation_mode == mode


def test_line_creation_in_blank_editing_background_keeps_container_active(line_canvas):
    view = line_canvas
    container = group(view, [drawing(view)])
    container.setDimensions(400, 300)
    view.enterGroup(container)
    a = view.mapFromScene(container.mapToScene(QtCore.QPointF(300, 180)))
    b = view.mapFromScene(container.mapToScene(QtCore.QPointF(350, 220)))
    view.addLine(True)
    QTest.mouseClick(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=a)
    assert view._lines.origin is not None
    move_pointer(view, b)
    with patch.object(LinePropertiesDialog, 'exec', return_value=QtWidgets.QDialog.DialogCode.Accepted):
        QTest.mouseClick(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=b)
    assert view._groups.editing is container
