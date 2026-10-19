"""Real Qt gestures for independent line authoring and endpoint editing."""
from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET

import pytest
from PyQt6.QtTest import QTest

from gns3.qt import QtCore, QtGui, QtWidgets
from gns3.graphics_view import GraphicsView
from gns3.items.line_item import LineItem
from gns3.dialogs.line_properties_dialog import LinePropertiesDialog


@pytest.fixture
def line_canvas(main_window):
    main_window.uiSnapToGridAction.isChecked.return_value = False
    window = QtWidgets.QMainWindow()
    central = QtWidgets.QWidget(window)
    window.setCentralWidget(central)
    view = GraphicsView(central)
    view._main_window = main_window
    main_window.uiGraphicsView = view
    view._topology = MagicMock()
    view._topology.project.return_value = None
    view._topology.links.return_value = []
    view.toggleUiDeviceMenu = MagicMock()
    for name in ('uiDrawLineAction', 'uiDrawRectangleAction', 'uiDrawEllipseAction',
                 'uiAddNoteAction', 'uiAddLinkAction'):
        action = QtGui.QAction(window)
        action.setCheckable(True)
        setattr(main_window, name, action)
    window.resize(820, 620)
    view.resize(800, 600)
    window.show()
    QtWidgets.QApplication.processEvents()
    yield view
    window.close()
    window.deleteLater()


def make_line(view, delta=(200, 100)):
    item = view.createDrawingItem('line', -100, -50, 1, create=False)
    item.setLine(0, 0, *delta)
    item.setSelected(True)
    return item


@pytest.mark.parametrize('zoom', [.2, 1, 5])
@pytest.mark.parametrize('accept', [False, True])
def test_two_clicks_preview_and_style_transaction(line_canvas, zoom, accept):
    view = line_canvas
    view.scale(zoom, zoom)
    project = MagicMock()
    view._topology.project.return_value = project
    a, b = QtCore.QPoint(160, 180), QtCore.QPoint(440, 330)
    start, end = view.mapToScene(a), view.mapToScene(b)

    calls = []

    def properties(dialog):
        calls.append(dialog)
        project.post.assert_not_called()
        project.put.assert_not_called()
        dialog.thickness.setValue(7)
        dialog.lineStyle.setCurrentIndex(dialog.lineStyle.findData(QtCore.Qt.PenStyle.DashDotLine))
        dialog._color = QtGui.QColor('#e03050')
        dialog.buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Apply).click()
        item = next(item for item in view.scene().items() if isinstance(item, LineItem))
        assert item.pen().width() == 7
        assert dialog.result() != QtWidgets.QDialog.DialogCode.Accepted
        project.post.assert_not_called()
        project.put.assert_not_called()
        (dialog.accept if accept else dialog.reject)()
        return dialog.result()

    with patch.object(LinePropertiesDialog, 'exec', new=properties):
        view.addLine(True)
        QTest.mouseMove(view.viewport(), a)
        QTest.mouseClick(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=a)
        assert view._lines.origin == start
        assert not view._dragging
        assert not any(isinstance(item, LineItem) for item in view.scene().items())
        QTest.mouseMove(view.viewport(), b)
        assert view._lines.preview.line() == QtCore.QLineF(start, end)
        assert len(view._lines.preview.childItems()) == 1  # Mark the first endpoint.
        assert not calls
        QTest.mouseClick(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=b)
        assert len(calls) == 1
    assert view._lines.preview is None and not view._adding_line
    assert not view._main_window.uiDrawLineAction.isChecked()
    items = [item for item in view.scene().items() if isinstance(item, LineItem)]
    assert len(items) == int(accept)
    if accept:
        project.post.assert_called_once()
        project.put.assert_not_called()
        item = items[0]
        assert item.mapToScene(item.line().p1()) == start
        assert item.mapToScene(item.line().p2()) == end
        assert item.pen().style() == QtCore.Qt.PenStyle.DashDotLine
    else:
        project.post.assert_not_called()
        project.delete.assert_not_called()


def test_first_click_requires_empty_area_second_may_overlap_item(line_canvas):
    view = line_canvas
    existing = make_line(view)
    occupied = view.mapFromScene(existing.mapToScene(existing.line().center()))
    empty = QtCore.QPoint(120, 100)
    view.addLine(True)
    QTest.mouseClick(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=occupied)
    assert view._lines.origin is None
    QTest.mouseClick(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=empty)
    with patch.object(LinePropertiesDialog, 'exec', return_value=QtWidgets.QDialog.DialogCode.Accepted) as dialog:
        QTest.mouseClick(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=occupied)
        dialog.assert_called_once()
    assert len([item for item in view.scene().items() if isinstance(item, LineItem)]) == 2


