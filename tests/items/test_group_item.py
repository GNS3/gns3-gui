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
    assert isinstance(copy, GroupItem) and copy.name == "Copy of Site"
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
    with patch("gns3.canvas_groups.GroupPropertiesDialog.getProperties", return_value=None):
        canvas.groupSelectedNodes()
    assert a.parentItem() is None
    with patch("gns3.canvas_groups.GroupPropertiesDialog.getProperties", return_value=("LAN 1", 250, 160)):
        canvas.groupSelectedNodes()
    assert a.parentItem().name == "LAN 1"
    assert a.parentItem().rect().width() == 250


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


@pytest.mark.parametrize("entry", ["canvas", "summary"])
def test_async_node_duplicate_waits_for_all_ids_and_restores_internal_link(canvas, summary, entry):
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
    if entry == "summary":
        summary.groupMenu(outer).actions()[1].trigger()
    else:
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
    copied_outer = a_copy.parentItem().parentItem()
    assert copied_outer.name == "Copy of Site"
    assert a_copy.pos() == a.pos() and b_copy.pos() == b.pos()
    assert a.parentItem() is inner and inner.parentItem() is outer
    canvas.addLink.assert_called_once_with(a_copy.node(), source_port, b_copy.node(), destination_port)
    # Notifications/reload must preserve the copied ownership, not just its
    # immediate appearance while the operation is completing.
    canvas._groups.restore()
    assert a_copy.parentItem().parentItem() is copied_outer
    row = add_summary_node(summary, canvas, a_copy, 101)
    assert row.parent().group is a_copy.parentItem()
    assert row.parent().parent().group is copied_outer


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


def test_duplicate_names_distinguish_repeated_copies_without_renaming_original(canvas):
    original = group(canvas, [drawing(canvas)], "LAN 1")
    canvas.duplicateActionSlot()
    first = canvas._groups.selected()[0]
    assert first.name == "Copy of LAN 1"
    canvas.scene().clearSelection()
    original.setSelected(True)
    canvas.duplicateActionSlot()
    second = canvas._groups.selected()[0]
    assert second.name == "Copy 2 of LAN 1"
    assert original.name == "LAN 1"
    assert read_group(second.toSvg())["name"] == second.name


def test_invalid_metadata_and_stale_acknowledgment(canvas):
    container = group(canvas, [drawing(canvas)])
    svg = container.toSvg()
    import copy
    import xml.etree.ElementTree as ET
    for key, value in (("version", 99), ("size", {"width": -1, "height": 100}),
                       ("origin", {"x": float("nan"), "y": 0})):
        data = copy.deepcopy(read_group(svg))
        data[key] = value
        root = ET.fromstring(svg)
        metadata = next(element for element in root.iter() if element.get("id") == "gns3-canvas-group")
        metadata.text = json.dumps(data)
        with pytest.raises(ValueError):
            read_group(ET.tostring(root, encoding="unicode"))
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


def test_fixed_dimensions_margin_and_child_clipping(canvas):
    from gns3.qt import QtGui
    from gns3.items.group_item import set_scene_position
    child = drawing(canvas, x=0, y=0)
    _, width, height = canvas._groups.initialGeometry([child])
    assert width >= child.sceneBoundingRect().width() * 1.3
    assert height >= child.sceneBoundingRect().height() * 1.3 + GroupItem.TITLE_HEIGHT
    container = group(canvas, [child])
    assert container.rect().width() == width and container.rect().height() == height
    rect = container.rect()
    child.setPos(child.pos() + QtCore.QPointF(400, 300))
    assert container.rect() == rect
    set_scene_position(container, QtCore.QPointF(0, 0))
    container.setDimensions(100, 100)
    child.setRect(0, 0, 80, 40)
    child.setPen(QtGui.QPen(QtCore.Qt.PenStyle.NoPen))
    child.setBrush(QtGui.QColor("#ff0000"))
    child.setPos(80, 40)
    image = QtGui.QImage(160, 120, QtGui.QImage.Format.Format_ARGB32)
    image.fill(QtGui.QColor("white"))
    painter = QtGui.QPainter(image)
    canvas.scene().render(painter, QtCore.QRectF(0, 0, 160, 120), QtCore.QRectF(0, 0, 160, 120))
    painter.end()
    assert image.pixelColor(90, 60).name() == "#ff0000"
    assert image.pixelColor(130, 60).name() == "#ffffff"
    assert container.flags() & QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape


