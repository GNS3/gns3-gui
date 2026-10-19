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
import logging

from unittest.mock import MagicMock, patch


@pytest.fixture
def real_main_window():
    from gns3.main_window import MainWindow
    handlers = set(logging.getLogger().handlers)
    with patch.object(MainWindow, "run_later"):
        window = MainWindow()
    yield window
    window._local_config_timer.stop()
    for handler in set(logging.getLogger().handlers) - handlers:
        logging.getLogger().removeHandler(handler)
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


def test_navigation_toolbar_tracks_view_mode(real_main_window):
    window = real_main_window
    assert window.uiHandAction.isChecked()
    for action in (window.uiHandAction, window.uiSelectionAction):
        assert not action.icon().isNull()
        assert action.statusTip()
        button = window.uiAnnotationToolBar.widgetForAction(action)
        assert button.statusTip() == action.statusTip()
    window.uiSelectionAction.trigger()
    assert window.uiGraphicsView._navigation_mode == 'selection'
    assert not window.uiHandAction.isChecked()
    window.uiGraphicsView.setNavigationMode('hand')
    assert window.uiHandAction.isChecked()
    assert not window.uiSelectionAction.isChecked()


def test_line_toolbar_switches_between_authoring_tools(real_main_window):
    window = real_main_window
    window.uiDrawLineAction.trigger()
    assert window.uiGraphicsView._adding_line
    assert window.uiDrawLineAction.isChecked()
    window.uiDrawRectangleAction.trigger()
    assert window.uiGraphicsView._adding_rectangle
    assert not window.uiGraphicsView._adding_line
    assert not window.uiDrawLineAction.isChecked()


def test_history_toolbar_order_and_reopened_dialog(real_main_window):
    from tests.history.test_session import session, edit, settled
    window = real_main_window
    toolbar = window.uiControlToolBar.actions()
    index = toolbar.index(window.uiSnapshotAction)
    assert toolbar[index - 3:index] == [window.uiUndoAction, window.uiHistoryAction, window.uiRedoAction]
    assert window.uiUndoAction.shortcut().toString() == 'Ctrl+Z'
    assert window.uiRedoAction.shortcut().toString() == 'Ctrl+Y'
    owner, history, server = session()
    window._history_ui.history = history
    history.changed.connect(window._history_ui.refresh)
    from tests.history.test_model_replay import node
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    assert window.uiUndoAction.isEnabled() and not window.uiRedoAction.isEnabled()
    ui = window._history_ui
    ui.showHistory()
    assert ui.dialog.operations.count() == 2
    ui.dialog.reject()
    assert ui.dialog is None
    ui.showHistory()
    window.uiUndoAction.trigger()
    settled(history)
    assert ui.dialog.operations.currentRow() == 0
    assert window.uiRedoAction.isEnabled() and not window.uiUndoAction.isEnabled()
    with patch('gns3.history.ui.QtWidgets.QMessageBox.question', return_value=__import__('gns3.qt', fromlist=['QtWidgets']).QtWidgets.QMessageBox.StandardButton.Yes):
        ui.dialog.clearHistory()
    settled(history)
    assert not history.document.entries and not server.state
    ui.dialog.reject()
    history.changed.disconnect(ui.refresh)
    ui.history = None


def test_history_shortcuts_preserve_native_text_undo(real_main_window):
    from PyQt6.QtTest import QTest
    from gns3.qt import QtCore, QtWidgets
    from tests.history.test_session import session, edit, settled
    from tests.history.test_model_replay import node
    window = real_main_window
    owner, history, server = session()
    window._history_ui.history = history
    history.changed.connect(window._history_ui.refresh)
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    text = QtWidgets.QLineEdit(window)
    text.setGeometry(10, 10, 150, 30)
    window.show()
    text.show()
    window.activateWindow()
    text.setFocus()
    QTest.qWait(10)
    text.insert('edit')
    QTest.keyClick(text, QtCore.Qt.Key.Key_Z, QtCore.Qt.KeyboardModifier.ControlModifier)
    assert text.text() == '' and history.document.cursor == 1
    text.hide()
    window.uiGraphicsView.setFocus()
    QTest.keyClick(window.uiGraphicsView, QtCore.Qt.Key.Key_Z, QtCore.Qt.KeyboardModifier.ControlModifier)
    settled(history)
    assert history.document.cursor == 0
    QTest.keyClick(window.uiGraphicsView, QtCore.Qt.Key.Key_Y, QtCore.Qt.KeyboardModifier.ControlModifier)
    settled(history)
    assert history.document.cursor == 1
    history.changed.disconnect(window._history_ui.refresh)
    window._history_ui.history = None


def test_old_project_and_archived_recovery_do_not_open_startup_dialogs(real_main_window):
    from tests.history.test_session import session, edit, settled
    from tests.history.test_model_replay import node, key, drain
    from gns3.topology import Topology
    owner, history, server = session()
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    server.state[key('nodes', node())]['x'] = 123
    topology = MagicMock()
    topology.project.return_value = owner
    ui = real_main_window._history_ui
    with patch.object(Topology, 'instance', return_value=topology):
        ui.bind()
        loaded = []
        history.load(dict(server.state), lambda: loaded.append(True))
        drain(lambda: bool(loaded))
        settled(history)
        assert history.recovery_message
        assert not ui._messages
        ui.showHistory()
        assert 'New changes are recorded normally' in ui.dialog.status.text()
        ui.dialog.reject()
        history.changed.disconnect(ui.refresh)
        history.failed.disconnect(ui.error)
        ui.history = None
