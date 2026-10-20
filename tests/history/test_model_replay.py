"""State-machine tests use an API-shaped server, not GUI-only undo mocks."""
import copy
import uuid
from unittest.mock import MagicMock
import pytest
from PyQt6.QtTest import QTest
from gns3.history.model import HistoryDocument, canonical, state_from_lists
from gns3.history.replay import Replay, plan
from gns3.history.storage import encode, decode


def identity(name):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, name))


def node(name='N', x=0):
    return dict(node_id=identity(name), name=name, node_type='ethernet_switch',
                compute_id='local', properties={}, x=x, y=0, z=0, locked=False)


def link(a, b):
    return dict(link_id=identity(a['name'] + b['name']), nodes=[
        dict(node_id=a['node_id'], adapter_number=0, port_number=0),
        dict(node_id=b['node_id'], adapter_number=0, port_number=1)])


def drawing(name='shape', x=0, width=100):
    return dict(drawing_id=identity(name), x=x, y=0, z=0, locked=False, rotation=0,
                svg='<svg width="{}" height="80"><rect width="{}" height="80"/></svg>'.format(width, width))


def key(kind, value):
    return kind + '/' + value[dict(nodes='node_id', links='link_id', drawings='drawing_id')[kind]]


def delta(kind, before, after):
    return {key(kind, after or before): dict(before=canonical(kind, before), after=canonical(kind, after))}


def drain(condition):
    for _ in range(200):
        if condition():
            return
        QTest.qWait(1)
    assert condition(), 'asynchronous history operation did not settle'


class Server:
    def __init__(self, state=None):
        self.state = copy.deepcopy(state or {})
        self.calls = []
        self.fail = None
        self.started = set()
        self.apply_then_timeout = False

    def request(self, method, path, callback=None, body=None, **kwargs):
        self.calls.append((method, path, copy.deepcopy(body)))
        k = path.lstrip('/')
        kind = k.split('/')[0]
        if self.fail and self.fail(method, path, body):
            if self.apply_then_timeout and method == 'PUT':
                self.state[k].update(copy.deepcopy(body))
            if callback:
                callback(dict(status=409, message='Rejected by test server'), error=True)
            return
        if method == 'GET':
            if '/' not in k:
                value = [copy.deepcopy(v) for name, v in self.state.items() if name.startswith(k + '/')]
            elif k in self.state:
                value = copy.deepcopy(self.state[k])
                if kind == 'nodes':
                    value['status'] = 'started' if value['node_id'] in self.started else 'stopped'
            else:
                callback(dict(status=404, message='Not found'), error=True)
                return
        elif method == 'POST':
            value = copy.deepcopy(body)
            k = key(kind, value)
            assert k not in self.state
            self.state[k] = value
        elif method == 'PUT':
            assert k in self.state
            self.state[k].update(copy.deepcopy(body))
            value = copy.deepcopy(self.state[k])
        else:
            assert k in self.state
            removed = self.state.pop(k)
            if kind == 'nodes':
                for name, value in list(self.state.items()):
                    if name.startswith('links/') and any(n['node_id'] == removed['node_id'] for n in value['nodes']):
                        del self.state[name]
            value = {}
        if callback:
            callback(value)


def replay(server, changes):
    done = []
    runner = Replay(server.request, changes, lambda *args: done.append(args))
    runner.start()
    drain(lambda: bool(done))
    return done[0]


def test_linear_cursor_branching_and_noop():
    a = node()
    doc = HistoryDocument(identity('project'))
    assert doc.record(delta('nodes', None, a))
    doc.record(delta('nodes', a, node(x=10)))
    assert doc.cursor == 2
    doc.cursor = 1
    doc.state[key('nodes', a)] = a
    assert not doc.record(delta('nodes', a, a))
    assert len(doc.entries) == 2  # No-op must not discard redo.
    doc.record(delta('nodes', a, node(x=20)))
    assert len(doc.entries) == 2 and doc.entries[1]['changes'][key('nodes', a)]['after']['x'] == 20
    assert HistoryDocument.load(doc.payload()).payload() == doc.payload()


def test_rolling_limit_retains_a_reversible_initial_state():
    a = node()
    doc = HistoryDocument(identity('project'), {key('nodes', a): a})
    for i in range(120):
        doc.record(delta('nodes', node(x=i), node(x=i + 1)))
    assert len(doc.entries) == doc.cursor == 100
    loaded = HistoryDocument.load(doc.payload())
    for entry in reversed(loaded.entries):
        for k, c in entry['changes'].items():
            assert loaded.state[k] == c['after']
            loaded.state[k] = c['before']
        loaded.cursor -= 1
    assert loaded.state[key('nodes', a)]['x'] == 20


def test_clear_keeps_current_state_and_resets_cursor():
    doc = HistoryDocument(identity('project'))
    doc.record(delta('nodes', None, node()))
    state = copy.deepcopy(doc.state)
    doc.clear()
    assert doc.state == state and not doc.entries and doc.cursor == 0


