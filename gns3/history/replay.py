# SPDX-License-Identifier: GPL-3.0-or-later
"""Asynchronous resource-delta replay with preflight and verified compensation."""
import copy
import json
import xml.etree.ElementTree as ET
from ..qt import QtCore
from .model import canonical, resource, IDS

# Built-in network objects report "started" permanently and have no power
# lifecycle. Applying VM stop restrictions to them would make undo unusable.
ALWAYS_ON = {'ethernet_switch', 'ethernet_hub', 'cloud', 'nat', 'frame_relay_switch', 'atm_switch'}


def running(value):
    return value.get('status') in ('started', 'suspended') and value.get('node_type') not in ALWAYS_ON


def connections(value):
    return sorted((n['node_id'], n['adapter_number'], n['port_number']) for n in value['nodes'])


def plan(changes):
    """Dependency order: disconnect, delete, create nodes, visuals, reconnect."""
    steps = []
    for key, change in changes.items():
        before, after = change['before'], change['after']
        kind, _ = resource(key)
        reconnect = kind == 'links' and before and after and connections(before) != connections(after)
        if before is not None and (after is None or reconnect):
            rank = {'links': 0, 'drawings': 1, 'nodes': 2}[kind]
            steps.append((rank, 'DELETE', key, None))
        if after is not None and (before is None or reconnect):
            rank = {'nodes': 3, 'drawings': 5, 'links': 6}[kind]
            steps.append((rank, 'POST', key, after))
        elif before is not None and after is not None and not reconnect:
            body = {field: copy.deepcopy(value) for field, value in after.items()
                    if field != IDS[kind] and before.get(field) != value}
            # Server updates are patches, but properties is a complete saved
            # emulator property object. No runtime/start/stop endpoint is used.
            if body:
                steps.append((4 if kind == 'nodes' else 5 if kind == 'drawings' else 6, 'PUT', key, body))
    return sorted(steps, key=lambda s: (s[0], s[2]))


