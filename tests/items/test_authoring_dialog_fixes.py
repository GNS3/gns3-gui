from unittest.mock import MagicMock, patch
import pytest
from gns3.qt import QtCore, QtWidgets
from test_group_item import canvas, drawing, device


def test_numeric_dimensions_have_scoped_white_backgrounds(canvas):
    from gns3.dialogs.image_properties_dialog import ImagePropertiesDialog
    from gns3.dialogs.style_editor_dialog import StyleEditorDialog
    from gns3.dialogs.container_style_widget import ContainerStyleWidget
    container_style = ContainerStyleWidget(parent=canvas)
    image = ImagePropertiesDialog(canvas, 100, 50)
    shape = StyleEditorDialog(canvas, [drawing(canvas)])
    for field in (image.widthEdit, image.heightEdit, shape.uiWidthSpinBox, shape.uiHeightSpinBox, container_style.borderWidth):
        assert 'background-color: white' in field.styleSheet()
        assert 'color: black' in field.styleSheet()


def test_zero_width_hides_shape_and_container_borders(canvas):
    from gns3.dialogs.style_editor_dialog import StyleEditorDialog
    from test_group_item import group
    from gns3.qt import QtGui
    item = drawing(canvas)
    dialog = StyleEditorDialog(canvas, [item])
    dialog.uiBorderWidthSpinBox.setValue(0)
    dialog.accept()
    assert item.pen().style() == QtCore.Qt.PenStyle.NoPen
    container = group(canvas, [item])
    container.setStyle(dict(border_width=0))
    from unittest.mock import MagicMock
    painter = MagicMock()
    container.paint(painter, None)
    assert painter.setPen.call_args_list[0].args[0].style() == QtCore.Qt.PenStyle.NoPen
    assert container.style['border_width'] == 0
