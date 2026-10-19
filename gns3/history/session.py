# SPDX-License-Identifier: GPL-3.0-or-later
"""Capture confirmed resource CRUD, group GUI gestures, and own replay/storage."""
import copy
import functools
import inspect
import re
from ..qt import QtCore
from .model import HistoryDocument, canonical, resource, IDS, KINDS, description, state_from_lists
from .replay import Replay
from .storage import background, encode, decode, SLOTS

WRITE = re.compile(r'^/(nodes|links|drawings)(?:/([a-fA-F0-9-]{36}))?$')
CREATE = re.compile(r'^/(?:templates/[a-fA-F0-9-]{36}|nodes/[a-fA-F0-9-]{36}/duplicate)$')


def current_history(owner=None):
    view = getattr(owner, 'view', owner)
    topology = getattr(view, '_topology', None)
    if topology is None:
        from ..topology import Topology
        topology = Topology.instance()
    project = topology.project()
    history = getattr(project, 'history', None)
    return history if isinstance(history, HistorySession) else None


def action(label=None):
    """One logical dialog/command, including its asynchronous child requests."""
    def decorate(function):
        parameters = inspect.signature(function).parameters.values()
        maximum = None if any(p.kind == p.VAR_POSITIONAL for p in parameters) else sum(
            p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) for p in parameters) - 1
        @functools.wraps(function)
        def wrapped(owner, *args, **kwargs):
            # QAction.triggered(bool) normally drops surplus arguments when
            # connected to a zero-argument slot; preserve that Qt behavior.
            if maximum is not None:
                args = args[:maximum]
            history = current_history(owner)
            if history is None or not history.ready:
                return function(owner, *args, **kwargs)
            if history.replaying:
                return
            history.begin(label)
            try:
                return function(owner, *args, **kwargs)
            finally:
                history.end()
        return wrapped
    return decorate


