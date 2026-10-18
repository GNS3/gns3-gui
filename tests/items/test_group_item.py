# -*- coding: utf-8 -*-
"""Exercise real Qt parenting/events and the persisted hierarchy transport."""

import json
import uuid
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtTest import QTest

from gns3.qt import QtCore, QtWidgets
from gns3.graphics_view import GraphicsView
from gns3.items.group_item import GroupItem, read_group, reparent, set_scene_position
from gns3.items.node_item import NodeItem


@pytest.fixture
def canvas(main_window):
    main_window.uiSnapToGridAction.isChecked.return_value = False
    window = QtWidgets.QMainWindow()
    central = QtWidgets.QWidget(window)
    window.setCentralWidget(central)
    view = GraphicsView(central)
    view._main_window = main_window
    view.toggleUiDeviceMenu = MagicMock()
    main_window.uiGraphicsView = view
    view._topology = MagicMock()
    view._topology.project.return_value = None
    view._topology.links.return_value = []
    view.resize(800, 600)
    view.show()
    yield view
    window.close()


def device(view, x=0, y=0):
    node = MagicMock()
    node.x.return_value, node.y.return_value = x, y
    node.z.return_value = 1
    node.locked.return_value = False
    node.initialized.return_value = False
    node.node_id.return_value = str(uuid.uuid4())
    node.name.return_value = "Device-" + node.node_id.return_value
    item = NodeItem(node)
    view.scene().addItem(item)
    return item


def drawing(view, kind="rect", x=0, y=0):
    svg = '<svg width="80" height="40"><rect width="80" height="40" /></svg>'
    if kind == "text":
        svg = '<svg width="80" height="40"><text x="0" y="16">hello</text></svg>'
    return view.createDrawingItem(kind, x, y, 0, svg=svg)


def group(view, items, name="LAN 1", parent=None):
    view.scene().clearSelection()
    return view._groups.add(name, items, parent=parent)


def test_named_container_mixed_children_and_nested_coordinates(canvas):
    node = device(canvas, 100, 80)
    items = [node, drawing(canvas, "rect", 200, 120), drawing(canvas, "ellipse", 300, 140),
             drawing(canvas, "text", 400, 160), drawing(canvas, "image", 500, 180)]
    before = {item: item.scenePos() for item in items}
    inner = group(canvas, items)
    assert inner.name == "LAN 1"
    assert all(item.parentItem() is inner for item in items)
    assert all(item.scenePos() == before[item] for item in items)
    local_positions = {item: item.pos() for item in items}
    outer = group(canvas, [inner, drawing(canvas, x=650, y=240)], "Building")
    assert inner.parentItem() is outer
    outer.setPos(outer.pos() + QtCore.QPointF(40, 30))
    assert all(item.pos() == local_positions[item] for item in items)
    assert all(item.scenePos() == before[item] + QtCore.QPointF(40, 30) for item in items)
    payload = read_group(inner.toSvg())
    assert {member["type"] for member in payload["children"]} == {"node", "drawing"}
    node_data = next(member for member in payload["children"] if member["type"] == "node")
    assert QtCore.QPointF(node_data["x"], node_data["y"]) == node.pos()
    assert {member["type"] for member in read_group(outer.toSvg())["children"]} == {"group", "drawing"}


def test_mouse_drag_owns_children_and_updates_links(canvas):
    a, b = device(canvas, 0), device(canvas, 100)
    link = MagicMock()
    a._links.append(link)
    container = group(canvas, [a, b])
    canvas.scene().clearSelection()
    QtWidgets.QApplication.processEvents()
    start = canvas.mapFromScene(a.sceneBoundingRect().center())
    delta = QtCore.QPoint(40, 30)
    before = [item.scenePos() for item in (a, b)]
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    assert container.isSelected()
    assert not a.isSelected() and not b.isSelected()
    QTest.mouseMove(canvas.viewport(), start + delta)
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start + delta)
    assert a.scenePos() - before[0] == b.scenePos() - before[1] == QtCore.QPointF(delta)
    assert link.adjust.called
    assert a.node().setGraphics.called and b.node().setGraphics.called
    b.setLocked(True)
    old = container.pos()
    container.setPos(old + QtCore.QPointF(25, 25))
    assert container.pos() == old


