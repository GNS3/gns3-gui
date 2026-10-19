"""Logical GUI boundaries, real callbacks, asynchronous storage and project isolation."""
import copy
from pathlib import Path
from unittest.mock import MagicMock
import pytest
from gns3.qt import QtCore
from gns3.history.model import HistoryDocument, canonical
from gns3.history.session import HistorySession
from gns3.history.storage import SLOTS, decode
from .test_model_replay import Server, node, link, drawing, key, identity, drain, delta


class Project(QtCore.QObject):
    def __init__(self, name='project'):
        super().__init__()
        self.identity = identity(name)

    def id(self):
        return self.identity


class FileServer(Server):
    def __init__(self, state=None):
        super().__init__(state)
        self.files = {}
        self.reject_upload = False

    def request(self, method, path, callback=None, body=None, **kwargs):
        if path.startswith('/files/'):
            if method == 'POST' and not self.reject_upload:
                self.files[path] = Path(body).read_bytes()
                callback({})
            elif path in self.files and method == 'GET':
                callback({}, raw_body=self.files[path])
            else:
                callback(dict(status=409 if self.reject_upload and method == 'POST' else 404, message='Cannot access file'), error=True)
            return
        super().request(method, path, callback, body, **kwargs)


def session(server=None, name='project'):
    owner = Project(name)
    server = server or FileServer()
    history = HistorySession(owner, server.request)
    owner.history = history
    history.document = HistoryDocument(owner.id(), {k: canonical(k.split("/")[0], v) for k, v in server.state.items()})
    history.ready = True
    history._apply_gui = MagicMock()
    history._request = history._raw  # Test API shape without drawing upload adapter.
    return owner, history, server


def edit(history, server, method, path, body=None, callback=None):
    wrapped = history.capture(method, path, callback, body)
    server.request(method, path, wrapped, body)


def settled(history):
    drain(lambda: not history.busy and not history._saving)


def test_nested_mouse_operation_groups_move_and_membership_and_ignores_roundtrip():
    a, b = node('A'), node('B')
    group = drawing('container')
    owner, history, server = session(FileServer({key('nodes', a): a, key('nodes', b): b, key('drawings', group): group}))
    history.begin()
    history.begin('Move group')
    edit(history, server, 'PUT', '/' + key('nodes', a), {'x': 50})
    edit(history, server, 'PUT', '/' + key('nodes', b), {'x': 50})
    history.end()
    assert not history.document.entries
    edit(history, server, 'PUT', '/' + key('drawings', group), {'svg': drawing(width=120)['svg']})
    history.end()
    settled(history)
    assert len(history.document.entries) == 1
    assert len(history.document.entries[0]['changes']) == 3
    assert history.navigate(0)
    settled(history)
    assert server.state == {key('nodes', a): a, key('nodes', b): b, key('drawings', group): group}
    assert history.navigate(1)
    settled(history)
    history.begin()
    edit(history, server, 'PUT', '/' + key('nodes', a), {'x': 100})
    edit(history, server, 'PUT', '/' + key('nodes', a), {'x': 50})
    history.end()
    settled(history)
    assert len(history.document.entries) == 1


def test_delete_device_captures_incident_links_and_restores_in_order():
    a, b = node('A'), node('B')
    connection = canonical('links', link(a, b))
    state = {key('nodes', a): a, key('nodes', b): b, key('links', connection): connection}
    owner, history, server = session(FileServer(state))
    history.begin()
    edit(history, server, 'DELETE', '/' + key('nodes', a))
    # A websocket delete echo must not introduce a second operation.
    history.observe('links', {'link_id': connection['link_id']}, deleted=True, external=True)
    history.end()
    settled(history)
    assert len(history.document.entries) == 1
    assert len(history.document.entries[0]['changes']) == 2
    history.navigate(0)
    settled(history)
    assert server.state == state
    history.navigate(1)
    settled(history)
    assert server.state == {key('nodes', b): b}