@pytest.mark.parametrize('cancel', ['escape', 'right', 'off', 'focus', 'rectangle', 'reset'])
def test_pending_line_cancellation_leaves_no_drawing(line_canvas, cancel):
    view = line_canvas
    view.addLine(True)
    point = QtCore.QPoint(120, 100)
    QTest.mouseClick(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=point)
    with patch.object(LinePropertiesDialog, 'exec') as dialog:
        if cancel == 'escape':
            QTest.keyClick(view, QtCore.Qt.Key.Key_Escape)
        elif cancel == 'right':
            QTest.mouseClick(view.viewport(), QtCore.Qt.MouseButton.RightButton, pos=point)
        elif cancel == 'off':
            view.addLine(False)
        elif cancel == 'focus':
            view.focusOutEvent(QtGui.QFocusEvent(QtCore.QEvent.Type.FocusOut))
        elif cancel == 'rectangle':
            view.addRectangle(True)
        else:
            view.reset()
        dialog.assert_not_called()
    assert view._lines.preview is None and view._lines.origin is None
    assert not view._adding_line and not view._main_window.uiDrawLineAction.isChecked()
    assert not any(isinstance(item, LineItem) for item in view.scene().items())


def test_repeated_same_point_keeps_draft_until_distinct_second_click(line_canvas):
    view = line_canvas
    view.addLine(True)
    point = QtCore.QPoint(120, 100)
    with patch.object(LinePropertiesDialog, 'exec') as dialog:
        QTest.mouseClick(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=point)
        QTest.mouseClick(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=point)
        dialog.assert_not_called()
    assert view._adding_line and view._lines.preview is not None