def test_round_trip_rebuilds_nested_hierarchy_with_arbitrary_drawing_order(canvas):
    node = device(canvas, 120, 80)
    shape = drawing(canvas, x=250, y=100)
    inner = group(canvas, [node, shape])
    note = drawing(canvas, "text", 400, 200)
    outer = group(canvas, [inner, note], "Site")
    outer.setPos(outer.pos() + QtCore.QPointF(50, 70))
    canvas._groups.save([outer])
    expected = {item: (item.parentItem(), item.pos(), item.scenePos()) for item in (node, shape, inner, note)}
    # Recreate objects from the same JSON drawing payloads used by the API and
    # server-side project export. Parent group intentionally arrives first.
    payloads = [item.__json__() for item in (outer, inner)]
    for item, payload in zip((outer, inner), payloads):
        payload["svg"] = item.toSvg()
    for item in (node, shape, inner, note):
        reparent(item, None)
    for item in (inner, outer):
        canvas.scene().removeItem(item)
    replacements = {}
    for payload in payloads:
        new = canvas.createDrawingItem("group", payload["x"], payload["y"], payload["z"],
                                       svg=payload["svg"], drawing_id=payload["drawing_id"])
        replacements[payload["drawing_id"]] = new
    canvas._groups.restore()
    for item in (node, shape, note):
        parent, local, scene = expected[item]
        assert item.parentItem() is replacements[parent.drawing_id()]
        assert item.pos() == local and item.scenePos() == scene
    assert replacements[inner.drawing_id()].parentItem() is replacements[outer.drawing_id()]


def test_local_alignment_and_api_acknowledgment(canvas):
    a, b = device(canvas, 120, 80), device(canvas, 260, 150)
    shape = drawing(canvas, x=300, y=240)
    container = group(canvas, [a, b, shape])
    canvas.enterGroup(container)
    a.setSelected(True)
    b.setSelected(True)
    canvas.horizontalAlignmentSlot()
    assert a.y() == b.y()
    absolute = a.scenePos()
    a.node().settings.return_value = {"x": absolute.x(), "y": absolute.y(), "z": 1}
    with patch.object(a, "setSymbol"), patch.object(a, "_updateLabel"):
        a.updatedSlot()
    assert a.scenePos() == absolute
    payload = shape.__json__()
    shape.updateDrawingCallback(payload)
    assert shape.scenePos() == QtCore.QPointF(payload["x"], payload["y"])
    assert shape.pos() == container.mapFromScene(shape.scenePos())
    canvas._groups.leave()
    assert not container.editing


def test_ungroup_preserves_scene_positions_and_nested_parent(canvas):
    node, shape = device(canvas, 100), drawing(canvas, x=200, y=50)
    inner = group(canvas, [node, shape])
    outer = group(canvas, [inner, drawing(canvas, x=400)], "Site")
    before = node.scenePos()
    canvas.enterGroup(outer)
    inner.setSelected(True)
    canvas.ungroupSelectedNodes()
    assert node.parentItem() is outer and shape.parentItem() is outer
    assert node.scenePos() == before
    assert inner.scene() is None


def test_recursive_delete_and_cancel(canvas):
    node, shape = device(canvas), drawing(canvas, x=100)
    inner = group(canvas, [node, shape])
    outer = group(canvas, [inner], "Site")
    with patch.object(QtWidgets.QMessageBox, "question", return_value=QtWidgets.QMessageBox.StandardButton.No):
        canvas.deleteActionSlot()
    assert node.scene() is canvas.scene()
    with patch.object(QtWidgets.QMessageBox, "question", return_value=QtWidgets.QMessageBox.StandardButton.Yes):
        canvas.deleteActionSlot()
    assert node.node().delete.called
    assert all(item.scene() is None for item in (shape, inner, outer))
    assert not canvas._groups.groups()