@pytest.mark.parametrize('damage', ['version', 'cursor', 'path', 'chain', 'count'])
def test_invalid_history_is_not_executable(damage):
    doc = HistoryDocument(identity('project'))
    doc.record(delta('nodes', None, node()))
    data = doc.payload()
    if damage == 'version':
        data['version'] = 99
    elif damage == 'cursor':
        data['cursor'] = -1
    elif damage == 'path':
        data['state']['../../projects'] = node()
    elif damage == 'chain':
        data['state'][key('nodes', node())] = node(x=99)
    else:
        data['entries'] = data['entries'] * 101
    with pytest.raises(ValueError):
        HistoryDocument.load(data)


def test_checksum_roundtrip_and_corruption():
    doc = HistoryDocument(identity('project'))
    doc.record(delta('nodes', None, node()))
    path = encode(doc.payload())
    try:
        assert decode(path.read_bytes()).payload() == doc.payload()
        with pytest.raises((ValueError, OSError, EOFError)):
            decode(path.read_bytes()[:-8])
    finally:
        path.unlink()


def test_add_move_delete_node_and_connections():
    a, b = node('A'), node('B')
    connection = link(a, b)
    server = Server({key('nodes', b): b})
    changes = dict(delta('nodes', None, a), **delta('links', None, connection))
    assert replay(server, changes)[:3] == (True, '', True)
    assert [method for method, _, _ in server.calls if method != 'GET'] == ['POST', 'POST']
    before = copy.deepcopy(server.state)
    deleting = {k: dict(before=v, after=None) for k, v in before.items() if k != key('nodes', b)}
    assert replay(server, deleting)[0]
    assert set(server.state) == {key('nodes', b)}
    restoring = {k: dict(before=None, after=c['before']) for k, c in deleting.items()}
    assert replay(server, restoring)[0]
    assert server.state == before


@pytest.mark.parametrize('kind', ['drawings', 'nodes'])
def test_move_resize_and_properties_patch_only_changed_resource(kind):
    before = drawing() if kind == 'drawings' else node()
    after = drawing(x=40, width=250) if kind == 'drawings' else node(x=40)
    server = Server({key(kind, before): before, key('nodes', node('Other')): node('Other')})
    assert replay(server, delta(kind, before, after))[0]
    writes = [c for c in server.calls if c[0] != 'GET']
    assert len(writes) == 1 and writes[0][0] == 'PUT'
    assert 'node_id' not in writes[0][2] and 'drawing_id' not in writes[0][2]


def test_rejection_after_partial_success_is_compensated():
    a, b = node('A'), node('B')
    server = Server({key('nodes', b): b})
    original = copy.deepcopy(server.state)
    server.fail = lambda method, path, body: method == 'POST' and path == '/links'
    changes = dict(delta('nodes', None, a), **delta('links', None, link(a, b)))
    success, message, trusted, state = replay(server, changes)
    assert not success and trusted and 'Rejected' in message
    assert server.state == original


def test_timeout_after_applied_write_recovers_actual_state_before_compensation():
    a = node()
    server = Server({key('nodes', a): a})
    failures = []
    def fail(method, path, body):
        if method == 'PUT' and not failures:
            failures.append(True)
            return True
        return False
    server.fail = fail
    server.apply_then_timeout = True
    result = replay(server, delta('nodes', a, node(x=100)))
    assert not result[0] and result[2]
    assert server.state[key('nodes', a)] == a


def test_failed_compensation_is_untrustworthy():
    a, b = node('A'), node('B')
    server = Server({key('nodes', b): b})
    server.fail = lambda method, path, body: (method == 'POST' and path == '/links') or method == 'DELETE'
    result = replay(server, dict(delta('nodes', None, a), **delta('links', None, link(a, b))))
    assert not result[0] and not result[2]


def test_server_divergence_and_running_nodes_prevent_destructive_replay():
    a = dict(node(), node_type='qemu')
    server = Server({key('nodes', a): node(x=5)})
    assert not replay(server, delta('nodes', a, None))[2]
    assert all(c[0] == 'GET' for c in server.calls)
    server = Server({key('nodes', a): a})
    server.started.add(a['node_id'])
    assert not replay(server, delta('nodes', a, None))[0]
    assert replay(server, delta('nodes', a, dict(a, x=30)))[0]  # Layout remains editable.


def test_unrecorded_incident_link_blocks_node_deletion():
    a, b = node('A'), node('B')
    connection = link(a, b)
    server = Server({key('nodes', a): a, key('nodes', b): b, key('links', connection): connection})
    assert not replay(server, delta('nodes', a, None))[0]
    assert all(c[0] == 'GET' for c in server.calls)


def test_import_remaps_current_and_deleted_resource_ids():
    project, imported = identity('project'), identity('imported')
    a = node('A')
    doc = HistoryDocument(project)
    doc.record(delta('nodes', None, a))
    doc.record(delta('nodes', a, None))
    loaded = HistoryDocument.load(doc.payload()).remap_import(imported, {})
    new_id = loaded.entries[0]['changes'].popitem()[1]['after']['node_id']
    assert new_id != a['node_id']
    doc = HistoryDocument(project)
    doc.record(delta('nodes', None, a))
    new = dict(a, node_id=identity('importedA'))
    loaded = doc.remap_import(imported, {key('nodes', new): new})
    assert loaded.project_id == imported and loaded.state == {key('nodes', new): new}