@pytest.mark.parametrize("corner,delta,expected", [
    ("br", (30, 20), (230, 180)), ("tl", (30, 20), (170, 140)),
    ("tr", (30, 20), (230, 140)), ("bl", (30, 20), (170, 180)),
])
def test_resize_each_corner_preserves_child_scene_position(canvas, corner, delta, expected):
    child = drawing(canvas)
    container = canvas._groups.add("Fixed", [child], position=QtCore.QPointF(-100, -80), width=200, height=160)
    before = child.scenePos()
    QtWidgets.QApplication.processEvents()
    point = canvas.mapFromScene(container.mapToScene(container.corners()[corner]))
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=point)
    assert canvas._groups._resize is not None
    QTest.mouseMove(canvas.viewport(), point + QtCore.QPoint(*delta))
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=point + QtCore.QPoint(*delta))
    assert (container.rect().width(), container.rect().height()) == expected
    assert child.scenePos() == before
    assert canvas._groups._resize is None
    saved = read_group(container.toSvg())
    assert saved["size"] == {"width": expected[0], "height": expected[1]}
    loaded = GroupItem(svg=container.toSvg())
    assert loaded.rect() == container.rect()


def test_title_double_click_renames_and_outside_click_clears_editing(canvas):
    a, b = device(canvas), device(canvas, 100)
    container = group(canvas, [a, b])
    QtWidgets.QApplication.processEvents()
    title = canvas.mapFromScene(container.mapToScene(container.labelRect().center()))
    with patch("gns3.canvas_groups.GroupPropertiesDialog.getProperties", return_value=("Renamed", 300, 200)):
        QTest.mouseDClick(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=title)
    assert container.name == "Renamed" and container.rect().width() == 300
    canvas.enterGroup(container)
    outside = canvas.mapFromScene(container.mapToScene(QtCore.QPointF(-30, -30)))
    QTest.mouseClick(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=outside)
    assert canvas._groups.editing is None and not container.editing


def test_direct_parent_guides_snap_and_disappear_on_release(canvas):
    node = device(canvas)
    inner = group(canvas, [node])
    outer = group(canvas, [inner, drawing(canvas, x=300)], "Site")
    inner.setDimensions(200, 160)
    canvas.enterGroup(inner)
    QtWidgets.QApplication.processEvents()
    start = canvas.mapFromScene(node.sceneBoundingRect().center())
    destination = canvas.mapFromScene(inner.mapToScene(inner.rect().center())) + QtCore.QPoint(3, -2)
    before_svg = inner.toSvg()
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(canvas.viewport(), destination)
    assert canvas._groups.guide_parent is inner
    assert canvas._groups.guide_parent is not outer
    center = node.mapRectToParent(node.boundingRect()).center()
    assert center == inner.rect().center()
    assert len(inner.members()) == 1
    # Guides are view-only, never serialized as topology elements.
    assert "e53935" not in inner.toSvg() and "guide" not in inner.toSvg()
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=destination)
    assert canvas._groups.guide_parent is None
    assert canvas._groups._drag_item is None


def test_v1_group_migrates_once_to_fixed_frame(canvas):
    import xml.etree.ElementTree as ET
    node = device(canvas)
    container = group(canvas, [node])
    before = node.scenePos()
    root = ET.fromstring(container.toSvg())
    metadata = next(element for element in root.iter() if element.get("id") == "gns3-canvas-group")
    data = json.loads(metadata.text)
    data["version"] = 1
    data.pop("size")
    metadata.text = json.dumps(data)
    container.fromSvg(ET.tostring(root, encoding="unicode"))
    canvas._groups.restore()
    assert node.scenePos() == before
    rect = container.rect()
    node.setPos(node.pos() + QtCore.QPointF(400, 400))
    assert container.rect() == rect
    assert read_group(container.toSvg())["version"] == 2


@pytest.fixture
def summary(canvas):
    from gns3.topology_summary_view import TopologySummaryView
    # Use real (synchronous in tests) topology signals, not MagicMock.connect.
    canvas._topology.hierarchy_changed_signal = QtCore.Signal()
    with patch("gns3.topology_summary_view.Topology.instance", return_value=canvas._topology):
        tree = TopologySummaryView(None)
    yield tree
    tree.deleteLater()


