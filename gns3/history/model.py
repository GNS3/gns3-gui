# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded, JSON-only operation log. No Qt, networking or live object references."""
import copy
import json
import re
import uuid
import xml.etree.ElementTree as ET

LIMIT = 100
VERSION = 1
KINDS = ('nodes', 'links', 'drawings')
FIELDS = {
    'nodes': {'node_id', 'name', 'node_type', 'compute_id', 'properties', 'console',
              'console_type', 'console_auto_start', 'symbol', 'x', 'y', 'z', 'locked',
              'label', 'port_name_format', 'port_segment_size', 'first_port_name', 'custom_adapters'},
    'links': {'link_id', 'nodes', 'filters', 'suspend', 'link_style'},
    'drawings': {'drawing_id', 'x', 'y', 'z', 'locked', 'rotation', 'svg'},
}
IDS = {'nodes': 'node_id', 'links': 'link_id', 'drawings': 'drawing_id'}
RESOURCE = re.compile(r'^(nodes|links|drawings)/([a-fA-F0-9-]{36})$')
UUID_TOKEN = re.compile(r'(?<![a-fA-F0-9-])[a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}(?![a-fA-F0-9-])')


def resource(key):
    match = RESOURCE.fullmatch(key)
    if not match:
        raise ValueError('Invalid history resource identifier')
    kind, identity = match.groups()
    if str(uuid.UUID(identity)) != identity.lower():
        raise ValueError('Invalid history UUID')
    return kind, identity


def canonical(kind, data):
    """Retain API-writable topology state, excluding emulator/capture runtime."""
    if data is None:
        return None
    if kind not in KINDS or not isinstance(data, dict) or IDS[kind] not in data:
        raise ValueError('Invalid history resource')
    result = copy.deepcopy({key: value for key, value in data.items() if key in FIELDS[kind]})
    resource(kind + '/' + result[IDS[kind]])
    if kind == 'links':
        if len(result.get('nodes', [])) != 2:
            raise ValueError('A history link needs two endpoints')
        result['nodes'] = sorted(result['nodes'], key=lambda n: (n['node_id'], n['adapter_number'], n['port_number']))
        for end in result['nodes']:
            resource('nodes/' + end['node_id'])
            if not isinstance(end['adapter_number'], int) or not isinstance(end['port_number'], int):
                raise ValueError('Invalid link interface')
    if kind == 'nodes' and not all(isinstance(result.get(field), str) for field in ('name', 'node_type', 'compute_id')):
        raise ValueError('Incomplete node definition')
    if kind == 'drawings':
        if not isinstance(result.get('svg'), str):
            raise ValueError('Missing history drawing SVG')
        try:
            root = ET.fromstring(result['svg'])
        except ET.ParseError as error:
            raise ValueError('Invalid history drawing SVG') from error
        metadata = next((e for e in root.iter() if e.get('id') == 'gns3-canvas-group'), None)
        if metadata is not None:
            data = json.loads(metadata.text)
            data['revision'] = 0  # Transport echo ordering is not a user edit.
            metadata.text = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
            result['svg'] = ET.tostring(root, encoding='unicode')
    # Reject non-JSON values and NaN before they reach disk or a server request.
    json.dumps(result, allow_nan=False)
    return result


def state_from_lists(lists):
    state = {}
    for kind in KINDS:
        for value in lists.get(kind, []):
            data = canonical(kind, value)
            state[kind + '/' + data[IDS[kind]]] = data
    return state


def drawing_type(data):
    root = ET.fromstring(data['svg'])
    if any(e.get('id') == 'gns3-canvas-group' for e in root.iter()):
        return 'container'
    for child in root:
        tag = child.tag.rsplit('}', 1)[-1]
        if tag != 'metadata':
            return {'ellipse': 'circle', 'rect': 'rectangle', 'line': 'line', 'text': 'note'}.get(tag, 'image')
    return 'drawing'


