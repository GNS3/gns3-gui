# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 GNS3 Technologies Inc.
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

import pytest

from unittest.mock import MagicMock, patch


@pytest.fixture
def real_main_window():
    from gns3.main_window import MainWindow
    with patch.object(MainWindow, "run_later"):
        window = MainWindow()
    yield window
    window._local_config_timer.stop()
    window.deleteLater()


def test_main_window_settings_changed_signal(real_main_window):
    settings = real_main_window.settings()
    signal = MagicMock()
    real_main_window.settings_updated_signal = signal
    real_main_window.setSettings(settings)
    assert signal.emit.called


def test_main_window_settings_changed_slot(real_main_window):
    instance = MagicMock()
    manager = MagicMock()
    manager.instance.return_value = instance
    real_main_window._appliance_manager =  manager
    real_main_window.settingsChangedSlot()
    assert instance.refresh.called


def test_node_grouping_actions(real_main_window):
    from gns3.qt import QtCore
    window = real_main_window
    group = window.uiGroupNodesAction
    ungroup = window.uiUngroupNodesAction
    assert group in window.uiAnnotationToolBar.actions()
    assert ungroup in window.uiAnnotateMenu.actions()
    assert not group.icon().isNull()
    assert group.shortcut().toString() == "Ctrl+G"
    assert ungroup.shortcut().toString() == "Ctrl+Shift+G"
    assert group.shortcutContext() == QtCore.Qt.ShortcutContext.WidgetShortcut


def test_group_toolbar_is_momentary_with_status_and_hover_icon(real_main_window):
    from gns3.qt import QtGui, QtCore
    window = real_main_window
    action = window.uiGroupNodesAction
    button = window.uiAnnotationToolBar.widgetForAction(action)
    assert action.statusTip() == "Container elements (Ctrl+G)"
    assert button.statusTip() == action.statusTip()
    assert not action.isCheckable()
    assert button.focusPolicy() == QtCore.Qt.FocusPolicy.NoFocus
    icon = action.icon()
    normal = icon.pixmap(32, 32, QtGui.QIcon.Mode.Normal).toImage()
    active = icon.pixmap(32, 32, QtGui.QIcon.Mode.Active).toImage()
    assert normal != active
    button.setDown(True)
    action.trigger()
    assert not button.isDown() and not action.isChecked()


def test_group_toolbar_hover_reaches_status_bar(real_main_window):
    from PyQt6.QtTest import QTest
    from gns3.qt import QtWidgets
    window = real_main_window
    window.show()
    QtWidgets.QApplication.processEvents()
    button = window.uiAnnotationToolBar.widgetForAction(window.uiGroupNodesAction)
    QTest.mouseMove(button, button.rect().center())
    QtWidgets.QApplication.processEvents()
    assert window.uiStatusBar.currentMessage() == window.uiGroupNodesAction.statusTip()
    QTest.mouseMove(window.uiGraphicsView.viewport(), window.uiGraphicsView.viewport().rect().center())
    QtWidgets.QApplication.processEvents()
    assert not button.isDown() and not window.uiGroupNodesAction.isChecked()
