# SPDX-License-Identifier: GPL-3.0-or-later
"""Two checked project-file slots; encoding/decoding stays off the GUI thread."""
import gzip
import hashlib
import io
import json
import tempfile
from pathlib import Path
from ..qt import QtCore
from .model import HistoryDocument

MAX_BYTES = 64 * 1024 * 1024
# Avoid .json/.gz: MIME guessing enables JSON parsing or transparent HTTP gzip
# decoding. The checked gzip payload is an opaque project asset, not HTTP gzip.
SLOTS = ('gns3-gui-history-A.history', 'gns3-gui-history-B.history')


def encode(payload):
    # A moved image can have the same multi-megabyte SVG in 100 deltas. Store
    # each distinct SVG once; immutable strings can be shared on decoding too.
    assets = {}
    def pack(value):
        if isinstance(value, list):
            return [pack(v) for v in value]
        if isinstance(value, dict):
            result = {k: pack(v) for k, v in value.items()}
            if isinstance(value.get('svg'), str):
                digest = hashlib.sha256(value['svg'].encode('utf-8')).hexdigest()
                assets[digest] = value['svg']
                result['svg'] = {'asset': digest}
            return result
        return value
    envelope = {'codec': 1, 'document': pack(payload), 'assets': assets}
    content = json.dumps(envelope, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
    if len(content) > MAX_BYTES:
        raise ValueError('History exceeds the 64 MiB safety limit; clear history to continue saving')
    checksum = hashlib.sha256(content).hexdigest().encode('ascii')
    with tempfile.NamedTemporaryFile(prefix='gns3-history-', suffix='.json.gz', delete=False) as file:
        path = Path(file.name)
        try:
            file.write(gzip.compress(checksum + b'\n' + content))
        except Exception:
            path.unlink(missing_ok=True)
            raise
    return path


def decode(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('History file is too large')
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as file:
        content = file.read(MAX_BYTES + 66)
    if len(content) > MAX_BYTES + 65:
        raise ValueError('Expanded history file is too large')
    checksum, document = content.split(b'\n', 1)
    if checksum.decode('ascii') != hashlib.sha256(document).hexdigest():
        raise ValueError('History checksum does not match')
    payload = json.loads(document)
    if isinstance(payload, dict) and 'codec' in payload:
        if payload['codec'] != 1 or not isinstance(payload.get('assets'), dict):
            raise ValueError('Unsupported history asset codec')
        assets = payload['assets']
        for digest, svg in assets.items():
            if not isinstance(svg, str) or hashlib.sha256(svg.encode('utf-8')).hexdigest() != digest:
                raise ValueError('Invalid history SVG asset')
        def unpack(value):
            if isinstance(value, list):
                return [unpack(v) for v in value]
            if isinstance(value, dict):
                result = {k: unpack(v) for k, v in value.items()}
                if isinstance(value.get('svg'), dict):
                    result['svg'] = assets[value['svg']['asset']]
                return result
            return value
        payload = unpack(payload['document'])
    return HistoryDocument.load(payload)


class _Signals(QtCore.QObject):
    finished = QtCore.pyqtSignal(object, object)


class Work(QtCore.QRunnable):
    def __init__(self, function, callback):
        super().__init__()
        self.function = function
        self.signals = _Signals()
        self.signals.finished.connect(callback)

    def run(self):
        try:
            result = self.function()
        except Exception as error:
            self.signals.finished.emit(None, str(error))
        else:
            self.signals.finished.emit(result, None)


def background(function, callback):
    QtCore.QThreadPool.globalInstance().start(Work(function, callback))


def recovery_copy(raw):
    """Preserve exact bytes, even from an obsolete or corrupt history codec."""
    name = 'gns3-gui-history-recovery-' + hashlib.sha256(raw).hexdigest() + '.history'
    with tempfile.NamedTemporaryFile(prefix='gns3-history-recovery-', delete=False) as file:
        file.write(raw)
        return name, Path(file.name)