def description(changes, hint=None):
    groups = []
    membership = False
    for key, change in changes.items():
        if key.startswith('drawings/'):
            values = []
            for value in (change['before'], change['after']):
                root = ET.fromstring(value['svg']) if value else []
                meta = next((e for e in root.iter() if e.get('id') == 'gns3-canvas-group'), None) if value else None
                values.append(json.loads(meta.text) if meta is not None else None)
            if any(values):
                groups.append(values)
                if all(values):
                    membership |= {(v['type'], v['id']) for v in values[0].get('children', [])} != {
                        (v['type'], v['id']) for v in values[1].get('children', [])}
    if hint:
        names = ', '.join((after or before).get('name', 'container') for before, after in groups[:2])
        return hint + (' ' + names if names and 'container' in hint.lower() else '')
    nodes = [(key, c) for key, c in changes.items() if key.startswith('nodes/')]
    if nodes and any(c['before'] is None or c['after'] is None for _, c in nodes):
        added = nodes[0][1]['before'] is None
        names = ', '.join((c['after'] or c['before']).get('name', key) for key, c in nodes[:3])
        return ('New device ' if added else 'Delete device ') + names
    if len(changes) > 1:
        if membership:
            return 'Move selection and update container membership'
        if groups:
            return 'Move or change container ' + (groups[0][1] or groups[0][0]).get('name', '')
        if all(c['before'] and c['after'] and
               {f for f in c['before'].keys() | c['after'].keys() if c['before'].get(f) != c['after'].get(f)} <= {'x', 'y', 'z'}
               for c in changes.values()):
            return 'Move selection ({} elements)'.format(len(changes))
        return 'Change selection ({} elements)'.format(len(changes))
    key, change = next(iter(changes.items()))
    before, after = change['before'], change['after']
    kind, _ = resource(key)
    value = after or before
    if kind == 'links':
        ends = value['nodes']
        endpoints = ' to '.join('{} ({}:{})'.format(n['node_id'], n['adapter_number'], n['port_number']) for n in ends)
        return ('Create link from ' if before is None else 'Delete link from ' if after is None else 'Change link ') + endpoints
    noun = value.get('name', 'device') if kind == 'nodes' else drawing_type(value)
    if groups:
        noun += ' ' + (groups[0][1] or groups[0][0]).get('name', '')
    if before is None:
        return ('New ' if kind == 'nodes' else 'Draw ') + noun
    if after is None:
        return 'Delete ' + noun
    changed = {field for field in before.keys() | after.keys() if before.get(field) != after.get(field)}
    if changed <= {'x', 'y', 'z'}:
        return 'Move ' + noun
    if kind == 'drawings' and 'svg' in changed:
        if groups and all(groups[0]):
            before_group, after_group = groups[0]
            if before_group.get('size') != after_group.get('size'):
                return 'Resize ' + noun
            if membership:
                return 'Update membership of ' + noun
            return 'Change {} properties'.format(noun)
        return 'Resize or change ' + noun
    return 'Change {} properties'.format(noun)