def test_direct_navigation_branch_and_concurrent_rejection():
    owner, history, server = session()
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    for x in (10, 20, 30):
        edit(history, server, 'PUT', '/' + key('nodes', node()), {'x': x})
        settled(history)
    assert history.navigate(1)
    assert not history.navigate(0)
    rejected = []
    blocked = history.capture('POST', '/nodes', lambda result, error=False: rejected.append(error), node('C'))
    assert blocked[0] == 'blocked'
    blocked[1]()
    assert rejected == [True]
    settled(history)
    assert history.document.cursor == 1 and server.state[key('nodes', node())]['x'] == 0
    edit(history, server, 'PUT', '/' + key('nodes', node()), {'x': 99})
    settled(history)
    assert len(history.document.entries) == 2 and not history.can_redo


def test_rejected_replay_keeps_cursor_and_compensates_and_untrusted_blocks():
    owner, history, server = session()
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    server.fail = lambda method, path, body: method == 'DELETE'
    history.navigate(0)
    settled(history)
    assert history.document.cursor == 1 and history.can_undo
    assert server.state == history.document.state
    server.state[key('nodes', node())]['x'] = 44
    history.navigate(0)
    settled(history)
    assert history.document.cursor == 1 and history.invalid and not history.can_undo


def test_failed_original_edit_blocks_history_until_clear_and_no_change_to_server():
    owner, history, server = session()
    server.fail = lambda *args: True
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    assert history.invalid and not history.document.entries
    server.fail = None
    assert history.clear()
    settled(history)
    assert not history.invalid and server.state == {}


def test_persistence_reopen_export_import_old_and_project_isolation():
    owner, history, server = session()
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    edit(history, server, 'PUT', '/' + key('nodes', node()), {'x': 10})
    settled(history)
    history.navigate(1)
    settled(history)
    archive = copy.deepcopy(server.files)  # Same root files exported by server.
    owner2, reopened, _ = session(server)
    loaded = []
    reopened.ready = False
    reopened.load(copy.deepcopy(server.state), lambda: loaded.append(True))
    drain(lambda: bool(loaded))
    assert not reopened.invalid and reopened.document.cursor == 1 and reopened.can_redo
    reopened.navigate(2)
    settled(reopened)
    assert server.state[key('nodes', node())]['x'] == 10
    imported_node = dict(node(), node_id=identity('imported-node'))
    imported_server = FileServer({key('nodes', imported_node): imported_node})
    imported_server.files = archive
    owner3, imported, _ = session(imported_server, 'imported-project')
    loaded.clear()
    imported.ready = False
    imported.load(copy.deepcopy(imported_server.state), lambda: loaded.append(True))
    drain(lambda: bool(loaded))
    assert not imported.invalid and imported.document.cursor == 1
    imported.navigate(2)
    settled(imported)
    assert imported_server.state[key('nodes', imported_node)]['x'] == 10
    owner4, empty, old_server = session(name='old-project')
    loaded.clear()
    empty.load({}, lambda: loaded.append(True))
    drain(lambda: bool(loaded))
    assert empty.ready and not empty.invalid and not empty.document.entries
    assert history.document.cursor == 1 and reopened.document.cursor == 2


def test_two_slots_corruption_fallback_and_flush_failure():
    owner, history, server = session()
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    edit(history, server, 'PUT', '/' + key('nodes', node()), {'x': 10})
    settled(history)
    # Corrupt older slot: newest remains usable.
    server.files['/files/' + SLOTS[1]] = b'broken'
    owner2, reopened, _ = session(server)
    done = []
    reopened.load(copy.deepcopy(server.state), lambda: done.append(True))
    drain(lambda: bool(done))
    assert not reopened.invalid and reopened.document.cursor == 2
    server.reject_upload = True
    edit(history, server, 'PUT', '/' + key('nodes', node()), {'x': 20})
    settled(history)
    assert history._save_error
    done.clear()
    history.flush(lambda ok: done.append(ok))
    drain(lambda: bool(done))
    assert done == [False]
    server.reject_upload = False
    done.clear()
    history.flush(lambda ok: done.append(ok))
    drain(lambda: bool(done))
    assert done == [True]