def test_runtime_is_not_captured_and_container_revision_is_not_an_edit():
    assert canonical('nodes', dict(node(), status='started', command_line='qemu')) == node()
    base = drawing()
    base['svg'] = '<svg><metadata id="gns3-canvas-group">{"revision":1,"name":"LAN"}</metadata></svg>'
    other = dict(base, svg=base['svg'].replace('"revision":1', '"revision":5'))
    assert canonical('drawings', base) == canonical('drawings', other)


def test_saved_container_load_normalizes_xml_prefixes_without_losing_operations():
    import xml.etree.ElementTree as ET
    namespaces = dict(ET._namespace_map)
    try:
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        a = dict(drawing(), svg='<svg xmlns="http://www.w3.org/2000/svg"><metadata id="gns3-canvas-group">{"revision":3,"name":"LAN","children":[]}</metadata><rect width="100" height="80"/></svg>')
        doc = HistoryDocument(identity('project'))
        doc.record(delta('drawings', None, a))
        doc.record(delta('drawings', a, dict(a, x=40)))
        payload = doc.payload()
        ET.register_namespace('other', 'http://www.w3.org/2000/svg')
        loaded = HistoryDocument.load(payload)
        assert len(loaded.entries) == loaded.cursor == 2
        actual = canonical('drawings', dict(a, x=40))
        assert loaded.state == {key('drawings', a): actual}
        assert loaded.remap_import(doc.project_id, loaded.state) is loaded
        assert HistoryDocument.load(loaded.payload()).payload() == loaded.payload()
    finally:
        ET._namespace_map.clear()
        ET._namespace_map.update(namespaces)


def test_container_numeric_formatting_is_not_an_edit():
    a = dict(drawing(), svg='<svg width="100" height="80"><metadata id="gns3-canvas-group">{"revision":1,"name":"LAN","origin":{"x":10,"y":20},"size":{"width":100,"height":80},"children":[]}</metadata><rect/></svg>')
    b = dict(a, svg=a['svg'].replace('100', '100.0').replace('80', '80.0').replace(':10,', ':10.0,').replace(':20}', ':20.0}'))
    assert canonical('drawings', a) == canonical('drawings', b)


def test_container_move_and_resize_descriptions_do_not_depend_on_secondary_node_updates():
    import json
    def frame(origin, size):
        data = {'revision': 0, 'name': 'LAN', 'origin': {'x': origin, 'y': 0},
                'size': {'width': size, 'height': 80}, 'children': []}
        return dict(drawing(), x=origin, svg='<svg><metadata id="gns3-canvas-group">' + json.dumps(data) + '</metadata><rect/></svg>')
    before, moved, resized = frame(0, 100), frame(30, 100), frame(0, 200)
    for related in (False, True):
        doc = HistoryDocument(identity('project'))
        changes = delta('drawings', before, moved)
        if related:
            changes.update(delta('nodes', node(), node(x=30)))
        doc.record(changes)
        assert doc.entries[-1]['description'] == 'Move container LAN'
        changes = delta('drawings', before, resized)
        if related:
            changes.update(delta('nodes', node(), node(x=30)))
        doc.record(changes)
        assert doc.entries[-1]['description'] == 'Resize container LAN'


@pytest.mark.parametrize('node_type', ['cloud', 'nat', 'ethernet_hub', 'frame_relay_switch', 'atm_switch'])
def test_non_console_builtin_history_survives_server_console_default(node_type):
    original = dict(node(), node_type=node_type, console_type=None)
    reopened = dict(original, console_type='none')
    assert canonical('nodes', original) == canonical('nodes', reopened)
    missing = dict(original)
    del missing['console_type']
    assert canonical('nodes', missing) == canonical('nodes', reopened)
    history = HistoryDocument(identity('project'), {key('nodes', original): canonical('nodes', original)})
    changed = dict(original, x=100)
    history.record(delta('nodes', original, changed), 'Move device')
    payload = copy.deepcopy(history.payload())
    for value in payload['state'].values():
        value['console_type'] = None
    for entry in payload['entries']:
        for change in entry['changes'].values():
            change['before']['console_type'] = None
            change['after']['console_type'] = None
    loaded = HistoryDocument.load(payload)
    assert loaded.state == {key('nodes', changed): canonical('nodes', dict(changed, console_type='none'))}
    assert loaded.cursor == 1
    for value in payload['state'].values():
        del value['console_type']
    for entry in payload['entries']:
        for change in entry['changes'].values():
            del change['before']['console_type']
            del change['after']['console_type']
    assert HistoryDocument.load(payload).state == loaded.state


def test_console_normalization_preserves_real_console_changes():
    original = dict(node(), node_type='qemu', console_type=None)
    assert canonical('nodes', original) != canonical('nodes', dict(original, console_type='none'))
    assert canonical('nodes', dict(original, console_type='telnet')) != canonical('nodes', dict(original, console_type='vnc'))