def add_summary_node(summary, canvas, node, identity):
    node.node().id.return_value = identity
    node.node().links.return_value = []
    node.node().consoleType.return_value = "none"
    canvas._topology.getNode.return_value = node.node()
    summary._nodeAddedSlot(identity)
    return summary._node_items[identity]


def test_summary_nested_groups_ports_and_group_actions(canvas, summary):
    from gns3.topology_summary_view import TopologyGroupItem
    node = device(canvas)
    row = add_summary_node(summary, canvas, node, 12)
    # Preserve an existing port row while the device changes hierarchy.
    port_row = QtWidgets.QTreeWidgetItem(row, ["Ethernet0"])
    inner = group(canvas, [node], "LAN 1")
    outer = group(canvas, [inner, drawing(canvas, x=300)], "Site")
    assert summary.topLevelItemCount() == 1
    top = summary.topLevelItem(0)
    assert isinstance(top, TopologyGroupItem) and top.group is outer
    assert row.parent().group is inner and row.parent().parent() is top
    assert row.child(0) is port_row
    menu = summary.groupMenu(inner)
    assert [action.text() for action in menu.actions()] == ["Rename group", "Duplicate", "Delete"]
    with patch("gns3.canvas_groups.GroupPropertiesDialog.getProperties", return_value=("LAN renamed", 220, 180)):
        menu.actions()[0].trigger()
    assert row.parent().text(0) == "LAN renamed"
    with patch("gns3.canvas_groups.GroupPropertiesDialog.getProperties", return_value=("Site renamed", 600, 400)):
        summary._itemDoubleClickedSlot(top, 0)
    assert outer.name == "Site renamed" and top.text(0) == "Site renamed"
    with patch.object(canvas, "duplicateActionSlot") as duplicate:
        summary.groupMenu(inner).actions()[1].trigger()
        duplicate.assert_called_once()
        assert canvas._groups.selected() == [inner]
    with patch.object(canvas, "deleteActionSlot") as delete:
        summary.groupMenu(inner).actions()[2].trigger()
        delete.assert_called_once()
        assert canvas._groups.selected() == [inner]
    row.setExpanded(True)
    canvas._groups.save([outer])
    assert row.isExpanded() and row.child(0) is port_row


def test_summary_filters_and_nested_node_removal(canvas, summary):
    a, b = device(canvas), device(canvas, 100)
    row_a = add_summary_node(summary, canvas, a, 13)
    row_b = add_summary_node(summary, canvas, b, 14)
    container = group(canvas, [a, b])
    summary.show_only_devices_with_capture = True
    summary.refreshAllLinks()
    assert summary._group_items[container.drawing_id()].isHidden()
    summary.show_only_devices_with_capture = False
    summary.refreshAllLinks()
    assert not summary._group_items[container.drawing_id()].isHidden()
    row_a._deletedNodeSlot()
    assert 13 not in summary._node_items and 13 not in summary.nodes_id
    assert row_b.parent() is summary._group_items[container.drawing_id()]
    summary._projectChangedSlot()
    assert summary.topLevelItemCount() == 0
    assert not summary.nodes_id and not summary._group_items


def test_duplicate_nested_group_retains_parent_and_fixed_dimensions(canvas):
    inner = group(canvas, [drawing(canvas)], "LAN")
    outer = group(canvas, [inner, drawing(canvas, x=300)], "Site")
    inner.setDimensions(140, 110)
    canvas.enterGroup(outer)
    inner.setSelected(True)
    canvas.duplicateActionSlot()
    copy = canvas._groups.selected()[0]
    assert copy is not inner and isinstance(copy, GroupItem)
    assert copy.parentItem() is outer
    assert copy.pos() == inner.pos() + QtCore.QPointF(20, 20)
    assert copy.rect() == inner.rect()


