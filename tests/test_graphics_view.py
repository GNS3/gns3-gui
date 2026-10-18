#!/usr/bin/env python
#
# Copyright (C) 2017 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from unittest.mock import MagicMock, patch
import pytest
from gns3.qt import QtCore, QtGui, QtWidgets
from gns3.graphics_view import GraphicsView
from gns3.node import Node


def test_console_to_node_vncviewer_and_ipv6():
    node = MagicMock(
        initialized=MagicMock(return_value=True),
        status=MagicMock(return_value=Node.started),
        consoleCommand=MagicMock(return_value="vncviewer"),
        consoleHost=MagicMock(return_value="::1")
    )
    view = GraphicsView.__new__(GraphicsView)
    with patch('gns3.qt.QtWidgets.QMessageBox.warning') as warning_mock:
        view.consoleToNode(node)
        assert warning_mock.called
        assert warning_mock.call_args[0][1] == 'TightVNC'


@pytest.fixture
def zoom_view(main_window):
    window = QtWidgets.QMainWindow()
    central = QtWidgets.QWidget(window)
    window.setCentralWidget(central)
    view = GraphicsView(central)
    view._main_window = main_window
    view._topology = MagicMock()
    view.setGeometry(0, 0, 800, 600)
    window.resize(820, 620)
    window.show()
    QtWidgets.QApplication.processEvents()
    yield view
    window.close()


def wheel(view, position, delta, modifiers=QtCore.Qt.KeyboardModifier.ControlModifier):
    event = QtGui.QWheelEvent(QtCore.QPointF(position), QtCore.QPointF(view.viewport().mapToGlobal(position)),
                             QtCore.QPoint(), QtCore.QPoint(0, delta), QtCore.Qt.MouseButton.NoButton,
                             modifiers, QtCore.Qt.ScrollPhase.NoScrollPhase, False)
    QtWidgets.QApplication.sendEvent(view.viewport(), event)
    return event


@pytest.mark.parametrize("position", [QtCore.QPoint(80, 90), QtCore.QPoint(690, 480)])
@pytest.mark.parametrize("scene_size", [(2000, 1000), (100, 80)])
@pytest.mark.parametrize("initial_scale", [.2, 1, 5])
def test_control_wheel_centers_selected_scene_region(zoom_view, position, scene_size, initial_scale):
    view = zoom_view
    view.setSceneSize(*scene_size)
    view.scale(initial_scale, initial_scale)
    original_scene = view.scene().sceneRect()
    view.centerOn(original_scene.bottomRight())
    point = view.mapToScene(position)
    # No mouse-move event: cached/global cursor coordinates must not decide zoom.
    for delta in (120, 120, -120, -120):
        assert wheel(view, position, delta).isAccepted()
        error = view.mapFromScene(point) - view.viewport().rect().center()
        assert abs(error.x()) <= 2 and abs(error.y()) <= 2
    assert view.transform().m11() == pytest.approx(initial_scale)
    assert view.scene().sceneRect() == original_scene
    assert view.transformationAnchor() == QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse
    assert view._topology.project().setZoom.call_args.args == (round(initial_scale * 100),)


def test_wheel_zoom_limits_do_not_move_view_or_save_project(zoom_view):
    view = zoom_view
    position = QtCore.QPoint(120, 100)
    for scale, delta in ((.1, -120), (10, 120)):
        view.resetTransform()
        view.scale(scale, scale)
        before = view.viewportTransform()
        view._topology.project().reset_mock()
        wheel(view, position, delta)
        assert view.viewportTransform() == before
        view._topology.project().update.assert_not_called()


def test_wheel_without_control_scrolls_without_zooming(zoom_view):
    view = zoom_view
    bar = view.verticalScrollBar()
    bar.setValue((bar.minimum() + bar.maximum()) // 2)
    before = bar.value()
    wheel(view, QtCore.QPoint(100, 100), -120, QtCore.Qt.KeyboardModifier.NoModifier)
    assert view.transform().m11() == 1
    assert bar.value() > before
    view._topology.project().update.assert_not_called()


def test_project_scene_size_resets_navigation_padding(zoom_view):
    view = zoom_view
    view.setSceneSize(100, 80)
    wheel(view, QtCore.QPoint(100, 100), -120)
    assert view.sceneRect() != view.scene().sceneRect()
    view.setSceneSize(2000, 1000)
    assert view.sceneRect() == view.scene().sceneRect()


def test_zoom_acknowledgments_preserve_navigation_and_viewport_geometry(zoom_view):
    view = zoom_view
    view.setSceneSize(2000, 1000)
    wheel(view, QtCore.QPoint(700, 400), 120)
    before = view.viewportTransform()
    bounds = view.sceneRect()
    viewport = view.viewport().geometry()
    for _ in range(3):
        view.setSceneSize(2000, 1000)
        QtWidgets.QApplication.processEvents()
        assert view.viewportTransform() == before
        assert view.sceneRect() == bounds
        assert view.viewport().geometry() == viewport


def test_zoom_between_opposite_regions_without_scrollbars(zoom_view):
    view = zoom_view
    view.setSceneSize(4000, 2000)
    left, right = QtCore.QPointF(-1000, 0), QtCore.QPointF(1000, 0)
    view.scale(.2, .2)
    view.centerOn(0, 0)
    wheel(view, view.mapFromScene(left), 120)
    for _ in range(3):
        wheel(view, view._wheel_zoom_position, 120)
        assert (view.mapFromScene(left) - view.viewport().rect().center()).manhattanLength() <= 2
        view.setSceneSize(4000, 2000)  # Project update/notification echoes.
    for _ in range(6):
        wheel(view, QtCore.QPoint(100, 100), -120)
    position = view.mapFromScene(right)
    assert view.viewport().rect().contains(position)
    wheel(view, position, 120)
    assert (view.mapFromScene(right) - view.viewport().rect().center()).manhattanLength() <= 2