def test_drawing_only_recursive_duplicate(canvas):
    shape = drawing(canvas, x=100, y=120)
    note = drawing(canvas, "text", x=200, y=180)
    inner = group(canvas, [shape, note])
    outer = group(canvas, [inner], "Site")
    canvas.duplicateActionSlot()
    copy = canvas._groups.selected()[0]
    assert isinstance(copy, GroupItem) and copy.name == "Site"
    assert copy.drawing_id() != outer.drawing_id()
    assert copy.scenePos() == outer.scenePos() + QtCore.QPointF(20, 20)
    child = copy.members()[0]
    assert isinstance(child, GroupItem) and child.name == "LAN 1"
    assert len(child.members()) == 2
    assert {item.drawing_id() for item in child.members()}.isdisjoint({shape.drawing_id(), note.drawing_id()})
    assert sorted((item.x(), item.y()) for item in child.members()) == sorted((item.x(), item.y()) for item in inner.members())


def test_hierarchy_validation_is_atomic(canvas):
    node = device(canvas)
    first, second = group(canvas, [node]), group(canvas, [drawing(canvas)])
    first._members = [{"type": "group", "id": second.drawing_id(), "x": 0, "y": 0}]
    second._members = [{"type": "group", "id": first.drawing_id(), "x": 0, "y": 0}]
    with pytest.raises(ValueError, match="Cyclic"):
        canvas._groups.restore()
    assert first.parentItem() is None and node.parentItem() is first
    second._members = [{"type": "node", "id": node.node().node_id(), "x": 0, "y": 0}]
    first._members = second._members
    with pytest.raises(ValueError, match="more than one"):
        canvas._groups.restore()


def test_name_dialog_cancel_and_empty_name(canvas):
    a = device(canvas)
    a.setSelected(True)
    for answer in (("LAN", False), ("   ", True)):
        with patch.object(QtWidgets.QInputDialog, "getText", return_value=answer):
            canvas.groupSelectedNodes()
        assert a.parentItem() is None
    with patch.object(QtWidgets.QInputDialog, "getText", return_value=(" LAN 1 ", True)):
        canvas.groupSelectedNodes()
    assert a.parentItem().name == "LAN 1"


def test_enter_nested_group_edit_child_and_escape(canvas):
    a, b = device(canvas, 100, 80), device(canvas, 200, 80)
    inner = group(canvas, [a, b])
    outer = group(canvas, [inner, drawing(canvas, x=400)], "Site")
    canvas.enterGroup(inner)
    assert inner.editing and outer.editing
    QtWidgets.QApplication.processEvents()
    initial = a.pos()
    start = canvas.mapFromScene(a.sceneBoundingRect().center())
    delta = QtCore.QPoint(30, 20)
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(canvas.viewport(), start + delta)
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start + delta)
    assert a.pos() == initial + QtCore.QPointF(delta)
    assert b.pos() != a.pos()
    QTest.keyClick(canvas, QtCore.Qt.Key.Key_Escape)
    assert not inner.editing and not outer.editing and canvas._groups.editing is None


def test_portable_import_remaps_all_server_ids(canvas):
    node = device(canvas, 100, 80)
    shape = drawing(canvas, x=200, y=100)
    inner = group(canvas, [node, shape])
    outer = group(canvas, [inner], "Site")
    payloads = [item.__json__() for item in (outer, inner, shape)]
    for item, payload in zip((outer, inner, shape), payloads):
        if "svg" not in payload:
            item._hash_svg = None
            payload.update(item.__json__())
    before = node.scenePos()
    for item in (node, shape, inner):
        reparent(item, None)
    for item in (shape, inner, outer):
        canvas.scene().removeItem(item)
    node.node().node_id.return_value = str(uuid.uuid4())
    loaded = []
    for payload, kind in zip(payloads, ("group", "group", "rect")):
        loaded.append(canvas.createDrawingItem(kind, payload["x"], payload["y"], payload["z"],
                      svg=payload["svg"], drawing_id=str(uuid.uuid4())))
    canvas._groups.restore()
    new_outer, new_inner, new_shape = loaded
    assert node.parentItem() is new_inner and new_shape.parentItem() is new_inner
    assert new_inner.parentItem() is new_outer and node.scenePos() == before
    assert read_group(new_inner.toSvg())["drawing_id"] == new_inner.drawing_id()
    assert {child["id"] for child in read_group(new_inner.toSvg())["children"]} == {node.node().node_id(), new_shape.drawing_id()}