@pytest.mark.parametrize('index', [0, 1])
@pytest.mark.parametrize('delta', [(200, 0), (0, -160), (-200, -100), (200, -100)])
@pytest.mark.parametrize('rotation', [0, 25, 90])
@pytest.mark.parametrize('zoom', [.5, 1, 2])
def test_endpoint_resize_preserves_opposite_end_and_saves_once(line_canvas, index, delta, rotation, zoom):
    view = line_canvas
    view.scale(zoom, zoom)
    item = make_line(view, delta)
    item.setRotation(rotation)
    original = QtCore.QLineF(item.line())
    endpoints = (original.p1(), original.p2())
    fixed = item.mapToScene(endpoints[1 - index])
    start = view.mapFromScene(item.mapToScene(endpoints[index]))
    end = start + QtCore.QPoint(35, -25)
    before = item.sceneTransform().inverted()[0]
    expected = endpoints[index] + before.map(view.mapToScene(end)) - before.map(view.mapToScene(start))
    flags = item.flags()
    with patch.object(item, 'updateDrawing') as save:
        QTest.mousePress(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
        assert view._lines._resize is not None and not view._dragging
        QTest.mouseMove(view.viewport(), end)
        save.assert_not_called()
        QTest.mouseRelease(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
        save.assert_called_once()
    assert view._lines._resize is None
    moved = item.line().p1() if index == 0 else item.line().p2()
    assert (moved - expected).manhattanLength() < 1e-8
    stationary = item.line().p2() if index == 0 else item.line().p1()
    assert (item.mapToScene(stationary) - fixed).manhattanLength() < 1e-8
    assert item.flags() == flags
    loaded = LineItem(svg=item.toSvg())
    assert (loaded.line().p1() - item.line().p1()).manhattanLength() < 1e-8
    assert (loaded.line().p2() - item.line().p2()).manhattanLength() < 1e-8


def test_outer_endpoint_hit_does_not_start_hand_pan(line_canvas):
    view = line_canvas
    item = make_line(view, (200, 0))
    start = view.mapFromScene(item.mapToScene(item.line().p1())) - QtCore.QPoint(6, 6)
    assert view.itemAt(start) is None
    QTest.mouseMove(view.viewport(), start)
    assert view.cursor().shape() == QtCore.Qt.CursorShape.CrossCursor
    QTest.mousePress(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    assert view._lines._resize is not None and not view._dragging
    QTest.mouseRelease(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)


def test_body_drag_moves_both_endpoints_and_persists(line_canvas):
    view = line_canvas
    item = make_line(view)
    before = [item.mapToScene(point) for point in (item.line().p1(), item.line().p2())]
    center = view.mapFromScene(item.mapToScene(item.line().center()))
    delta = QtCore.QPoint(30, 20)
    with patch.object(item, 'updateDrawing') as save:
        QTest.mousePress(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=center)
        assert view._lines._resize is None
        QTest.mouseMove(view.viewport(), center + delta)
        QTest.mouseRelease(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=center + delta)
        save.assert_called_once()
    for point, original in zip((item.line().p1(), item.line().p2()), before):
        assert item.mapToScene(point) - original == QtCore.QPointF(delta)


def test_locked_line_cannot_resize_or_become_movable(line_canvas):
    view = line_canvas
    item = make_line(view)
    item.setLocked(True)
    original = QtCore.QLineF(item.line()), item.pos(), item.flags()
    start = view.mapFromScene(item.mapToScene(item.line().p1()))
    QTest.mousePress(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    assert view._lines._resize is None
    QTest.mouseMove(view.viewport(), start + QtCore.QPoint(40, 30))
    QTest.mouseRelease(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start + QtCore.QPoint(40, 30))
    assert (item.line(), item.pos(), item.flags()) == original


@pytest.mark.parametrize('finish', ['focus', 'extra_button', 'removed'])
def test_resize_interruption_does_not_double_save_or_change_gesture(line_canvas, finish):
    view = line_canvas
    item = make_line(view)
    start = view.mapFromScene(item.mapToScene(item.line().p1()))
    end = start + QtCore.QPoint(30, 20)
    with patch.object(item, 'updateDrawing') as save:
        QTest.mousePress(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
        if finish == 'extra_button':
            QTest.mousePress(view.viewport(), QtCore.Qt.MouseButton.RightButton, pos=start)
            QTest.mouseRelease(view.viewport(), QtCore.Qt.MouseButton.RightButton, pos=start)
            assert view._lines._resize is not None
        QTest.mouseMove(view.viewport(), end)
        if finish == 'focus':
            view.focusOutEvent(QtGui.QFocusEvent(QtCore.QEvent.Type.FocusOut))
        elif finish == 'removed':
            view.scene().removeItem(item)
        QTest.mouseRelease(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
        assert save.call_count == (0 if finish == 'removed' else 1)
    assert view._lines._resize is None


@pytest.mark.parametrize('accept', [False, True])
def test_existing_style_apply_then_cancel_or_ok(line_canvas, accept):
    item = make_line(line_canvas)
    original = QtGui.QPen(item.pen())

    def properties(dialog):
        field = dialog.thickness
        assert 'background-color: white' in field.styleSheet()
        assert 'color: black' in field.styleSheet()
        assert field.findChild(QtWidgets.QLineEdit).palette().color(QtGui.QPalette.ColorRole.Text) == QtGui.QColor('black')
        field.setValue(12)
        dialog.buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Apply).click()
        assert item.pen().width() == 12
        save.assert_not_called()
        (dialog.accept if accept else dialog.reject)()
        return dialog.result()

    with patch.object(LinePropertiesDialog, 'exec', new=properties), patch.object(item, 'updateDrawing') as save:
        line_canvas.styleActionSlot()
        assert save.call_count == int(accept)
    assert item.pen().width() == (12 if accept else original.width())


def test_svg_precision_negative_endpoints_opacity_and_nonzero_viewport(line_canvas):
    item = make_line(line_canvas)
    item.setLine(-25.125, 40.625, -25.125, -30.375)
    pen = QtGui.QPen(QtGui.QColor(20, 40, 60, 90), 9, QtCore.Qt.PenStyle.DotLine)
    item.setPen(pen)
    svg = ET.fromstring(item.toSvg())
    assert float(svg.get('width')) > 0 and float(svg.get('height')) > 0
    # Metadata may precede the line when a drawing is stored in a container.
    svg.insert(0, ET.Element('metadata'))
    copy = LineItem(svg=ET.tostring(svg, encoding='unicode'))
    assert copy.line() == item.line()
    assert copy.pen().color() == item.pen().color()
    assert copy.pen().width() == 9 and copy.pen().style() == QtCore.Qt.PenStyle.DotLine