def test_external_change_and_unsupported_operations_are_not_recorded():
    owner, history, server = session()
    callback = MagicMock()
    for method, path in [('POST', '/nodes/' + identity('N') + '/start'), ('POST', '/snapshots'), ('PUT', '/')]:
        assert history.capture(method, path, callback, {}) is callback
    history.observe('nodes', node(), external=True)
    assert history.invalid and not history.document.entries


def test_large_asset_is_stored_once_and_restored_losslessly():
    from gns3.history.storage import encode
    svg = '<svg><!--' + 'a' * 900000 + '--><rect width="10" height="20"/></svg>'
    a = dict(drawing(), svg=svg)
    doc = HistoryDocument(identity('project'))
    doc.record(delta('drawings', None, a))
    for x in range(1, 101):
        doc.record(delta('drawings', dict(a, x=x - 1), dict(a, x=x)))
    path = encode(doc.payload())
    try:
        assert decode(path.read_bytes()).payload() == doc.payload()
    finally:
        path.unlink()


class ReallocatingServer(FileServer):
    """The official link POST ignores the requested link_id."""
    timeout_link = False
    def request(self, method, path, callback=None, body=None, **kwargs):
        if method == 'POST' and path == '/links':
            import uuid
            body = dict(body, link_id=str(uuid.uuid4()))
            if self.timeout_link:
                self.timeout_link = False
                super().request(method, path, None, body, **kwargs)
                callback({'status': 504, 'message': 'timeout'}, error=True)
                return
        return super().request(method, path, callback, body, **kwargs)


def test_server_allocated_link_ids_rebind_the_entire_history_after_each_redo():
    a, b = node('A'), node('B')
    owner, history, server = session(ReallocatingServer({key('nodes', a): a, key('nodes', b): b}))
    owner._event_received = MagicMock()
    connection = link(a, b)
    edit(history, server, 'POST', '/links', connection)
    settled(history)
    initial_id = next(k for k in server.state if k.startswith('links/'))
    for _ in range(3):
        history.navigate(0)
        settled(history)
        assert not any(k.startswith('links/') for k in server.state)
        history.navigate(1)
        settled(history)
        assert history.document.cursor == 1 and not history.invalid
        current_id = next(k for k in server.state if k.startswith('links/'))
        assert current_id != initial_id
        assert current_id in history.document.entries[0]['changes']
        assert HistoryDocument.load(history.document.payload()).state == history.document.state
        initial_id = current_id


def test_lost_link_creation_ack_discovers_and_removes_allocated_orphan():
    a, b = node('A'), node('B')
    owner, history, server = session(ReallocatingServer({key('nodes', a): a, key('nodes', b): b}))
    owner._event_received = MagicMock()
    edit(history, server, 'POST', '/links', link(a, b))
    settled(history)
    history.navigate(0)
    settled(history)
    server.timeout_link = True
    history.navigate(1)
    settled(history)
    assert history.document.cursor == 0 and not history.invalid
    assert not any(k.startswith('links/') for k in server.state)
    history.navigate(1)
    settled(history)
    assert history.document.cursor == 1


def test_controller_captures_writes_without_an_explicit_callback(controller):
    from gns3.topology import Topology
    from unittest.mock import patch
    owner, history, server = session()
    topology = MagicMock()
    topology.project.return_value = owner
    prefix = '/projects/' + owner.id()
    def request(method, path, callback=None, body=None, **kwargs):
        return server.request(method, path[len(prefix):], callback, body, **kwargs)
    controller._http_client.createHTTPQuery.side_effect = request
    with patch.object(Topology, '_instance', topology, create=True):
        controller.createHTTPQuery('POST', prefix + '/nodes', body=node())
        settled(history)
    assert len(history.document.entries) == 1
    assert history.can_undo


