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


@pytest.mark.parametrize('shape', ['rect', 'triangle', 'ellipse'])
def test_container_style_roundtrip_and_rectangular_resize_bounds(canvas, shape):
    from test_group_item import group
    from gns3.items.group_item import GroupItem, read_group
    node = device(canvas, 100, 100)
    container = group(canvas, [node])
    position = node.scenePos()
    container.setStyle(dict(shape=shape, fill_color='#4088aa22', border_color='#ff123456',
                           border_width=6, border_style=2))
    svg = container.toSvg()
    copy = GroupItem(svg=svg)
    assert copy.style == container.style
    assert read_group(svg)['style']['shape'] == shape
    assert node.scenePos() == position
    assert bool(container.flags() & QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape) is (shape == 'rect')
    assert container.shape().contains(container.rect().topLeft() + QtCore.QPointF(1, 1))
    canvas.enterGroup(container)
    container.setSelected(True)
    container.setDimensions(500, 350)
    for corner, point in container.corners().items():
        hit = canvas._groups.resizeHandleAt(container.mapToScene(point))
        assert hit == (container, corner)
    assert node.scenePos() == position


def test_container_dialog_has_accessible_exclusive_icon_choices(canvas):
    from gns3.dialogs.group_properties_dialog import GroupPropertiesDialog
    dialog = GroupPropertiesDialog(canvas, 'LAN', 500, 300)
    assert dialog.tabs.currentIndex() == 0
    editor = dialog.styleEditor
    assert editor.shape_buttons['rect'].isChecked()
    editor.shape_buttons['triangle'].click()
    assert editor.style()['shape'] == 'triangle'
    assert not editor.shape_buttons['rect'].isChecked()
    assert all(not button.text() and button.accessibleName() and not button.icon().isNull()
               for button in editor.shape_buttons.values())
