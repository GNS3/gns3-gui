#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify GUI history against a disposable GNS3 2.2 server (never a personal project).

Uses the actual Qt HTTP client, Project, node/link models and canvas. Creates and
removes its own projects; no emulator/image is needed for Ethernet switches.
"""
import argparse
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import urllib.request
import uuid
import zipfile
from unittest.mock import patch
from urllib.parse import urlparse
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from gns3.qt import QtWidgets, QtCore, QtGui
from gns3.local_config import LocalConfig
from gns3.main_window import MainWindow
from gns3.topology import Topology
from gns3.controller import Controller
from gns3.project import Project
from gns3.http_client import HTTPClient
from gns3.history.storage import SLOTS
from gns3.items.group_item import GroupItem
from gns3.items.rectangle_item import RectangleItem


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server', required=True)
    args = parser.parse_args()
    app = QtWidgets.QApplication([])
    directory = Path(tempfile.mkdtemp(prefix='gns3-history-check-'))
    LocalConfig._instance = LocalConfig(config_file=str(directory / 'gui.json'))
    url = urlparse(args.server)
    base = args.server.rstrip('/') + '/v2'
    def request(method, path, body=None, raw=False):
        data = body if isinstance(body, bytes) else json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(base + path, data=data, method=method,
            headers={'Content-Type': 'application/octet-stream' if isinstance(body, bytes) else 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as response:
            value = response.read()
        return value if raw else json.loads(value) if value else {}
    def wait(condition, timeout=15):
        start = time.monotonic()
        while not condition() and time.monotonic() - start < timeout:
            app.processEvents()
            time.sleep(.005)
        assert condition(), 'Timed out waiting for history/server synchronization'
    http = HTTPClient({'host': url.hostname, 'port': url.port or 80, 'protocol': url.scheme})
    http._connected = True
    controller = Controller.instance()
    controller._http_client = http
    controller._connected = True
    with patch.object(MainWindow, 'run_later'):
        window = MainWindow()
    topo = Topology.instance()
    ids = []
    def attach(pid):
        project = Project()
        project.setId(pid)
        project.setName('History integration')
        project._created = True
        project._closed = False
        topo.setProject(project)
        project._startListenNotifications()
        wait(lambda: project._websocket.isValid())
        return project
    def settled(history):
        wait(lambda: not history.busy and not history._saving)
        assert not history.invalid, history.invalid
    def edit(project, method, path, body=None):
        done = []
        getattr(project, method.lower())(path, lambda result, error=False, **kw: done.append((result, error)), body=body)
        wait(lambda: bool(done))
        assert not done[0][1], done[0][0]
        settled(project.history)
        return done[0][0]
    try:
        pid = request('POST', '/projects', {'name': 'Disposable history integration'})['project_id']
        ids.append(pid)
        project = attach(pid)
        history = project.history
        history.failed.connect(lambda message: print('HISTORY:', message, flush=True))
        loaded = []
        history.load({}, lambda: loaded.append(True))
        wait(lambda: bool(loaded))
        assert not history.invalid, history.invalid
        a = edit(project, 'POST', '/nodes', dict(node_type='ethernet_switch', compute_id='local', name='A', x=0, y=0))
        b = edit(project, 'POST', '/nodes', dict(node_type='ethernet_switch', compute_id='local', name='B', x=200, y=0))
        # Normal creation callbacks above intentionally have no canvas callback;
        # create the real objects as the ordinary Project notification path does.
        if topo.getNodeFromUuid(a['node_id']) is None:
            topo.createNode(a)
        if topo.getNodeFromUuid(b['node_id']) is None:
            topo.createNode(b)
        settled(history)
        connection = edit(project, 'POST', '/links', {'nodes': [
            dict(node_id=a['node_id'], adapter_number=0, port_number=0),
            dict(node_id=b['node_id'], adapter_number=0, port_number=0)]})
        if topo.getLinkFromUuid(connection['link_id']) is None:
            topo.createLink(connection)
        rectangle = RectangleItem(project=project, pos=QtCore.QPointF(20, 120))
        window.uiGraphicsView.scene().addItem(rectangle)
        topo.addDrawing(rectangle)
        rectangle.create()
        settled(history)
        rectangle.setRect(0, 0, 180, 100)
        rectangle.updateDrawing()
        settled(history)
        before = history.document.cursor
        history.begin('Move group')
        for data in (a, b):
            project.put('/nodes/' + data['node_id'], None, body={'x': data['x'] + 40})
        history.end()
        settled(history)
        assert history.document.cursor == before + 1
        target = history.document.cursor
        history.navigate(0)
        settled(history)
        assert request('GET', '/projects/' + pid + '/nodes') == []
        assert not topo.nodes() and not topo.links()
        history.navigate(target)
        settled(history)
        assert len(topo.nodes()) == 2 and len(topo.links()) == 1
        assert len(request('GET', '/projects/' + pid + '/drawings')) == 1
        # Device deletion cascades its link; undo reconstructs both server and GUI.
        edit(project, 'DELETE', '/nodes/' + a['node_id'])
        history.navigate(target)
        settled(history)
        assert len(topo.nodes()) == 2 and len(topo.links()) == 1
        # Move a real container, then move a member out and undo association+position.
        view = window.uiGraphicsView
        first = next(item for item in view.scene().items() if hasattr(item, 'node') and item.node() is topo.getNodeFromUuid(a['node_id']))
        second = next(item for item in view.scene().items() if hasattr(item, 'node') and item.node() is topo.getNodeFromUuid(b['node_id']))
        group = GroupItem(name='LAN', project=project, width=400, height=300)
        view.scene().addItem(group)
        topo.addDrawing(group)
        history.begin('Create container')
        from gns3.items.group_item import reparent
        reparent(first, group)
        reparent(second, group)
        group.create()
        view._groups.save([group])
        history.end()
        settled(history)
        group_id = group.drawing_id()
        membership_cursor = history.document.cursor
        original_size = group.rect().size()
        history.begin()
        group.setDimensions(500, 350)
        view._groups.save([group])
        history.end()
        settled(history)
        history.navigate(membership_cursor)
        settled(history)
        assert group.rect().size() == original_size
        history.navigate(membership_cursor + 1)
        settled(history)
        assert group.rect().size() == QtCore.QSizeF(500, 350)
        history.navigate(membership_cursor)
        settled(history)
        origin = group.pos()
        position = first.scenePos()
        history.begin()
        group.setPos(origin + QtCore.QPointF(100, 100))
        view._groups.save([group])
        history.end()
        settled(history)
        history.navigate(membership_cursor)
        settled(history)
        assert group.pos() == origin and first.scenePos() == position
        from PyQt6.QtTest import QTest
        window.resize(1100, 800)
        window.show()
        view.centerOn(group)
        view.enterGroup(group)
        app.processEvents()
        start = view.mapFromScene(first.sceneBoundingRect().center())
        end = view.mapFromScene(group.mapToScene(QtCore.QPointF(group.rect().right() + 100, 100)))
        QTest.mousePress(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=start)
        QTest.mouseMove(view.viewport(), end)
        assert first.parentItem() is group
        QTest.mouseRelease(view.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=end)
        assert first.parentItem() is None
        detached_position = first.scenePos()
        settled(history)
        assert len(history.document.entries[-1]['changes']) == 2, history.document.entries[-1]
        assert 'membership' in history.document.entries[-1]['description']
        history.navigate(membership_cursor)
        settled(history)
        assert first.parentItem() is topo.getDrawingFromUuid(group_id)
        assert first.scenePos() == position
        history.navigate(membership_cursor + 1)
        settled(history)
        assert first.parentItem() is None and first.scenePos() == detached_position
        stored = request('GET', '/projects/' + pid + '/nodes/' + a['node_id'])
        assert (stored['x'], stored['y']) == (int(detached_position.x()), int(detached_position.y()))
        history.navigate(membership_cursor)
        settled(history)
        assert first.parentItem() is group and first.scenePos() == position
        # Flush before export, close/reopen, then replay the persisted cursor.
        flushed = []
        history.flush(lambda ok: flushed.append(ok))
        wait(lambda: bool(flushed))
        assert flushed == [True]
        exported_result = []
        project.get('/export?include_images=no&keep_compute_ids=yes',
                    lambda result, error=False, raw_body=None, **kwargs: exported_result.append((raw_body, error)), timeout=None)
        wait(lambda: bool(exported_result))
        archive, error = exported_result[0]
        assert not error
        with zipfile.ZipFile(io.BytesIO(archive)) as exported:
            assert any(name.endswith(SLOTS[0]) or name.endswith(SLOTS[1]) for name in exported.namelist())
        project.close()
        wait(lambda: project._closed and topo.project() is None)
        request('POST', '/projects/' + pid + '/open')
        reopened = attach(pid)
        reopened._listNodesCallback(request('GET', '/projects/' + pid + '/nodes'))
        wait(lambda: reopened.history.ready)
        settled(reopened.history)
        assert reopened.history.document.cursor == membership_cursor
        reopened.history.navigate(membership_cursor - 1)
        settled(reopened.history)
        assert topo.getDrawingFromUuid(group_id) is None
        reopened.history.navigate(membership_cursor)
        settled(reopened.history)
        newid = str(uuid.uuid4())
        imported_data = request('POST', '/projects/' + newid + '/import', archive)
        ids.append(newid)
        request('POST', '/projects/' + newid + '/open')
        imported = attach(newid)
        imported._listNodesCallback(request('GET', '/projects/' + newid + '/nodes'))
        wait(lambda: imported.history.ready)
        settled(imported.history)
        assert imported.history.document.cursor == membership_cursor
        imported.history.navigate(membership_cursor - 1)
        settled(imported.history)
        assert not view._groups.groups()
        imported.history.navigate(membership_cursor)
        settled(imported.history)
        assert len(view._groups.groups()) == 1
        assert len(view._groups.groups()[0].members()) == 2
        # Oversized image replay must reuse streamed SVG transport, excluding
        # its temporary directory seed from the logical history.
        from gns3.items.image_item import ImageItem
        import base64
        pixels = os.urandom(650 * 450 * 4)
        image = QtGui.QImage(pixels, 650, 450, QtGui.QImage.Format.Format_RGBA8888).copy()
        png = QtCore.QByteArray()
        buffer = QtCore.QBuffer(png)
        buffer.open(QtCore.QIODeviceBase.OpenModeFlag.WriteOnly)
        image.save(buffer, 'PNG')
        svg = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="650" height="450"><image width="650" height="450" xlink:href="data:image/png;base64,' + base64.b64encode(bytes(png)).decode() + '"/></svg>'
        large = ImageItem(project=imported, svg=svg, pos=QtCore.QPointF(600, 200))
        view.scene().addItem(large)
        topo.addDrawing(large)
        initial = imported.history.document.cursor
        large.create()
        settled(imported.history)
        assert imported.history.document.cursor == initial + 1
        assert len(imported.history.document.entries[-1]['changes']) == 1
        large_id = large.drawing_id()
        imported.history.navigate(initial)
        settled(imported.history)
        assert topo.getDrawingFromUuid(large_id) is None
        imported.history.navigate(initial + 1)
        settled(imported.history)
        assert topo.getDrawingFromUuid(large_id) is not None
        assert base64.b64encode(bytes(png)).decode() in request('GET', '/projects/' + newid + '/drawings/' + large_id)['svg']
        print('PASS: real server + Qt canvas CRUD, grouped moves, device/link restoration, container movement/resize/membership, persistent reopen and portable import/replay, oversized images, WebSocket echoes', flush=True)
    except Exception:
        import traceback
        traceback.print_exc()
        raise
    finally:
        topo.setProject(None)
        window._local_config_timer.stop()
        http._shutdown = True
        window.deleteLater()
        app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
        app.processEvents()
        for pid in reversed(ids):
            request('DELETE', '/projects/' + pid)


if __name__ == '__main__':
    main()