def test_creation_acknowledgment_precedes_drawing_updates(canvas):
    project = MagicMock()
    container = GroupItem(name="Copy", project=project)
    canvas.scene().addItem(container)
    container.create()
    posted = project.post.call_args.kwargs["body"]
    acknowledge = project.post.call_args.args[1]
    container.name = "Edited while creating"
    container.setDimensions(350, 240)
    container.updateDrawing()
    container.updateDrawing()
    assert project.post.call_count == 1
    assert not project.put.called  # no PUT to a UUID not yet present on the server
    acknowledge(posted)
    assert project.put.call_count == 1
    latest = project.put.call_args.kwargs["body"]
    assert read_group(latest["svg"])["name"] == "Edited while creating"
    assert read_group(latest["svg"])["size"] == {"width": 350, "height": 240}
    assert container.rect().width() == 350


def test_duplicate_queues_all_drawing_updates_until_post_ack(canvas):
    shape = drawing(canvas)
    original = group(canvas, [shape])
    project = MagicMock()
    canvas._topology.project.return_value = project
    canvas.duplicateActionSlot()
    assert project.post.call_count == 2  # one group and one shape
    assert not project.put.called
    requests = list(project.post.call_args_list)
    for call in reversed(requests):  # deliberately acknowledge children before parents
        call.args[1](call.kwargs["body"])
    assert project.put.call_count == 2
    copy = canvas._groups.selected()[0]
    assert copy.drawing_id() != original.drawing_id()
    assert len(copy.members()) == 1
    assert read_group(copy.toSvg())["children"][0]["id"] == copy.members()[0].drawing_id()


def test_delete_drawing_while_creation_is_pending_cleans_server_copy(canvas):
    project = MagicMock()
    shape = canvas.createDrawingItem("rect", 0, 0, 0, create=False)
    shape._project = project
    shape.create()
    acknowledge = project.post.call_args.args[1]
    posted = project.post.call_args.kwargs["body"]
    shape.delete()
    assert not project.delete.called
    acknowledge(posted)
    project.delete.assert_called_once_with("/drawings/" + shape.drawing_id(), None)


def test_dimension_inputs_remain_white_under_dark_parent_style(canvas):
    from gns3.qt import QtGui
    from gns3.dialogs.group_properties_dialog import GroupPropertiesDialog
    dialog = GroupPropertiesDialog(canvas, "LAN", 400, 250)
    dialog.setStyleSheet("QDoubleSpinBox {background-color: #222222; color: #eeeeee;}")
    for field in (dialog.widthEdit, dialog.heightEdit):
        field.ensurePolished()
        assert field.palette().color(QtGui.QPalette.ColorRole.Base).name() == "#ffffff"
        assert field.palette().color(QtGui.QPalette.ColorRole.Text).name() == "#000000"
    assert not dialog.nameEdit.styleSheet()  # override is scoped to dimensions
    dialog.deleteLater()


def test_template_drag_highlight_guides_and_async_group_insertion(canvas):
    from gns3.qt import QtGui
    container = group(canvas, [drawing(canvas)])
    mime = QtCore.QMimeData()
    mime.setData("application/x-gns3-template", b"test-template")
    scene_point = container.mapToScene(container.rect().center())
    point = canvas.mapFromScene(scene_point)
    enter = QtGui.QDragEnterEvent(point, QtCore.Qt.DropAction.CopyAction, mime,
                                 QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.KeyboardModifier.NoModifier)
    QtWidgets.QApplication.sendEvent(canvas.viewport(), enter)
    before = container.toSvg()
    move = QtGui.QDragMoveEvent(point, QtCore.Qt.DropAction.CopyAction, mime,
                               QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.KeyboardModifier.NoModifier)
    QtWidgets.QApplication.sendEvent(canvas.viewport(), move)
    assert container.drop_hover and canvas._groups.guide_parent is container
    assert container.toSvg() == before
    manager = MagicMock()
    manager.createNodeFromTemplateId.return_value = True
    local = container.mapFromScene(canvas.mapToScene(point))
    drop = QtGui.QDropEvent(QtCore.QPointF(point), QtCore.Qt.DropAction.CopyAction, mime,
                           QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.KeyboardModifier.NoModifier)
    with patch("gns3.graphics_view.TemplateManager.instance", return_value=manager):
        QtWidgets.QApplication.sendEvent(canvas.viewport(), drop)
    assert drop.isAccepted()
    assert not container.drop_hover and canvas._groups.guide_parent is None
    callback = manager.createNodeFromTemplateId.call_args.kwargs["callback"]
    # Only the node returned by this request is adopted; moving the group while
    # waiting must retain the original local drop location.
    container.setPos(container.pos() + QtCore.QPointF(70, 30))
    node = device(canvas, 300, 200)
    canvas._topology.getNodeFromUuid.return_value = node.node()
    callback({"node_id": node.node().node_id()})
    assert node.parentItem() is container and node.pos() == local