def test_stale_manifest_preserves_original_and_resumes_recording():
    owner, history, server = session()
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    # A saved topology edited by another client must not execute stale deltas.
    actual = {key('nodes', node()): node(x=900)}
    server.state = copy.deepcopy(actual)
    loaded = []
    owner2, reopened, _ = session(server)
    reopened.load(actual, lambda: loaded.append(True))
    drain(lambda: bool(loaded))
    settled(reopened)
    assert not reopened.invalid and reopened.document.cursor == 0
    assert not reopened.can_undo and reopened.recovery_message
    assert server.state == actual
    assert any('history-recovery-' in path for path in server.files)
    edit(reopened, server, 'PUT', '/' + key('nodes', node()), {'x': 910})
    settled(reopened)
    assert reopened.can_undo
    reopened.navigate(0)
    settled(reopened)
    assert server.state == actual


def test_gui_apply_failure_never_claims_success_or_leaves_replay_locked():
    owner, history, server = session()
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    history._apply_gui.side_effect = RuntimeError('Unavailable GUI resource')
    history.navigate(0)
    settled(history)
    assert history.invalid and history.document.cursor == 1
    assert not history.replaying and not history.can_undo
    assert server.state == {}


def test_navigation_failure_persists_last_successful_intermediate_cursor():
    a = node()
    owner, history, server = session()
    edit(history, server, 'POST', '/nodes', a)
    settled(history)
    edit(history, server, 'PUT', '/' + key('nodes', a), {'x': 10})
    settled(history)
    edit(history, server, 'PUT', '/' + key('nodes', a), {'x': 20})
    settled(history)
    server.fail = lambda method, path, body: method == 'DELETE'
    history.navigate(0)
    settled(history)
    assert history.document.cursor == 1 and not history.invalid
    assert history._saved_revision == history.document.revision
    assert server.state[key('nodes', a)]['x'] == 0


@pytest.mark.parametrize('raw_cached', [False, True])
def test_partial_drawing_notifications_retain_confirmed_svg(raw_cached):
    shape = drawing()
    owner, history, server = session(FileServer({key('drawings', shape): shape}))
    if raw_cached:
        history.observe('drawings', shape)
    history.begin()
    patch = {'drawing_id': shape['drawing_id'], 'x': 50}
    history.observe('drawings', patch, external=True)
    edit(history, server, 'PUT', '/' + key('drawings', shape), {'x': 50})
    history.end()
    settled(history)
    assert not history.invalid and len(history.document.entries) == 1
    assert history.document.state[key('drawings', shape)]['svg'] == shape['svg']
    assert history._raw_state[key('drawings', shape)]['svg'] == shape['svg']
    history.navigate(0)
    settled(history)
    assert history.document.state[key('drawings', shape)] == shape


def test_detachment_and_partial_container_echo_are_one_reversible_operation():
    import json
    a = node('A', x=20)
    def container(children):
        metadata = {'revision': 1, 'name': 'LAN', 'children': children}
        svg = '<svg><metadata id="gns3-canvas-group">' + json.dumps(metadata) + '</metadata><rect width="100" height="80"/></svg>'
        return dict(drawing('LAN'), svg=svg)
    before = canonical('drawings', container([{'type': 'node', 'id': a['node_id']}]))
    after = canonical('drawings', container([]))
    owner, history, server = session(FileServer({key('nodes', a): a, key('drawings', before): before}))
    history.begin()
    edit(history, server, 'PUT', '/' + key('nodes', a), {'x': 500})
    history.observe('drawings', {'drawing_id': before['drawing_id'], 'x': 0}, external=True)
    edit(history, server, 'PUT', '/' + key('drawings', before), {'svg': after['svg']})
    history.end()
    settled(history)
    assert len(history.document.entries) == 1
    assert len(history.document.entries[0]['changes']) == 2
    assert 'membership' in history.document.entries[0]['description']
    history.navigate(0)
    settled(history)
    assert history.document.state[key('nodes', a)]['x'] == 20
    assert history.document.state[key('drawings', before)] == before
    history.navigate(1)
    settled(history)
    assert history.document.state[key('nodes', a)]['x'] == 500
    assert history.document.state[key('drawings', before)] == after


