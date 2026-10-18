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
    assert editor.styleData()['shape'] == 'triangle'
    assert not editor.shape_buttons['rect'].isChecked()
    assert all(not button.text() and button.accessibleName() and not button.icon().isNull()
               for button in editor.shape_buttons.values())


@pytest.mark.parametrize('accept', [False, True])
def test_note_creation_dialog_confirms_or_discards(canvas, accept):
    from gns3.items.text_item import TextItem
    canvas._adding_note = True
    result = QtWidgets.QDialog.DialogCode.Accepted if accept else QtWidgets.QDialog.DialogCode.Rejected
    with patch('gns3.graphics_view.TextEditorDialog.exec', return_value=result) as dialog:
        QTest.mouseClick(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=QtCore.QPoint(160, 140))
        dialog.assert_called_once()
    assert len([item for item in canvas.scene().items() if isinstance(item, TextItem)]) == int(accept)


def test_note_typography_defaults_project_fonts_and_svg_roundtrip(canvas):
    from gns3.dialogs.text_editor_dialog import TextEditorDialog
    from gns3.items.text_item import TextItem
    note = drawing(canvas, 'text')
    initial = note.font()
    dialog = TextEditorDialog(canvas, [note])
    assert dialog.fontFamily.currentText() == initial.family()
    assert dialog.fontSize.value() == initial.pointSizeF()
    dialog.fontSize.setValue(32)
    dialog.underline.setChecked(True)
    dialog.uiPlainTextEdit.setPlainText('Network LAN')
    dialog.accept()
    copy = TextItem(svg=note.toSvg())
    assert copy.font().underline() and copy.font().pointSizeF() == 32
    assert copy.toPlainText() == 'Network LAN'


@pytest.fixture
def image_path(tmp_path):
    from gns3.qt import QtGui
    path = tmp_path / 'image.png'
    image = QtGui.QImage(100, 50, QtGui.QImage.Format.Format_ARGB32)
    image.fill(QtGui.QColor('green'))
    image.save(str(path))
    return str(path)


@pytest.mark.parametrize('accept', [False, True])
def test_import_image_properties_transaction(canvas, image_path, accept):
    from gns3.items.image_item import ImageItem
    value = (400, 200, True) if accept else None
    with patch('gns3.dialogs.image_properties_dialog.ImagePropertiesDialog.getDimensions', return_value=value):
        canvas.addImage(image_path)
    images = [item for item in canvas.scene().items() if isinstance(item, ImageItem)]
    assert len(images) == int(accept)
    if accept:
        assert images[0].boundingRect().size() == QtCore.QSizeF(400, 200)
        copy = ImageItem(svg=images[0].toSvg())
        assert copy.boundingRect().size() == QtCore.QSizeF(400, 200)


@pytest.mark.parametrize('corner', ['tl', 'br'])
@pytest.mark.parametrize('keep', [True, False])
def test_image_corner_resize_preserves_opposite_corner_and_serializes(canvas, image_path, corner, keep):
    from gns3.items.image_item import ImageItem
    from test_group_item import group
    image = ImageItem(image_path=image_path, pos=QtCore.QPointF(100, 100))
    image.keep_aspect = keep
    canvas.scene().addItem(image)
    container = group(canvas, [image])
    container.setDimensions(500, 400)
    canvas.enterGroup(container)
    QtWidgets.QApplication.processEvents()
    r = image.boundingRect()
    point = r.topLeft() + QtCore.QPointF(2, 2) if corner == 'tl' else r.bottomRight() - QtCore.QPointF(2, 2)
    opposite = image.mapToScene(r.bottomRight() if corner == 'tl' else r.topLeft())
    start = canvas.mapFromScene(image.mapToScene(point))
    end = start + (QtCore.QPoint(-40, -30) if corner == 'tl' else QtCore.QPoint(40, 30))
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(canvas.viewport(), end)
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
    assert image.boundingRect().width() > r.width()
    if keep:
        assert image.boundingRect().width() / image.boundingRect().height() == pytest.approx(2)
    fixed = image.mapToScene(image.boundingRect().bottomRight() if corner == 'tl' else image.boundingRect().topLeft())
    assert (fixed - opposite).manhattanLength() < 1
    restored = ImageItem(svg=image.toSvg())
    assert restored.boundingRect().size() == image.boundingRect().size()
    assert restored.keep_aspect is keep


def test_image_dimension_dialog_ratio_and_free_size(canvas):
    from gns3.dialogs.image_properties_dialog import ImagePropertiesDialog
    dialog = ImagePropertiesDialog(canvas, 100, 50)
    dialog.widthEdit.setValue(400)
    assert dialog.heightEdit.value() == 200
    dialog.keepAspect.setChecked(False)
    dialog.heightEdit.setValue(350)
    assert dialog.widthEdit.value() == 400


def test_container_color_controls_remain_readable_and_draft_cancels_on_focus_loss(canvas):
    from gns3.dialogs.container_style_widget import ContainerStyleWidget
    from gns3.qt import QtGui
    editor = ContainerStyleWidget()
    button = QtWidgets.QPushButton()
    editor.updateColorButton(button, '#00000000')
    assert button.text() == 'Transparent' and 'color: black' in button.styleSheet()
    editor.updateColorButton(button, '#ff000000')
    assert 'color: white' in button.styleSheet()
    assert isinstance(editor.style(), QtWidgets.QStyle)  # QWidget API is not shadowed.
    canvas._adding_rectangle = True
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=QtCore.QPoint(100, 100))
    canvas.focusOutEvent(QtGui.QFocusEvent(QtCore.QEvent.Type.FocusOut))
    assert canvas._shape_preview is None
