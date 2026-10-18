"""Canvas authoring gestures use drafts until their properties are accepted."""
from unittest.mock import patch
import pytest
from gns3.qt import QtCore, QtWidgets
from gns3.items.shape_item import ShapeItem
from test_group_item import canvas, drawing, device
from PyQt6.QtTest import QTest


@pytest.mark.parametrize('kind', ['rect', 'ellipse'])
@pytest.mark.parametrize('reverse', [False, True])
@pytest.mark.parametrize('accept', [False, True])
def test_shape_drag_preview_and_properties_transaction(canvas, kind, reverse, accept):
    canvas._adding_rectangle = kind == 'rect'
    canvas._adding_ellipse = kind == 'ellipse'
    a, b = QtCore.QPoint(180, 150), QtCore.QPoint(420, 330)
    if reverse:
        a, b = b, a
    expected = QtCore.QRectF(canvas.mapToScene(a), canvas.mapToScene(b)).normalized()
    result = QtWidgets.QDialog.DialogCode.Accepted if accept else QtWidgets.QDialog.DialogCode.Rejected
    with patch('gns3.graphics_view.StyleEditorDialog.exec', return_value=result) as dialog:
        QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=a)
        QTest.mouseMove(canvas.viewport(), b)
        assert canvas._shape_preview.rect() == expected
        assert not any(isinstance(item, ShapeItem) for item in canvas.scene().items())
        dialog.assert_not_called()
        QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=b)
        dialog.assert_called_once()
    assert canvas._shape_preview is None
    items = [item for item in canvas.scene().items() if isinstance(item, ShapeItem)]
    assert len(items) == int(accept)
    if accept:
        assert items[0].scenePos() == expected.topLeft()
        assert items[0].rect().size() == expected.size()


def test_shape_escape_and_large_style_dimensions(canvas):
    from gns3.dialogs.style_editor_dialog import StyleEditorDialog
    canvas._adding_rectangle = True
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=QtCore.QPoint(100, 100))
    QTest.keyClick(canvas, QtCore.Qt.Key.Key_Escape)
    assert canvas._shape_preview is None
    item = drawing(canvas)
    dialog = StyleEditorDialog(canvas, [item])
    dialog.uiWidthSpinBox.setValue(25000)
    dialog.uiHeightSpinBox.setValue(15000)
    dialog.accept()
    assert item.rect().size() == QtCore.QSizeF(25000, 15000)