class Replay:
    """Transport signature: request(method, path, callback, body=None).

    finished(success, message, trustworthy, state) runs only after verification.
    GUI application and cursor mutation belong to the caller, not HTTP callbacks.
    """
    def __init__(self, request, changes, finished):
        self.transport = request
        self.identities = {}
        self.uncertain_link = None
        self.link_ids = set()
        self.changes = copy.deepcopy(changes)
        self.finished = finished
        self.raw = {}
        self.actual = {}
        self.original = {}
        self.applied = []
        self.steps = plan(changes)
        self.error = ''
        self.rolling_back = False
        self.queue = list(changes)
        # Link creation/deletion/reconnection must respect running endpoints.
        self.extra_nodes = set()
        for key, change in changes.items():
            if key.startswith('links/') and (change['before'] is None or change['after'] is None or
                    connections(change['before']) != connections(change['after'])):
                for value in change.values():
                    if value:
                        self.extra_nodes.update('nodes/' + n['node_id'] for n in value['nodes'])
        self.extra_nodes.difference_update(changes)

    def start(self):
        self._preflight_next()

    def request(self, method, path, callback, body=None):
        physical = path
        if path.startswith('/links/'):
            identity = path.split('/')[-1]
            physical = '/links/' + self.identities.get(identity, identity)
        def received(result, error=False, **kwargs):
            if not error and isinstance(result, dict) and 'link_id' in result:
                if method == 'POST' and path == '/links':
                    logical = body['link_id']
                    if logical != result['link_id']:
                        self.identities[logical] = result['link_id']
                else:
                    logical = path.split('/')[-1]
                result = dict(result, link_id=logical)
            callback(result, error=error, **kwargs)
        self.transport(method, physical, received, body=body)

    def _later(self, function):
        QtCore.QTimer.singleShot(0, function)

    def _preflight_next(self):
        if self.queue:
            key = self.queue.pop(0)
            self.request('GET', '/' + key, lambda result, error=False, **kw: self._read(key, result, error))
            return
        if self.extra_nodes:
            key = self.extra_nodes.pop()
            self.request('GET', '/' + key, lambda result, error=False, **kw: self._running_endpoint(key, result, error))
            return
        # Verify there are no unrecorded connections about to be cascade-deleted.
        removing = {resource(key)[1] for key, c in self.changes.items() if key.startswith('nodes/') and c['after'] is None}
        creating_links = [c['after'] for key, c in self.changes.items()
                          if key.startswith('links/') and c['before'] is None and c['after'] is not None]
        if removing or creating_links:
            def links(result, error=False, **kw):
                if error:
                    return self._stop('Cannot verify connections before deleting a device')
                for value in result:
                    self.link_ids.add(value['link_id'])
                    if any(connections(value) == connections(after) for after in creating_links):
                        return self._stop('A connection already occupies the interfaces being restored', trustworthy=False)
                    if any(n['node_id'] in removing for n in value['nodes']):
                        key = 'links/' + value['link_id']
                        if key not in self.changes or self.changes[key]['after'] is not None:
                            return self._stop('The device has a connection outside this history operation')
                self._step()
            self.request('GET', '/links', links)
        else:
            self._step()

    def _read(self, key, result, error):
        expected = self.changes[key]['before']
        if error:
            if result.get('status') != 404 or expected is not None:
                return self._stop('Cannot read {}: {}'.format(key, result.get('message', 'request failed')))
            value = None
        else:
            try:
                value = canonical(resource(key)[0], result)
            except (ValueError, KeyError, TypeError):
                return self._stop('Invalid server state for ' + key, trustworthy=False)
            self.raw[key] = result
        if value != expected:
            return self._stop('The server state has changed for {}. History was not applied.'.format(key), trustworthy=False)
        if key.startswith('nodes/') and value is not None and running(result):
            after = self.changes[key]['after']
            fields = set(value) if after is None else {f for f in value.keys() | after.keys() if value.get(f) != after.get(f)}
            visual = {'x', 'y', 'z', 'label', 'locked', 'symbol'}
            if not fields <= visual:
                return self._stop('Stop device {} before undoing this structural or property change'.format(value.get('name', key)))
        self.actual[key] = value
        self.original[key] = copy.deepcopy(value)
        self._later(self._preflight_next)

    def _running_endpoint(self, key, result, error):
        # A node being restored by the same operation does not exist yet and is
        # already checked in changes; other endpoint devices must be available.
        if error or running(result):
            return self._stop('Stop the connected devices before changing their connections')
        self._later(self._preflight_next)

    def _body(self, key, data):
        body = copy.deepcopy(data)
        if key.startswith('drawings/') and 'svg' in body:
            root = ET.fromstring(body['svg'])
            meta = next((e for e in root.iter() if e.get('id') == 'gns3-canvas-group'), None)
            if meta is not None:
                previous = self.raw.get(key, {}).get('svg', '')
                revision = 0
                if previous:
                    old = next((e for e in ET.fromstring(previous).iter() if e.get('id') == 'gns3-canvas-group'), None)
                    if old is not None:
                        revision = json.loads(old.text).get('revision', 0)
                value = json.loads(meta.text)
                value['revision'] = revision + 1
                meta.text = json.dumps(value, ensure_ascii=False)
                body['svg'] = ET.tostring(root, encoding='unicode')
        return body

    def _step(self):
        if not self.steps:
            self.queue = list(self.changes)
            return self._verify_next()
        _, method, key, body = self.steps.pop(0)
        before = copy.deepcopy(self.actual.get(key))
        kind, _ = resource(key)
        path = '/' + (kind if method == 'POST' else key)
        def completed(result, error=False, **kw):
            if error:
                if method == 'POST' and kind == 'links':
                    self.uncertain_link = (key, body)
                return self._fail('{} {}: {}'.format(method, key, result.get('message', 'request failed')))
            try:
                value = None if method == 'DELETE' else canonical(kind, result)
            except (ValueError, KeyError, TypeError):
                return self._fail('Invalid server acknowledgment for ' + key)
            self.actual[key] = value
            if method != 'DELETE':
                self.raw[key] = result
            self.applied.append((key, before, copy.deepcopy(value)))
            self._later(self._step)
        self.request(method, path, completed, body=self._body(key, body) if body is not None else None)

    def _verify_next(self):
        if not self.queue:
            if self.rolling_back:
                return self.finished(False, self.error, True, self.original)
            return self.finished(True, '', True, self.actual)
        key = self.queue.pop(0)
        expected = self.original.get(key) if self.rolling_back else self.changes[key]['after']
        def verified(result, error=False, **kw):
            try:
                value = None if error and result.get('status') == 404 else canonical(resource(key)[0], result) if not error else False
            except (ValueError, KeyError, TypeError):
                value = False
            if value != expected:
                if self.rolling_back:
                    return self._stop(self.error + '\nCompensation could not be verified. Clear history after reviewing the topology.', False)
                return self._fail('The server did not retain the requested state for ' + key)
            self.actual[key] = value
            self._later(self._verify_next)
        self.request('GET', '/' + key, verified)

    def _fail(self, message):
        if self.rolling_back:
            return self._stop(self.error + '\nCompensation failed: ' + message, False)
        self.error = message
        self.rolling_back = True
        self.queue = list(self.changes)
        if self.uncertain_link:
            key, body = self.uncertain_link
            def discovered(result, error=False, **kwargs):
                if error:
                    return self._stop(message + '\nCannot locate a possibly created connection.', False)
                matches = [v for v in result if v['link_id'] not in self.link_ids and connections(v) == connections(body)]
                if len(matches) > 1:
                    return self._stop(message + '\nAmbiguous connection after a failed creation.', False)
                if matches:
                    self.identities[resource(key)[1]] = matches[0]['link_id']
                self._recover_next()
            return self.transport('GET', '/links', discovered)
        self._recover_next()

    def _recover_next(self):
        # A timeout does not prove a write was rejected. Read all affected
        # resources before compensating, including the failed request's target.
        if not self.queue:
            changes = {key: {'before': self.actual.get(key), 'after': value}
                       for key, value in self.original.items() if self.actual.get(key) != value}
            self.steps = plan(changes)
            return self._later(self._step)
        key = self.queue.pop(0)
        def recovered(result, error=False, **kw):
            if error and result.get('status') != 404:
                return self._stop(self.error + '\nCannot establish the state for compensation.', False)
            try:
                self.actual[key] = None if error else canonical(resource(key)[0], result)
            except (ValueError, KeyError, TypeError):
                return self._stop(self.error + '\nInvalid state during compensation.', False)
            self._later(self._recover_next)
        self.request('GET', '/' + key, recovered)

    def _stop(self, message, trustworthy=True):
        self.finished(False, message, trustworthy, self.actual)
