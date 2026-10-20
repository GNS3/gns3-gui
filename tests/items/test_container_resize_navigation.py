"""Resize hit areas must win over blank-canvas hand navigation."""
from unittest.mock import patch

import pytest
from PyQt6.QtTest import QTest
from gns3.qt import QtCore, QtWidgets
from test_group_item import canvas, drawing


@pytest.mark.parametrize('shape', ['rect', 'ellipse', 'triangle'])
@pytest.mark.parametrize('corner,offset', [
    ('tl', (-5, -5)), ('tr', (5, -5)),
    ('bl', (-5, 5)), ('br', (5, 5)),
])
@pytest.mark.parametrize('zoom', [0.5, 1, 2])
def test_outer_corner_resizes_instead_of_panning(canvas, shape, corner, offset, zoom):
    child = drawing(canvas)
    container = canvas._groups.add('Resize', [child], position=QtCore.QPointF(-100, -80),
                                   width=200, height=160)
    container.setStyle(dict(shape=shape))
    canvas.enterGroup(container)
    container.setSelected(True)
    canvas.scale(zoom, zoom)
    QtWidgets.QApplication.processEvents()
    before = child.scenePos()
    point = (canvas.mapFromScene(container.mapToScene(container.corners()[corner])) +
             QtCore.QPoint(*offset))
    assert canvas.itemAt(point) is None
    assert canvas._groups.resizeHandleAt(canvas.mapToScene(point)) == (container, corner)
    QTest.mouseMove(canvas.viewport(), point)
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=point)
    assert canvas._groups._resize is not None
    assert not canvas._dragging
    assert canvas._groups.editing is container
    end = point + QtCore.QPoint(20, 10)
    QTest.mouseMove(canvas.viewport(), end)
    with patch.object(canvas._groups, 'save') as save:
        QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
        save.assert_called_once_with([container])
    assert container.rect().width() == pytest.approx(200 + (-20 if 'l' in corner else 20) / zoom)
    assert container.rect().height() == pytest.approx(160 + (-10 if 't' in corner else 10) / zoom)
    assert child.scenePos() == before
    assert canvas._groups._resize is None


def test_blank_canvas_still_pans(canvas):
    point = QtCore.QPoint(20, 20)
    assert canvas.itemAt(point) is None
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=point)
    assert canvas._dragging
    assert canvas._groups._resize is None
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=point)
    assert not canvas._dragging