def test_recovered_history_survives_two_reopens_and_preserves_both_slots():
    owner, original, server = session()
    edit(original, server, 'POST', '/nodes', node())
    settled(original)
    edit(original, server, 'PUT', '/' + key('nodes', node()), {'x': 10})
    settled(original)
    originals = dict(server.files)
    server.state[key('nodes', node())]['x'] = 400
    owner2, recovered, _ = session(server)
    done = []
    recovered.load(copy.deepcopy(server.state), lambda: done.append(True))
    drain(lambda: bool(done))
    settled(recovered)
    copies = {path: raw for path, raw in server.files.items() if 'history-recovery-' in path}
    assert set(copies.values()) == set(originals.values())
    assert not recovered.invalid and not recovered.document.entries
    edit(recovered, server, 'PUT', '/' + key('nodes', node()), {'x': 450})
    settled(recovered)
    for cycle in range(2):
        owner3, reopened, _ = session(server)
        done.clear()
        reopened.load(copy.deepcopy(server.state), lambda: done.append(True))
        drain(lambda: bool(done))
        assert not reopened.invalid and not reopened.recovery_message
        assert reopened.document.cursor == 1 and reopened.can_undo
        reopened.navigate(0)
        settled(reopened)
        assert server.state[key('nodes', node())]['x'] == 400
        reopened.navigate(1)
        settled(reopened)
        assert server.state[key('nodes', node())]['x'] == 450
    assert copies == {path: raw for path, raw in server.files.items() if 'history-recovery-' in path}


def test_failed_recovery_upload_never_overwrites_original_slots():
    owner, history, server = session()
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    before = dict(server.files)
    server.state[key('nodes', node())]['x'] = 999
    server.reject_upload = True
    owner2, reopened, _ = session(server)
    done = []
    reopened.load(copy.deepcopy(server.state), lambda: done.append(True))
    drain(lambda: bool(done))
    assert reopened.invalid and 'left untouched' in reopened.invalid
    assert server.files == before
    assert not reopened.can_undo


def test_corrupt_or_newer_version_slots_are_archived_before_recording_resumes():
    owner, history, server = session()
    server.files['/files/' + SLOTS[0]] = b'unsupported or truncated file'
    done = []
    history.load({}, lambda: done.append(True))
    drain(lambda: bool(done))
    settled(history)
    assert not history.invalid and history.recovery_message
    assert b'unsupported or truncated file' in [raw for name, raw in server.files.items() if 'history-recovery-' in name]
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    assert history.can_undo


def test_unreadable_slot_is_never_replaced_by_recovery():
    owner, history, server = session()
    edit(history, server, 'POST', '/nodes', node())
    settled(history)
    originals = dict(server.files)
    server.state[key('nodes', node())]['x'] = 500
    owner2, reopened, _ = session(server)
    def transport(method, path, callback=None, **kwargs):
        if method == 'GET' and path == '/files/' + SLOTS[0]:
            callback({'status': 403, 'message': 'Access denied'}, error=True)
        else:
            server.request(method, path, callback, **kwargs)
    reopened._transport = transport
    done = []
    reopened.load(copy.deepcopy(server.state), lambda: done.append(True))
    drain(lambda: bool(done))
    assert reopened.invalid and 'could not be read' in reopened.invalid
    assert server.files == originals