def test_template_hover_prefers_nested_group_and_clears_on_leave(canvas):
    from gns3.qt import QtGui
    inner = group(canvas, [drawing(canvas)])
    outer = group(canvas, [inner, drawing(canvas, x=350)], "Site")
    canvas._groups.setDropTarget(inner.mapToScene(inner.rect().center()))
    assert canvas._groups.drop_target is inner and inner.drop_hover and not outer.drop_hover
    canvas.dragLeaveEvent(QtGui.QDragLeaveEvent())
    assert not inner.drop_hover and canvas._groups.drop_target is None
    assert canvas._groups.guide_parent is None
    canvas._groups.setDropTarget(inner.mapToScene(inner.rect().center()))
    mime = QtCore.QMimeData()
    mime.setUrls([QtCore.QUrl.fromLocalFile("/tmp/example.gns3")])
    move = QtGui.QDragMoveEvent(QtCore.QPoint(0, 0), QtCore.Qt.DropAction.CopyAction, mime,
                               QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.KeyboardModifier.NoModifier)
    canvas.dragMoveEvent(move)
    assert not inner.drop_hover and canvas._groups.guide_parent is None


@pytest.mark.parametrize("delta", [QtCore.QPoint(240, 0), QtCore.QPoint(-240, 0),
                                    QtCore.QPoint(0, 200), QtCore.QPoint(0, -200)])
def test_device_drag_outside_group_detaches_on_release_and_persists(canvas, summary, delta):
    node = device(canvas, 100, 100)
    row = add_summary_node(summary, canvas, node, 201)
    container = group(canvas, [node])
    link = MagicMock()
    node._links.append(link)
    canvas.enterGroup(container)
    QtWidgets.QApplication.processEvents()
    start = canvas.mapFromScene(node.sceneBoundingRect().center())
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(canvas.viewport(), start + delta)
    before_release = node.scenePos()
    assert node.parentItem() is container  # Ownership changes only on release.
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start + delta)
    assert node.parentItem() is None and node.scenePos() == before_release
    assert read_group(container.toSvg())["children"] == []
    assert row.parent() is None
    assert link.adjust.called and node.node().setGraphics.called
    canvas._groups.restore()
    assert node.parentItem() is None
    assert not canvas._groups._drag_nodes and canvas._groups.guide_parent is None


@pytest.mark.parametrize("outside_outer", [False, True])
def test_drag_out_of_nested_group_uses_nearest_containing_ancestor(canvas, outside_outer):
    node = device(canvas, 100, 100)
    inner = group(canvas, [node])
    outer = group(canvas, [inner, drawing(canvas, x=400, y=300)], "Site")
    canvas.enterGroup(inner)
    QtWidgets.QApplication.processEvents()
    start = canvas.mapFromScene(node.sceneBoundingRect().center())
    target = outer.mapToScene(outer.rect().center())
    if outside_outer:
        target = outer.mapToScene(outer.rect().bottomRight() + QtCore.QPointF(40, 40))
    end = canvas.mapFromScene(target)
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(canvas.viewport(), end)
    before_release = node.scenePos()
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
    assert node.parentItem() is (None if outside_outer else outer)
    assert node.scenePos() == before_release and inner.members() == []
    canvas._groups.restore()
    assert node.parentItem() is (None if outside_outer else outer)


@pytest.mark.parametrize("selected,editing", [(False, False), (True, False), (False, True), (True, True)])
def test_template_drop_highlight_border_is_continuous_and_temporary(canvas, selected, editing):
    from gns3.qt import QtGui
    container = group(canvas, [drawing(canvas)])
    canvas.scene().clearSelection()
    container.setSelected(selected)
    container.setEditing(editing)
    container.setPos(20, 20)
    container.setDimensions(160, 100)

    def border_colors(x=180):
        image = QtGui.QImage(200, 150, QtGui.QImage.Format.Format_ARGB32)
        image.fill(QtGui.QColor("white"))
        painter = QtGui.QPainter(image)
        canvas.scene().render(painter, QtCore.QRectF(0, 0, 200, 150), QtCore.QRectF(0, 0, 200, 150))
        painter.end()
        return [image.pixelColor(x, y).name() for y in range(35, 100)]

    assert set(border_colors()) == {"#3484c6"}
    canvas._groups.setDropTarget(container.mapToScene(container.rect().center()))
    assert set(border_colors()) == {"#3484c6"}
    assert set(border_colors(181)) == {"#3484c6"}
    canvas._groups.clearDropTarget()
    assert set(border_colors()) == {"#3484c6"}


