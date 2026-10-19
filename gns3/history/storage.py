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
SLOTS = ('gns3-gui-history-A.json.gz', 'gns3-gui-history-B.json.gz')


def encode(payload):
    content = json.dumps(payload, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
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
    return HistoryDocument.load(json.loads(document))


class _Signals(QtCore.QObject):
    finished = QtCore.Signal(object, object)


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
