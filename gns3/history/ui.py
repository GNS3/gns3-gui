# SPDX-License-Identifier: GPL-3.0-or-later
"""Three toolbar commands and a small cursor-based project history dialog."""
from ..qt import QtCore, QtGui, QtWidgets, sip_is_deleted
from .session import HistorySession


class HistoryDialog(QtWidgets.QDialog):
    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.history = history
        self.setWindowTitle('History')
        self.resize(560, 420)
        layout = QtWidgets.QVBoxLayout(self)
        self.status = QtWidgets.QLabel(self)
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.operations = QtWidgets.QListWidget(self)
        self.operations.setAccessibleName('Topology history states')
        self.operations.itemClicked.connect(self.navigate)
        self.operations.itemActivated.connect(self.navigate)
        layout.addWidget(self.operations)
        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Close, parent=self)
        self.clearButton = self.buttons.addButton('Clear history', QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.clearButton.clicked.connect(self.clearHistory)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        history.changed.connect(self.refresh)
        self.finished.connect(self.disconnectHistory)
        self.refresh()

    def disconnectHistory(self):
        try:
            self.history.changed.disconnect(self.refresh)
        except (TypeError, RuntimeError):
            pass

    def refresh(self):
        doc = self.history.document
        self.status.setText(self.history.invalid or 'State {} of {}{}'.format(
            doc.cursor, len(doc.entries), ' — waiting for server' if self.history.busy else ''))
        blocker = QtCore.QSignalBlocker(self.operations)
        self.operations.clear()
        labels = ['Initial retained state'] + [entry['description'] for entry in doc.entries]
        for index, label in enumerate(labels):
            item = QtWidgets.QListWidgetItem(('▶ ' if index == doc.cursor else '   ') + label)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, index)
            font = item.font()
            font.setBold(index == doc.cursor)
            item.setFont(font)
            if index > doc.cursor:
                item.setForeground(self.palette().brush(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Text))
            self.operations.addItem(item)
        self.operations.setCurrentRow(doc.cursor)
        self.operations.setEnabled(not self.history.busy and not self.history.invalid)
        self.clearButton.setEnabled(not self.history.busy)

    def navigate(self, item):
        self.history.navigate(item.data(QtCore.Qt.ItemDataRole.UserRole))

    def clearHistory(self):
        answer = QtWidgets.QMessageBox.question(
            self, 'Clear history', 'Clear all undo and redo operations? The current topology will remain unchanged.',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No)
        if answer == QtWidgets.QMessageBox.StandardButton.Yes:
            self.history.clear()


class HistoryUI(QtCore.QObject):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.history = None
        self.dialog = None
        self._messages = []
        style = window.style()
        self.undo = QtGui.QAction(style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowBack), 'Undo', window)
        self.show = QtGui.QAction(style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileDialogDetailedView), 'History', window)
        self.redo = QtGui.QAction(style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowForward), 'Redo', window)
        for name, action in [('Undo', self.undo), ('History', self.show), ('Redo', self.redo)]:
            action.setObjectName('ui' + name + 'Action')
            action.setStatusTip(name + ' topology changes')
            window.uiControlToolBar.insertAction(window.uiSnapshotAction, action)
            window.addAction(action)
            setattr(window, action.objectName(), action)
        self.undo.setShortcut(QtGui.QKeySequence('Ctrl+Z'))
        self.redo.setShortcut(QtGui.QKeySequence('Ctrl+Y'))
        self.undo.triggered.connect(lambda: self.history and self.history.navigate(self.history.document.cursor - 1))
        self.redo.triggered.connect(lambda: self.history and self.history.navigate(self.history.document.cursor + 1))
        self.show.triggered.connect(self.showHistory)
        from ..topology import Topology
        Topology.instance().project_changed_signal.connect(self.bind)
        QtWidgets.QApplication.instance().installEventFilter(self)
        self.bind()

    def bind(self):
        if self.history is not None:
            try:
                self.history.changed.disconnect(self.refresh)
                self.history.failed.disconnect(self.error)
            except (TypeError, RuntimeError):
                pass
        if self.dialog is not None:
            self.dialog.close()
            self.dialog = None
        from ..topology import Topology
        project = Topology.instance().project()
        history = getattr(project, 'history', None)
        self.history = history if isinstance(history, HistorySession) else None
        if self.history is not None:
            self.history.changed.connect(self.refresh)
            self.history.failed.connect(self.error)
        self.refresh()

    def refresh(self):
        history = self.history
        self.undo.setEnabled(bool(history and history.can_undo))
        self.redo.setEnabled(bool(history and history.can_redo))
        self.show.setEnabled(bool(history and history.ready))
        if history is not None:
            blocked = not history.ready or history.replaying or (history.pending and not history.depth)
            # Keep keyboard focus in the canvas across consecutive shortcuts.
            # GraphicsView.setEnabled(False) also resets the entire topology.
            self.window.uiGraphicsView.setInteractive(not blocked)
            self.window.uiAnnotationToolBar.setEnabled(not blocked)
            self.window.uiControlToolBar.setEnabled(not blocked)
            self.window.uiAnnotateMenu.setEnabled(not blocked)

    def textFocus(self):
        focus = QtWidgets.QApplication.focusWidget()
        while focus is not None:
            if isinstance(focus, (QtWidgets.QLineEdit, QtWidgets.QTextEdit, QtWidgets.QPlainTextEdit, QtWidgets.QAbstractSpinBox)):
                return True
            focus = focus.parentWidget()
        view = self.window.uiGraphicsView
        item = view.scene().focusItem()
        return isinstance(item, QtWidgets.QGraphicsTextItem) and bool(item.textInteractionFlags() & QtCore.Qt.TextInteractionFlag.TextEditorInteraction)

    def eventFilter(self, watched, event):
        if (event.type() == QtCore.QEvent.Type.ShortcutOverride and
                event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier and
                event.key() in (QtCore.Qt.Key.Key_Z, QtCore.Qt.Key.Key_Y) and self.textFocus()):
            event.accept()  # Native text editing owns this shortcut.
        return False

    def showHistory(self):
        if self.history is None or not self.history.ready:
            return
        if self.dialog is None or sip_is_deleted(self.dialog):
            self.dialog = HistoryDialog(self.history, self.window)
            dialog = self.dialog
            def closed():
                if self.dialog is dialog:
                    self.dialog = None
                dialog.deleteLater()
            dialog.finished.connect(closed)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def error(self, message):
        box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, 'Topology history', message,
                                    QtWidgets.QMessageBox.StandardButton.Ok, self.window)
        self._messages.append(box)
        box.finished.connect(lambda: self._messages.remove(box) if box in self._messages else None)
        box.open()