class HistorySession(QtCore.QObject):
    changed = QtCore.pyqtSignal()
    failed = QtCore.pyqtSignal(str)

    def __init__(self, project, request=None):
        super().__init__(project)
        self.project = project
        self.document = HistoryDocument(project.id())
        self.ready = False
        self.replaying = False
        self.invalid = ''
        self.pending = 0
        self.depth = 0
        self.active = None
        self._saving = False
        self._saved_revision = 0
        self._save_error = ''
        self._flush_callbacks = []
        self._transport = request
        self._runner = None
        self._raw_state = {}
        self.auxiliary = set()
        self._settle = QtCore.QTimer(self)
        self._settle.setSingleShot(True)
        self._settle.timeout.connect(self._finalize)

    @property
    def busy(self):
        return not self.ready or self.replaying or bool(self.pending or self.depth or self.active)

    @property
    def can_undo(self):
        return not self.busy and not self.invalid and self.document.cursor > 0

    @property
    def can_redo(self):
        return not self.busy and not self.invalid and self.document.cursor < len(self.document.entries)

    def _raw(self, method, path, callback=None, body=None, **kwargs):
        if self._transport is not None:
            return self._transport(method, path, callback, body=body, **kwargs)
        from ..controller import Controller
        client = Controller.instance()._http_client
        if client is None:
            if callback:
                QtCore.QTimer.singleShot(0, lambda: callback({'message': 'Server disconnected'}, error=True))
            return
        return client.createHTTPQuery(method, '/projects/{}{}'.format(self.project.id(), path),
                                      callback, body=body, showProgress=False, ignoreErrors=True, **kwargs)

    def _request(self, method, path, callback=None, body=None):
        if method in ('POST', 'PUT') and path.startswith('/drawings') and body and 'svg' in body:
            # Reuse the existing lossless large-SVG transport, including its
            # transparent directory seed, without recording its implementation.
            from ..items.drawing_item import DrawingItem
            session = self
            class Proxy:
                def post(self, path, callback, body=None, **kwargs):
                    return session._raw('POST', path, callback, body, **kwargs)
                def put(self, path, callback, body=None, **kwargs):
                    return session._raw('PUT', path, callback, body, **kwargs)
                def delete(self, path, callback, **kwargs):
                    return session._raw('DELETE', path, callback, **kwargs)
            class Wire:
                _sendDrawing = DrawingItem._sendDrawing
                def __init__(self):
                    self._project = Proxy()
                    self._hash_svg = None
            return Wire()._sendDrawing(method.lower(), path, callback, body)
        return self._raw(method, path, callback, body)

    def begin(self, label=None):
        if not self.ready or self.replaying or self.invalid:
            return
        if self.active is not None and not self.depth and not self.pending:
            self._finalize()
        self._settle.stop()
        if self.active is None:
            self.active = {'changes': {}, 'label': label, 'failed': False}
        elif label and not self.active['label']:
            self.active['label'] = label
        self.depth += 1
        self.changed.emit()

    def end(self):
        self.depth = max(0, self.depth - 1)
        self._schedule_finalize()

    def hold(self):
        """Keep file-upload/creation pipelines in one pending logical operation."""
        if not self.ready or self.replaying or self.invalid:
            return lambda: None
        if self.active is None:
            self.active = {'changes': {}, 'label': None, 'failed': False}
        self.pending += 1
        self._settle.stop()
        self.changed.emit()
        released = False
        def release():
            nonlocal released
            if not released:
                released = True
                self.pending -= 1
                self._schedule_finalize()
        return release

    def _schedule_finalize(self):
        if self.active is not None and not self.depth and not self.pending:
            self._settle.start(0)
        self.changed.emit()

    def _stage(self, key, value):
        before = self.document.state.get(key)
        if self.active is not None:
            change = self.active['changes'].setdefault(key, {'before': copy.deepcopy(before), 'after': None})
            change['after'] = copy.deepcopy(value)
        if value is None:
            self.document.state.pop(key, None)
        else:
            self.document.state[key] = value

    def observe(self, kind, data, deleted=False, external=False):
        """Server acknowledgments and websocket echoes share a canonical cache."""
        key = kind + '/' + data[IDS[kind]]
        if key in self.auxiliary:
            return
        if not deleted:
            # drawing.updated intentionally omits SVG when it did not change.
            # Merge partial notifications with the confirmed resource, retaining
            # the container's membership metadata as well as its geometry.
            data = dict(self._raw_state.get(key, self.document.state.get(key, {})), **data)
        value = None if deleted else canonical(kind, data)
        self._raw_state[key] = copy.deepcopy(data)
        old = self.document.state.get(key)
        if external and self.ready and not self.replaying and self.active is None and old != value:
            self.invalid = 'The topology changed outside a recorded GUI operation. Clear history to use the current state as the new baseline.'
            self.failed.emit(self.invalid)
        self._stage(key, value)
        if deleted and kind == 'nodes':
            identity = data['node_id']
            for link_key, link in list(self.document.state.items()):
                if link_key.startswith('links/') and any(n['node_id'] == identity for n in link['nodes']):
                    self._stage(link_key, None)
        self.changed.emit()

    def capture(self, method, path, callback, body):
        match = WRITE.fullmatch(path)
        create = method == 'POST' and CREATE.fullmatch(path)
        if method not in ('POST', 'PUT', 'DELETE') or (not match and not create):
            return callback
        if match:
            kind, identity = match.groups()
            if method in ('PUT', 'DELETE') and identity is None:
                return callback
        else:
            kind, identity = 'nodes', None
        if (identity is not None and kind + '/' + identity in self.auxiliary) or (
                method == 'POST' and isinstance(body, dict) and kind + '/' + str(body.get(IDS[kind])) in self.auxiliary):
            return callback
        if getattr(self, '_applying_gui', False):
            return ('ignored', None)
        if self.replaying:
            def rejected(*args, **kwargs):
                if callback:
                    callback({'message': 'A history operation is in progress'}, error=True)
            return ('blocked', rejected)
        if not self.ready:
            return callback  # Initial load establishes the authoritative baseline.
        if self.active is None:
            self.active = {'changes': {}, 'label': None, 'failed': False}
        self._settle.stop()
        self.pending += 1
        self.changed.emit()
        def completed(result, error=False, **kwargs):
            try:
                if error:
                    self.active['failed'] = True
                elif method == 'DELETE':
                    self.observe(kind, {IDS[kind]: identity}, deleted=True)
                else:
                    self.observe(kind, result)
                if callback:
                    callback(result, error=error, **kwargs)
            finally:
                self.pending = max(0, self.pending - 1)
                self._schedule_finalize()
        return completed

    def _finalize(self):
        if self.pending or self.depth or self.active is None:
            return
        active, self.active = self.active, None
        if active['failed']:
            # The original GUI may already have removed objects optimistically.
            # Reload confirmed server state instead of treating partial success
            # as a complete reversible user action.
            self.invalid = 'An edit failed or completed partially. Review the topology and clear history before undoing.'
            self.failed.emit(self.invalid)
            self.replaying = True
            def reconciled(ok):
                self.replaying = False
                self.changed.emit()
                self._finish_flush()
            self.refresh(reconciled)
        elif not self.invalid and self.document.record(active['changes'], active['label']):
            # Substitute available names for UUIDs in readable descriptions.
            entry = self.document.entries[-1]
            for key, change in entry['changes'].items():
                value = change['after'] or change['before']
                if key.startswith('nodes/'):
                    entry['description'] = entry['description'].replace(value['node_id'], value['name'])
            for key, value in self.document.state.items():
                if key.startswith('nodes/'):
                    entry['description'] = entry['description'].replace(value['node_id'], value['name'])
            self.persist()
        self.changed.emit()
        self._finish_flush()

    def refresh(self, callback):
        lists = {}
        def next_kind(index):
            if index == len(KINDS):
                state = state_from_lists(lists)
                try:
                    self._apply_gui(state, force=True)
                except Exception as error:
                    self.document.state = state
                    self.invalid = 'Cannot reconcile the canvas with the server: ' + str(error)
                    self.failed.emit(self.invalid)
                    return callback(False)
                self.document.state = state
                return callback(True)
            kind = KINDS[index]
            def received(result, error=False, **kw):
                if error:
                    self.failed.emit('Cannot refresh project topology: ' + result.get('message', 'request failed'))
                    return callback(False)
                lists[kind] = result
                for value in result:
                    self._raw_state[kind + '/' + value[IDS[kind]]] = value
                next_kind(index + 1)
            self._raw('GET', '/' + kind, received)
        next_kind(0)

    def _apply_gui(self, state, force=False):
        self._applying_gui = True
        try:
            self._apply_gui_impl(state, force)
        finally:
            self._applying_gui = False

    def _apply_gui_impl(self, state, force=False):
        """Update only changed resources through the existing notification path."""
        from ..topology import Topology
        topo = Topology.instance()
        if topo.project() is not self.project:
            return
        from ..items.group_item import GroupItem, item_reference, reparent
        # Removing a frame must not hide retained children with Qt's parent.
        # The server stores these as independent resources; restore() reapplies
        # their target ownership after the changed frames have been applied.
        for key in set(self.document.state) - set(state):
            if key.startswith('drawings/'):
                frame = topo.getDrawingFromUuid(resource(key)[1])
                if isinstance(frame, GroupItem):
                    for child in list(frame.descendants()):
                        kind, identity = item_reference(child)
                        child_key = ('nodes/' if kind == 'node' else 'drawings/') + identity
                        if child_key in state:
                            reparent(child, None)
        old = self.document.state
        for kind in ('links', 'drawings', 'nodes'):
            for key in set(old) - set(state):
                if key.startswith(kind + '/'):
                    self.project._event_received({'action': kind[:-1] + '.deleted', 'event': {IDS[kind]: resource(key)[1]}}, history_replay=True)
        visible_nodes = {ref[1] for item in topo._main_window.uiGraphicsView.scene().items()
                         if (ref := item_reference(item)) and ref[0] == 'node'}
        for kind in KINDS:
            for key, value in state.items():
                if not key.startswith(kind + '/'):
                    continue
                finder = {'nodes': topo.getNodeFromUuid, 'links': topo.getLinkFromUuid,
                          'drawings': topo.getDrawingFromUuid}[kind]
                live = finder(value[IDS[kind]])
                if kind == 'nodes' and live is not None:
                    if value['node_id'] not in visible_nodes:
                        self.project._event_received({'action': 'node.deleted', 'event': {'node_id': value['node_id']}}, history_replay=True)
                        live = None
                if live is not None and getattr(live, 'deleting', lambda: False)():
                    self.project._event_received({'action': kind[:-1] + '.deleted', 'event': {IDS[kind]: value[IDS[kind]]}}, history_replay=True)
                    live = None
                if not force and old.get(key) == value and live is not None:
                    continue
                raw = copy.deepcopy(self._raw_state.get(key, value))
                raw.update(value)
                if kind == 'nodes' and key not in self._raw_state:
                    # Recreated node callbacks retain the complete API response.
                    raw.setdefault('status', 'stopped')
                if kind == 'drawings':
                    item = topo.getDrawingFromUuid(value['drawing_id'])
                    if item is not None and hasattr(item, '_revision'):
                        item._revision = 0
                event = kind[:-1] + ('.updated' if live is not None else '.created')
                self.project._event_received({'action': event, 'event': raw}, history_replay=True)
        view = topo._main_window.uiGraphicsView
        view._groups.restore(persist=False)
        view.toggleUiDeviceMenu()

    def navigate(self, target):
        if self.busy or self.invalid or type(target) is not int or not 0 <= target <= len(self.document.entries):
            return False
        if target == self.document.cursor:
            return True
        self.replaying = True
        self.changed.emit()
        self._navigate_next(target)
        return True

    def _navigate_next(self, target):
        if self.document.cursor == target:
            self.replaying = False
            self.persist()
            self.changed.emit()
            self._finish_flush()
            return
        backwards = target < self.document.cursor
        entry = self.document.entries[self.document.cursor - 1 if backwards else self.document.cursor]
        changes = {key: {'before': c['after'] if backwards else c['before'],
                         'after': c['before'] if backwards else c['after']} for key, c in entry['changes'].items()}
        def completed(success, message, trustworthy, state):
            mapping = self._runner.identities
            if mapping:
                self._applying_gui = True
                try:
                    for identity in mapping:
                        self.project._event_received({'action': 'link.deleted', 'event': {'link_id': identity}}, history_replay=True)
                finally:
                    self._applying_gui = False
                rewrite = self.document.rebind_links(mapping)
                state = rewrite(state)
            self._runner = None
            if success:
                updated = dict(self.document.state)
                for key, value in state.items():
                    if value is None:
                        updated.pop(key, None)
                    else:
                        updated[key] = value
                try:
                    self._apply_gui(updated)
                except Exception as error:
                    self.invalid = 'The server applied the change, but the canvas could not be synchronized: ' + str(error)
                    self.document.state = updated
                    self.failed.emit(self.invalid)
                    def reconciled(ok):
                        self.replaying = False
                        self.changed.emit()
                        self._finish_flush()
                    self.refresh(reconciled)
                    return
                self.document.state = updated
                self.document.cursor += -1 if backwards else 1
                self.document.revision += 1
                self.changed.emit()
                QtCore.QTimer.singleShot(0, lambda: self._navigate_next(target))
            else:
                if not trustworthy:
                    self.invalid = message
                self.failed.emit(message)
                # Reconcile the visual tree after a compensated or partial error.
                def reconciled(ok):
                    self.replaying = False
                    if not ok:
                        self.invalid = 'Cannot verify the topology after a failed history operation. Reconnect and clear history.'
                    self.changed.emit()
                    if ok:
                        self.persist()
                    self._finish_flush()
                self.refresh(reconciled)
        def request(method, path, callback, body=None):
            def received(result, error=False, **kw):
                if not error and method != 'DELETE' and WRITE.fullmatch(path):
                    match = WRITE.fullmatch(path)
                    kind = match.group(1)
                    if isinstance(result, dict) and IDS[kind] in result:
                        self._raw_state[kind + '/' + result[IDS[kind]]] = copy.deepcopy(result)
                callback(result, error=error, **kw)
            return self._request(method, path, received, body)
        self._runner = Replay(request, changes, completed)
        self._runner.start()

    def clear(self):
        if self.busy:
            return False
        self.replaying = True
        self.changed.emit()
        def refreshed(ok):
            self.replaying = False
            if ok:
                self.document.clear()
                self.invalid = ''
                self.persist()
            self.changed.emit()
        self.refresh(refreshed)
        return True

    def load(self, state, callback):
        self.ready = False
        self.invalid = ''
        self._save_error = ''
        self._saved_revision = 0
        self.document = HistoryDocument(self.project.id(), state)
        slots, errors = [], []
        def read(index):
            if index == len(SLOTS):
                def decode_slots():
                    documents, problems = [], []
                    for raw in slots:
                        try:
                            documents.append(decode(raw))
                        except (ValueError, KeyError, TypeError, OSError, EOFError, RecursionError) as reason:
                            problems.append(str(reason))
                    return documents, problems
                return background(decode_slots, decoded)
            def received(result, error=False, raw_body=None, **kw):
                if not error and raw_body:
                    slots.append(raw_body)
                elif error and result.get('status') != 404:
                    errors.append(result.get('message', 'Cannot read history'))
                read(index + 1)
            self._raw('GET', '/files/' + SLOTS[index], received)
        def decoded(result, error):
            documents = []
            if result is not None:
                documents, problems = result
                errors.extend(problems)
            if error:
                errors.append(error)
                documents = []
            candidates = sorted(documents or [], key=lambda d: d.revision, reverse=True)
            loaded = None
            for document in candidates:
                try:
                    loaded = document.remap_import(self.project.id(), self.document.state)
                    break
                except (ValueError, KeyError, TypeError) as reason:
                    errors.append(str(reason))
            if loaded is not None:
                actual = self.document.state
                differences = {key: {'before': actual.get(key), 'after': value} for key, value in loaded.state.items()
                               if actual.get(key) != value}
                if differences:
                    self.replaying = True
                    def rebound(success, message, trustworthy, state):
                        self._runner = None
                        self.replaying = False
                        if success:
                            self._apply_gui(loaded.state)
                            self.document = loaded
                            self.document.revision += 1
                            self.ready = True
                            self.persist()
                        else:
                            self.ready = True
                            self.invalid = 'Cannot rebind imported history: ' + message
                            self.failed.emit(self.invalid)
                        self.changed.emit()
                        callback()
                    self._runner = Replay(self._request, differences, rebound)
                    self._runner.start()
                    return
                self.document = loaded
                self._saved_revision = loaded.revision
            elif errors or slots:
                self.invalid = 'History could not be recovered safely: ' + '; '.join(errors)
                self.failed.emit(self.invalid)
            self.ready = True
            self.changed.emit()
            callback()
        read(0)

    def persist(self):
        if not self.ready or self.invalid or self._saving or self.document.revision == self._saved_revision:
            return
        self._saving = True
        revision = self.document.revision
        payload = self.document.payload()
        def encoded(path, error):
            if error:
                return saved({}, error=True, reason=error)
            def uploaded(result, error=False, **kw):
                path.unlink(missing_ok=True)
                saved(result, error=error)
            self._raw('POST', '/files/' + SLOTS[revision % 2], uploaded, body=path)
        def saved(result, error=False, reason=None, **kw):
            self._saving = False
            if error:
                self._save_error = reason or result.get('message', 'Cannot save project history')
                self.failed.emit('History was not saved: ' + self._save_error)
            else:
                self._save_error = ''
                self._saved_revision = revision
                self.persist()
            self.changed.emit()
            self._finish_flush()
        background(lambda: encode(payload), encoded)

    def flush(self, callback):
        self._flush_callbacks.append(callback)
        self.persist()
        self._finish_flush()

    def _finish_flush(self):
        if self.busy or self._saving:
            return
        ok = not self._save_error and (self.invalid or self.document.revision == self._saved_revision)
        callbacks, self._flush_callbacks = self._flush_callbacks, []
        for callback in callbacks:
            callback(bool(ok))


def gesture(phase):
    """Keep a gesture open across mouse events, including its early returns."""
    def decorate(function):
        @functools.wraps(function)
        def wrapped(view, event):
            history = current_history(view)
            if phase == 'press' and history is not None and history.ready:
                if history.replaying or (history.pending and not history.depth):
                    event.accept()
                    return
                if getattr(view, '_history_gesture', None) is None:
                    history.begin()
                    view._history_gesture = history
            try:
                return function(view, event)
            finally:
                if phase == 'focus' or (phase == 'release' and not event.buttons()):
                    opened = getattr(view, '_history_gesture', None)
                    view._history_gesture = None
                    if opened is not None:
                        opened.end()
        return wrapped
    return decorate
