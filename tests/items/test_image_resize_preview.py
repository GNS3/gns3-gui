from unittest.mock import patch
import pytest
from gns3.qt import QtCore
from PyQt6.QtTest import QTest
from test_group_item import canvas
from test_canvas_authoring import image_path


@pytest.mark.parametrize('corner', ['tl', 'tr', 'bl', 'br'])
def test_image_resize_reuses_renderer_until_release(canvas, image_path, corner):
    from gns3.items.image_item import ImageItem
    image = ImageItem(image_path=image_path, pos=QtCore.QPointF(100, 100))
    image.setRotation(15)
    canvas.scene().addItem(image)
    r = image.boundingRect().adjusted(2, 2, -2, -2)
    points = dict(tl=r.topLeft(), tr=r.topRight(), bl=r.bottomLeft(), br=r.bottomRight())
    start = canvas.mapFromScene(image.mapToScene(points[corner]))
    dx = -1 if 'l' in corner else 1
    dy = -1 if 't' in corner else 1
    renderer = image.renderer()
    with patch.object(image, 'fromSvg', wraps=image.fromSvg) as decode:
        QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
        for step in range(1, 8):
            end = start + QtCore.QPoint(dx * step * 5, dy * step * 4)
            QTest.mouseMove(canvas.viewport(), end)
            assert image.renderer() is renderer
            decode.assert_not_called()
        QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
        decode.assert_called_once()
    assert image.boundingRect().width() > 100
    assert image.transform().isIdentity()
