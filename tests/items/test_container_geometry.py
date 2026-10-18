from unittest.mock import patch
import pytest
from gns3.qt import QtCore
from test_group_item import canvas, device, drawing, group


@pytest.mark.parametrize('shape', ['triangle', 'ellipse'])
def test_shape_change_repositions_full_child_bounds_and_uses_outline_for_drop(canvas, shape):
    nodes = [device(canvas, x, y) for x, y in [(0, 0), (250, 0), (0, 200), (250, 200)]]
    container = group(canvas, nodes)
    sizes = {node: node.boundingRect().size() for node in nodes}
    container.setStyle(dict(shape=shape))
    assert not container.shape().contains(container.rect().topLeft() + QtCore.QPointF(1, 1))
    assert canvas._groups.groupAt(container.mapToScene(container.rect().topLeft() + QtCore.QPointF(1, 1))) is None
    for node in nodes:
        bounds = node.mapRectToParent(node.boundingRect().united(node.childrenBoundingRect()))
        assert container.shape().contains(bounds)
        assert node.parentItem() is container and node.boundingRect().size() == sizes[node]
    assert canvas._groups.groupAt(container.mapToScene(container.rect().center())) is container
    positions = {node: node.pos() for node in nodes}
    canvas._groups.save([container])
    canvas._groups.restore()
    assert all(node.pos() == positions[node] for node in nodes)


def test_shape_apply_then_cancel_restores_child_positions_and_dimensions(canvas):
    node = device(canvas)
    container = group(canvas, [node, drawing(canvas, x=300)])
    before = container.rect(), dict(container.style), {item: item.pos() for item in container.members()}
    def preview(*args, **kwargs):
        kwargs['preview'](('LAN', 150, 150, dict(shape='triangle')))
        assert container.shape().contains(node.mapRectToParent(node.boundingRect()))
        return None
    with patch('gns3.canvas_groups.GroupPropertiesDialog.getProperties', side_effect=preview):
        canvas._groups.rename(container)
    assert container.rect() == before[0] and container.style == before[1]
    assert all(item.pos() == position for item, position in before[2].items())