def test_async_node_duplicate_waits_for_all_ids_and_restores_internal_link(canvas):
    a, b = device(canvas, 100), device(canvas, 200)
    inner = group(canvas, [a, b])
    outer = group(canvas, [inner], "Site")
    source_port, destination_port = MagicMock(), MagicMock()
    for port in (source_port, destination_port):
        port.adapterNumber.return_value = 0
        port.portNumber.return_value = 1
    link = MagicMock()
    link.sourceNode.return_value, link.destinationNode.return_value = a.node(), b.node()
    link.sourcePort.return_value, link.destinationPort.return_value = source_port, destination_port
    canvas._topology.links.return_value = [link]
    canvas.addLink = MagicMock()
    canvas.duplicateActionSlot()
    callback_a = a.node().duplicate.call_args.kwargs["callback"]
    callback_b = b.node().duplicate.call_args.kwargs["callback"]
    a_copy, b_copy = device(canvas, 120), device(canvas, 220)
    a_copy.node().ports.return_value = [source_port]
    b_copy.node().ports.return_value = [destination_port]
    canvas._topology.getNodeFromUuid.return_value = a_copy.node()
    callback_a({"node_id": a_copy.node().node_id()})
    assert a_copy.parentItem() is None and not canvas.addLink.called
    callback_b({"node_id": b_copy.node().node_id()})
    assert a_copy.parentItem() is b_copy.parentItem()
    assert a_copy.parentItem() is not inner
    assert a_copy.parentItem().parentItem() is not outer
    canvas.addLink.assert_called_once_with(a_copy.node(), source_port, b_copy.node(), destination_port)


def test_async_duplicate_failure_rolls_back_successful_copies(canvas):
    a, b = device(canvas, 100), device(canvas, 200)
    group(canvas, [a, b])
    canvas.duplicateActionSlot()
    copied = device(canvas, 120)
    canvas._topology.getNodeFromUuid.return_value = copied.node()
    a.node().duplicate.call_args.kwargs["callback"]({"node_id": copied.node().node_id()})
    with patch.object(QtWidgets.QMessageBox, "warning"):
        b.node().duplicate.call_args.kwargs["callback"]({"message": "failure"}, error=True)
    copied.node().delete.assert_called_once()
    assert len(canvas._groups.groups()) == 1


def test_invalid_metadata_and_stale_acknowledgment(canvas):
    container = group(canvas, [drawing(canvas)])
    svg = container.toSvg()
    for bad in (svg.replace('"version": 1', '"version": 99'),
                svg.replace('"x": 0.5', '"x": NaN')):
        if bad != svg:
            with pytest.raises(ValueError):
                read_group(bad)
    payload = container.__json__()
    payload["svg"] = container.toSvg()
    old_position = container.pos()
    container.setPos(old_position + QtCore.QPointF(30, 40))
    container.updateDrawing()
    container.updateDrawingCallback(payload)
    assert container.pos() == old_position + QtCore.QPointF(30, 40)


def test_drag_closed_nested_container_and_double_click_one_level(canvas):
    a, b = device(canvas, 100, 80), device(canvas, 200, 80)
    inner = group(canvas, [a, b])
    outer = group(canvas, [inner, drawing(canvas, x=400)], "Site")
    canvas.scene().clearSelection()
    QtWidgets.QApplication.processEvents()
    before, local = a.scenePos(), a.pos()
    start = canvas.mapFromScene(a.sceneBoundingRect().center())
    delta = QtCore.QPoint(30, 20)
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(canvas.viewport(), start + delta)
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start + delta)
    assert a.scenePos() == before + QtCore.QPointF(delta) and a.pos() == local
    assert outer.isSelected() and not inner.isSelected() and not a.isSelected()
    start = canvas.mapFromScene(a.sceneBoundingRect().center())
    QTest.mouseDClick(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    assert outer.editing and not inner.editing
    QTest.mouseDClick(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    assert inner.editing and canvas._groups.editing is inner
