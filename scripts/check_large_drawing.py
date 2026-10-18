#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify lossless oversized image upload against a disposable GNS3 2.2 server."""
import argparse
import io
import json
import os
from pathlib import Path
import sys
import urllib.request
import zipfile
from unittest.mock import MagicMock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from gns3.qt import QtWidgets, QtGui, QtCore
from gns3.items.image_item import ImageItem


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server', required=True, help='Disposable test server, never an active project')
    args = parser.parse_args()
    base = args.server.rstrip('/') + '/v2'

    def request(method, path, data=None, raw=False):
        if isinstance(data, Path):
            data = data.read_bytes()
        binary = isinstance(data, bytes)
        payload = data if binary else json.dumps(data).encode() if data is not None else None
        req = urllib.request.Request(base + path, data=payload, method=method,
                                     headers={'Content-Type': 'application/octet-stream' if binary else 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as response:
            value = response.read()
        return value if raw else json.loads(value) if value else None

    app = QtWidgets.QApplication([])
    project_id = request('POST', '/projects', {'name': 'Disposable large drawing check'})['project_id']
    prefix = '/projects/' + project_id
    calls = []

    class Project:
        def post(self, path, callback, body=None, **kwargs):
            calls.append((path, body if isinstance(body, dict) else 'raw asset'))
            callback(request('POST', prefix + path, body))

        def delete(self, path, callback=None, **kwargs):
            request('DELETE', prefix + path)

        def put(self, path, callback, body=None, **kwargs):
            calls.append((path, body))
            callback(request('PUT', prefix + path, body))

    try:
        # High-entropy lossless pixels exceed the 1 MiB JSON request limit.
        pixels = os.urandom(900 * 600 * 4)
        image = QtGui.QImage(pixels, 900, 600, QtGui.QImage.Format.Format_RGBA8888).copy()
        png = QtCore.QByteArray()
        buffer = QtCore.QBuffer(png)
        buffer.open(QtCore.QIODeviceBase.OpenModeFlag.WriteOnly)
        image.save(buffer, 'PNG')
        import base64
        svg = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="900" height="600"><image width="900" height="600" xlink:href="data:image/png;base64,' + base64.b64encode(bytes(png)).decode() + '"/></svg>'
        main_window = MagicMock()
        with patch('gns3.main_window.MainWindow.instance', return_value=main_window):
            item = ImageItem(svg=svg, project=Project(), pos=QtCore.QPointF(0, 0))
            item.setDimensions(640, 360)
            expected = item.toSvg()
            assert len(expected.encode()) > 1048576
            item.create()
            assert item._server_created
            assert item.boundingRect().size() == QtCore.QSizeF(640, 360)
            assert bytes(png) == base64.b64decode(item.toSvg().split('base64,')[1].split('"')[0])
            item.setDimensions(800, 400)
            item.updateDrawing()
            stored = request('GET', prefix + '/drawings/' + item.drawing_id())
            reloaded = ImageItem(svg=stored['svg'])
            assert reloaded.boundingRect().size() == QtCore.QSizeF(800, 400)
            for path, body in calls:
                if isinstance(body, dict):
                    assert len(json.dumps(body).encode()) < 1048576
            assert len(request('GET', prefix + '/drawings')) == 1
            archive = request('GET', prefix + '/export?include_images=no&keep_compute_ids=yes', raw=True)
            with zipfile.ZipFile(io.BytesIO(archive)) as exported:
                assert any(name.endswith('.svg') for name in exported.namelist())
            print('PASS: lossless SVG >1 MiB, raw upload, compact POST/PUT, dimensions on reload, portable asset export')
    finally:
        request('DELETE', prefix)


if __name__ == '__main__':
    main()