@pytest.mark.parametrize("move", [False, True])
def test_device_click_or_partial_overflow_keeps_group_membership(canvas, move):
    node = device(canvas, 100, 100)
    container = group(canvas, [node])
    canvas.enterGroup(container)
    QtWidgets.QApplication.processEvents()
    start = canvas.mapFromScene(node.sceneBoundingRect().center())
    end = start
    if move:
        # Part of the symbol overflows, but its center remains inside.
        center = container.mapToScene(QtCore.QPointF(container.rect().right() - 2,
                                                    container.rect().center().y()))
        end = canvas.mapFromScene(center)
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    if move:
        QTest.mouseMove(canvas.viewport(), end)
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
    assert node.parentItem() is container
    assert read_group(container.toSvg())["children"][0]["id"] == node.node().node_id()


def test_exiting_device_preview_is_unclipped_without_exposing_other_children(canvas, tmp_path):
    from gns3.qt import QtGui
    from gns3.qt.qimage_svg_renderer import QImageSvgRenderer
    symbol = tmp_path / "drag-symbol.svg"
    symbol.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><rect width="40" height="40" fill="#00ff00"/></svg>')
    renderer = QImageSvgRenderer(str(symbol))
    node, hidden = device(canvas), device(canvas)
    node.setSharedRenderer(renderer)
    hidden.setSharedRenderer(renderer)
    container = group(canvas, [node, hidden])
    container.setPos(20, 20)
    container.setDimensions(100, 100)
    node.setPos(60, 40)
    hidden.setPos(160, 80)
    label = QtWidgets.QGraphicsRectItem(0, 0, 10, 10, node)
    label.setPos(0, 45)
    label.setBrush(QtGui.QColor("red"))
    label.setPen(QtGui.QPen(QtCore.Qt.PenStyle.NoPen))
    canvas.enterGroup(container)
    QtWidgets.QApplication.processEvents()
    start = canvas.mapFromScene(node.sceneBoundingRect().center())
    end = start + QtCore.QPoint(50, 0)
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(canvas.viewport(), end)
    assert container.exit_hover and node in canvas._groups._outside_nodes
    assert node.parentItem() is container
    assert "exit_hover" not in container.toSvg()
    image = QtGui.QImage(300, 200, QtGui.QImage.Format.Format_ARGB32)
    image.fill(QtGui.QColor("white"))
    painter = QtGui.QPainter(image)
    canvas.scene().render(painter, QtCore.QRectF(0, 0, 300, 200), QtCore.QRectF(0, 0, 300, 200))
    canvas._groups.drawDragPreviews(painter)
    painter.end()
    assert image.pixelColor(165, 95).name() == "#00ff00"
    assert image.pixelColor(135, 110).name() == "#ff0000"
    assert image.pixelColor(190, 110).name() == "#ffffff"
    assert image.pixelColor(120, 40).name() == "#e53935"
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
    assert node.parentItem() is None and not container.exit_hover
    assert not canvas._groups._outside_nodes


@pytest.mark.parametrize("from_group", [False, True])
def test_existing_device_drop_into_group_previews_and_persists(canvas, summary, from_group):
    node = device(canvas, 30, 50)
    row = add_summary_node(summary, canvas, node, 301)
    source = group(canvas, [node], "Source") if from_group else None
    target = group(canvas, [drawing(canvas, x=280, y=120)], "Target")
    if source:
        canvas.enterGroup(source)
    else:
        canvas.scene().clearSelection()
    QtWidgets.QApplication.processEvents()
    start = canvas.mapFromScene(node.sceneBoundingRect().center())
    end = canvas.mapFromScene(target.mapToScene(target.rect().center()))
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(canvas.viewport(), end)
    position = node.scenePos()
    assert node.parentItem() is source
    assert target.drop_hover and canvas._groups.guide_parent is target
    if source:
        assert source.exit_hover
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
    assert node.parentItem() is target and node.scenePos() == position
    assert row.parent().group is target
    assert not target.drop_hover and (source is None or not source.exit_hover)
    canvas._groups.restore()
    assert node.parentItem() is target


