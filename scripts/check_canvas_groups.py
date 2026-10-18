#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check persistent canvas groups against an isolated GNS3 2.2 test server.

Uses real Qt containers and HTTP persistence/export/import. Lightweight device
model adapters avoid launching simulators or connecting the desktop controller.
Creates and removes only its own disposable projects. Does not need image files.
"""
import argparse
import gc
import time
import io
import tempfile
import json
import os
import sys
import urllib.request
import uuid
import zipfile
from pathlib import Path
from urllib.parse import urlparse
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from gns3.qt import QtWidgets, QtCore, QtGui
from gns3.main_window import MainWindow
from gns3.graphics_view import GraphicsView
from gns3.topology import Topology
from gns3.topology_summary_view import TopologySummaryView
from gns3.items.node_item import NodeItem
from gns3.items.group_item import GroupItem, read_group
from gns3.local_config import LocalConfig
from gns3.template_manager import TemplateManager
from gns3.http_client import HTTPClient
from gns3.node import Node

def main():
    app = QtWidgets.QApplication([])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server', required=True, help='Isolated GNS3 2.2 server URL, e.g. http://127.0.0.1:3099')
    parser.add_argument('--output-dir', type=Path, default=None)
    args = parser.parse_args()
    output = args.output_dir or Path(tempfile.mkdtemp(prefix='gns3-group-check-'))
    output.mkdir(parents=True, exist_ok=True)
    LocalConfig._instance = LocalConfig(config_file=str(output / 'gui.json'))
    base = args.server.rstrip('/') + '/v2'
    address = urlparse(args.server)
    http = HTTPClient({'host': address.hostname, 'port': address.port or (443 if address.scheme == 'https' else 80),
                       'protocol': address.scheme})
    http._connected = True

    def request(method, path, data=None, raw=False):
        body = data if isinstance(data, bytes) else json.dumps(data).encode() if data is not None else None
        req = urllib.request.Request(base+path, data=body, method=method,
                                    headers={'Content-Type': 'application/octet-stream' if isinstance(data, bytes) else 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as response:
            value = response.read()
        return value if raw else json.loads(value) if value else None

    project_ids = []
    template_ids = []
    try:
        created = request('POST', '/projects', {'name': 'Canvas hierarchy integration'})
        pid = created['project_id']
        project_ids.append(pid)
        class Bridge:
            def __init__(self, identity):
                self.identity = identity
                self.defer_drawings = False
                self.pending_drawings = []
            def id(self):
                return self.identity

            def call(self, method, path, callback=None, body=None, **kwargs):
                result = request(method, '/projects/'+self.identity+path, body)
                if callback:
                    callback(result)
                return result
            def post(self, path, callback=None, **kwargs):
                if self.defer_drawings and path == '/drawings':
                    self.pending_drawings.append((path, callback, kwargs))
                    return
                return self.call('POST', path, callback, **kwargs)

            def flush_drawings(self):
                self.defer_drawings = False
                pending, self.pending_drawings = self.pending_drawings, []
                for path, callback, kwargs in reversed(pending):
                    self.call('POST', path, callback, **kwargs)
            def put(self, path, callback=None, **kwargs):
                return self.call('PUT', path, callback, **kwargs)
            def delete(self, path, callback=None, **kwargs):
                return self.call('DELETE', path, callback, **kwargs)

        main = MagicMock()
        MainWindow._instance = main
        main.uiSnapToGridAction.isChecked.return_value = False
        main.settings.return_value = {'style':'Classic'}
        window = QtWidgets.QMainWindow()
        central = QtWidgets.QWidget(window)
        window.setCentralWidget(central)
        view = GraphicsView(central)
        view._main_window = main
        view.toggleUiDeviceMenu = MagicMock()
        main.uiGraphicsView = view
        topo = Topology.instance()
        topo._main_window = main
        topo._project = Bridge(pid)
        view._topology = topo

        def item_for(data):
            node = MagicMock()
            node.node_id.return_value = data['node_id']
            node.id.return_value = len(topo.nodes()) + 1
            node.name.return_value = data['name']
            node.x.return_value, node.y.return_value = data['x'], data['y']
            node.z.return_value = data.get('z',1)
            node.locked.return_value = False
            node.links.return_value = []
            node.consoleType.return_value = "none"
            node.initialized.return_value = False
            ports = []
            for number in range(8):
                port = MagicMock()
                port.adapterNumber.return_value = 0
                port.portNumber.return_value = number
                ports.append(port)
            node.ports.return_value = ports
            node.setGraphics.side_effect = lambda item: topo._project.put('/nodes/'+node.node_id() ,body={
                'x':int(item.scenePos().x()), 'y':int(item.scenePos().y()), 'z':int(item.zValue())})
            node.delete.side_effect = lambda: topo._project.delete('/nodes/'+node.node_id())
            # Keep the real Node completion hook and Qt HTTP transport. A
            # synchronous adapter hid replies being collected before finished.
            node.post.side_effect = lambda path, callback, **kwargs: http.createHTTPQuery(
                'POST', '/projects/'+topo._project.id()+'/nodes/'+node.node_id()+path,
                callback, **kwargs)
            node.duplicate.side_effect = lambda x,y,z,callback=None: Node.duplicate(node, x, y, z, callback)
            item = NodeItem(node)
            view.scene().addItem(item)
            QtWidgets.QGraphicsSimpleTextItem(data['name'], item).setPos(0, 35)
            topo.addNode(node)
            return item

        topo.createNode = item_for
        nodes = [item_for(topo._project.post('/nodes',body={
            'name':name, 'node_type':'ethernet_switch','compute_id':'local','x':x,'y':80,
            'symbol':':/symbols/classic/switch.svg'})) for name,x in [('SW1',100),('SW2',250)]]
        def add_link(source, source_port, destination, destination_port):
            topo._project.post('/links', body={'nodes':[
                {'node_id':source.node_id(), 'adapter_number':source_port.adapterNumber(), 'port_number':source_port.portNumber()},
                {'node_id':destination.node_id(), 'adapter_number':destination_port.adapterNumber(), 'port_number':destination_port.portNumber()}]})
            link = MagicMock()
            link.sourceNode.return_value, link.destinationNode.return_value = source, destination
            link.sourcePort.return_value, link.destinationPort.return_value = source_port, destination_port
            topo._links.append(link)
        view.addLink = add_link
        add_link(nodes[0].node(), nodes[0].node().ports()[0], nodes[1].node(), nodes[1].node().ports()[0])
        shape = view.createDrawingItem('rect',60,40,-1)
        note = view.createDrawingItem('text',100,180,1,svg='<svg width="180" height="30"><text x="0" y="16">LAN de teste</text></svg>')
        image = view.createDrawingItem('image',400,80,0,svg='<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60"><circle cx="30" cy="30" r="25" fill="#42a5f5"/></svg>')
        inner = view._groups.add('LAN 1',nodes+[shape,note])
        outer = view._groups.add('Site São Paulo',[inner,image])
        summary = TopologySummaryView(None)
        for node in topo.nodes():
            summary._nodeAddedSlot(node.id())
        assert summary.topLevelItemCount() == 1
        assert summary.topLevelItem(0).child(0).group is inner
        outer_size = outer.rect().size()
        inner.setDimensions(inner.rect().width() * .8, inner.rect().height() * .9)
        view._groups.save([inner])
        assert outer.rect().size() == outer_size
        expected_sizes = {group.name: group.rect().size() for group in view._groups.groups()}
        before = nodes[0].scenePos()
        outer.setPos(outer.pos()+QtCore.QPointF(80,50))
        view._groups.save([outer])
        assert nodes[0].scenePos()==before+QtCore.QPointF(80,50)
        # Exercise the existing template endpoint and the new drop callback.
        template_data = request('POST', '/templates', {
            'name': 'Canvas drop ' + str(uuid.uuid4()),
            'template_type': 'ethernet_switch', 'compute_id': 'local'})
        template_id = template_data['template_id']
        template_ids.append(template_id)
        templates = TemplateManager()
        template = MagicMock()
        template.id.return_value = template_id
        template.compute_id.return_value = 'local'
        templates._templates = {template_id: template}
        templates._controller = MagicMock()
        templates._controller.connected.return_value = True

        def instantiate(path, callback, body, **kwargs):
            result = request('POST', path, body)
            item_for(result)  # simulate the creation notification arriving first
            callback(result)
        templates._controller.post.side_effect = instantiate
        point = view.mapFromScene(inner.mapToScene(inner.rect().center()))
        mime = QtCore.QMimeData()
        mime.setData('application/x-gns3-template', template_id.encode())
        move = QtGui.QDragMoveEvent(point, QtCore.Qt.DropAction.CopyAction, mime,
                                   QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.KeyboardModifier.NoModifier)
        view.dragMoveEvent(move)
        assert inner.drop_hover and view._groups.guide_parent is inner
        drop = QtGui.QDropEvent(QtCore.QPointF(point), QtCore.Qt.DropAction.CopyAction, mime,
                               QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.KeyboardModifier.NoModifier)
        with patch('gns3.graphics_view.TemplateManager.instance', return_value=templates):
            view.dropEvent(drop)
        assert drop.isAccepted() and not inner.drop_hover
        assert view._groups.guide_parent is None
        assert len([item for item in inner.members() if isinstance(item, NodeItem)]) == 3
        # Duplicate real server nodes through the asynchronous-callback API adapter.
        view.scene().clearSelection(); outer.setSelected(True)
        # Hold drawing POSTs while the Qt-side copy continues. Any premature
        # PUT would reach the actual server and fail with the reported 404.
        topo._project.defer_drawings = True
        view.duplicateActionSlot()
        gc.collect()  # No timeout or progress dialog may retain these replies.
        deadline = time.monotonic() + 15
        while len(topo._project.pending_drawings) < 5 and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.01)
        assert len(topo._project.pending_drawings) == 5
        assert len(topo._project.call('GET', '/drawings')) == 5
        topo._project.flush_drawings()
        assert len(topo._project.call('GET', '/drawings')) == 10
        assert len(topo._project.call('GET','/nodes'))==6
        assert len(topo._project.call('GET','/links'))==2
        assert len(view._groups.groups())==4
        expected_sizes['Copy of ' + outer.name] = expected_sizes[outer.name]
        assert all(group.rect().size() == expected_sizes[group.name] for group in view._groups.groups())
        copies=view._groups.selected()
        assert len(copies)==1 and isinstance(copies[0],GroupItem)
        assert copies[0].name == 'Copy of ' + outer.name
        copied_nodes = {item.node().node_id() for item in copies[0].descendants() if isinstance(item, NodeItem)}
        original_nodes = {item.node().node_id() for item in outer.descendants() if isinstance(item, NodeItem)}
        assert len(copied_nodes) == 3 and copied_nodes.isdisjoint(original_nodes)
        copied_links = [link for link in topo._project.call('GET', '/links')
                        if {side['node_id'] for side in link['nodes']} <= copied_nodes]
        assert len(copied_links) == 1
        assert not http._active_replies
        # Export then import: GNS3 regenerates all IDs, including drawing IDs.
        archive=request('GET','/projects/'+pid+'/export?include_images=no&keep_compute_ids=yes',raw=True)
        (output / 'hierarchy.gns3p').write_bytes(archive)
        with zipfile.ZipFile(io.BytesIO(archive)) as exported:
            name=next(name for name in exported.namelist() if name.endswith('.gns3'))
            exported_data=json.loads(exported.read(name))
            assert len(exported_data['topology']['nodes'])==6
            print('Exported archive:', len(exported_data['topology']['drawings']), 'drawings including four nested groups')
        newid=str(uuid.uuid4())
        project_ids.append(newid)
        imported=request('POST','/projects/'+newid+'/import',archive)
        request('POST','/projects/'+newid+'/open')
        summary._projectChangedSlot()
        topo._project=Bridge(newid)
        topo._nodes.clear()
        topo._links.clear()
        topo._drawings.clear()
        view._groups.reset()
        view.scene().clear()
        for data in topo._project.call('GET','/nodes'): item_for(data)
        for data in topo._project.call('GET','/drawings'): topo.createDrawing(data)
        view._groups.restore()
        groups=view._groups.groups()
        assert len(groups)==4
        assert all(group.rect().size() == expected_sizes[group.name] for group in groups)
        assert summary.topLevelItemCount() == 2
        assert len([group for group in groups if group.parentItem() is None])==2
        for group in groups:
            if group.name=='LAN 1':
                assert len(group.members())==5
                assert len([item for item in group.members() if isinstance(item,NodeItem)])==3
            else:
                assert len(group.members())==2
                assert len([item for item in group.members() if isinstance(item,GroupItem)])==1
        # The repaired IDs must survive a second load, without name-based fallback.
        for group in groups:
            stored=read_group(topo._project.call('GET','/drawings/'+group.drawing_id())['svg'])
            assert stored['drawing_id']==group.drawing_id()
            for member in stored['children']:
                assert any((item.node().node_id() if isinstance(item,NodeItem) else item.drawing_id())==member['id'] for item in group.members())
        window.resize(1200,800)
        window.show()
        view.resize(1100,700)
        view.show()
        app.processEvents()
        view.fitInView(view.scene().itemsBoundingRect().adjusted(-50,-50,50,50),QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        app.processEvents()
        view.viewport().grab().save(str(output / 'hierarchy.png'))
        summary.setColumnCount(2)
        summary.setHeaderLabels(["Topology Summary", "Console"])
        summary.resize(400, 600)
        summary.show()
        summary.expandAll()
        app.processEvents()
        summary.grab().save(str(output / 'topology-summary.png'))
        # Capture the transient foreground separately from the saved project.
        inner_group = next(group for group in groups if group.name == 'LAN 1')
        direct_node = next(item for item in inner_group.members() if isinstance(item, NodeItem))
        view.enterGroup(inner_group)
        view._groups.beginDrag(direct_node)
        view._groups.showGuides()
        app.processEvents()
        view.viewport().grab().save(str(output / 'alignment-guides.png'))
        view._groups.clearDrag()
        view._groups.leave()
        # Delete just one imported root recursively; its sibling copy remains.
        view.scene().clearSelection()
        root=next(group for group in groups if group.parentItem() is None)
        root.setSelected(True)
        with patch.object(QtWidgets.QMessageBox,'question',return_value=QtWidgets.QMessageBox.StandardButton.Yes):
            view.deleteActionSlot()
        assert len(topo._project.call('GET','/nodes'))==3
        assert len(topo._project.call('GET','/links'))==1
        assert len(view._groups.groups())==2
        print('PASS: template drop, delayed drawing creation, node/link duplication, portable import, ID remapping and recursive deletion')
        print('Artifacts:', output)

    finally:
        for identity in reversed(project_ids):
            try:
                request('DELETE', '/projects/' + identity)
            except Exception as error:
                print('Could not clean test project', identity, error, file=sys.stderr)
        for identity in template_ids:
            try:
                request('DELETE', '/templates/' + identity)
            except Exception as error:
                print('Could not clean test template', identity, error, file=sys.stderr)


if __name__ == '__main__':
    main()
