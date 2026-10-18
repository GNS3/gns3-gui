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
    assert 'Edit container' not in [action.text() for action in menu.actions()]
    canvas.enterGroup(container)
    container.setSelected(True)
    menu = QtWidgets.QMenu()
    canvas.populateDeviceContextualMenu(menu)
    action = next(action for action in menu.actions() if action.text() == 'Edit container')
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