def test_drag_back_into_original_group_clears_exit_preview(canvas):
    node = device(canvas, 100, 100)
    container = group(canvas, [node])
    canvas.enterGroup(container)
    QtWidgets.QApplication.processEvents()
    start = canvas.mapFromScene(node.sceneBoundingRect().center())
    QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(canvas.viewport(), start + QtCore.QPoint(200, 0))
    assert container.exit_hover
    QTest.mouseMove(canvas.viewport(), start)
    assert not container.exit_hover and not container.drop_hover
    assert not canvas._groups._outside_nodes
    QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
    assert node.parentItem() is container


@pytest.mark.parametrize("cancel_dialog", [False, True])
def test_toolbar_groups_exact_rubber_band_selection_on_release(canvas, cancel_dialog):
    from gns3.main_window import MainWindow
    a, b = device(canvas, 100, 100), device(canvas, 220, 100)
    note = drawing(canvas, "text", 100, 180)
    outside = device(canvas, 600, 400)
    main = canvas._main_window
    main.uiAnnotationToolBar = QtWidgets.QToolBar(canvas.window())
    main.uiAnnotateMenu = QtWidgets.QMenu(canvas.window())
    canvas.window().addToolBar(main.uiAnnotationToolBar)
    MainWindow._setupNodeGroupingActions(main)
    canvas.window().show()
    QtWidgets.QApplication.processEvents()
    button = main.uiAnnotationToolBar.widgetForAction(main.uiGroupNodesAction)
    result = None if cancel_dialog else ("Selected LAN", 400, 300)
    with patch("gns3.canvas_groups.GroupPropertiesDialog.getProperties", return_value=result) as dialog:
        QTest.mouseClick(button, QtCore.Qt.MouseButton.LeftButton)
        assert canvas._groups.selection_pending and not dialog.called
        start = canvas.mapFromScene(QtCore.QPointF(60, 60))
        end = canvas.mapFromScene(QtCore.QPointF(350, 240))
        QTest.mousePress(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
        QTest.mouseMove(canvas.viewport(), end)
        assert not dialog.called
        assert set(canvas._groups.selected()) == {a, b, note}
        QTest.mouseRelease(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
        dialog.assert_called_once()
    if cancel_dialog:
        assert not canvas._groups.groups()
        assert set(canvas._groups.selected()) == {a, b, note}
    else:
        container = canvas._groups.groups()[0]
        assert set(container.members()) == {a, b, note} and outside.parentItem() is None
    assert not canvas._groups.selection_pending and not button.isDown()
    # Ordinary selection after consuming the request must not reopen the dialog.
    with patch("gns3.canvas_groups.GroupPropertiesDialog.getProperties") as dialog:
        QTest.mouseClick(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=canvas.mapFromScene(outside.sceneBoundingRect().center()))
        dialog.assert_not_called()


@pytest.mark.parametrize("cancel_dialog", [False, True])
def test_group_request_with_preselection_remains_immediate(canvas, cancel_dialog):
    node = device(canvas, 100, 100)
    node.setSelected(True)
    result = None if cancel_dialog else ("LAN", 200, 150)
    with patch("gns3.canvas_groups.GroupPropertiesDialog.getProperties", return_value=result) as dialog:
        canvas.groupSelectedNodes()
        dialog.assert_called_once()
    assert not canvas._groups.selection_pending
    assert bool(canvas._groups.groups()) is not cancel_dialog
    assert node.isSelected() if cancel_dialog else node.parentItem() is not None


def test_group_selection_empty_release_and_escape(canvas):
    canvas.groupSelectedNodes()
    with patch("gns3.canvas_groups.GroupPropertiesDialog.getProperties") as dialog:
        QTest.mouseClick(canvas.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=QtCore.QPoint(30, 30))
        assert canvas._groups.selection_pending
        QTest.keyClick(canvas, QtCore.Qt.Key.Key_Escape)
        assert not canvas._groups.selection_pending
        dialog.assert_not_called()