class HistoryDocument:
    def __init__(self, project_id, state=None):
        self.project_id = str(project_id)
        self.state = copy.deepcopy(state or {})
        self.entries = []
        self.cursor = 0
        self.revision = 0

    def record(self, changes, hint=None):
        changes = {key: copy.deepcopy(value) for key, value in changes.items() if value['before'] != value['after']}
        if not changes:
            return False
        for key, change in changes.items():
            if change['after'] is None:
                self.state.pop(key, None)
            else:
                self.state[key] = copy.deepcopy(change['after'])
        self.entries[self.cursor:] = []
        self.entries.append({'description': description(changes, hint)[:512], 'changes': changes})
        if len(self.entries) > LIMIT:
            del self.entries[:len(self.entries) - LIMIT]
        self.cursor = len(self.entries)
        self.revision += 1
        return True

    def clear(self):
        self.entries = []
        self.cursor = 0
        self.revision += 1

    def rebind_links(self, mapping):
        """GNS3 allocates fresh link UUIDs on POST, including compensation."""
        def rewrite(value):
            if isinstance(value, str):
                return UUID_TOKEN.sub(lambda match: mapping.get(match.group(), match.group()), value)
            if isinstance(value, list):
                return [rewrite(v) for v in value]
            if isinstance(value, dict):
                return {rewrite(k): rewrite(v) for k, v in value.items()}
            return value
        self.state = rewrite(self.state)
        self.entries = rewrite(self.entries)
        self.revision += 1
        return rewrite

    def payload(self):
        # Values are replaced, never mutated by the recorder; shallow snapshots
        # can be serialized in a worker without copying an entire large topology.
        return dict(version=VERSION, project_id=self.project_id, cursor=self.cursor,
                    revision=self.revision, entries=list(self.entries), state=dict(self.state))

    @classmethod
    def load(cls, data):
        if not isinstance(data, dict) or data.get('version') != VERSION:
            raise ValueError('Unsupported history version')
        entries, cursor, state = data.get('entries'), data.get('cursor'), data.get('state')
        if (not isinstance(entries, list) or len(entries) > LIMIT or type(cursor) is not int or
                not 0 <= cursor <= len(entries) or not isinstance(state, dict)):
            raise ValueError('Invalid history cursor or operation count')
        result = cls(str(uuid.UUID(data['project_id'])))
        for key, value in state.items():
            kind, identity = resource(key)
            normalized = canonical(kind, value)
            if normalized.keys() != value.keys() or normalized[IDS[kind]] != identity:
                raise ValueError('Invalid history state')
            result.state[key] = normalized
        entries = copy.deepcopy(entries)
        for entry in entries:
            if (not isinstance(entry, dict) or not isinstance(entry.get('description'), str) or
                    not 0 < len(entry['description']) <= 512 or not isinstance(entry.get('changes'), dict) or not entry['changes']):
                raise ValueError('Invalid history operation')
            for key, change in entry['changes'].items():
                kind, identity = resource(key)
                if not isinstance(change, dict) or set(change) != {'before', 'after'} or change['before'] == change['after']:
                    raise ValueError('Invalid history delta')
                for side, value in change.items():
                    if value is not None:
                        normalized = canonical(kind, value)
                        if normalized.keys() != value.keys() or normalized[IDS[kind]] != identity:
                            raise ValueError('Invalid history resource in operation')
                        change[side] = normalized
        result.entries = entries
        result.cursor = cursor
        result.revision = data.get('revision', 0)
        if type(result.revision) is not int or result.revision < 0:
            raise ValueError('Invalid history revision')
        # Validate the delta chain in both directions, relative to the actual
        # cursor manifest, rather than trusting arbitrary before/after pairs.
        for backwards, sequence in ((True, reversed(entries[:cursor])), (False, iter(entries[cursor:]))):
            check = dict(result.state)
            for entry in sequence:
                source, target = ('after', 'before') if backwards else ('before', 'after')
                for key, change in entry['changes'].items():
                    if check.get(key) != change[source]:
                        raise ValueError('Inconsistent history operation chain')
                    if change[target] is None:
                        check.pop(key, None)
                    else:
                        check[key] = change[target]
        return result

    def remap_import(self, project_id, actual):
        """Rebind the entire log to imported resources using unique identities.

        Ambiguous or changed resources fail closed; never guess a device by
        an approximate position or silently drop a broken history reference.
        """
        if self.project_id == str(project_id):
            if self.state != actual:
                raise ValueError('Saved history does not match the server topology')
            return self
        mapping, compute_map = {}, {}
        for kind in KINDS:
            old = [(key, value) for key, value in self.state.items() if key.startswith(kind + '/')]
            new = [(key, value) for key, value in actual.items() if key.startswith(kind + '/')]
            if len(old) != len(new):
                raise ValueError('Imported history has a different resource count')
            unused = dict(new)
            for key, value in old:
                def matches(candidate):
                    if kind == 'nodes':
                        return (candidate['name'], candidate['node_type']) == (value['name'], value['node_type'])
                    if kind == 'drawings':
                        return candidate['svg'] == value['svg'] and candidate.get('x') == value.get('x') and candidate.get('y') == value.get('y')
                    def endpoints(record, remap):
                        return sorted((remap.get(n['node_id'], n['node_id']), n['adapter_number'], n['port_number']) for n in record['nodes'])
                    return endpoints(candidate, {}) == endpoints(value, mapping)
                candidates = [(k, v) for k, v in unused.items() if matches(v)]
                if len(candidates) != 1:
                    raise ValueError('Cannot unambiguously remap imported ' + kind)
                new_key, candidate = candidates[0]
                mapping[value[IDS[kind]]] = candidate[IDS[kind]]
                if kind == 'nodes':
                    old_compute, new_compute = value['compute_id'], candidate['compute_id']
                    if old_compute in compute_map and compute_map[old_compute] != new_compute:
                        raise ValueError('Ambiguous imported compute mapping')
                    compute_map[old_compute] = new_compute
                del unused[new_key]
        # Deleted/future resources have no current counterpart. Give them stable
        # project-specific IDs, also rewriting UUIDs embedded in container SVGs.
        for entry in self.entries:
            for key in entry['changes']:
                _, identity = resource(key)
                mapping.setdefault(identity, str(uuid.uuid5(uuid.UUID(str(project_id)), identity)))
        def rewrite(value):
            if isinstance(value, str):
                return UUID_TOKEN.sub(lambda m: mapping.get(m.group(), m.group()), value)
            if isinstance(value, list):
                return [rewrite(x) for x in value]
            if isinstance(value, dict):
                result = {rewrite(k): rewrite(v) for k, v in value.items()}
                if 'compute_id' in result:
                    result['compute_id'] = compute_map.get(result['compute_id'], result['compute_id'])
                return result
            return value
        data = rewrite(self.payload())
        data['project_id'] = str(project_id)
        # Imported consoles can be reallocated. Rebase only unchanged console
        # values, preserving deliberate historical changes to the console field.
        for old_key, old_value in self.state.items():
            if old_key.startswith('nodes/'):
                new_key = rewrite(old_key)
                current = actual[new_key]
                for entry in data['entries']:
                    for value in entry['changes'].get(new_key, {}).values():
                        if value is not None and value.get('console') == old_value.get('console'):
                            if 'console' in current:
                                value['console'] = current['console']
                if 'console' in current:
                    data['state'][new_key]['console'] = current['console']
        # Link endpoint order may change after UUID remapping.
        for key, value in list(data['state'].items()):
            data['state'][key] = canonical(resource(key)[0], value)
        for entry in data['entries']:
            for key, change in entry['changes'].items():
                for side in change:
                    change[side] = canonical(resource(key)[0], change[side])
        result = self.load(data)
        # The server retains old UUIDs inside container metadata. The GUI's
        # existing restore path repairs these; comparison allows those exact
        # imported SVG strings until the first confirmed container save.
        expected = copy.deepcopy(actual)
        for key in expected:
            if key.startswith('drawings/'):
                expected[key]['svg'] = rewrite(expected[key]['svg'])
        if result.state != expected:
            raise ValueError('Imported topology differs from the saved history manifest')
        return result
