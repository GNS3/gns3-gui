from unittest.mock import MagicMock, patch
import pytest
from gns3.qt import QtCore, QtWidgets
from test_group_item import canvas, drawing, device


@pytest.mark.parametrize('confirm', [False, True])
def test_container_apply_previews_and_cancel_rolls_back(canvas, confirm):
    from test_group_item import group
    container = group(canvas, [drawing(canvas)])
    original = container.name, container.rect(), dict(container.style)
    def properties(*args, **kwargs):
        data = ('Preview', 600, 450, dict(shape='ellipse', border_width=0))
        kwargs['preview'](data)
        assert container.name == 'Preview' and container.style['shape'] == 'ellipse'
        return data if confirm else None
    with patch('gns3.canvas_groups.GroupPropertiesDialog.getProperties', side_effect=properties):
        canvas._groups.rename(container)
    if confirm:
        assert container.name == 'Preview' and container.rect().width() == 600
    else:
        assert (container.name, container.rect(), container.style) == original


def test_edit_container_context_action_only_while_editing(canvas):
    from test_group_item import group
    container = group(canvas, [drawing(canvas)])
    menu = QtWidgets.QMenu()
    canvas.populateDeviceContextualMenu(menu)
    assert 'Edit' not in [action.text() for action in menu.actions()]
    canvas.enterGroup(container)
    container.setSelected(True)
    menu = QtWidgets.QMenu()
    canvas.populateDeviceContextualMenu(menu)
    assert menu.actions()[0].text() == 'Edit'
    action = menu.actions()[0]
    with patch.object(canvas._groups, 'rename') as edit:
        action.trigger()
        edit.assert_called_once_with(container)


def test_apply_button_uses_current_dialog_fields(canvas):
    from gns3.dialogs.group_properties_dialog import GroupPropertiesDialog
    preview = MagicMock()
    dialog = GroupPropertiesDialog(canvas, 'LAN', 200, 150, preview=preview)
    dialog.nameEdit.setText('Preview LAN')
    dialog.widthEdit.setValue(700)
    dialog.styleEditor.shape_buttons['triangle'].click()
    dialog.applyButton.click()
    preview.assert_called_once()
    values = preview.call_args.args[0]
    assert values[:3] == ('Preview LAN', 700, 150)
    assert values[3]['shape'] == 'triangle'
    assert dialog.result() != QtWidgets.QDialog.DialogCode.Accepted


def test_stationary_right_click_in_editing_container_offers_edit_first(canvas):
    from PyQt6.QtTest import QTest
    from test_group_item import group
    container = group(canvas, [drawing(canvas)])
    canvas.enterGroup(container)
    # Choose a blank area of the container, away from its child.
    pos = canvas.mapFromScene(container.mapToScene(QtCore.QPointF(5, 5)))
    captured = []
    def context_menu(position):
        menu = QtWidgets.QMenu()
        canvas.populateDeviceContextualMenu(menu)
        captured.extend(action.text() for action in menu.actions())
        with patch.object(canvas._groups, 'rename') as edit:
            menu.actions()[0].trigger()
            edit.assert_called_once_with(container)
    canvas._showDeviceContextualMenu = context_menu
    QTest.mouseClick(canvas.viewport(), QtCore.Qt.MouseButton.RightButton, pos=pos)
    assert captured[0] == 'Edit'
    assert canvas._groups.editing is container


@pytest.mark.parametrize('outer_open', [False, True])
def test_double_click_enters_deepest_container_without_parent_propagation(canvas, outer_open):
    from PyQt6.QtTest import QTest
    from test_group_item import group
    node = device(canvas, 100, 100)
    inner = group(canvas, [node], name='Inner')
    outer = group(canvas, [inner], name='Outer')
    # A negative local layer must not redirect the gesture to the ancestor.
    inner.setZValue(-10)
    if outer_open:
        canvas.enterGroup(outer)
    pos = canvas.mapFromScene(node.sceneBoundingRect().center())
    with patch.object(canvas._groups, 'enter', wraps=canvas._groups.enter) as enter:
        QTest.mouseDClick(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=pos)
        enter.assert_called_once_with(inner)
    assert canvas._groups.editing is inner
    assert outer.editing and inner.editing
