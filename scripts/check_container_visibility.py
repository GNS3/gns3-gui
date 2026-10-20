#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exercise container exits with native mouse input and unforced screenshots.

Use a disposable GNS3 Server and an isolated X11 display (or nested Wayland
compositor). Requires PyAutoGUI and Pillow. Only its own project is modified.
Weak references and explicit garbage collection expose SIP ownership regressions.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import urllib.request
from unittest.mock import patch
from urllib.parse import urlparse
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('QT_QPA_PLATFORM', 'xcb')
from gns3.qt import QtWidgets, QtCore, QtGui
from gns3.local_config import LocalConfig
from gns3.main_window import MainWindow
from gns3.topology import Topology
from gns3.controller import Controller
from gns3.project import Project
from gns3.http_client import HTTPClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server', required=True)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    parser.add_argument('--zoom', type=float, default=1.41)
    args = parser.parse_args()
    from gns3.application import Application
    app = Application([])
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
            app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
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
    import weakref
    import gc
    import threading
    import pyautogui
    from PIL import ImageGrab
    from gns3.qt import sip
    from gns3.items.node_item import NodeItem
    from gns3.items.group_item import reparent
    evidence = args.evidence_dir.resolve()
    evidence.mkdir(exist_ok=True)
    diagnostic = open(evidence / 'state.log', 'w')
    window.resize(1200, 900)
    window.show()
    window.activateWindow()
    view = window.uiGraphicsView
    # Fixture CRUD must not open a delayed modal dialog during native drags.
    HTTPClient.setProgressCallback(None)
    # Never retain graphics items: doing so hides the ownership defect.
    items = []
    identities = []
    def mouse(function):
        wait(lambda: app.activeModalWidget() is None and view.isInteractive() and not history.busy)
        errors = []
        def run():
            try: function()
            except Exception as error: errors.append(error)
        worker = threading.Thread(target=run)
        worker.start()
        wait(lambda: not worker.is_alive())
        worker.join()
        if errors: raise errors[0]
        app.processEvents()
    def drag(item, destination):
        start = view.viewport().mapToGlobal(view.mapFromScene(item.sceneBoundingRect().center()))
        end = view.viewport().mapToGlobal(view.mapFromScene(destination))
        def action():
            pyautogui.moveTo(start.x(), start.y())
            pyautogui.dragTo(end.x(), end.y(), duration=.18)
            pyautogui.moveTo(1100, 800)
        mouse(action)
        settled(history)
        wait(lambda: app.activeModalWidget() is None)
        from PyQt6.QtTest import QTest
        QTest.qWait(20)
        assert item.parentItem() is None, ("drag did not detach",item.node().name())
    def check(label):
        wait(lambda: app.activeModalWidget() is None and not history.busy)
        from PyQt6.QtTest import QTest
        QTest.qWait(20)
        # QWidget.grab()/scene.render() request painting and can mask damage.
        image = ImageGrab.grab(xdisplay=os.environ['DISPLAY'])
        image.save(evidence / (label + '.png'))
        for identity, reference in zip(identities, items):
            item = reference()
            if item is None:
                diagnostic.write(label + ' GRAPHICS ITEM DESTROYED ' + str(dict(
                    model_exists=topo.getNodeFromUuid(identity) is not None,
                    server_exists=any(n['node_id'] == identity for n in request('GET', '/projects/' + pid + '/nodes')))) + '\n')
                diagnostic.flush()
            assert item is not None, ('graphics item destroyed', label)
            rect = view.mapFromScene(item.sceneBoundingRect()).boundingRect()
            assert view.viewport().rect().contains(rect), (label, "symbol outside viewport")
            offset = view.viewport().mapToGlobal(QtCore.QPoint())
            rect.translate(offset)
            colored = sum(max(image.getpixel((x,y))[:3])-min(image.getpixel((x,y))[:3]) > 10
                          for y in range(rect.top(),rect.bottom()) for x in range(rect.left(),rect.right()) if 0<=x<image.width and 0<=y<image.height)
            info = dict(name=item.node().name(), xy=(item.scenePos().x(),item.scenePos().y()), parent=bool(item.parentItem()),
                        visible=item.isVisible(), renderer=item.renderer().isValid(), clipped=item.isClipped(), pixels=colored)
            diagnostic.write(label + ' ' + str(info) + '\n')
            diagnostic.flush()
            assert colored > 30, ('VISUAL DISAPPEARANCE', label, info)
    try:
        pid = request('POST', '/projects', {'name': 'Disposable visibility ' + directory.name})['project_id']
        ids.append(pid)
        project = attach(pid)
        history = project.history
        loaded=[]
        history.load({}, lambda: loaded.append(True))
        wait(lambda: bool(loaded))
        def add(number, x, y):
            data = edit(project, 'POST', '/nodes', dict(node_type='ethernet_hub', compute_id='local', symbol=':/symbols/hub.svg', name='Hub'+str(number), x=x, y=y))
            if topo.getNodeFromUuid(data['node_id']) is None: topo.createNode(data)
            item = next(i for i in view.scene().items() if isinstance(i,NodeItem) and i.node().node_id()==data['node_id'])
            wait(lambda: item._initialized)
            settled(history)
            identities.append(item.node().node_id())
            items.append(weakref.ref(item))
            return item
        a, b = add(1, -60,0), add(2, 60,0)
        view.scale(args.zoom, args.zoom)
        view.centerOn(0,0)
        app.processEvents()
        positions = [view.viewport().mapToGlobal(view.mapFromScene(i.sceneBoundingRect().center())) for i in [a,b]]
        def create_container():
            pyautogui.click(positions[0].x(),positions[0].y())
            pyautogui.keyDown('ctrl')
            pyautogui.click(positions[1].x(),positions[1].y())
            pyautogui.keyUp('ctrl')
            pyautogui.hotkey('ctrl','g')
            time.sleep(.4)
            pyautogui.press('enter')
        mouse(create_container)
        wait(lambda: len(view._groups.groups()) == 1)
        frame = view._groups.groups()[0]
        settled(history)
        center = view.viewport().mapToGlobal(view.mapFromScene(frame.sceneBoundingRect().center()))
        mouse(lambda: pyautogui.doubleClick(center.x(),center.y(),interval=.15))
        assert frame.editing
        settled(history)
        from PyQt6.QtTest import QTest
        QTest.qWait(1600)
        check('00-grouped')
        original_rect = view.mapFromScene(a.sceneBoundingRect()).boundingRect()
        original_rect.translate(view.viewport().mapToGlobal(QtCore.QPoint()))
        drag(a, QtCore.QPointF(-240,0))
        outside_rect = view.mapFromScene(a.sceneBoundingRect()).boundingRect()
        outside_rect.translate(view.viewport().mapToGlobal(QtCore.QPoint()))
        del a
        gc.collect()
        check('01-detach-first')
        target_first = history.document.cursor
        def shortcut(key, cursor):
            view.setFocus()
            app.processEvents()
            mouse(lambda: pyautogui.hotkey('ctrl', key))
            wait(lambda: history.document.cursor == cursor)
            settled(history)
            QTest.qWait(50)
        def absent(rect, name):
            image = ImageGrab.grab(xdisplay=os.environ['DISPLAY'])
            image.save(evidence / (name + '.png'))
            colored = sum(max(image.getpixel((x,y))[:3])-min(image.getpixel((x,y))[:3]) > 10
                          for y in range(rect.top()+2, rect.bottom()-2)
                          for x in range(rect.left()+2, rect.right()-2))
            live = [i for i in view.scene().items() if isinstance(i, NodeItem) and i.node().node_id() == identities[0]]
            assert len(live) == 1, ('duplicate graphics UUID', name, len(live))
            current = view.mapFromScene(live[0].sceneBoundingRect()).boundingRect()
            current.translate(view.viewport().mapToGlobal(QtCore.QPoint()))
            visible_pixels = sum(max(image.getpixel((x,y))[:3])-min(image.getpixel((x,y))[:3]) > 10
                                 for y in range(current.top()+2, current.bottom()-2)
                                 for x in range(current.left()+2, current.right()-2))
            assert visible_pixels > 30, ('missing current symbol', name, visible_pixels)
            diagnostic.write(name + ' ' + str(dict(pixels_in_old_position=colored, pixels_in_current_position=visible_pixels, graphics_count=len(live),
                parent=bool(live[0].parentItem()), position=(live[0].scenePos().x(),live[0].scenePos().y()))) + '\n')
            diagnostic.flush()
            return colored
        for attempt in range(6):
            shortcut('z', target_first - 1)
            undo_pixels = absent(outside_rect, 'replay-%02d-undo' % attempt)
            shortcut('y', target_first)
            redo_pixels = absent(original_rect, 'replay-%02d-redo' % attempt)
            assert undo_pixels < 10 and redo_pixels < 10, ('stale visual clone', attempt, undo_pixels, redo_pixels)
        drag(b, QtCore.QPointF(240,0))
        del b
        gc.collect()
        check('02-detach-second')
        for number in range(3,9):
            node = add(number, -30, 0)
            history.begin('Add device to container')
            reparent(node,frame)
            view._groups.save([frame])
            history.end()
            settled(history)
            check(str(number)+'-added')
            view.enterGroup(frame)
            settled(history)
            drag(node,[QtCore.QPointF(x,y) for x,y in [(-240,150),(-100,150),(40,150),(180,150),(-240,-170),(-100,-170)]][number-3])
            del node
            gc.collect()
            check(str(number)+'-detached')
        target = history.document.cursor
        history.navigate(target - 1)
        settled(history)
        gc.collect()
        check('09-undo-last')
        history.navigate(target)
        settled(history)
        gc.collect()
        check('10-redo-last')
        assert len(topo.nodes()) == len(items) == len(request('GET', '/projects/' + pid + '/nodes'))
        from gns3.history.model import state_from_lists
        (evidence / 'before-reopen.json').write_text(json.dumps(dict(cursor=history.document.cursor,
            state=history.document.state, server=state_from_lists({kind: request('GET', '/projects/' + pid + '/' + kind)
            for kind in ['nodes', 'links', 'drawings']})), indent=2))
        project.close()
        wait(lambda: project._closed and topo.project() is None)
        assert all(reference() is None or sip.isdeleted(reference()) for reference in items)
        items.clear()
        request('POST', '/projects/' + pid + '/open')
        project = attach(pid)
        history = project.history
        project._listNodesCallback(request('GET', '/projects/' + pid + '/nodes'))
        wait(lambda: history.ready)
        settled(history)
        (evidence / 'after-reopen.json').write_text(json.dumps(dict(cursor=history.document.cursor,
            target=target, recovery=history.recovery_message, entries=history.document.entries,
            state=history.document.state), indent=2))
        assert history.document.cursor == target, (history.document.cursor, target, history.recovery_message)
        for identity in identities:
            item = next(i for i in view.scene().items() if isinstance(i, NodeItem) and i.node().node_id() == identity)
            items.append(weakref.ref(item))
        del item, frame
        wait(lambda: all(reference() and reference()._initialized for reference in items))
        view.resetTransform()
        view.scale(args.zoom, args.zoom)
        view.centerOn(0, 0)
        gc.collect()
        check('11-reopened')
        history.navigate(target - 1)
        settled(history)
        history.navigate(target)
        settled(history)
        gc.collect()
        check('12-reopened-redo')
        print('PASS: native mouse, screenshots, weak ownership, undo/redo and persistent reopen', flush=True)
    except Exception:
        import traceback
        traceback.print_exc()
        raise
    finally:
        diagnostic.close()
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
